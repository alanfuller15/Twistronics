#!/usr/bin/env python3
"""Bounded synthetic controls; never imports or executes the physical model."""
from __future__ import annotations

import copy
import json
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import common
import verify as packet_verify

HERE = Path(__file__).resolve().parent
SYNTHETIC_PROVENANCE_DIGEST = common.sha256_bytes(
    common.canonical_object_bytes({"synthetic": True}))


def require(condition: bool, label: str) -> None:
    if not condition:
        raise RuntimeError(label)
    print("PASS", label)


def synthetic_physical_evidence(cell: tuple[int, int, int]) -> dict:
    x_box, y_box = packet_verify.exact_cell_box(cell)

    def endpoint(label: str, shift: str, expected: int) -> dict:
        pivots = [["-2", "-1"]] * expected + [["1", "2"]] * (196 - expected)
        return {"label": label, "shift": shift, "pivots": pivots,
                "status": "CERTIFIED", "negative": expected,
                "expected_negative": expected}

    definitions = {
        "lower": {"left": "0", "right": "1", "width_meV": "1",
                  "target_lower_meV": "1/100000", "expected_negative": 97},
        "upper": {"left": "2", "right": "3", "width_meV": "1",
                  "target_lower_meV": "1/100000", "expected_negative": 99},
    }
    windows = {
        name: {"width_meV": definition["width_meV"],
               "target_lower_meV": definition["target_lower_meV"],
               "certified": True,
               "endpoints": [endpoint("left", definition["left"], definition["expected_negative"]),
                             endpoint("right", definition["right"], definition["expected_negative"])]}
        for name, definition in definitions.items()
    }
    attempt = {"decimal_digits": 17, "gram_margin_min": ["1", "2"],
               "windows": windows, "certified": True}
    recomputation = copy.deepcopy(attempt)
    recomputation["decimal_digits"] = 10
    recomputation["uses_primary_recorded_shifts"] = True
    return {
        "cell": {**common.cell_ref(cell),
                 "x": [str(value) for value in x_box],
                 "y": [str(value) for value in y_box]},
        "precision_bits": 128,
        "dimension": 196,
        "window_definitions": definitions,
        "primary": attempt,
        "recomputation": recomputation,
    }


def require_verification_error(callable_, code: str, label: str) -> None:
    try:
        callable_()
    except Exception as exc:  # exact code is the retained control contract
        require(code in str(exc), label)
    else:
        raise RuntimeError(label)


def run() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="packet002-kill-") as tmp:
        output = Path(tmp) / "run"
        command = [sys.executable, str(HERE / "supervisor.py"),
                   "--output", str(output),
                   "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
                   "--runtime-provenance-digest", SYNTHETIC_PROVENANCE_DIGEST,
                   "--evaluator", "synthetic", "--fault", "partial_then_block",
                   "--test-soft-seconds", "0.4", "--test-hard-seconds", "1.0",
                   "--verify"]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=10)
        require(completed.returncode == 0, "mid_record_sigkill_supervised_and_verified")
        checks += 1
        receipt = json.loads((output / "SUPERVISOR_RECEIPT.json").read_text())
        results = json.loads((output / "RESULTS.json").read_text())
        partition = json.loads((output / "PARTITION.json").read_text())
        require(receipt["termination_reason"] == "WATCHDOG_TIMEOUT", "timeout_precedence")
        require(receipt["sigkill_sent_at_or_null"] is not None, "hard_sigkill_exercised")
        require(receipt["post_reap_killpg_result_ESRCH"] is True, "process_group_empty_after_reap")
        require(results["status"] == "INCONCLUSIVE_WATCHDOG_TIMEOUT", "timeout_status_retained")
        require(results["attempted_cells"] == 0, "partial_record_not_counted")
        require(len(partition["unprocessed_frontier_cells"]) == 437, "inflight_cell_returned_to_frontier")
        require(len(partition["accepted_cells"]) == 83, "accepted_prefix_preserved")
        require((output / "ATTEMPTS.ndjson").read_bytes().endswith(b"\n"), "partial_fragment_discarded")
        require(receipt["fault_ready_observed"] is True, "fault_point_was_reached")
        require(receipt["pre_trim_durable_log_bytes"] > receipt["post_trim_durable_log_bytes"],
                "partial_fragment_was_trimmed")
        require(not (output / "FAULT_READY").exists(), "fault_marker_removed_before_packaging")
        checks += 11

        check_only = subprocess.run(
            [sys.executable, str(HERE / "verify.py"), "--output", str(output),
             "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
             "--allow-test-mode", "--check-only"], capture_output=True, text=True)
        require(check_only.returncode == 0, "packaged_output_is_repeatably_checkable")
        checks += 1
        (output / "UNEXPECTED").write_text("unexpected\n")
        unexpected = subprocess.run(
            [sys.executable, str(HERE / "verify.py"), "--output", str(output),
             "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
             "--allow-test-mode", "--check-only"], capture_output=True, text=True)
        require(unexpected.returncode != 0 and "OUTPUT_FILE_SET_MISMATCH" in unexpected.stderr,
                "unexpected_output_file_rejected")
        (output / "UNEXPECTED").unlink()
        checks += 1

        # A complete malformed line must fail, unlike an unterminated tail.
        with (output / "ATTEMPTS.ndjson").open("ab") as stream:
            stream.write(b"{}\n")
        raw = (output / "ATTEMPTS.ndjson").read_bytes()
        receipt["durable_log_bytes"] = len(raw)
        receipt["durable_log_sha256"] = hashlib.sha256(raw).hexdigest()
        receipt["post_trim_durable_log_bytes"] = len(raw)
        receipt["pre_trim_durable_log_bytes"] = max(
            receipt["pre_trim_durable_log_bytes"], len(raw))
        common.atomic_json(output / "SUPERVISOR_RECEIPT.json", receipt)
        bad = subprocess.run([sys.executable, str(HERE / "verify.py"),
                              "--output", str(output),
                              "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
                              "--allow-test-mode", "--check-only"],
                             capture_output=True, text=True)
        require(bad.returncode != 0 and "RECORD_SELF_HASH_MISMATCH" in bad.stderr,
                "complete_malformed_record_rejected_by_record_hash")
        checks += 1

    spec, _, _ = common.load_frozen_state()
    state = common.initial_replay_state()
    # I3: exercise the verifier classification with an empty queue at the cap.
    state["frontier"] = []
    state["unresolved"] = [(9, 256, 256)]
    state["attempts"] = spec["limits"]["max_new_attempted_cells"]
    status = packet_verify.classify_status(
        state, {"termination_reason": "NORMAL_EXIT"}, spec)
    require(status == "INCONCLUSIVE_BOUNDED_COVERAGE",
            "empty_queue_precedes_cap_classification")
    checks += 1

    header, line, line_sha = common.hashed_record({
        "kind": "header", "sequence": -1, "previous_record_sha256": None})
    require(common.verify_hashed_record(header, line, None) == line_sha,
            "exact_line_hash_encoding_round_trip")
    checks += 1

    spec, _, _ = common.load_frozen_state()
    cell = (5, 16, 16)
    evidence = synthetic_physical_evidence(cell)
    require(packet_verify.verify_physical_evidence(
        evidence, "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS", spec, cell) == (4, 4),
        "synthetic_physical_evidence_baseline_accepts")
    checks += 1
    mutations = [
        (lambda item: item["cell"].update({"ix": 17}),
         "PHYSICAL_EVIDENCE_CELL_BINDING_MISMATCH", "wrong_cell_evidence_rejected"),
        (lambda item: item.update({"precision_bits": 64}),
         "PHYSICAL_EVIDENCE_PARAMETER_MISMATCH", "wrong_precision_rejected"),
        (lambda item: item.update({"dimension": 192}),
         "PHYSICAL_EVIDENCE_PARAMETER_MISMATCH", "wrong_dimension_rejected"),
        (lambda item: item["primary"].update({"decimal_digits": 16}),
         "PHYSICAL_EVIDENCE_PARAMETER_MISMATCH", "wrong_primary_digits_rejected"),
        (lambda item: item["primary"].update({"certified": False}),
         "PRIMARY_STATUS_MISMATCH", "wrong_primary_certified_flag_rejected"),
        (lambda item: item["recomputation"].update({"certified": False}),
         "RECOMPUTATION_STATUS_MISMATCH", "wrong_recomputation_certified_flag_rejected"),
        (lambda item: item["window_definitions"]["lower"].update({"expected_negative": 96}),
         "FROZEN_WINDOW_DEFINITION_MISMATCH", "wrong_expected_inertia_rejected"),
        (lambda item: item["window_definitions"]["lower"].update({"target_lower_meV": "1/200000"}),
         "FROZEN_WINDOW_DEFINITION_MISMATCH", "wrong_target_window_rejected"),
    ]
    for mutate, code, label in mutations:
        changed = copy.deepcopy(evidence)
        mutate(changed)
        require_verification_error(
            lambda changed=changed: packet_verify.verify_physical_evidence(
                changed, "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS", spec, cell),
            code, label)
        checks += 1

    lock = json.loads(common.WHEEL_LOCK_PATH.read_text())
    provenance = {
        "wheel": lock,
        "installed_native_member_count": 42,
        "loaded_extension_bound_to_wheel": True,
        "mapped_native_library_count": 3,
        "mapped_native_libraries_bound_to_wheel": True,
        "proc_maps_checked": True,
    }
    provenance_header = {
        "runtime_provenance": provenance,
        "runtime_provenance_digest": common.sha256_bytes(
            common.canonical_object_bytes(provenance)),
    }
    packet_verify.verify_runtime_provenance(provenance_header, test_mode=False)
    require(True, "locked_runtime_provenance_accepts")
    checks += 1
    changed_provenance = copy.deepcopy(provenance)
    changed_provenance["wheel"]["sha256"] = "0" * 64
    changed_header = {
        "runtime_provenance": changed_provenance,
        "runtime_provenance_digest": common.sha256_bytes(
            common.canonical_object_bytes(changed_provenance)),
    }
    require_verification_error(
        lambda: packet_verify.verify_runtime_provenance(changed_header, test_mode=False),
        "RUNTIME_WHEEL_LOCK_MISMATCH", "wrong_runtime_wheel_rejected")
    checks += 1

    with tempfile.TemporaryDirectory(prefix="packet002-physical-fault-") as tmp:
        forbidden = subprocess.run(
            [sys.executable, str(HERE / "supervisor.py"),
             "--output", str(Path(tmp) / "run"),
             "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
             "--runtime-provenance-digest", "unused",
             "--evaluator", "physical", "--fault", "partial_then_block"],
            capture_output=True, text=True)
        require(forbidden.returncode != 0
                and "FAULT_INJECTION_REQUIRES_SYNTHETIC_MODE" in forbidden.stderr,
                "physical_fault_injection_rejected_before_execution")
        checks += 1

    with tempfile.TemporaryDirectory(prefix="packet002-cap-") as tmp:
        output = Path(tmp) / "run"
        command = [sys.executable, str(HERE / "supervisor.py"),
                   "--output", str(output),
                   "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
                   "--runtime-provenance-digest", SYNTHETIC_PROVENANCE_DIGEST,
                   "--evaluator", "synthetic", "--verify"]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
        require(completed.returncode == 0, "full_1024_attempt_cap_run_verified")
        results = json.loads((output / "RESULTS.json").read_text())
        require(results["status"] == "INCONCLUSIVE_RESOURCE_CAP",
                "full_cap_status_retained")
        require(results["attempted_cells"] == 1024, "full_cap_attempt_count_retained")
        require(results["primary_factorizations"] == 4096,
                "full_cap_factorization_count_retained")
        second = subprocess.run(
            [sys.executable, str(HERE / "verify.py"), "--output", str(output),
             "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
             "--allow-test-mode", "--check-only"], capture_output=True, text=True)
        require(second.returncode == 0, "full_cap_packet_check_only_replay")
        checks += 5

    require(checks == 34, "expected_control_count")
    print(f"{checks + 1}/{checks + 1} synthetic controls pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
