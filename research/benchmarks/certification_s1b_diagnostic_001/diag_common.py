#!/usr/bin/env python3
"""Standard-library contract, identity and durable journal primitives."""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
APPROVED_PROTOCOL_COMMIT = "a4c1720401913946d776e707f2bcb690189bc942"
PROTOCOL_PINS = {
    "SPEC.json": "c33be233d931449342e1c2f4a63ac0ccbcafee4dab3a0fc93200633ed47713f6",
    "INPUTS.json": "839bd0f90572fb0d9be8540861f805f3ec6c7998d464c586d5fa77180a710736",
    "SOURCE_BINDINGS.json": "205ebe34e18fe08592c6257b9468cd65a7cf6c087727885cd13d790cf26a95d5",
}
RUNTIME_FILES = {"diag_common.py", "worker.py", "engine.py", "supervisor.py",
                 "verify.py", "assessments.py", "runtime_identity.py", "NATIVE_LOCK.json", "package_io.py"}


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha256_bytes(canonical_bytes(value))


def json_bytes(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True,
                      allow_nan=False).encode("ascii") + b"\n"


def fsync_directory(path):
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("wb") as stream:
        stream.write(json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)
    fsync_directory(path.parent)


def load_contract():
    for name, expected in PROTOCOL_PINS.items():
        if sha256_bytes((HERE / name).read_bytes()) != expected:
            raise ValueError("PROTOCOL_BINDING_MISMATCH:" + name)
    return (json.loads((HERE / "SPEC.json").read_bytes()),
            json.loads((HERE / "INPUTS.json").read_bytes()))


def verify_implementation_files():
    """Validate the complete audited source closure, including imported references.

    An implementation manifest is the reviewed trust anchor, not a signature.
    Its own digest is included in each run header; audit pins its commit.
    """
    load_contract()
    manifest_path = HERE / "IMPLEMENTATION_MANIFEST.json"
    manifest = json.loads(manifest_path.read_bytes())
    if manifest["approved_protocol_commit"] != APPROVED_PROTOCOL_COMMIT:
        raise ValueError("IMPLEMENTATION_PROTOCOL_MISMATCH")
    required = {str((HERE / name).relative_to(ROOT)) for name in RUNTIME_FILES}
    for source in ("MANIFEST.json", "SOURCE_BINDINGS.json"):
        required.update(x["path"] for x in json.loads((HERE / source).read_bytes())["entries"])
        required.add(str((HERE / source).relative_to(ROOT)))
    entries = manifest["entries"]
    names = [x["path"] for x in entries]
    if len(names) != len(set(names)) or not required <= set(names):
        raise ValueError("SOURCE_CLOSURE_MEMBERSHIP")
    bindings = {}
    for entry in entries:
        path = ROOT / entry["path"]
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError("UNSAFE_SOURCE_PATH")
        data = path.read_bytes()
        actual = {"sha256": sha256_bytes(data), "bytes": len(data)}
        if actual != {k: entry[k] for k in actual}:
            raise ValueError("SOURCE_BINDING_MISMATCH:" + entry["path"])
        bindings[entry["path"]] = actual
    # Existing source pins are independent of the new manifest.
    for source in ("MANIFEST.json", "SOURCE_BINDINGS.json"):
        for entry in json.loads((HERE / source).read_bytes())["entries"]:
            if bindings[entry["path"]] != {k: entry[k] for k in ("sha256", "bytes")}:
                raise ValueError("HISTORICAL_SOURCE_PIN_MISMATCH")
    data = manifest_path.read_bytes()
    bindings[str(manifest_path.relative_to(ROOT))] = {"sha256": sha256_bytes(data), "bytes": len(data)}
    return bindings


def rational(value):
    if not isinstance(value, str) or len(value) > 20000:
        raise ValueError("INVALID_RATIONAL")
    result = Fraction(value)
    if str(result) != value:
        raise ValueError("NONCANONICAL_RATIONAL")
    return result


def interval(value):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("INVALID_INTERVAL")
    lo, hi = map(rational, value)
    if lo > hi:
        raise ValueError("REVERSED_INTERVAL")
    return lo, hi


def config_binding(specimen, arm, basis_hash):
    radius = Fraction(arm["radius_multiplier"]) * Fraction(specimen["original_half_width"])
    return {
        "specimen_id": specimen["id"], "arm_id": arm["id"],
        "source_sequence": specimen["source_sequence"],
        "source_record_sha256": specimen["source_record_sha256"],
        "source_raw_log_sha256": "328b42afbdb508b631fbccbaf13afbdf5197824ab97822a7c5a4aa755b674679",
        "cell": specimen["cell"], "center": specimen["center"],
        "box": [[str(Fraction(c) - radius), str(Fraction(c) + radius)] for c in specimen["center"]],
        "radius_multiplier": arm["radius_multiplier"], "basis_sha256": basis_hash,
        "precision_bits": arm["precision_bits"], "column_order": arm["column_order"],
        "permutation": list(range(195, -1, -1)) if arm["column_order"] != "identity" else list(range(196)),
        "shifts": [specimen["windows"][w][e] for w in ("lower", "upper") for e in ("left", "right")],
        "expected_negative_counts": [97, 97, 99, 99],
    }


class Journal:
    """One writer; starts are durable before numerical operations are admitted."""
    def __init__(self, path):
        self.path = Path(path)
        if self.path.exists() and self.path.stat().st_size:
            raise ValueError("NO_RESUME")
        self.path.touch(exist_ok=True)
        self.sequence = 0
        self.previous = None
        self.bytes_written = 0

    def emit(self, kind, **payload):
        if set(payload) & {"kind", "sequence", "previous_record_sha256", "record_sha256"}:
            raise ValueError("RESERVED_RECORD_FIELDS")
        record = {"kind": kind, "sequence": self.sequence,
                  "previous_record_sha256": self.previous, **payload}
        record["record_sha256"] = digest(record)
        raw = canonical_bytes(record)
        if self.bytes_written + len(raw) + 1 > 268435456:
            raise ValueError("RAW_EVIDENCE_CAP")
        with self.path.open("ab", buffering=0) as stream:
            stream.write(raw + b"\n")
            os.fsync(stream.fileno())
        fsync_directory(self.path.parent)
        self.bytes_written += len(raw) + 1
        self.previous = sha256_bytes(raw)
        self.sequence += 1
        return record
