#!/usr/bin/env python3
"""Bounded exploratory point spectra; no cell certification or LDL calls."""
from __future__ import annotations

import argparse
from fractions import Fraction
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DIAG = ROOT / "research/benchmarks/certification_s1b_diagnostic_001"
PREVIOUS = ROOT / "research/benchmarks/momentum_mapping_scout_001"
PREVIOUS_RESULTS_SHA256 = "45648684252cbc628a56f18fea593bf7baf6539c0363fa1ac7959979dc2bef29"
sys.path.insert(0, str(DIAG))
import diag_common as C
import runtime_identity as R
import supervisor as S

RAW_CAP = 8388608
CLAIM = "Exploratory binary64 point spectra only; no certified gaps, cell interiors, coverage, topology, or physical gap-closure claim. Historical coverage remains 29663/65536."


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract():
    spec = json.loads((HERE / "SPEC.json").read_bytes())
    parent = next(x for x in json.loads((DIAG / "INPUTS.json").read_bytes())["specimens"] if x["id"] == "upper_both")
    predecessor_bytes = (PREVIOUS / "RUN/RESULTS.json").read_bytes()
    if C.sha256_bytes(predecessor_bytes) != PREVIOUS_RESULTS_SHA256:
        raise ValueError("PREDECESSOR_RESULTS_BINDING")
    predecessor = json.loads(predecessor_bytes)
    if predecessor["status"] != "EXPLORATORY_COMPLETE" or predecessor["points_completed"] != 64:
        raise ValueError("PREDECESSOR_NOT_COMPLETE")
    ranked = sorted(predecessor["points"], key=lambda row: (
        Fraction(row["diagnostic"]["local_gap_estimates_meV"]["upper"]),
        row["point"]["cell"]["depth"], row["point"]["cell"]["ix"], row["point"]["cell"]["iy"]))[:4]
    selected = [{"rank": rank, "source_point_index": row["point"]["index"],
                 "cell": row["point"]["cell"], "center": row["point"]["center"],
                 "upper_gap_estimate_meV": row["diagnostic"]["local_gap_estimates_meV"]["upper"]}
                for rank, row in enumerate(ranked)]
    expected = []
    for selected_parent in selected:
        cell = selected_parent["cell"]
        if cell["depth"] != 12:
            raise ValueError("PREDECESSOR_PARENT_DEPTH")
        for ix in range(4 * cell["ix"], 4 * cell["ix"] + 4):
            for iy in range(4 * cell["iy"], 4 * cell["iy"] + 4):
                expected.append({"index": len(expected), "parent_rank": selected_parent["rank"],
                                 "parent_cell": cell, "cell": {"depth": 14, "ix": ix, "iy": iy},
                                 "center": [str(Fraction(2 * ix + 1, 32768)), str(Fraction(2 * iy + 1, 32768))]})
    selection = {"predecessor_results_path": str((PREVIOUS / "RUN/RESULTS.json").relative_to(ROOT)),
                 "predecessor_results_sha256": PREVIOUS_RESULTS_SHA256,
                 "rule": "four smallest exact retained upper-gap rationals; ties ascending (depth,ix,iy)",
                 "parents": selected, "single_sampled_cluster": True, "stop_after_one_frozen_batch": True}
    limits = {"eigensolver_starts": 64, "workers": 1, "native_threads": 1,
              "address_space_bytes": 2147483648, "soft_seconds": 120,
              "hard_seconds": 150, "retries": 0, "raw_bytes": RAW_CAP}
    if (C.canonical_bytes(spec["points"]) != C.canonical_bytes(expected)
            or C.canonical_bytes(spec["selection"]) != C.canonical_bytes(selection)
            or C.canonical_bytes(spec["parent_specimen"]) != C.canonical_bytes(parent)
            or C.canonical_bytes(spec["limits"]) != C.canonical_bytes(limits)
            or spec["packet_id"] != "MOMENTUM-MAPPING-SCOUT-002"
            or spec["dimension"] != 196 or spec["selected_bands_zero_based"] != [97, 98]
            or spec["cutoff"] != "a" or spec["assembly_precision_bits"] != 128):
        raise ValueError("SCOUT_FROZEN_CONTRACT_MISMATCH")
    if len(expected) != 64 or len({tuple(x["center"]) for x in expected}) != 64:
        raise ValueError("SCOUT_POINT_COUNT_OR_DUPLICATE")
    old_centers = {tuple(row["point"]["center"]) for row in predecessor["points"]}
    if old_centers & {tuple(x["center"]) for x in expected}:
        raise ValueError("PREDECESSOR_POINT_REUSED")
    return spec


def source_bindings():
    bindings = C.verify_implementation_files()
    manifest = json.loads((HERE / "SOURCE_MANIFEST.json").read_bytes())
    own = {str((HERE / n).relative_to(ROOT)) for n in ("SPEC.json", "README.md", "scout.py")}
    previous = {str((PREVIOUS / n).relative_to(ROOT)) for n in (
        "SPEC.json", "README.md", "scout.py", "SOURCE_MANIFEST.json", "RUN/RESULTS.json", "RUN/MANIFEST.json")}
    entries = manifest["entries"]
    if len(entries) != len({x["path"] for x in entries}) or {x["path"] for x in entries} != set(bindings) | own | previous:
        raise ValueError("SCOUT_SOURCE_MEMBERSHIP")
    for e in entries:
        p = ROOT / e["path"]
        if p.is_symlink() or not p.resolve().is_relative_to(ROOT):
            raise ValueError("UNSAFE_SOURCE_PATH")
        b = p.read_bytes()
        actual = {"bytes": len(b), "sha256": C.sha256_bytes(b)}
        if actual != {k: e[k] for k in actual}:
            raise ValueError("SCOUT_SOURCE_BINDING")
        bindings[e["path"]] = actual
    # The predecessor scaffold remains immutable and independently source-bound.
    predecessor_manifest = json.loads((PREVIOUS / "SOURCE_MANIFEST.json").read_bytes())
    for entry in predecessor_manifest["entries"]:
        if bindings.get(entry["path"]) != {k: entry[k] for k in ("bytes", "sha256")}:
            raise ValueError("PREDECESSOR_SOURCE_BINDING")
    p = HERE / "SOURCE_MANIFEST.json"
    b = p.read_bytes()
    bindings[str(p.relative_to(ROOT))] = {"bytes": len(b), "sha256": C.sha256_bytes(b)}
    return bindings


def diagnostic(values, selected, windows):
    """Exact replay arithmetic on approximate, retained binary64 spectra."""
    if any(not isinstance(v, str) or not math.isfinite(float(v)) or format(float(v), ".17g") != v for v in values):
        raise ValueError("SPECTRUM_NOT_CANONICAL_FINITE_DECIMALS")
    e = [Fraction(v) for v in values]
    if e != sorted(e):
        raise ValueError("SPECTRUM_NOT_SORTED")
    lo, hi = selected
    gaps = {"lower": e[lo] - e[lo - 1], "upper": e[hi + 1] - e[hi]}
    fixed, local = {}, {}
    for name, a, b, n in (("lower", e[lo - 1], e[lo], lo), ("upper", e[hi], e[hi + 1], hi + 1)):
        local[name] = {"left": str(a + Fraction(3, 8) * (b - a)),
                       "right": str(a + Fraction(5, 8) * (b - a)),
                       "width_meV": str((b - a) / 4), "expected_negative": n,
                       "status": "NUMERICAL_PROPOSAL_NOT_CERTIFIED"}
        for side in ("left", "right"):
            shift = Fraction(windows[name][side])
            left, right = shift - e[n - 1], e[n] - shift
            fixed[name + "." + side] = {
                "shift": str(shift), "expected_negative": n,
                "numerical_negative_count": sum(v < shift for v in e),
                "numerical_equality_count": sum(v == shift for v in e),
                "left_margin_meV": str(left), "right_margin_meV": str(right),
                "minimum_margin_meV": str(min(left, right)),
                "nearest_eigenvalue_distance_meV": str(min(abs(v - shift) for v in e)),
            }
    return {"band_energies_meV": {str(i): values[i] for i in (lo - 1, lo, hi, hi + 1)},
            "local_gap_estimates_meV": {k: str(v) for k, v in gaps.items()},
            "local_window_proposals": local, "fixed_parent_endpoint_diagnostics": fixed}


def worker(output, wheel):
    spec, bindings = contract(), source_bindings()
    resource.setrlimit(resource.RLIMIT_AS, (2147483648, 2147483648))
    resource.setrlimit(resource.RLIMIT_FSIZE, (RAW_CAP, RAW_CAP))
    journal = C.Journal(output / "EVENTS.ndjson")
    try:
        import numpy as np
        from flint import ctx
        ctx.prec, ctx.threads = 128, 1
        provenance = R.collect(wheel)
        assembly = load_module(ROOT / "research/benchmarks/certification_s1a_hardening_001/check.py", "scout_locked_assembly")
        base = load_module(ROOT / "research/benchmarks/certification_s1b_001/check.py", "scout_affine_helpers")
        case = json.loads((ROOT / "docs/certification-readiness/CASE.json").read_bytes())
        assembly.validate_case(case)
        cutoff = case["cutoffs"]["a"]
        if case["case_id"] != spec["case_id"] or cutoff["dimension"] != 196 or cutoff["selected_bands_zero_based"] != [97, 98]:
            raise ValueError("CASE_IDENTITY")
        journal.emit("HEADER", packet_id=spec["packet_id"], source_bindings=bindings,
                     runtime_provenance=provenance, runtime_provenance_digest=C.digest(provenance),
                     spec_sha256=C.sha256_bytes((HERE / "SPEC.json").read_bytes()), claim=CLAIM)
        # One fixed-precision affine assembly is shared across the frozen points.
        ctx.prec, ctx.threads = 128, 1
        coefficients, _ = assembly.assemble_coefficients(cutoff["ordered_indices"], case)
        for point in spec["points"]:
            if ctx.prec != 128 or ctx.threads != 1:
                raise ValueError("NUMERIC_SETTINGS_CHANGED")
            center = base.matrix_from_coefficients(coefficients, *map(Fraction, point["center"]))
            matrix = assembly.mid_float([[center[i, j] for j in range(196)] for i in range(196)])
            if matrix.shape != (196, 196) or not np.isfinite(matrix).all() or not np.array_equal(matrix, matrix.T):
                raise ValueError("MIDPOINT_MATRIX_NOT_FINITE_SYMMETRIC")
            matrix_hash = C.sha256_bytes(np.asarray(matrix, dtype="<f8", order="C").tobytes())
            journal.emit("EIGEN_STARTED", point=point, matrix_midpoint_sha256=matrix_hash)
            eigenvalues = np.linalg.eigvalsh(matrix, UPLO="L")
            values = [format(float(v), ".17g") for v in eigenvalues]
            if len(values) != 196:
                raise ValueError("EIGENVALUE_COUNT")
            journal.emit("EIGEN_FINISHED", point=point, matrix_midpoint_sha256=matrix_hash,
                         eigenvalues_meV=values,
                         diagnostic=diagnostic(values, [97, 98], spec["parent_specimen"]["windows"]))
        journal.emit("RUN_FINISHED", points_completed=64)
        return 0
    except Exception as exc:
        # Class names carry failure information without local paths or environment.
        journal.emit("WORKER_ERROR", error_type=type(exc).__name__)
        return 1


def review(output):
    """Read-only structural replay; never assembles a matrix or calls a solver."""
    spec, bindings = contract(), source_bindings()
    allowed = {"EVENTS.ndjson", "SUPERVISOR_RECEIPT.json", "RESULTS.json", "MANIFEST.json"}
    if not {x.name for x in output.iterdir()} <= allowed:
        raise ValueError("OUTPUT_MEMBERSHIP")
    path = output / "EVENTS.ndjson"
    if path.is_symlink() or path.stat().st_size > RAW_CAP:
        raise ValueError("RAW_EVIDENCE_SIZE_OR_SYMLINK")
    raw = path.read_bytes()
    receipt_bytes = (output / "SUPERVISOR_RECEIPT.json").read_bytes()
    receipt = json.loads(receipt_bytes)
    required_receipt = {"schema_version", "source_bindings_sha256", "monotonic_start", "soft_deadline_at",
                        "hard_deadline_at", "reaped_at", "sigterm_sent_at", "sigkill_sent_at",
                        "post_reap_group_empty", "worker_exit_code", "termination_reason", "pre_trim_bytes",
                        "durable_log_bytes", "durable_log_sha256"}
    if (set(receipt) != required_receipt or type(receipt["schema_version"]) is not int
            or receipt["schema_version"] != 1 or type(receipt["worker_exit_code"]) is not int
            or type(receipt["post_reap_group_empty"]) is not bool
            or any(type(receipt[k]) is not int or receipt[k] < 0 for k in ("pre_trim_bytes", "durable_log_bytes"))):
        raise ValueError("RECEIPT_SCHEMA")
    for key in ("monotonic_start", "soft_deadline_at", "hard_deadline_at", "reaped_at", "sigterm_sent_at", "sigkill_sent_at"):
        value = receipt[key]
        if value is None and key in ("sigterm_sent_at", "sigkill_sent_at"):
            continue
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("RECEIPT_TIME")
    if receipt["reaped_at"] < receipt["monotonic_start"] or receipt["pre_trim_bytes"] < receipt["durable_log_bytes"]:
        raise ValueError("RECEIPT_ORDER")
    signalled = receipt["sigterm_sent_at"] is not None or receipt["sigkill_sent_at"] is not None
    for key, deadline in (("sigterm_sent_at", "soft_deadline_at"), ("sigkill_sent_at", "hard_deadline_at")):
        if receipt[key] is not None and not receipt[deadline] <= receipt[key] <= receipt["reaped_at"]:
            raise ValueError("RECEIPT_SIGNAL_TIME")
    if (receipt["termination_reason"] not in ("NORMAL_EXIT", "WATCHDOG_TIMEOUT", "UNEXPECTED_EXIT")
            or (receipt["termination_reason"] == "WATCHDOG_TIMEOUT" and not signalled)
            or (receipt["termination_reason"] == "NORMAL_EXIT" and (signalled or receipt["worker_exit_code"] != 0))):
        raise ValueError("RECEIPT_TERMINATION")
    if receipt["durable_log_bytes"] != len(raw) or receipt["durable_log_sha256"] != C.sha256_bytes(raw):
        raise ValueError("RECEIPT_LOG_BINDING")
    if (receipt["source_bindings_sha256"] != C.digest(bindings) or receipt["soft_deadline_at"] != receipt["monotonic_start"] + 120
            or receipt["hard_deadline_at"] != receipt["monotonic_start"] + 150):
        raise ValueError("RECEIPT_SOURCE_OR_LIMIT_BINDING")
    if raw and not raw.endswith(b"\n"):
        raise ValueError("PARTIAL_RECORD")
    prior, started, pending, completed, terminal, provenance = None, 0, None, [], None, None
    for sequence, line in enumerate(raw.splitlines()):
        row = json.loads(line)
        if type(row["sequence"]) is not int or row["sequence"] != sequence or row["previous_record_sha256"] != prior:
            raise ValueError("RECORD_SEQUENCE")
        if C.canonical_bytes(row) != line or row["record_sha256"] != C.digest({k: v for k, v in row.items() if k != "record_sha256"}):
            raise ValueError("RECORD_HASH_OR_ENCODING")
        prior = C.sha256_bytes(line)
        fields = set(row) - {"kind", "sequence", "previous_record_sha256", "record_sha256"}
        kind = row["kind"]
        if terminal is not None:
            raise ValueError("RECORD_AFTER_TERMINAL")
        if kind == "WORKER_ERROR":
            if fields != {"error_type"} or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,100}", row["error_type"]):
                raise ValueError("WORKER_ERROR_SCHEMA")
            terminal = "WORKER_ERROR"
        elif kind == "HEADER":
            if sequence != 0 or fields != {"packet_id", "source_bindings", "runtime_provenance", "runtime_provenance_digest", "spec_sha256", "claim"}:
                raise ValueError("HEADER_SCHEMA")
            if (C.canonical_bytes(row["source_bindings"]) != C.canonical_bytes(bindings)
                    or row["packet_id"] != spec["packet_id"] or row["claim"] != CLAIM
                    or row["spec_sha256"] != C.sha256_bytes((HERE / "SPEC.json").read_bytes())):
                raise ValueError("HEADER_BINDING")
            provenance = row["runtime_provenance"]
            R.verify(provenance)
            if row["runtime_provenance_digest"] != C.digest(provenance):
                raise ValueError("RUNTIME_DIGEST")
        elif kind in ("EIGEN_STARTED", "EIGEN_FINISHED"):
            expected_fields = {"point", "matrix_midpoint_sha256"} | ({"eigenvalues_meV", "diagnostic"} if kind == "EIGEN_FINISHED" else set())
            if provenance is None or fields != expected_fields or not re.fullmatch(r"[0-9a-f]{64}", row["matrix_midpoint_sha256"]):
                raise ValueError("EIGEN_SCHEMA")
            if kind == "EIGEN_STARTED":
                if pending is not None or started >= 64 or C.canonical_bytes(row["point"]) != C.canonical_bytes(spec["points"][started]):
                    raise ValueError("FROZEN_POINT_OR_START_LIMIT")
                started += 1
                pending = (row["point"], row["matrix_midpoint_sha256"])
            else:
                if (pending is None or C.canonical_bytes(pending[0]) != C.canonical_bytes(row["point"])
                        or pending[1] != row["matrix_midpoint_sha256"] or len(row["eigenvalues_meV"]) != 196):
                    raise ValueError("UNMATCHED_COMPLETION")
                expected = diagnostic(row["eigenvalues_meV"], [97, 98], spec["parent_specimen"]["windows"])
                if C.canonical_bytes(expected) != C.canonical_bytes(row["diagnostic"]):
                    raise ValueError("NUMERICAL_DIAGNOSTIC_REPLAY")
                completed.append({"point": row["point"], "diagnostic": expected})
                pending = None
        elif kind == "RUN_FINISHED":
            if fields != {"points_completed"} or type(row["points_completed"]) is not int or row["points_completed"] != 64 or len(completed) != 64 or pending is not None:
                raise ValueError("PREMATURE_FINISH")
            terminal = "RUN_FINISHED"
        else:
            raise ValueError("UNKNOWN_RECORD_KIND")
    good_receipt = receipt["post_reap_group_empty"] is True and receipt["termination_reason"] == "NORMAL_EXIT" and receipt["worker_exit_code"] == 0
    if good_receipt and terminal == "RUN_FINISHED":
        status = "EXPLORATORY_COMPLETE"
    elif receipt["termination_reason"] == "WATCHDOG_TIMEOUT" and receipt["post_reap_group_empty"] is True and terminal != "WORKER_ERROR":
        status = "EXPLORATORY_TIMEOUT"
    else:
        status = "EXECUTION_ERROR"
    return {"schema_version": 1, "packet_id": spec["packet_id"], "status": status,
            "eigensolver_starts": started, "points_completed": len(completed), "points": completed,
            "pending_eigensolver_point": pending[0] if pending else None,
            "uncompleted_points": spec["points"][len(completed):],
            "interval_factorizations": 0, "source_bindings_sha256": C.digest(bindings),
            "runtime_provenance_digest": C.digest(provenance) if provenance else None,
            "raw_bytes": len(raw), "raw_sha256": C.sha256_bytes(raw),
            "receipt_sha256": C.sha256_bytes(receipt_bytes), "claim": CLAIM,
            "verification_limit": "Record/source/runtime integrity and deterministic arithmetic on retained approximate spectra; no offline numerical recomputation or matrix-hash reconstruction."}


def finalize(output, check_only=False):
    result = review(output)
    if check_only:
        if (output / "RESULTS.json").read_bytes() != C.json_bytes(result):
            raise ValueError("RESULTS_REPLAY_MISMATCH")
    else:
        C.atomic_json(output / "RESULTS.json", result)
    names = {"EVENTS.ndjson", "RESULTS.json", "SUPERVISOR_RECEIPT.json"}
    if {x.name for x in output.iterdir()} not in (names, names | {"MANIFEST.json"}):
        raise ValueError("EXACT_OUTPUT_MEMBERSHIP")
    entries = []
    for name in sorted(names):
        q = output / name
        if q.is_symlink():
            raise ValueError("EVIDENCE_SYMLINK")
        data = q.read_bytes()
        entries.append({"path": name, "bytes": len(data), "sha256": C.sha256_bytes(data)})
    manifest = {"schema_version": 1, "entries": entries}
    if check_only:
        if (output / "MANIFEST.json").read_bytes() != C.json_bytes(manifest):
            raise ValueError("MANIFEST_MISMATCH")
    else:
        C.atomic_json(output / "MANIFEST.json", manifest)
    return result


def supervise(output, wheel):
    contract()
    bindings = source_bindings()
    output.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env.update({n: "1" for n in R.THREAD_VARIABLES})
    command = [sys.executable, "-B", "-E", "-s", str(HERE / "scout.py"), "--worker", "--output", str(output), "--wheel", str(wheel.resolve())]
    start, term, kill, proc, code, error = time.monotonic(), None, None, None, 127, False
    try:
        proc = subprocess.Popen(command, start_new_session=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while proc.poll() is None:
            now = time.monotonic()
            if term is None and now >= start + 120:
                term = S.signal_group(proc.pid, signal.SIGTERM)
            if kill is None and now >= start + 150:
                kill = S.signal_group(proc.pid, signal.SIGKILL)
            time.sleep(0.01)
        code = proc.wait()
    except Exception:
        error = True
        if proc is not None:
            S.signal_group(proc.pid, signal.SIGKILL)
            code = proc.wait()
    reaped = time.monotonic()
    empty = proc is None or S.group_has_gone(proc.pid)
    if not empty:
        S.signal_group(proc.pid, signal.SIGKILL)
        error = True
    log = output / "EVENTS.ndjson"
    if not log.exists():
        log.touch()
    pre = log.stat().st_size
    if term is not None or kill is not None:
        S.trim_timeout_fragment(log)
    raw = log.read_bytes()
    reason = "UNEXPECTED_EXIT" if error else "WATCHDOG_TIMEOUT" if term is not None or kill is not None else "NORMAL_EXIT" if code == 0 else "UNEXPECTED_EXIT"
    C.atomic_json(output / "SUPERVISOR_RECEIPT.json", {
        "schema_version": 1, "source_bindings_sha256": C.digest(bindings), "monotonic_start": start,
        "soft_deadline_at": start + 120, "hard_deadline_at": start + 150, "reaped_at": reaped,
        "sigterm_sent_at": term, "sigkill_sent_at": kill, "post_reap_group_empty": empty,
        "worker_exit_code": code, "termination_reason": reason, "pre_trim_bytes": pre,
        "durable_log_bytes": len(raw), "durable_log_sha256": C.sha256_bytes(raw)})
    result = finalize(output)
    print(json.dumps({k: result[k] for k in ("status", "points_completed", "eigensolver_starts", "claim")}, sort_keys=True))
    return 1 if result["status"] == "EXECUTION_ERROR" else 0


def self_test():
    values = ["-2", "-1", "1", "2"]
    windows = {"lower": {"left": "-7/4", "right": "-5/4"}, "upper": {"left": "5/4", "right": "7/4"}}
    d = diagnostic(values, [1, 2], windows)
    assert d["local_gap_estimates_meV"] == {"lower": "1", "upper": "1"}
    assert d["local_window_proposals"]["lower"]["left"] == "-13/8"
    assert d["fixed_parent_endpoint_diagnostics"]["lower.left"]["minimum_margin_meV"] == "1/4"
    assert d["fixed_parent_endpoint_diagnostics"]["upper.left"]["numerical_negative_count"] == 3
    assert d["fixed_parent_endpoint_diagnostics"]["upper.left"]["numerical_equality_count"] == 0
    print(json.dumps({"status": "PASS", "fixture": "four exact synthetic eigenvalues", "assertions": 5, "physical_calls": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--wheel", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run-reviewed-scout", action="store_true")
    mode.add_argument("--worker", action="store_true")
    mode.add_argument("--check-only", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.output is None or ((args.worker or args.run_reviewed_scout) and args.wheel is None):
        parser.error("output and, for execution, locked wheel are required")
    output = args.output.resolve()
    if args.check_only:
        print(json.dumps({"status": finalize(output, True)["status"], "check_only": True}))
        return 0
    return worker(output, args.wheel) if args.worker else supervise(output, args.wheel)


if __name__ == "__main__":
    raise SystemExit(main())
