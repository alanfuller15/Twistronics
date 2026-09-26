#!/usr/bin/env python3
"""External process-group watchdog and post-reap receipt writer."""
from __future__ import annotations

import argparse
import errno
import hashlib
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import common


def trim_timeout_fragment(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data.endswith(b"\n"):
        return len(data), len(data)
    cut = data.rfind(b"\n")
    if cut < 0:
        raise RuntimeError("TIMEOUT_LOG_HAS_NO_COMPLETE_HEADER")
    with path.open("r+b", buffering=0) as stream:
        stream.truncate(cut + 1)
        stream.flush()
        os.fsync(stream.fileno())
    common.fsync_directory(path.parent)
    return len(data), cut + 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--implementation-commit", required=True)
    parser.add_argument("--runtime-provenance-digest", required=True)
    parser.add_argument("--evaluator", choices=("physical", "synthetic"), required=True)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--fault", choices=("none", "partial_then_block"), default="none")
    parser.add_argument("--test-soft-seconds", type=float)
    parser.add_argument("--test-hard-seconds", type=float)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    common.verify_implementation_files()
    spec, _, _ = common.load_frozen_state()
    test_mode = args.evaluator == "synthetic"
    if args.fault != "none" and not test_mode:
        raise RuntimeError("FAULT_INJECTION_REQUIRES_SYNTHETIC_MODE")
    if (args.test_soft_seconds is not None or args.test_hard_seconds is not None) and not test_mode:
        raise RuntimeError("DEADLINE_OVERRIDE_REQUIRES_SYNTHETIC_MODE")
    soft = args.test_soft_seconds if test_mode and args.test_soft_seconds is not None else spec["limits"]["worker_wall_seconds"]
    hard = args.test_hard_seconds if test_mode and args.test_hard_seconds is not None else spec["limits"]["supervisor_hard_deadline_seconds"]
    if not 0 < soft < hard:
        raise RuntimeError("INVALID_DEADLINES")

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    worker = Path(__file__).with_name("worker.py")
    command = [sys.executable, str(worker), "--output", str(output),
               "--implementation-commit", args.implementation_commit,
               "--runtime-provenance-digest", args.runtime_provenance_digest,
               "--evaluator", args.evaluator, "--fault", args.fault]
    if args.wheel:
        command += ["--wheel", str(args.wheel.resolve())]

    started = time.monotonic()
    worker_env = dict(os.environ)
    worker_env["OPENBLAS_NUM_THREADS"] = "1"
    worker_env["OMP_NUM_THREADS"] = "1"
    proc = subprocess.Popen(command, start_new_session=True, env=worker_env)
    sigterm_at = sigkill_at = None
    deadline_signal_sent = False
    while proc.poll() is None:
        elapsed = time.monotonic() - started
        if sigterm_at is None and elapsed >= soft:
            os.killpg(proc.pid, signal.SIGTERM)
            sigterm_at = time.monotonic()
            deadline_signal_sent = True
        if elapsed >= hard and sigkill_at is None and proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            else:
                sigkill_at = time.monotonic()
                deadline_signal_sent = True
        time.sleep(0.01)
    returncode = proc.wait()
    reaped_at = time.monotonic()
    try:
        os.killpg(proc.pid, 0)
    except ProcessLookupError as exc:
        if exc.errno != errno.ESRCH:
            raise
        group_empty = True
    else:
        group_empty = False

    log_path = output / "ATTEMPTS.ndjson"
    fault_ready_path = output / "FAULT_READY"
    fault_ready_observed = fault_ready_path.is_file()
    pre_trim_bytes = log_path.stat().st_size if log_path.is_file() else 0
    post_trim_bytes = pre_trim_bytes
    if deadline_signal_sent and log_path.is_file():
        pre_trim_bytes, post_trim_bytes = trim_timeout_fragment(log_path)
    if fault_ready_path.exists():
        fault_ready_path.unlink()
        common.fsync_directory(output)
    log_bytes = log_path.read_bytes() if log_path.is_file() else b""
    if deadline_signal_sent:
        termination_reason = "WATCHDOG_TIMEOUT"
    elif returncode == 0:
        termination_reason = "NORMAL_EXIT"
    else:
        termination_reason = "UNEXPECTED_EXIT"
    receipt = {
        "schema_version": 1,
        "approved_protocol_commit": common.APPROVED_PROTOCOL_COMMIT,
        "implementation_commit": args.implementation_commit,
        "monotonic_start": started,
        "soft_deadline_at": started + soft,
        "hard_deadline_at": started + hard,
        "sigterm_sent_at_or_null": sigterm_at,
        "sigkill_sent_at_or_null": sigkill_at,
        "reaped_at": reaped_at,
        "worker_exit_code_or_signal": returncode,
        "post_reap_killpg_result_ESRCH": group_empty,
        "durable_log_bytes": len(log_bytes),
        "durable_log_sha256": hashlib.sha256(log_bytes).hexdigest(),
        "termination_reason": termination_reason,
        "test_mode": test_mode,
        "fault": args.fault,
        "fault_ready_observed": fault_ready_observed,
        "pre_trim_durable_log_bytes": pre_trim_bytes,
        "post_trim_durable_log_bytes": post_trim_bytes,
    }
    common.atomic_json(output / "SUPERVISOR_RECEIPT.json", receipt)

    if args.verify:
        verifier = Path(__file__).with_name("verify.py")
        verify_command = [sys.executable, str(verifier), "--output", str(output),
                          "--implementation-commit", args.implementation_commit]
        if test_mode:
            verify_command.append("--allow-test-mode")
        return subprocess.run(verify_command, check=False).returncode
    return 0 if termination_reason in {"NORMAL_EXIT", "WATCHDOG_TIMEOUT"} and group_empty else 1


if __name__ == "__main__":
    raise SystemExit(main())
