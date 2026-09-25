#!/usr/bin/env python3
"""Shared deterministic state and durable-record rules for packet 002."""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SPEC_PATH = HERE / "SPEC.json"
PREDECESSOR = ROOT / "research/benchmarks/certification_s1b_quadrant_a_001"
PREDECESSOR_PARTITION = PREDECESSOR / "PARTITION.json"
PREDECESSOR_RESULTS = PREDECESSOR / "RESULTS.json"
IMPLEMENTATION_MANIFEST = HERE / "IMPLEMENTATION_MANIFEST.json"
CASE_PATH = ROOT / "docs/certification-readiness/CASE.json"
WHEEL_LOCK_PATH = ROOT / "research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json"
BASE_S1B_SPEC_PATH = ROOT / "research/benchmarks/certification_s1b_001/SPEC.json"

APPROVED_PROTOCOL_COMMIT = "8c86166a954b870145858ff0b783a5983fd90521"
PREDECESSOR_PARTITION_SHA256 = "2bbc19927b996e6d3b43ed9c17fe1d3b92f029bd1866cc031390b76d5814e000"
PREDECESSOR_RESULTS_SHA256 = "e38b8a5d71f5a21521f0dde17924393e3e334a9d22ed263a7fbf567da491fa45"


class VerificationError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_object_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def canonical_line(value: Any) -> bytes:
    return canonical_object_bytes(value) + b"\n"


def hashed_record(value: dict[str, Any]) -> tuple[dict[str, Any], bytes, str]:
    """Return record, exact line, and SHA of exact line bytes excluding newline.

    ``record_sha256`` hashes the canonical object with that field omitted.
    ``previous_record_sha256`` always means the SHA-256 of the exact preceding
    complete canonical line excluding its newline.  The header follows the
    same rules and has previous_record_sha256=null.  This is the I1 encoding.
    """
    if "record_sha256" in value:
        raise VerificationError("RECORD_HASH_FIELD_ALREADY_PRESENT")
    record = dict(value)
    record["record_sha256"] = sha256_bytes(canonical_object_bytes(record))
    line_without_newline = canonical_object_bytes(record)
    return record, line_without_newline + b"\n", sha256_bytes(line_without_newline)


def verify_hashed_record(record: dict[str, Any], exact_line: bytes,
                         expected_previous: str | None) -> str:
    if exact_line.endswith(b"\n"):
        exact_line = exact_line[:-1]
    if canonical_object_bytes(record) != exact_line:
        raise VerificationError("NONCANONICAL_RECORD")
    claimed = record.get("record_sha256")
    unsigned = dict(record)
    unsigned.pop("record_sha256", None)
    if claimed != sha256_bytes(canonical_object_bytes(unsigned)):
        raise VerificationError("RECORD_SELF_HASH_MISMATCH")
    if record.get("previous_record_sha256") != expected_previous:
        raise VerificationError("RECORD_CHAIN_MISMATCH")
    return sha256_bytes(exact_line)


def fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def append_durable(path: Path, line: bytes) -> None:
    with path.open("ab", buffering=0) as stream:
        stream.write(line)
        stream.flush()
        os.fsync(stream.fileno())
    fsync_directory(path.parent)


def atomic_json(path: Path, value: Any) -> None:
    data = json.dumps(value, sort_keys=True, indent=2,
                      ensure_ascii=True, allow_nan=False).encode("ascii") + b"\n"
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)
    fsync_directory(path.parent)


def cell_tuple(value: dict[str, Any] | list[int] | tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(value, dict):
        return int(value["depth"]), int(value["ix"]), int(value["iy"])
    return tuple(map(int, value))  # type: ignore[return-value]


def cell_ref(cell: tuple[int, int, int]) -> dict[str, int]:
    return {"depth": cell[0], "ix": cell[1], "iy": cell[2]}


def children(cell: tuple[int, int, int]) -> list[tuple[int, int, int]]:
    depth, ix, iy = cell
    return [(depth + 1, 2 * ix + xb, 2 * iy + yb)
            for xb in (0, 1) for yb in (0, 1)]


def axis_distance(target: Fraction, lo: Fraction, hi: Fraction) -> Fraction:
    if target < lo:
        return lo - target
    if target > hi:
        return target - hi
    return Fraction(0)


def priority_key(cell: tuple[int, int, int]) -> tuple[Fraction, int, int, int]:
    depth, ix, iy = cell
    denominator = 1 << depth
    target = Fraction(23, 32)
    dx = axis_distance(target, Fraction(ix, denominator), Fraction(ix + 1, denominator))
    dy = axis_distance(target, Fraction(iy, denominator), Fraction(iy + 1, denominator))
    return max(dx, dy), -depth, ix, iy


def priority_record(cell: tuple[int, int, int]) -> list[int]:
    distance, negative_depth, ix, iy = priority_key(cell)
    return [distance.numerator, distance.denominator, negative_depth, ix, iy]


def load_frozen_state() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if sha256_file(PREDECESSOR_PARTITION) != PREDECESSOR_PARTITION_SHA256:
        raise VerificationError("PREDECESSOR_PARTITION_BINDING_MISMATCH")
    if sha256_file(PREDECESSOR_RESULTS) != PREDECESSOR_RESULTS_SHA256:
        raise VerificationError("PREDECESSOR_RESULTS_BINDING_MISMATCH")
    spec = json.loads(SPEC_PATH.read_text())
    partition = json.loads(PREDECESSOR_PARTITION.read_text())
    results = json.loads(PREDECESSOR_RESULTS.read_text())
    if (len(partition["accepted_cells"]), len(partition["unprocessed_frontier_cells"]),
            len(partition["unresolved_max_depth_cells"])) != (83, 437, 0):
        raise VerificationError("PREDECESSOR_EXACT_COUNT_MISMATCH")
    if results["partition"]["sha256"] != PREDECESSOR_PARTITION_SHA256:
        raise VerificationError("PREDECESSOR_CROSS_BINDING_MISMATCH")
    return spec, partition, results


def verify_implementation_files() -> None:
    manifest = json.loads(IMPLEMENTATION_MANIFEST.read_text())
    if manifest.get("approved_protocol_commit") != APPROVED_PROTOCOL_COMMIT:
        raise VerificationError("IMPLEMENTATION_PROTOCOL_BINDING_MISMATCH")
    for item in manifest.get("files", []):
        path = ROOT / item["path"]
        if (not path.is_file() or path.stat().st_size != item["bytes"]
                or sha256_file(path) != item["sha256"]):
            raise VerificationError("IMPLEMENTATION_FILE_BINDING_MISMATCH:" + item["path"])


def initial_replay_state() -> dict[str, Any]:
    _, partition, _ = load_frozen_state()
    return {
        "accepted": [cell_tuple(c) for c in partition["accepted_cells"]],
        "unresolved": [cell_tuple(c) for c in partition["unresolved_max_depth_cells"]],
        "frontier": [cell_tuple(c) for c in partition["unprocessed_frontier_cells"]],
        "attempts": 0,
        "primary_factorizations": 0,
        "recomputation_factorizations": 0,
    }


def select_current_minimum(frontier: list[tuple[int, int, int]]) -> tuple[int, int, int]:
    if not frontier:
        raise VerificationError("EMPTY_FRONTIER_SELECTION")
    return min(frontier, key=priority_key)


def apply_attempt(state: dict[str, Any], record: dict[str, Any], max_depth: int) -> None:
    cell = cell_tuple(record["cell"])
    expected = select_current_minimum(state["frontier"])
    if cell != expected or record["priority_key"] != priority_record(cell):
        raise VerificationError("PRIORITY_ORDER_MISMATCH")
    state["frontier"].remove(cell)
    outcome = record["outcome"]
    if outcome == "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS":
        state["accepted"].append(cell)
    elif outcome == "INCONCLUSIVE" and cell[0] < max_depth:
        state["frontier"].extend(children(cell))
    elif outcome == "INCONCLUSIVE" and cell[0] == max_depth:
        state["unresolved"].append(cell)
    else:
        raise VerificationError("ATTEMPT_OUTCOME_INVALID")
    state["attempts"] += 1
    state["primary_factorizations"] += int(record["primary_factorizations"])
    state["recomputation_factorizations"] += int(record["recomputation_factorizations"])


def admission_has_room(state: dict[str, Any], spec: dict[str, Any]) -> bool:
    limits = spec["limits"]
    reserve = spec["admission"]["require_room_for"]
    total = state["primary_factorizations"] + state["recomputation_factorizations"]
    return (
        state["attempts"] + reserve["attempted_cells"] <= limits["max_new_attempted_cells"]
        and state["primary_factorizations"] + reserve["primary_factorizations"] <= limits["max_new_primary_factorizations"]
        and state["recomputation_factorizations"] + reserve["recomputation_factorizations"] <= limits["max_new_recomputation_factorizations"]
        and total + reserve["total_factorizations"] <= limits["max_new_total_factorizations"]
    )


def is_ancestor(parent: tuple[int, int, int], child: tuple[int, int, int]) -> bool:
    pd, px, py = parent
    cd, cx, cy = child
    if pd >= cd:
        return False
    shift = cd - pd
    return cx >> shift == px and cy >> shift == py


def validate_complete_partition(state: dict[str, Any]) -> Fraction:
    cells = list(state["accepted"]) + list(state["unresolved"]) + list(state["frontier"])
    if len(cells) != len(set(cells)):
        raise VerificationError("PARTITION_DUPLICATE")
    for i, first in enumerate(cells):
        for second in cells[i + 1:]:
            if is_ancestor(first, second) or is_ancestor(second, first):
                raise VerificationError("PARTITION_ANCESTOR_OVERLAP")
    area = sum((Fraction(4 ** (1 - cell[0])) for cell in cells), Fraction(0))
    if area != 1:
        raise VerificationError("PARTITION_AREA_MISMATCH")
    return area


def read_complete_lines(path: Path) -> tuple[list[bytes], bool]:
    data = path.read_bytes()
    complete = data.endswith(b"\n")
    if not complete:
        cut = data.rfind(b"\n")
        data = data[:cut + 1] if cut >= 0 else b""
    return data.splitlines(keepends=True), complete


def parse_and_verify_log(path: Path, *, allow_test_mode: bool = False) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    lines, complete = read_complete_lines(path)
    if not complete:
        raise VerificationError("UNRECOVERED_TRAILING_FRAGMENT")
    if not lines:
        raise VerificationError("MISSING_LOG_HEADER")
    records: list[dict[str, Any]] = []
    previous: str | None = None
    for index, line in enumerate(lines):
        try:
            record = json.loads(line)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise VerificationError("MALFORMED_COMPLETE_RECORD") from exc
        previous = verify_hashed_record(record, line, previous)
        if index == 0:
            if record.get("kind") != "header" or record.get("sequence") != -1:
                raise VerificationError("INVALID_LOG_HEADER")
            if record.get("test_mode") and not allow_test_mode:
                raise VerificationError("TEST_LOG_NOT_ALLOWED")
            header = record
        else:
            if record.get("kind") != "attempt" or record.get("sequence") != index - 1:
                raise VerificationError("INVALID_ATTEMPT_SEQUENCE")
            records.append(record)
    return header, records
