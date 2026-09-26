#!/usr/bin/env python3
"""Materialize the hosted packet-002 run and perform exact check-only replay."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUN = HERE / "RUN"
VERIFY = HERE / "verify.py"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    destination = args.destination.resolve()
    if destination.exists():
        raise RuntimeError("DESTINATION_ALREADY_EXISTS")
    destination.mkdir(parents=True)

    results = json.loads((RUN / "RESULTS.json").read_text())
    for name in ("RESULTS.json", "PARTITION.json", "SUPERVISOR_RECEIPT.json"):
        shutil.copyfile(RUN / name, destination / name)
    compressed = bytearray()
    for entry in results["durable_log"]["parts"]:
        source = RUN / entry["path"]
        data = source.read_bytes()
        if len(data) != entry["bytes"] or sha256_bytes(data) != entry["sha256"]:
            raise RuntimeError("COMPRESSED_PART_BINDING_MISMATCH")
        shutil.copyfile(source, destination / entry["path"])
        compressed.extend(data)
    raw = gzip.decompress(bytes(compressed))
    if len(raw) != results["durable_log"]["bytes"]:
        raise RuntimeError("RAW_LOG_SIZE_MISMATCH")
    if sha256_bytes(raw) != results["durable_log"]["sha256"]:
        raise RuntimeError("RAW_LOG_SHA256_MISMATCH")
    (destination / "ATTEMPTS.ndjson").write_bytes(raw)

    command = [
        sys.executable,
        str(VERIFY),
        "--output", str(destination),
        "--implementation-commit", results["implementation_commit"],
        "--check-only",
    ]
    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
