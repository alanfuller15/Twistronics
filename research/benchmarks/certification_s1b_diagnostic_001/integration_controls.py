#!/usr/bin/env python3
"""Supervised synthetic execution and adversarial exact-record replay controls.

Never selects the physical evaluator. The all-zero commit identifies unpublished
test source bytes; the run header binds the complete implementation manifest.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

import diag_common as C
import verify as V
from assessments import assess
from package_io import materialize, write_hosted

TEST_COMMIT = "0" * 40


def chain(records):
    lines, previous = [], None
    for index, original in enumerate(records):
        rec = copy.deepcopy(original)
        rec.pop("record_sha256", None)
        rec["sequence"], rec["previous_record_sha256"] = index, previous
        rec["record_sha256"] = C.digest(rec)
        raw = C.canonical_bytes(rec)
        lines.append(raw + b"\n")
        previous = C.sha256_bytes(raw)
    return b"".join(lines)


def run(work, retained=None):
    spec, inputs = C.load_contract()
    bindings = C.verify_implementation_files()
    controls = []
    def ok(name, condition):
        if not condition:
            raise AssertionError(name)
        controls.append({"name": name, "pass": True})
    def supervise(name, profile, fault="none"):
        out = work / name
        command = [sys.executable, "-B", str(C.HERE / "supervisor.py"), "--output", str(out),
                   "--implementation-commit", TEST_COMMIT, "--evaluator", "synthetic",
                   "--synthetic-profile", profile, "--fault", fault]
        if fault != "none":
            command += ["--test-soft-seconds", "12", "--test-hard-seconds", "13"]
        done = subprocess.run(command, capture_output=True, text=True, timeout=90)
        if done.returncode:
            raise AssertionError("SUPERVISOR_FAILURE:" + done.stderr[-1500:])
        return out, json.loads((out / "RESULTS.json").read_bytes())
    default, complete = supervise("complete", "default")
    ok("complete_frozen_56_configurations", complete["status"] == "DIAGNOSTIC_COMPLETE" and complete["configurations_completed"] == 56)
    ok("all_448_durable_factorization_starts", (complete["primary_factorizations_started"], complete["verification_factorizations_started"]) == (224, 224))
    ok("seven_retained_bases_and_no_more", complete["eigensolver_calls_started"] == complete["bases_retained"] == 7)
    ok("faithful_historical_baselines", complete["baseline_divergence_detected"] is False and complete["control_mismatch_detected"] is False)
    mixed, mixed_result = supervise("mixed", "mixed")
    ok("mixed_complete_control_mismatch_terminal", mixed_result["status"] == "CONTROL_MISMATCH_REVIEW_REQUIRED")
    ok("complete_divergence_and_mismatch_retained", mixed_result["baseline_divergence_flagged_ids"] == ["upper_left"] and mixed_result["control_mismatch_flagged_ids"] == ["accepted_lower"])
    ok("gram_skips_consume_zero_calls", (mixed_result["primary_factorizations_started"], mixed_result["verification_factorizations_started"]) == (216, 216))
    interrupted, interrupted_result = supervise("sigkill", "mixed", "partial_then_block")
    receipt = json.loads((interrupted / "SUPERVISOR_RECEIPT.json").read_bytes())
    ok("real_sigkill_after_all_baselines", receipt["worker_exit_code_or_signal"] == -9 and receipt["fault_ready_observed"] is True and receipt["post_reap_killpg_result_ESRCH"] is True)
    ok("only_incomplete_final_line_trimmed", receipt["pre_trim_durable_log_bytes"] > receipt["post_trim_durable_log_bytes"] and (interrupted / "EVENTS.ndjson").read_bytes().endswith(b"\n"))
    ok("watchdog_keeps_both_material_flags", interrupted_result["status"] == "DIAGNOSTIC_INCOMPLETE_WATCHDOG" and interrupted_result["configurations_completed"] == 7 and interrupted_result["control_mismatch_detected"] is True and interrupted_result["baseline_divergence_detected"] is True)

    for label, out in (("complete", default), ("mixed", mixed), ("sigkill", interrupted)):
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in out.iterdir()}
        V.finalize(out, TEST_COMMIT, allow_test_mode=True, check_only=True)
        after = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in out.iterdir()}
        ok(label + "_check_only_is_read_only", before == after)
        hosted = work / (label + "_hosted")
        write_hosted(out, hosted)
        restored = work / (label + "_restored")
        materialize(hosted, restored)
        V.finalize(restored, TEST_COMMIT, allow_test_mode=True, check_only=True)
        ok(label + "_hosted_lossless_replay", (out / "RESULTS.json").read_bytes() == (restored / "RESULTS.json").read_bytes())
        if retained:
            shutil.copytree(hosted, retained / label)

    raw = (default / "EVENTS.ndjson").read_bytes()
    records = [json.loads(line) for line in raw.splitlines()]
    def replay(data):
        r = V.Replay(spec, inputs, TEST_COMMIT, bindings, True)
        r.consume(data)
        return r
    def rejection(name, kind, change, predicate=lambda r: True):
        altered = copy.deepcopy(records)
        rec = next(r for r in altered if r["kind"] == kind and predicate(r))
        change(rec)
        r = replay(chain(altered))
        ok(name, r.error is not None)
    rejection("header_protocol_identity", "HEADER", lambda r: r.update(approved_protocol_commit="f" * 40))
    rejection("full_source_closure_required", "HEADER", lambda r: r["source_bindings"].pop(next(iter(r["source_bindings"]))))
    def float_source_size(record):
        entry = next(iter(record["source_bindings"].values()))
        entry["bytes"] = float(entry["bytes"])
    rejection("source_size_integer_cannot_be_equivalent_float", "HEADER", float_source_size)
    rejection("conflicting_extra_endpoint_binding", "CALL_FINISHED", lambda r: r.update(basis_sha256="0" * 64))
    rejection("basis_hash_binding", "EIGEN_FINISHED", lambda r: r["basis"][0].__setitem__(0, "2"))
    rejection("all_seven_bases_before_seal", "BASIS_SEALED", lambda r: r["basis_hashes"].pop("upper_left"))
    rejection("frozen_cell_binding", "CONFIG_STARTED", lambda r: r["binding"]["cell"].update(ix=353))
    rejection("cell_integer_cannot_be_equivalent_float", "CONFIG_STARTED",
              lambda r: r["binding"]["cell"].update(ix=float(r["binding"]["cell"]["ix"])))
    rejection("exact_window_binding", "CONFIG_STARTED", lambda r: r["binding"]["shifts"].__setitem__(0, "0"))
    rejection("exact_radius_box_binding", "CONFIG_STARTED", lambda r: r["binding"]["box"][0].__setitem__(0, "0"))
    rejection("fresh_256_assembly_required", "GRAM_CHECK", lambda r: r["evidence"].update(assembly_precision_bits=128), lambda r: r["arm_id"] == "point_256")
    rejection("gram_reverse_interval", "GRAM_CHECK", lambda r: r["evidence"]["gram_margins"].__setitem__(0, ["2", "1"]))
    rejection("gram_nonfinite_rejected", "GRAM_CHECK", lambda r: r["evidence"]["gram_margins"].__setitem__(0, ["NaN", "1"]))
    rejection("call_cannot_follow_uncertified_gram", "GRAM_CHECK", lambda r: r["evidence"]["gram_margins"].__setitem__(0, ["0", "0"]))
    rejection("call_start_endpoint_order", "CALL_STARTED", lambda r: r.update(endpoint="upper.right"))
    rejection("finish_requires_exact_start_id", "CALL_FINISHED", lambda r: r.update(start_sequence=0))
    rejection("inertia_count_derived_from_pivots", "CALL_FINISHED", lambda r: r["evidence"].update(negative=98))
    rejection("full_inertia_requires196pivots", "CALL_FINISHED", lambda r: r["evidence"]["pivots"].pop())
    rejection("no_earlier_unsigned_pivot", "CALL_FINISHED", lambda r: r["evidence"]["pivots"].__setitem__(0, ["-1", "1"]))
    rejection("exact_repeat_enclosures_required", "CALL_FINISHED", lambda r: r["evidence"]["pivots"].__setitem__(0, ["-2", "-1"]), lambda r: r["stage"] == "repeat")
    rejection("canonical_reverse_matrices_unchanged", "GRAM_CHECK", lambda r: r["evidence"]["unpermuted_K_sha256"].__setitem__(0, "f" * 64), lambda r: r["arm_id"] == "original_reverse_128")
    rejection("resource_cap_requires_failed_admission", "RUN_FINISHED", lambda r: r.update(reason="RESOURCE_CAP"))
    first_finished = next(i for i, r in enumerate(records) if r["kind"] == "CONFIG_FINISHED")
    premature = copy.deepcopy(records[:first_finished + 1])
    premature.append(copy.deepcopy(next(r for r in records if r["kind"] == "RUN_FINISHED")))
    prematurely_complete = replay(chain(premature))
    ok("premature_complete_rejected", prematurely_complete.config_index == 1 and
       prematurely_complete.error is not None and "PREMATURE_COMPLETE" in prematurely_complete.error)
    ok("noncanonical_line_rejected", replay(b" " + raw).error is not None)
    tampered = raw.replace(b'"sequence":1,', b'"sequence":2,', 1)
    ok("self_hash_or_sequence_rejected", replay(tampered).error is not None)
    ok("unterminated_tail_rejected", replay(raw[:-1]).error is not None)
    added = copy.deepcopy(records)
    added.insert(2, copy.deepcopy(records[1]))
    ok("duplicate_eigen_start_rejected", replay(chain(added)).error is not None)
    # M1 findings must survive corruption after the baseline stage, and even
    # a partial baseline must preserve an already paired failure.
    mixed_records = [json.loads(line) for line in (mixed / "EVENTS.ndjson").read_bytes().splitlines()]
    after_seven = next(i for i, r in enumerate(mixed_records) if r["kind"] == "CONFIG_STARTED" and r["arm_id"] == "point_128")
    broken = replay(chain(mixed_records[:after_seven]) + b'{"broken":true}\n')
    flags = assess(spec, inputs, broken.configurations, invalid_reason=broken.error)
    ok("corrupt_middle_preserves_both_known_flags", broken.error is not None and flags["control_mismatch_detected"] is True and flags["baseline_divergence_detected"] is True)
    index = next(i for i, r in enumerate(mixed_records) if r["kind"] == "CALL_FINISHED" and r["specimen_id"] == "accepted_lower" and r["arm_id"] == "original_128" and r["stage"] == "repeat")
    partial = replay(chain(mixed_records[:index + 1]))
    flags = assess(spec, inputs, partial.configurations)
    ok("partial_accepted_control_failure_persists", flags["control_mismatch_detected"] is True and partial.config_index == 6)
    gram_index = next(i for i, r in enumerate(mixed_records) if r["kind"] == "GRAM_CHECK" and
                      r["specimen_id"] == "lower_both" and r["arm_id"] == "original_128" and
                      r["stage"] == "repeat")
    gram_prefix = replay(chain(mixed_records[:gram_index + 1]))
    gram_flags = assess(spec, inputs, gram_prefix.configurations)
    lower_both = next(row for row in gram_flags["baseline_assessments"] if row["specimen_id"] == "lower_both")
    ok("paired_gram_failure_known_before_skipped_slots", gram_prefix.error is None and
       lower_both["BASELINE_DIVERGENCE"] is False and
       lower_both["gram_positive"] == {"primary": False, "repeat": False} and
       lower_both["observed_endpoint_outcomes"] == {"primary": {}, "repeat": {}} and
       lower_both["baseline_matches_historical_label"] is None)
    stop = next(i for i, r in enumerate(records) if r["kind"] == "CALL_STARTED")
    pending = replay(chain(records[:stop + 1]))
    ok("interrupted_start_consumes_budget", pending.primary_count == 1 and pending.pending is not None and pending.config_index == 0)

    default_receipt = json.loads((default / "SUPERVISOR_RECEIPT.json").read_bytes())
    def bad_receipt(name, change, source=default_receipt, data=raw, header=records[0]):
        altered = copy.deepcopy(source)
        change(altered)
        try:
            V.check_receipt(altered, data, TEST_COMMIT, header, True)
        except Exception:
            ok(name, True)
        else:
            ok(name, False)
    bad_receipt("receipt_requires_real_reap", lambda r: r.update(post_reap_killpg_result_ESRCH=False))
    bad_receipt("receipt_hash_binding", lambda r: r.update(durable_log_sha256="0" * 64))
    bad_receipt("receipt_boolean_schema_rejected", lambda r: r.update(schema_version=True))
    bad_receipt("receipt_extra_keys_rejected", lambda r: r.update(hostname="not-allowed"))
    bad_receipt("deadline_does_not_hide_worker_crash", lambda r: r.update(worker_exit_code_or_signal=-11), receipt,
                (interrupted / "EVENTS.ndjson").read_bytes(), mixed_records[0] | {"fault": "partial_then_block"})
    # End-to-end invalid packet writes derived error RESULTS instead of losing
    # already proven flags. No repair of event bytes or complete lines occurs.
    damaged = work / "damaged"
    damaged.mkdir()
    corrupt_raw = chain(mixed_records[:after_seven]) + b'{"broken":true}\n'
    (damaged / "EVENTS.ndjson").write_bytes(corrupt_raw)
    altered_receipt = copy.deepcopy(json.loads((mixed / "SUPERVISOR_RECEIPT.json").read_bytes()))
    altered_receipt.update(durable_log_bytes=len(corrupt_raw), durable_log_sha256=C.sha256_bytes(corrupt_raw),
                           pre_trim_durable_log_bytes=len(corrupt_raw), post_trim_durable_log_bytes=len(corrupt_raw))
    C.atomic_json(damaged / "SUPERVISOR_RECEIPT.json", altered_receipt)
    error_result = V.finalize(damaged, TEST_COMMIT, True)
    ok("corrupt_middle_emits_error_RESULTS", error_result["status"] == "EXECUTION_ERROR" and (damaged / "RESULTS.json").is_file() and error_result["baseline_divergence_detected"] is True and error_result["control_mismatch_detected"] is True)
    extra = work / "extra"
    shutil.copytree(interrupted, extra)
    (extra / "stale.json").write_bytes(b"{}")
    error_result = V.finalize(extra, TEST_COMMIT, True)
    ok("extra_file_error_keeps_known_flags", error_result["status"] == "EXECUTION_ERROR" and error_result["control_mismatch_detected"] is True)
    empty = work / "empty"
    empty.mkdir()
    error_result = V.finalize(empty, TEST_COMMIT, True)
    ok("missing_evidence_still_reports_seven_unknowns", error_result["status"] == "EXECUTION_ERROR" and len(error_result["baseline_assessments"]) == 7 and error_result["baseline_divergence_detected"] is None and error_result["control_mismatch_detected"] is None)
    # Isolate reporting failures from the normal retained-run manifests so
    # each test reaches exactly the intended error path.
    def raw_copy(name):
        out = work / name
        out.mkdir()
        for filename in ("EVENTS.ndjson", "SUPERVISOR_RECEIPT.json"):
            shutil.copyfile(mixed / filename, out / filename)
        return out

    unavailable_contract = raw_copy("unavailable_contract")
    with patch.object(V.C, "load_contract", side_effect=ValueError("INJECTED_PROTOCOL_BINDING_FAILURE")):
        source_error = V.finalize(unavailable_contract, TEST_COMMIT, True)
    ok("invalid_protocol_reports_seven_explicit_unknowns",
       source_error["status"] == "EXECUTION_ERROR" and
       any(error.startswith("PROTOCOL:") for error in source_error["errors"]) and
       source_error["validated_prefix"]["records"] == 0 and
       len(source_error["baseline_assessments"]) == 7 and
       all(row["assessment_state"] == "INVALID_EVIDENCE" and
           row["baseline_matches_historical_label"] is None
           for row in source_error["baseline_assessments"]) and
       source_error["baseline_divergence_detected"] is None and
       source_error["control_mismatch_detected"] is None and
       (unavailable_contract / "RESULTS.json").read_bytes() == C.json_bytes(source_error))

    package_failure = raw_copy("package_failure")
    with patch("package_io.package_plan", side_effect=ValueError("INJECTED_PACKAGE_FAILURE")):
        package_error = V.finalize(package_failure, TEST_COMMIT, True)
    ok("packaging_failure_preserves_prefix_flags_in_error_RESULTS",
       package_error["status"] == "EXECUTION_ERROR" and
       package_error["event_package"] is None and
       any(error == "PACKAGE:INJECTED_PACKAGE_FAILURE" for error in package_error["errors"]) and
       package_error["baseline_divergence_flagged_ids"] == ["upper_left"] and
       package_error["control_mismatch_flagged_ids"] == ["accepted_lower"] and
       package_error["configurations_completed"] == 56 and
       (package_failure / "RESULTS.json").read_bytes() == C.json_bytes(package_error))

    oversized = work / "small_oversized_evidence.bin"
    payload = bytes(range(65))
    oversized.write_bytes(payload)
    prefix, read_error = V.bounded_evidence_read(oversized, 32)
    ok("oversized_read_returns_only_cap_plus_one_and_error",
       len(prefix) == 33 and prefix == payload[:33] and read_error == "EVIDENCE_BYTE_CAP")

    stale_manifest = work / "stale_manifest"
    shutil.copytree(default, stale_manifest)
    stale_path = stale_manifest / "MANIFEST.json"
    stale = json.loads(stale_path.read_bytes())
    stale["entries"][0]["bytes"] += 1
    C.atomic_json(stale_path, stale)
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in stale_manifest.iterdir()}
    try:
        V.finalize(stale_manifest, TEST_COMMIT, allow_test_mode=True, check_only=True)
    except ValueError as exc:
        ok("stale_manifest_check_only_is_strict", str(exc) == "MANIFEST_BINDING_OR_FORMAT_MISMATCH")
    else:
        ok("stale_manifest_check_only_is_strict", False)
    after = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in stale_manifest.iterdir()}
    ok("stale_manifest_check_only_never_repairs_bytes", before == after)
    for name in ("numpy", "flint", "threadpoolctl"):
        ok("offline_replay_never_imports_" + name, name not in sys.modules)
    return {"schema_version": 1, "scope": "Synthetic fixtures, adversarial record replay, packaging and real SIGKILL supervision only; no physical CASE execution",
            "test_commit_label": TEST_COMMIT, "passed": len(controls), "controls": controls,
            "retained_runs": ["complete", "mixed", "sigkill"] if retained else []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--retain", type=Path)
    args = parser.parse_args()
    if args.retain:
        args.retain.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="s1b-diagnostic-controls-") as path:
        result = run(Path(path), args.retain)
    if args.output:
        C.atomic_json(args.output, result)
    print(json.dumps({"status": "PASS_INTEGRATION_CONTROLS", "passed": result["passed"]}, sort_keys=True))


if __name__ == "__main__":
    main()
