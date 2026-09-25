#!/usr/bin/env python3
"""Bounded worker process-group supervision, followed by offline finalization."""
from __future__ import annotations

import argparse
import errno
import math
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

import diag_common as common


THREAD_VARIABLES = (
    "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
)


def trim_timeout_fragment(path: Path) -> tuple[int, int]:
    """Only remove a final unterminated line; complete invalid lines remain."""
    data = path.read_bytes()
    if not data or data.endswith(b"\n"):
        return len(data), len(data)
    kept = data.rfind(b"\n") + 1
    with path.open("r+b", buffering=0) as stream:
        stream.truncate(kept)
        os.fsync(stream.fileno())
    common.fsync_directory(path.parent)
    return len(data), kept


def signal_group(pid: int, sig: int) -> float | None:
    try:
        os.killpg(pid, sig)
    except ProcessLookupError as exc:
        if exc.errno != errno.ESRCH:
            raise
        return None
    return time.monotonic()


def group_has_gone(pid: int) -> bool:
    try:
        os.killpg(pid, 0)
    except ProcessLookupError as exc:
        if exc.errno != errno.ESRCH:
            raise
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--evaluator", choices=("physical", "synthetic"), required=True)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--fault", choices=("none", "partial_then_block"), default="none")
    parser.add_argument("--synthetic-profile", choices=(
        "default", "divergence", "control_mismatch", "gram_failure", "wrong_inertia", "mixed"),
        default="default")
    parser.add_argument("--test-soft-seconds", type=float)
    parser.add_argument("--test-hard-seconds", type=float)
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.implementation_commit) is None:
        parser.error("implementation commit must be a complete lowercase Git SHA")
    test_mode = args.evaluator == "synthetic"
    if not test_mode and (args.fault != "none" or args.synthetic_profile != "default"
                          or args.test_soft_seconds is not None
                          or args.test_hard_seconds is not None):
        parser.error("fault, profile and deadline overrides require synthetic mode")
    if not test_mode and args.wheel is None:
        parser.error("physical mode requires the locked wheel")
    common.verify_implementation_files()
    spec, _ = common.load_contract()
    soft = (args.test_soft_seconds if args.test_soft_seconds is not None
            else spec["limits"]["worker_wall_seconds"])
    hard = (args.test_hard_seconds if args.test_hard_seconds is not None
            else spec["limits"]["supervisor_hard_deadline_seconds"])
    if not (math.isfinite(soft) and math.isfinite(hard) and 0 < soft < hard):
        parser.error("deadlines must be finite with 0 < soft < hard")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    common.fsync_directory(output.parent)
    command = [sys.executable, "-B", "-E", "-s", str(common.HERE / "worker.py"),
               "--output", str(output), "--implementation-commit", args.implementation_commit,
               "--evaluator", args.evaluator, "--fault", args.fault]
    if test_mode:
        command += ["--synthetic-profile", args.synthetic_profile]
    if args.wheel is not None:
        command += ["--wheel", str(args.wheel.resolve())]
    worker_env = dict(os.environ)
    worker_env.update({name: "1" for name in THREAD_VARIABLES})
    # -E controls Python startup variables, not the explicit native thread settings.
    started = time.monotonic()
    term_at = kill_at = None
    proc = None
    returncode = 127
    group_empty = True
    supervision_error = False
    try:
        proc = subprocess.Popen(command, start_new_session=True, env=worker_env)
        while proc.poll() is None:
            now = time.monotonic()
            if term_at is None and now >= started + soft:
                term_at = signal_group(proc.pid, signal.SIGTERM)
            if kill_at is None and now >= started + hard and proc.poll() is None:
                kill_at = signal_group(proc.pid, signal.SIGKILL)
            time.sleep(0.01)
        returncode = proc.wait()
    except Exception:
        supervision_error = True
        if proc is not None:
            signal_group(proc.pid, signal.SIGKILL)
            returncode = proc.wait()
    reaped_at = time.monotonic()
    if proc is not None:
        group_empty = group_has_gone(proc.pid)
        if not group_empty:
            # A child left behind violates the protocol. Clean it up, but retain
            # the failed first post-reap check instead of concealing the breach.
            signal_group(proc.pid, signal.SIGKILL)
            supervision_error = True
    deadline_signal_sent = term_at is not None or kill_at is not None
    log_path = output / "EVENTS.ndjson"
    if not log_path.exists():
        with log_path.open("xb") as stream:
            stream.flush()
            os.fsync(stream.fileno())
        common.fsync_directory(output)
    pre_bytes = post_bytes = log_path.stat().st_size
    if deadline_signal_sent:
        pre_bytes, post_bytes = trim_timeout_fragment(log_path)
    fault_path = output / "FAULT_READY"
    fault_ready_observed = fault_path.is_file()
    if fault_path.exists():
        fault_path.unlink()
        common.fsync_directory(output)
    data = log_path.read_bytes()
    reason = ("UNEXPECTED_EXIT" if supervision_error else
              "WATCHDOG_TIMEOUT" if deadline_signal_sent else
              "NORMAL_EXIT" if returncode == 0 else "UNEXPECTED_EXIT")
    common.atomic_json(output / "SUPERVISOR_RECEIPT.json", {
        "schema_version": 1,
        "approved_protocol_commit": common.APPROVED_PROTOCOL_COMMIT,
        "implementation_commit": args.implementation_commit,
        "monotonic_start": started,
        "soft_deadline_at": started + soft,
        "hard_deadline_at": started + hard,
        "sigterm_sent_at_or_null": term_at,
        "sigkill_sent_at_or_null": kill_at,
        "reaped_at": reaped_at,
        "worker_exit_code_or_signal": returncode,
        "post_reap_killpg_result_ESRCH": group_empty,
        "durable_log_bytes": len(data),
        "durable_log_sha256": common.sha256_bytes(data),
        "termination_reason": reason,
        "test_mode": test_mode,
        "fault": args.fault,
        "fault_ready_observed": fault_ready_observed,
        "pre_trim_durable_log_bytes": pre_bytes,
        "post_trim_durable_log_bytes": post_bytes,
    })
    # Finalization must run even with an empty header, invalid log or worker error;
    # it preserves independently validated prefix findings in error RESULTS.
    import verify
    result = verify.finalize(output, args.implementation_commit,
                             allow_test_mode=test_mode, check_only=False)
    if isinstance(result, dict):
        return 1 if result.get("status", result.get("terminal_status")) == "EXECUTION_ERROR" else 0
    return 1 if reason == "UNEXPECTED_EXIT" or not group_empty else 0


if __name__ == "__main__":
    raise SystemExit(main())
