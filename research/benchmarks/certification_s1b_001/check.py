#!/usr/bin/env python3
"""Bounded physical S1b interval-inertia attempt.

The driver validates runtime provenance, then runs one watchdog-bounded worker
per declared cutoff. Workers retain every signed interval-LDL pivot used to
accept a window. Budget exhaustion is INCONCLUSIVE, never a failed physical gap.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import resource
import subprocess
import sys
import tempfile
import time
import zipfile
from collections import deque
from fractions import Fraction
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SPEC_PATH = HERE / "SPEC.json"
CASE_PATH = ROOT / "docs/certification-readiness/CASE.json"
PLAN_PATH = ROOT / "docs/certification-readiness/PLAN.json"
PARENT = ROOT / "research/benchmarks/certification_s1a_hardening_001"
PARENT_CHECK = PARENT / "check.py"
WHEEL_LOCK_PATH = PARENT / "WHEEL_LOCK.json"
RETAINED_PART_BYTES = 750_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def retain_compressed_parts(path: Path) -> None:
    payload = gzip.compress(path.read_bytes(), compresslevel=9, mtime=0)
    for offset in range(0, len(payload), RETAINED_PART_BYTES):
        index = offset // RETAINED_PART_BYTES
        part = path.with_name(path.name + f".gz.part{index:03d}")
        part.write_bytes(payload[offset:offset + RETAINED_PART_BYTES])
    path.unlink()


def load_parent():
    spec = importlib.util.spec_from_file_location("reviewed_s1a", PARENT_CHECK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def exact_arb(value: Fraction | str | int) -> arb:
    value = Fraction(value)
    return arb(value.numerator) / value.denominator


def exact_dyadic(value: arb) -> Fraction:
    mantissa, exponent = value.man_exp()
    mantissa, exponent = int(mantissa), int(exponent)
    if exponent >= 0:
        return Fraction(mantissa * (1 << exponent))
    return Fraction(mantissa, 1 << (-exponent))


def rational_text(value: Fraction) -> str:
    return (str(value.numerator) if value.denominator == 1 else
            f"{value.numerator}/{value.denominator}")


def endpoint(x: arb) -> list[str]:
    midpoint = exact_dyadic(x.mid())
    radius = exact_dyadic(x.rad())
    return [rational_text(midpoint - radius), rational_text(midpoint + radius)]


def strict_sign(x: arb) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def upper_float(x: arb) -> float:
    return float(x.mid()) + float(x.rad())


def runtime_provenance(wheel: Path, lock: dict) -> dict:
    import flint
    if wheel.name != lock["filename"] or sha256(wheel) != lock["sha256"]:
        raise RuntimeError("PYTHON_FLINT_WHEEL_LOCK_MISMATCH")
    if flint.__version__ != lock["python_flint_version"]:
        raise RuntimeError("PYTHON_FLINT_VERSION_MISMATCH")
    if flint.__FLINT_VERSION__ != lock["native_flint_version"]:
        raise RuntimeError("NATIVE_FLINT_VERSION_MISMATCH")
    dist = importlib.metadata.distribution("python-flint")
    artifacts = []
    installed_paths = {}
    wheel_hashes = {}
    with zipfile.ZipFile(wheel) as archive:
        for name in archive.namelist():
            if name.endswith(".so") or ".so." in name:
                wheel_hashes[name] = hashlib.sha256(archive.read(name)).hexdigest()
        for member in sorted(dist.files or [], key=str):
            name = str(member)
            if name not in wheel_hashes:
                continue
            installed_path = Path(dist.locate_file(member)).resolve()
            digest = sha256(installed_path)
            if digest != wheel_hashes[name]:
                raise RuntimeError("INSTALLED_NATIVE_MEMBER_DIFFERS_FROM_WHEEL:" + name)
            artifacts.append({"member": name, "sha256": digest,
                              "bytes": installed_path.stat().st_size})
            installed_paths[name] = str(installed_path)
    if set(a["member"] for a in artifacts) != set(wheel_hashes):
        raise RuntimeError("INSTALLED_NATIVE_MEMBER_SET_MISMATCH")
    pyflint = Path(importlib.import_module("flint.pyflint").__file__).resolve()
    extension = next((a for a in artifacts
                      if Path(installed_paths[a["member"]]) == pyflint), None)
    if extension is None:
        raise RuntimeError("LOADED_EXTENSION_NOT_BOUND_TO_WHEEL")
    maps_path = Path("/proc/self/maps")
    if not maps_path.is_file():
        raise RuntimeError("PROC_MAPS_REQUIRED")
    mapped_paths = set()
    for line in maps_path.read_text().splitlines():
        fields = line.split()
        if fields and fields[-1].startswith("/"):
            mapped_paths.add(str(Path(fields[-1]).resolve()))
    required_native = [a for a in artifacts if "python_flint.libs/" in a["member"]]
    mapped_native = [a for a in required_native
                     if installed_paths[a["member"]] in mapped_paths]
    if len(mapped_native) != len(required_native):
        missing = sorted(set(a["member"] for a in required_native) -
                         set(a["member"] for a in mapped_native))
        raise RuntimeError("MAPPED_NATIVE_LIBRARY_NOT_BOUND:" + ",".join(missing))
    return {
        "wheel": lock,
        "installed_native_member_count": len(artifacts),
        "loaded_extension_bound_to_wheel": extension is not None,
        "mapped_native_library_count": len(mapped_native),
        "mapped_native_libraries_bound_to_wheel": len(mapped_native) == len(required_native),
        "proc_maps_checked": True,
    }


def matrix_from_coefficients(coefficients, x: Fraction, y: Fraction) -> arb_mat:
    return (arb_mat(coefficients[0]) + exact_arb(x) * arb_mat(coefficients[1]) +
            exact_arb(y) * arb_mat(coefficients[2]))


def row_sum_norm_upper(matrix) -> arb:
    best = arb(0)
    for row in matrix:
        total = sum((abs(value) for value in row), arb(0))
        if total > best:
            best = total
        elif not (best >= total):
            # Overlapping row-sum balls: their union is bounded by the larger
            # upper endpoint represented as an outward Arb interval.
            best = arb(0, max(upper_float(best), upper_float(total)))
    return best


def decimal_matrix(values: np.ndarray) -> arb_mat:
    return arb_mat([[arb(format(float(value), ".17g")) for value in row]
                    for row in values])


def gram_certificate(V: arb_mat) -> tuple[arb_mat, list[list[str]], list[str]]:
    gram = V.transpose() * V
    margins = []
    for i in range(gram.nrows()):
        off = sum((abs(gram[i, j]) for j in range(gram.ncols()) if j != i), arb(0))
        margin = gram[i, i] - off
        if not (margin > 0):
            raise RuntimeError("CONGRUENCE_GRAM_NOT_CERTIFIED")
        margins.append(margin)
    minimum = min(margins, key=lambda value: float(value.mid()) - float(value.rad()))
    return gram, [endpoint(value) for value in margins], endpoint(minimum)


def interval_ldl(matrix: arb_mat) -> dict:
    n = matrix.nrows()
    lower = [[arb(0) for _ in range(i)] for i in range(n)]
    diagonal = []
    pivots = []
    for k in range(n):
        pivot = matrix[k, k]
        for j in range(k):
            pivot -= lower[k][j] * lower[k][j] * diagonal[j]
        sign = strict_sign(pivot)
        pivots.append(endpoint(pivot))
        if sign == 0:
            return {"status": "INCONCLUSIVE", "pivot_index": k,
                    "negative": sum(strict_sign(x) < 0 for x in diagonal),
                    "pivots": pivots}
        diagonal.append(pivot)
        for i in range(k + 1, n):
            value = matrix[i, k]
            for j in range(k):
                value -= lower[i][j] * lower[k][j] * diagonal[j]
            lower[i][k] = value / pivot
    return {"status": "CERTIFIED", "negative": sum(x < 0 for x in diagonal),
            "pivots": pivots}


def candidate_windows(eigenvalues: np.ndarray, lo: int, hi: int, spec: dict):
    left = Fraction(spec["candidate_window"]["left_fraction"])
    right = Fraction(spec["candidate_window"]["right_fraction"])

    def f(value):
        return Fraction(format(float(value), ".17g"))

    def window(a, b):
        a, b = f(a), f(b)
        return a + left * (b - a), a + right * (b - a)

    return {
        "lower": (*window(eigenvalues[lo - 1], eigenvalues[lo]), lo),
        "upper": (*window(eigenvalues[hi], eigenvalues[hi + 1]), hi + 1),
    }


def inertia_for_shift(center_congruence: arb_mat, gram: arb_mat,
                      shift: Fraction, counters: dict, limits: dict) -> dict:
    if counters["factorizations"] >= limits["max_inertia_factorizations_per_cutoff"]:
        return {"status": "BUDGET", "reason": "FACTORIZATION_BUDGET"}
    counters["factorizations"] += 1
    result = interval_ldl(center_congruence - exact_arb(shift) * gram)
    result["shift"] = f"{shift.numerator}/{shift.denominator}"
    return result


def certify_cell(parent, coefficients, norm_x: arb, norm_y: arb, cell: tuple,
                 precision: int, spec: dict, counters: dict) -> dict:
    depth, ix, iy = cell
    den = 1 << depth
    x = Fraction(2 * ix + 1, 2 * den)
    y = Fraction(2 * iy + 1, 2 * den)
    half = Fraction(1, 2 * den)
    ctx.prec = precision
    center = matrix_from_coefficients(coefficients, x, y)
    midpoint = parent.mid_float([[center[i, j] for j in range(center.ncols())]
                                 for i in range(center.nrows())])
    eigenvalues, vectors = np.linalg.eigh(midpoint)
    cutoff = spec["_cutoff"]
    lo, hi = cutoff["selected_bands_zero_based"]
    windows = candidate_windows(eigenvalues, lo, hi, spec)
    V = decimal_matrix(vectors)
    gram, gram_margins, gram_margin_min = gram_certificate(V)
    transformed = V.transpose() * center * V
    record = {
        "cell": {"depth": depth, "ix": ix, "iy": iy,
                 "x": [f"{ix}/{den}", f"{ix + 1}/{den}"],
                 "y": [f"{iy}/{den}", f"{iy + 1}/{den}"],
                 "center": [f"{x.numerator}/{x.denominator}", f"{y.numerator}/{y.denominator}"]},
        "precision_bits": precision,
        "congruence_gram_margin_min": gram_margin_min,
        "windows": {},
    }
    all_counts = True
    for name in ("lower", "upper"):
        left, right, expected = windows[name]
        left_result = inertia_for_shift(transformed, gram, left, counters, spec["limits"])
        right_result = inertia_for_shift(transformed, gram, right, counters, spec["limits"])
        count_ok = (left_result.get("status") == "CERTIFIED" and
                    right_result.get("status") == "CERTIFIED" and
                    left_result.get("negative") == expected and
                    right_result.get("negative") == expected)
        width = exact_arb(right - left)
        radius = (norm_x + norm_y) * exact_arb(half)
        margin = width - 2 * radius
        record["windows"][name] = {
            "expected_count": expected,
            "left": left_result,
            "right": right_result,
            "width_meV": endpoint(width),
            "weyl_radius_meV": endpoint(radius),
            "cell_gap_lower_meV": endpoint(margin),
            "count_certified": count_ok,
            "target_met": count_ok and margin >= exact_arb(spec["target_external_gap_lower_meV"]),
        }
        all_counts = all_counts and count_ok
    record["status"] = ("CERTIFIED" if all(w["target_met"] for w in record["windows"].values())
                        else "UNRESOLVED")
    record["counts_certified"] = all_counts
    return record


def run_cutoff(key: str, wheel: Path, result_path: Path) -> int:
    spec = json.loads(SPEC_PATH.read_text())
    case = json.loads(CASE_PATH.read_text())
    plan = json.loads(PLAN_PATH.read_text())
    lock = json.loads(WHEEL_LOCK_PATH.read_text())
    runtime_provenance(wheel, lock)
    parent = load_parent()
    parent.validate_case(case)
    cutoff = case["cutoffs"][key]
    spec["_cutoff"] = cutoff
    limits = spec["limits"]
    resource.setrlimit(resource.RLIMIT_AS,
                       (limits["worker_address_bytes"], limits["worker_address_bytes"]))
    ctx.threads = 1
    start = time.monotonic()
    coefficients_by_precision = {}

    def coefficients(precision):
        if precision not in coefficients_by_precision:
            ctx.prec = precision
            values, _ = parent.assemble_coefficients(cutoff["ordered_indices"], case)
            coefficients_by_precision[precision] = values
        return coefficients_by_precision[precision]

    base = coefficients(spec["precision_bits"][0])
    norm_x = row_sum_norm_upper(base[1])
    norm_y = row_sum_norm_upper(base[2])
    queue = deque([(0, 0, 0)])
    accepted, unresolved, attempts = [], [], []
    counters = {"attempted_cells": 0, "factorizations": 0,
                "max_depth_attempted": 0}
    stop_reason = None
    while queue:
        if time.monotonic() - start >= limits["worker_compute_seconds_per_cutoff"]:
            stop_reason = "WALL_BUDGET"
            break
        if counters["attempted_cells"] >= spec["subdivision"]["max_attempted_cells_per_cutoff"]:
            stop_reason = "CELL_BUDGET"
            break
        if counters["factorizations"] >= limits["max_inertia_factorizations_per_cutoff"]:
            stop_reason = "FACTORIZATION_BUDGET"
            break
        cell = queue.popleft()
        counters["attempted_cells"] += 1
        counters["max_depth_attempted"] = max(counters["max_depth_attempted"], cell[0])
        final = None
        precision_attempts = []
        for precision in spec["precision_bits"]:
            try:
                trial = certify_cell(parent, coefficients(precision), norm_x, norm_y,
                                     cell, precision, spec, counters)
            except RuntimeError as exc:
                trial = {"cell": {"depth": cell[0], "ix": cell[1], "iy": cell[2]},
                         "precision_bits": precision, "status": "UNRESOLVED",
                         "reason": str(exc)}
            final = trial
            precision_attempts.append(trial)
            # The frozen plan requires all precisions before an inconclusive
            # subdivision. A certified cell may stop early because the target
            # conclusion has already been established.
            if trial.get("status") == "CERTIFIED":
                break
        attempts.append({"cell": {"depth": cell[0], "ix": cell[1], "iy": cell[2]},
                         "precisions": precision_attempts})
        if final["status"] == "CERTIFIED":
            accepted.append(final)
            continue
        depth, ix, iy = cell
        if depth >= spec["subdivision"]["max_depth"]:
            final["reason"] = final.get("reason", "MAX_DEPTH")
            unresolved.append(final)
            continue
        # Fixed x-then-y, low-coordinate-first order.
        for xb in (0, 1):
            for yb in (0, 1):
                queue.append((depth + 1, 2 * ix + xb, 2 * iy + yb))
    if stop_reason:
        unresolved.append({"status": "UNRESOLVED", "reason": stop_reason,
                           "queued_cells": len(queue),
                           "frontier": [{"depth": d, "ix": i, "iy": j}
                                        for d, i, j in queue]})
    status = ("CERTIFIED_UNIFORM_EXTERNAL_ISOLATION" if not queue and not unresolved
              else "INCONCLUSIVE")
    result = {
        "schema": "twistronics_s1b_cutoff_result_v1",
        "spec_id": spec["spec_id"], "case_id": case["case_id"], "cutoff": key,
        "status": status,
        "reason": None if status.startswith("CERTIFIED") else (stop_reason or "UNRESOLVED_CELLS"),
        "dimension": cutoff["dimension"],
        "selected_bands_zero_based": cutoff["selected_bands_zero_based"],
        "required_counts": [cutoff["selected_bands_zero_based"][0],
                            cutoff["selected_bands_zero_based"][1] + 1],
        "coefficient_norm_upper_meV": {"Hx_row_sum": endpoint(norm_x),
                                        "Hy_row_sum": endpoint(norm_y)},
        "counters": {**counters, "accepted_cells": len(accepted),
                     "unresolved_records": len(unresolved),
                     "wall_seconds": time.monotonic() - start},
        "accepted_cells": accepted,
        "cell_attempts": attempts,
        "unresolved": unresolved,
        "limits": {"No projector, transport, seam, integer, relative-class, cutoff-convergence, or experimental claim.",
                   "An inconclusive cell or exhausted budget is not evidence of a physical gap closure."},
    }
    # JSON cannot serialize sets.
    result["limits"] = sorted(result["limits"])
    atomic_json(result_path, result)
    print(json.dumps({"cutoff": key, "status": status, "counters": result["counters"]},
                     sort_keys=True), flush=True)
    return 0


def driver(output: Path, wheel: Path) -> int:
    spec = json.loads(SPEC_PATH.read_text())
    case = json.loads(CASE_PATH.read_text())
    plan = json.loads(PLAN_PATH.read_text())
    lock = json.loads(WHEEL_LOCK_PATH.read_text())
    if output.exists():
        raise RuntimeError("OUTPUT_ALREADY_EXISTS")
    provenance = runtime_provenance(wheel, lock)
    output.mkdir(parents=True)
    started = time.monotonic()
    cutoff_results = {}
    for key in spec["cutoff_order"]:
        path = output / f"{key}_cells.json"
        command = [sys.executable, "-B", str(Path(__file__).resolve()),
                   "--worker", key, "--worker-output", str(path), "--wheel", str(wheel)]
        try:
            completed = subprocess.run(command, text=True, capture_output=True,
                                       timeout=spec["limits"]["worker_wall_seconds_per_cutoff"])
        except subprocess.TimeoutExpired:
            cutoff_results[key] = {"status": "INCONCLUSIVE", "reason": "WATCHDOG_TIMEOUT"}
            continue
        if completed.returncode != 0 or not path.is_file():
            cutoff_results[key] = {"status": "EXECUTION_ERROR", "reason": "WORKER_EXIT",
                                   "returncode": completed.returncode,
                                   "stderr": completed.stderr[-4000:]}
            continue
        cutoff_results[key] = json.loads(path.read_text())
        retain_compressed_parts(path)
    factor_total = sum(v.get("counters", {}).get("factorizations", 0)
                       for v in cutoff_results.values())
    if factor_total > spec["limits"]["max_inertia_factorizations_total"]:
        raise RuntimeError("GLOBAL_FACTORIZATION_BUDGET_EXCEEDED")
    statuses = [v.get("status") for v in cutoff_results.values()]
    if statuses and all(s == "CERTIFIED_UNIFORM_EXTERNAL_ISOLATION" for s in statuses):
        status = "CERTIFIED_UNIFORM_EXTERNAL_ISOLATION"
    elif any(s == "EXECUTION_ERROR" for s in statuses):
        status = "EXECUTION_ERROR"
    else:
        status = "INCONCLUSIVE"
    summary = {
        "schema": "twistronics_s1b_interval_inertia_v1",
        "spec_id": spec["spec_id"], "case_id": case["case_id"],
        "parent_reviewed_commit": spec["parent_reviewed_commit"],
        "status": status,
        "claim_ceiling": spec["claim_ceiling"],
        "cutoffs": {k: {"status": v.get("status"), "reason": v.get("reason"),
                         "counters": v.get("counters", {})}
                    for k, v in cutoff_results.items()},
        "global_counters": {"inertia_factorizations": factor_total,
                            "wall_seconds": time.monotonic() - started,
                            "physical_cases": 1, "parameter_sweeps": 0},
        "interpretation": ("Uniform external isolation certified for both declared finite systems."
                           if status.startswith("CERTIFIED") else
                           "The bounded sufficient method did not certify complete coverage; this is not evidence that a physical gap closes."),
        "limits": ["No projector, transport, seam, integer, topology, relative-class, cutoff-convergence, or experimental claim."],
    }
    atomic_json(output / "RESULTS.json", summary)
    env = {"python": platform.python_version(), "platform": platform.platform(),
           "worker_processes": 1, "runtime_provenance": provenance,
           "precision_bits": spec["precision_bits"]}
    atomic_json(output / "ENVIRONMENT.json", env)
    sources = {
        str(CASE_PATH.relative_to(ROOT)): sha256(CASE_PATH),
        str(PLAN_PATH.relative_to(ROOT)): sha256(PLAN_PATH),
        str(PARENT_CHECK.relative_to(ROOT)): sha256(PARENT_CHECK),
        str((PARENT / "verify.py").relative_to(ROOT)): sha256(PARENT / "verify.py"),
        str(WHEEL_LOCK_PATH.relative_to(ROOT)): sha256(WHEEL_LOCK_PATH),
        str(SPEC_PATH.relative_to(ROOT)): sha256(SPEC_PATH),
        str(Path(__file__).resolve().relative_to(ROOT)): sha256(Path(__file__).resolve()),
        str((HERE / "verify.py").relative_to(ROOT)): sha256(HERE / "verify.py"),
        str((HERE / "README.md").relative_to(ROOT)): sha256(HERE / "README.md"),
        "external-wheel://" + wheel.name: sha256(wheel),
    }
    atomic_json(output / "SOURCE_BINDINGS.json", sources)
    manifest = {p.name: sha256(p) for p in sorted(output.iterdir())}
    atomic_json(output / "MANIFEST.json", manifest)
    print(status)
    print(json.dumps(summary["global_counters"], indent=2))
    return 1 if status == "EXECUTION_ERROR" else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("wheel_positional", nargs="?", type=Path)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--worker", choices=("a", "b"))
    parser.add_argument("--worker-output", type=Path)
    args = parser.parse_args()
    wheel = (args.wheel or args.wheel_positional)
    if wheel is None:
        parser.error("wheel path is required")
    wheel = wheel.resolve()
    if args.worker:
        if args.worker_output is None:
            parser.error("--worker-output is required with --worker")
        return run_cutoff(args.worker, wheel, args.worker_output.resolve())
    if args.output is None:
        parser.error("output directory is required")
    return driver(args.output.resolve(), wheel)


if __name__ == "__main__":
    raise SystemExit(main())
