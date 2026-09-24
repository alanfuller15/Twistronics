#!/usr/bin/env python3
"""Offline authoritative replay, evidence verification and packaging."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

import common


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_physical_evidence(evidence: dict, outcome: str, spec: dict) -> tuple[int, int]:
    predecessor_verify = load_module(
        common.PREDECESSOR / "verify.py", "packet002_predecessor_verify")
    predecessor_verify.require_positive_interval(
        evidence["primary"]["gram_margin_min"], "PRIMARY_GRAM_INVALID")
    primary_ok, primary_factors = predecessor_verify.verify_windows(
        evidence["primary"]["windows"], evidence["window_definitions"])
    recomputation = evidence["recomputation"]
    recompute_factors = 0
    final_ok = False
    if primary_ok:
        if recomputation is None or not recomputation["uses_primary_recorded_shifts"]:
            raise common.VerificationError("MISSING_RECOMPUTATION")
        if recomputation["decimal_digits"] != spec["algorithm"]["recomputation_decimal_digits"]:
            raise common.VerificationError("RECOMPUTATION_DIGITS_MISMATCH")
        predecessor_verify.require_positive_interval(
            recomputation["gram_margin_min"], "RECOMPUTATION_GRAM_INVALID")
        final_ok, recompute_factors = predecessor_verify.verify_windows(
            recomputation["windows"], evidence["window_definitions"])
    elif recomputation is not None:
        raise common.VerificationError("UNNECESSARY_RECOMPUTATION")
    expected = "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS" if final_ok else "INCONCLUSIVE"
    if outcome != expected or primary_factors != 4 or recompute_factors not in (0, 4):
        raise common.VerificationError("PHYSICAL_EVIDENCE_STATUS_MISMATCH")
    return primary_factors, recompute_factors


def area(cells: list[tuple[int, int, int]]) -> Fraction:
    return sum((Fraction(4 ** (1 - c[0])) for c in cells), Fraction(0))


def histogram(cells: list[tuple[int, int, int]]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(c[0] for c in cells).items())}


def write_parts(output: Path, payload: bytes, part_bytes: int) -> list[dict]:
    compressed = gzip.compress(payload, compresslevel=9, mtime=0)
    parts = []
    for index, offset in enumerate(range(0, len(compressed), part_bytes)):
        path = output / f"ATTEMPTS.ndjson.gz.part{index:03d}"
        with path.open("xb") as stream:
            stream.write(compressed[offset:offset + part_bytes])
            stream.flush()
            os.fsync(stream.fileno())
        parts.append({"path": path.name, "bytes": path.stat().st_size,
                      "sha256": common.sha256_file(path)})
    common.fsync_directory(output)
    return parts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--allow-test-mode", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    common.verify_implementation_files()
    spec, predecessor_partition, _ = common.load_frozen_state()
    log_path = output / "ATTEMPTS.ndjson"
    receipt_path = output / "SUPERVISOR_RECEIPT.json"
    if not log_path.is_file() or not receipt_path.is_file():
        raise common.VerificationError("MISSING_LOG_OR_RECEIPT")
    receipt = json.loads(receipt_path.read_text())
    if (receipt.get("approved_protocol_commit") != common.APPROVED_PROTOCOL_COMMIT
            or receipt.get("implementation_commit") != args.implementation_commit
            or not receipt.get("post_reap_killpg_result_ESRCH")):
        raise common.VerificationError("RECEIPT_BINDING_OR_REAP_MISMATCH")
    raw = log_path.read_bytes()
    if (receipt.get("durable_log_bytes") != len(raw)
            or receipt.get("durable_log_sha256") != hashlib.sha256(raw).hexdigest()):
        raise common.VerificationError("RECEIPT_LOG_BINDING_MISMATCH")
    header, records = common.parse_and_verify_log(
        log_path, allow_test_mode=args.allow_test_mode)
    if (header.get("approved_protocol_commit") != common.APPROVED_PROTOCOL_COMMIT
            or header.get("predecessor_partition_sha256") != common.PREDECESSOR_PARTITION_SHA256
            or header.get("predecessor_results_sha256") != common.PREDECESSOR_RESULTS_SHA256
            or header.get("implementation_commit") != args.implementation_commit):
        raise common.VerificationError("HEADER_BINDING_MISMATCH")

    state = common.initial_replay_state()
    max_depth = spec["algorithm"]["max_depth"]
    test_mode = bool(header.get("test_mode"))
    for record in records:
        evidence = record["full_interval_evidence"]
        if test_mode:
            if not args.allow_test_mode or evidence.get("synthetic") is not True:
                raise common.VerificationError("SYNTHETIC_EVIDENCE_NOT_ALLOWED")
            expected_counts = (4, 0)
        else:
            expected_counts = verify_physical_evidence(evidence, record["outcome"], spec)
        if expected_counts != (record["primary_factorizations"],
                               record["recomputation_factorizations"]):
            raise common.VerificationError("FACTORIZATION_COUNT_MISMATCH")
        common.apply_attempt(state, record, max_depth)
    common.validate_complete_partition(state)
    if state["accepted"][:83] != [common.cell_tuple(c) for c in predecessor_partition["accepted_cells"]]:
        raise common.VerificationError("PREDECESSOR_ACCEPTED_PREFIX_MISMATCH")

    limits = spec["limits"]
    total_factors = state["primary_factorizations"] + state["recomputation_factorizations"]
    if (state["attempts"] > limits["max_new_attempted_cells"]
            or state["primary_factorizations"] > limits["max_new_primary_factorizations"]
            or state["recomputation_factorizations"] > limits["max_new_recomputation_factorizations"]
            or total_factors > limits["max_new_total_factorizations"]):
        raise common.VerificationError("CAP_EXCEEDED")

    reason = receipt.get("termination_reason")
    if reason == "WATCHDOG_TIMEOUT":
        status = "INCONCLUSIVE_WATCHDOG_TIMEOUT"
    elif reason != "NORMAL_EXIT":
        raise common.VerificationError("UNEXPECTED_TERMINATION")
    elif not state["frontier"]:
        status = ("CERTIFIED_CUTOFF_A_HARD_QUADRANT_COVERAGE"
                  if not state["unresolved"] else "INCONCLUSIVE_BOUNDED_COVERAGE")
    elif not common.admission_has_room(state, spec):
        status = "INCONCLUSIVE_RESOURCE_CAP"
    else:
        raise common.VerificationError("NORMAL_EXIT_WITH_WORK_REMAINING")

    partition = {
        "schema_version": 2,
        "accepted_cells": [common.cell_ref(c) for c in state["accepted"]],
        "unresolved_max_depth_cells": [common.cell_ref(c) for c in state["unresolved"]],
        "unprocessed_frontier_cells": [common.cell_ref(c) for c in sorted(state["frontier"], key=common.priority_key)],
        "accepted_depth_histogram": histogram(state["accepted"]),
        "unresolved_depth_histogram": histogram(state["unresolved"]),
        "frontier_depth_histogram": histogram(state["frontier"]),
        "accepted_area_fraction_of_quadrant": str(area(state["accepted"])),
        "unresolved_area_fraction_of_quadrant": str(area(state["unresolved"])),
        "frontier_area_fraction_of_quadrant": str(area(state["frontier"])),
        "complete_disjoint_partition": True,
    }
    common.atomic_json(output / "PARTITION.json", partition)
    parts = write_parts(output, raw, spec["replay_and_packaging"]["part_bytes"])
    results = {
        "schema_version": 2,
        "packet_id": spec["packet_id"],
        "status": status,
        "approved_protocol_commit": common.APPROVED_PROTOCOL_COMMIT,
        "implementation_commit": args.implementation_commit,
        "test_mode": test_mode,
        "attempted_cells": state["attempts"],
        "newly_accepted_cells": len(state["accepted"]) - 83,
        "unresolved_max_depth_cells": len(state["unresolved"]),
        "unprocessed_frontier_cells": len(state["frontier"]),
        "primary_factorizations": state["primary_factorizations"],
        "recomputation_factorizations": state["recomputation_factorizations"],
        "total_factorizations": total_factors,
        "durable_log": {"path": log_path.name, "bytes": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(), "parts": parts},
        "partition": {"path": "PARTITION.json",
                      "sha256": common.sha256_file(output / "PARTITION.json")},
        "claim_ceiling": spec["claim_ceiling"],
    }
    common.atomic_json(output / "RESULTS.json", results)
    print("PASS_PACKET002_REPLAY")
    print(json.dumps({"status": status, "attempts": state["attempts"],
                      "frontier": len(state["frontier"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
