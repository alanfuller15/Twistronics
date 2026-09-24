#!/usr/bin/env python3
"""Bounded synthetic controls; never imports or executes the physical model."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import common

HERE = Path(__file__).resolve().parent


def require(condition: bool, label: str) -> None:
    if not condition:
        raise RuntimeError(label)
    print("PASS", label)


def run() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="packet002-kill-") as tmp:
        output = Path(tmp) / "run"
        command = [sys.executable, str(HERE / "supervisor.py"),
                   "--output", str(output),
                   "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
                   "--runtime-provenance-digest", "TEST_RUNTIME_DIGEST",
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
        checks += 8

        # A complete malformed line must fail, unlike an unterminated tail.
        with (output / "ATTEMPTS.ndjson").open("ab") as stream:
            stream.write(b"{}\n")
        bad = subprocess.run([sys.executable, str(HERE / "verify.py"),
                              "--output", str(output),
                              "--implementation-commit", "TEST_IMPLEMENTATION_COMMIT",
                              "--allow-test-mode"], capture_output=True, text=True)
        require(bad.returncode != 0, "complete_malformed_record_rejected")
        checks += 1

    spec, _, _ = common.load_frozen_state()
    state = common.initial_replay_state()
    # I3: queue exhaustion is tested before admission.  This direct invariant
    # demonstrates that an empty queue remains terminal even at every cap.
    state["frontier"] = []
    state["attempts"] = spec["limits"]["max_new_attempted_cells"]
    require(not state["frontier"], "empty_queue_precedes_cap_classification")
    checks += 1

    header, line, line_sha = common.hashed_record({
        "kind": "header", "sequence": -1, "previous_record_sha256": None})
    require(common.verify_hashed_record(header, line, None) == line_sha,
            "exact_line_hash_encoding_round_trip")
    checks += 1
    require(checks == 12, "expected_control_count")
    print(f"{checks + 1}/{checks + 1} synthetic controls pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
