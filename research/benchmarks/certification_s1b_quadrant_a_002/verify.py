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
from typing import Any

import common


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE_OUTPUT_FILES = {"ATTEMPTS.ndjson", "SUPERVISOR_RECEIPT.json"}


def exact_cell_box(cell: tuple[int, int, int]) -> tuple[list[Fraction], list[Fraction]]:
    depth, ix, iy = cell
    denominator = 1 << depth
    return ([Fraction(ix, denominator), Fraction(ix + 1, denominator)],
            [Fraction(iy, denominator), Fraction(iy + 1, denominator)])


def verify_runtime_provenance(header: dict, *, test_mode: bool) -> None:
    provenance = header.get("runtime_provenance")
    digest = common.sha256_bytes(common.canonical_object_bytes(provenance))
    if digest != header.get("runtime_provenance_digest"):
        raise common.VerificationError("RUNTIME_PROVENANCE_DIGEST_MISMATCH")
    if test_mode:
        if provenance != {"synthetic": True}:
            raise common.VerificationError("SYNTHETIC_PROVENANCE_MISMATCH")
        return
    lock = json.loads(common.WHEEL_LOCK_PATH.read_text())
    if provenance.get("wheel") != lock:
        raise common.VerificationError("RUNTIME_WHEEL_LOCK_MISMATCH")
    required_true = (
        "loaded_extension_bound_to_wheel",
        "mapped_native_libraries_bound_to_wheel",
        "proc_maps_checked",
    )
    if any(provenance.get(name) is not True for name in required_true):
        raise common.VerificationError("RUNTIME_NATIVE_BINDING_MISMATCH")
    if (int(provenance.get("installed_native_member_count", 0)) < 3
            or int(provenance.get("mapped_native_library_count", 0)) < 3):
        raise common.VerificationError("RUNTIME_NATIVE_MEMBER_COUNT_MISMATCH")


def verify_frozen_windows(evidence: dict) -> None:
    case = json.loads(common.CASE_PATH.read_text())
    base_spec = json.loads(common.BASE_S1B_SPEC_PATH.read_text())
    cutoff = case["cutoffs"]["a"]
    lower, upper = cutoff["selected_bands_zero_based"]
    expected = {"lower": lower, "upper": upper + 1}
    target = Fraction(base_spec["target_external_gap_lower_meV"])
    definitions = evidence.get("window_definitions", {})
    if set(definitions) != set(expected):
        raise common.VerificationError("WINDOW_NAME_SET_MISMATCH")
    for name, expected_negative in expected.items():
        definition = definitions[name]
        if (definition.get("expected_negative") != expected_negative
                or Fraction(definition.get("target_lower_meV")) != target):
            raise common.VerificationError("FROZEN_WINDOW_DEFINITION_MISMATCH")
        for attempt_name in ("primary", "recomputation"):
            attempt = evidence.get(attempt_name)
            if attempt is None:
                continue
            window = attempt["windows"][name]
            if (Fraction(window.get("target_lower_meV")) != target
                    or any(factor.get("expected_negative") != expected_negative
                           for factor in window["endpoints"])):
                raise common.VerificationError("FROZEN_WINDOW_RECORD_MISMATCH")


def verify_physical_evidence(evidence: dict, outcome: str, spec: dict,
                             cell: tuple[int, int, int]) -> tuple[int, int]:
    evidence_cell = evidence.get("cell", {})
    x_box, y_box = exact_cell_box(cell)
    if (common.cell_tuple(evidence_cell) != cell
            or [Fraction(value) for value in evidence_cell.get("x", [])] != x_box
            or [Fraction(value) for value in evidence_cell.get("y", [])] != y_box):
        raise common.VerificationError("PHYSICAL_EVIDENCE_CELL_BINDING_MISMATCH")
    case = json.loads(common.CASE_PATH.read_text())
    if (evidence.get("precision_bits") != spec["algorithm"]["precision_bits"]
            or evidence.get("dimension") != case["cutoffs"]["a"]["dimension"]
            or evidence.get("primary", {}).get("decimal_digits") != 17):
        raise common.VerificationError("PHYSICAL_EVIDENCE_PARAMETER_MISMATCH")
    verify_frozen_windows(evidence)
    predecessor_verify = load_module(
        common.PREDECESSOR / "verify.py", "packet002_predecessor_verify")
    predecessor_verify.require_positive_interval(
        evidence["primary"]["gram_margin_min"], "PRIMARY_GRAM_INVALID")
    primary_ok, primary_factors = predecessor_verify.verify_windows(
        evidence["primary"]["windows"], evidence["window_definitions"])
    if evidence["primary"].get("certified") != primary_ok:
        raise common.VerificationError("PRIMARY_STATUS_MISMATCH")
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
        if recomputation.get("certified") != final_ok:
            raise common.VerificationError("RECOMPUTATION_STATUS_MISMATCH")
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


def compressed_parts(payload: bytes, part_bytes: int) -> list[tuple[str, bytes]]:
    compressed = gzip.compress(payload, compresslevel=9, mtime=0)
    return [(f"ATTEMPTS.ndjson.gz.part{index:03d}",
             compressed[offset:offset + part_bytes])
            for index, offset in enumerate(range(0, len(compressed), part_bytes))]


def part_records(parts: list[tuple[str, bytes]]) -> list[dict[str, Any]]:
    return [{"path": name, "bytes": len(payload),
             "sha256": hashlib.sha256(payload).hexdigest()}
            for name, payload in parts]


def write_parts(output: Path, parts: list[tuple[str, bytes]]) -> None:
    for name, payload in parts:
        path = output / name
        with path.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    common.fsync_directory(output)


def encoded_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True,
                       allow_nan=False).encode("ascii") + b"\n")


def require_exact_files(output: Path, expected: set[str]) -> None:
    actual = {path.name for path in output.iterdir()}
    if actual != expected:
        raise common.VerificationError(
            "OUTPUT_FILE_SET_MISMATCH:expected=" + ",".join(sorted(expected))
            + ":actual=" + ",".join(sorted(actual)))


def verify_receipt_consistency(receipt: dict, header: dict, raw_bytes: int) -> None:
    if (receipt.get("test_mode") != bool(header.get("test_mode"))
            or receipt.get("fault") != header.get("fault")
            or receipt.get("post_trim_durable_log_bytes") != raw_bytes
            or int(receipt.get("pre_trim_durable_log_bytes", -1)) < raw_bytes):
        raise common.VerificationError("RECEIPT_INTERNAL_BINDING_MISMATCH")
    reason = receipt.get("termination_reason")
    sigterm = receipt.get("sigterm_sent_at_or_null")
    sigkill = receipt.get("sigkill_sent_at_or_null")
    if reason == "NORMAL_EXIT":
        if receipt.get("worker_exit_code_or_signal") != 0 or sigterm is not None or sigkill is not None:
            raise common.VerificationError("NORMAL_EXIT_RECEIPT_INCONSISTENT")
    elif reason == "WATCHDOG_TIMEOUT":
        if sigterm is None and sigkill is None:
            raise common.VerificationError("TIMEOUT_WITHOUT_DEADLINE_SIGNAL")
        if sigterm is not None and sigterm < receipt.get("soft_deadline_at", float("inf")):
            raise common.VerificationError("EARLY_SIGTERM_TIMESTAMP")
        if sigkill is not None and sigkill < receipt.get("hard_deadline_at", float("inf")):
            raise common.VerificationError("EARLY_SIGKILL_TIMESTAMP")
    fault = header.get("fault")
    if fault == "partial_then_block":
        if (not header.get("test_mode") or receipt.get("fault_ready_observed") is not True
                or receipt.get("pre_trim_durable_log_bytes", 0) <= raw_bytes):
            raise common.VerificationError("FAULT_MARKER_MODE_MISMATCH")
    elif receipt.get("fault_ready_observed") is not False:
        raise common.VerificationError("UNEXPECTED_FAULT_MARKER")


def classify_status(state: dict, receipt: dict, spec: dict) -> str:
    reason = receipt.get("termination_reason")
    if reason == "WATCHDOG_TIMEOUT":
        return "INCONCLUSIVE_WATCHDOG_TIMEOUT"
    if reason != "NORMAL_EXIT":
        raise common.VerificationError("UNEXPECTED_TERMINATION")
    if not state["frontier"]:
        return ("CERTIFIED_CUTOFF_A_HARD_QUADRANT_COVERAGE"
                if not state["unresolved"] else "INCONCLUSIVE_BOUNDED_COVERAGE")
    if not common.admission_has_room(state, spec):
        return "INCONCLUSIVE_RESOURCE_CAP"
    raise common.VerificationError("NORMAL_EXIT_WITH_WORK_REMAINING")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--allow-test-mode", action="store_true")
    parser.add_argument("--check-only", action="store_true",
                        help="validate an already packaged directory without writing")
    args = parser.parse_args()
    output = args.output.resolve()
    common.verify_implementation_files()
    spec, predecessor_partition, _ = common.load_frozen_state()
    if not output.is_dir():
        raise common.VerificationError("OUTPUT_DIRECTORY_MISSING")
    if not args.check_only:
        require_exact_files(output, BASE_OUTPUT_FILES)
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
    test_mode = bool(header.get("test_mode"))
    if header.get("evaluator") != ("synthetic" if test_mode else "physical"):
        raise common.VerificationError("HEADER_EVALUATOR_MODE_MISMATCH")
    if header.get("fault") != "none" and not test_mode:
        raise common.VerificationError("PHYSICAL_FAULT_INJECTION_FORBIDDEN")
    verify_runtime_provenance(header, test_mode=test_mode)
    verify_receipt_consistency(receipt, header, len(raw))

    state = common.initial_replay_state()
    max_depth = spec["algorithm"]["max_depth"]
    for record in records:
        evidence = record["full_interval_evidence"]
        if test_mode:
            if not args.allow_test_mode or evidence.get("synthetic") is not True:
                raise common.VerificationError("SYNTHETIC_EVIDENCE_NOT_ALLOWED")
            expected_counts = (4, 0)
        else:
            expected_counts = verify_physical_evidence(
                evidence, record["outcome"], spec, common.cell_tuple(record["cell"]))
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

    status = classify_status(state, receipt, spec)

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
    partition_bytes = encoded_json(partition)
    parts = compressed_parts(raw, spec["replay_and_packaging"]["part_bytes"])
    part_entries = part_records(parts)
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
                        "sha256": hashlib.sha256(raw).hexdigest(), "parts": part_entries},
        "partition": {"path": "PARTITION.json",
                      "sha256": hashlib.sha256(partition_bytes).hexdigest()},
        "claim_ceiling": spec["claim_ceiling"],
    }
    results_bytes = encoded_json(results)
    final_files = BASE_OUTPUT_FILES | {"PARTITION.json", "RESULTS.json"} | {
        name for name, _ in parts}
    if args.check_only:
        require_exact_files(output, final_files)
        expected_payloads = {
            "PARTITION.json": partition_bytes,
            "RESULTS.json": results_bytes,
            **dict(parts),
        }
        for name, expected in expected_payloads.items():
            if (output / name).read_bytes() != expected:
                raise common.VerificationError("PACKAGED_FILE_BINDING_MISMATCH:" + name)
    else:
        common.atomic_json(output / "PARTITION.json", partition)
        write_parts(output, parts)
        common.atomic_json(output / "RESULTS.json", results)
        require_exact_files(output, final_files)
    print("PASS_PACKET002_REPLAY")
    print(json.dumps({"status": status, "attempts": state["attempts"],
                      "frontier": len(state["frontier"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
