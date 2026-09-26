#!/usr/bin/env python3
"""Run the fixed S1b narrow-window hard-region feasibility probe."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import platform
import resource
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
from flint import arb, arb_mat, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SPEC_PATH = HERE / "SPEC.json"
BASE = ROOT / "research/benchmarks/certification_s1b_001"
BASE_CHECK = BASE / "check.py"
PARENT_PACKET = ROOT / "research/benchmarks/certification_s1b_method_002"
CASE_PATH = ROOT / "docs/certification-readiness/CASE.json"
WHEEL_LOCK_PATH = ROOT / "research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json"
RETAINED_PART_BYTES = 18_000


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def exact_box(base, lo: Fraction, hi: Fraction):
    if not lo <= hi:
        raise RuntimeError("INVALID_EXACT_BOX")
    return base.exact_arb(lo).union(base.exact_arb(hi))


def decimal_matrix(values: np.ndarray, digits: int) -> arb_mat:
    return arb_mat([[arb(format(float(value), f".{digits}g")) for value in row]
                    for row in values])


def certified_congruence(base, coefficients, center: arb_mat, vectors: np.ndarray,
                         dx, dy, digits: int):
    V = decimal_matrix(vectors, digits)
    gram, margins, minimum = base.gram_certificate(V)
    VT = V.transpose()
    boxed = (VT * center * V + dx * (VT * arb_mat(coefficients[1]) * V) +
             dy * (VT * arb_mat(coefficients[2]) * V))
    return V, gram, margins, minimum, boxed


def run_windows(base, boxed: arb_mat, gram: arb_mat, window_defs: dict) -> tuple[dict, bool]:
    records = {}
    accepted = True
    for name, definition in window_defs.items():
        expected = definition["expected_negative"]
        endpoints = []
        for label in ("left", "right"):
            shift = Fraction(definition[label])
            result = base.interval_ldl(boxed - base.exact_arb(shift) * gram)
            result.update({"label": label, "shift": base.rational_text(shift),
                           "expected_negative": expected})
            endpoints.append(result)
        ok = all(r["status"] == "CERTIFIED" and r["negative"] == expected
                 for r in endpoints)
        accepted = accepted and ok
        records[name] = {"expected_negative": expected, "certified": ok,
                         "width_meV": definition["width_meV"],
                         "target_lower_meV": definition["target_lower_meV"],
                         "endpoints": endpoints}
    return records, accepted


def probe_cell(base, assembly, coefficients, cutoff: dict, spec: dict,
               cell: list[int]) -> dict:
    depth, ix, iy = cell
    den = 1 << depth
    x0, x1 = Fraction(ix, den), Fraction(ix + 1, den)
    y0, y1 = Fraction(iy, den), Fraction(iy + 1, den)
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    center = base.matrix_from_coefficients(coefficients, xc, yc)
    midpoint = assembly.mid_float([[center[i, j] for j in range(center.ncols())]
                                   for i in range(center.nrows())])
    eigenvalues, vectors = np.linalg.eigh(midpoint)
    dx = exact_box(base, x0 - xc, x1 - xc)
    dy = exact_box(base, y0 - yc, y1 - yc)
    parent_spec = json.loads((BASE / "SPEC.json").read_text())
    parent_spec["_cutoff"] = cutoff
    lo, hi = cutoff["selected_bands_zero_based"]
    proposed = base.candidate_windows(eigenvalues, lo, hi, parent_spec)
    target = Fraction(parent_spec["target_external_gap_lower_meV"])
    window_defs = {}
    for name, (left, right, expected) in proposed.items():
        width = right - left
        if width < target:
            raise RuntimeError("PROPOSED_WINDOW_BELOW_TARGET")
        window_defs[name] = {
            "left": base.rational_text(left), "right": base.rational_text(right),
            "width_meV": base.rational_text(width),
            "target_lower_meV": base.rational_text(target),
            "expected_negative": expected,
        }

    _, gram, margins, minimum, boxed = certified_congruence(
        base, coefficients, center, vectors, dx, dy, 17)
    primary_windows, primary_ok = run_windows(base, boxed, gram, window_defs)
    primary = {"decimal_digits": 17, "gram_margin_min": minimum,
               "gram_margins": margins, "windows": primary_windows,
               "certified": primary_ok}

    recomputation = None
    final_ok = False
    if primary_ok:
        digits = spec["recomputation_decimal_digits"]
        _, gram2, margins2, minimum2, boxed2 = certified_congruence(
            base, coefficients, center, vectors, dx, dy, digits)
        windows2, recompute_ok = run_windows(base, boxed2, gram2, window_defs)
        recomputation = {"decimal_digits": digits, "gram_margin_min": minimum2,
                         "gram_margins": margins2, "windows": windows2,
                         "certified": recompute_ok,
                         "uses_primary_recorded_shifts": True}
        final_ok = recompute_ok

    return {
        "cell": {"depth": depth, "ix": ix, "iy": iy,
                 "x": [base.rational_text(x0), base.rational_text(x1)],
                 "y": [base.rational_text(y0), base.rational_text(y1)]},
        "precision_bits": spec["precision_bits"], "dimension": cutoff["dimension"],
        "window_definitions": window_defs, "primary": primary,
        "recomputation": recomputation,
        "status": "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS" if final_ok else "INCONCLUSIVE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    output, wheel = args.output.resolve(), args.wheel.resolve()
    if output.exists():
        raise RuntimeError("OUTPUT_ALREADY_EXISTS")
    spec = json.loads(SPEC_PATH.read_text())
    case = json.loads(CASE_PATH.read_text())
    base = load_module(BASE_CHECK, "reviewed_s1b_base")
    assembly = base.load_parent()
    lock = json.loads(WHEEL_LOCK_PATH.read_text())
    provenance = base.runtime_provenance(wheel, lock)
    assembly.validate_case(case)
    resource.setrlimit(resource.RLIMIT_AS,
                       (spec["limits"]["address_bytes"], spec["limits"]["address_bytes"]))
    ctx.prec = spec["precision_bits"]
    ctx.threads = 1
    started = time.monotonic()
    records = []
    for key in spec["cutoff_order"]:
        cutoff = case["cutoffs"][key]
        coefficients, _ = assembly.assemble_coefficients(cutoff["ordered_indices"], case)
        for cell in spec["probe_cells"]:
            record = probe_cell(base, assembly, coefficients, cutoff, spec, cell)
            record["cutoff"] = key
            records.append(record)
            if time.monotonic() - started > spec["limits"]["wall_seconds"]:
                raise RuntimeError("DETERMINISTIC_WALL_CAP_EXCEEDED")

    limits = spec["limits"]
    primary_factors = 4 * len(records)
    recompute_factors = 4 * sum(r["recomputation"] is not None for r in records)
    total_factors = primary_factors + recompute_factors
    if len(records) != limits["probe_cells_total"]:
        raise RuntimeError("CELL_CAP_MISMATCH")
    if primary_factors != limits["primary_factorizations_total"]:
        raise RuntimeError("PRIMARY_FACTORIZATION_COUNT_MISMATCH")
    if recompute_factors > limits["max_recomputation_factorizations"]:
        raise RuntimeError("RECOMPUTATION_CAP_EXCEEDED")
    if total_factors > limits["max_factorizations_total"]:
        raise RuntimeError("TOTAL_FACTORIZATION_CAP_EXCEEDED")

    output.mkdir(parents=True)
    raw = (json.dumps(records, indent=2, sort_keys=True) + "\n").encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    for offset in range(0, len(compressed), RETAINED_PART_BYTES):
        index = offset // RETAINED_PART_BYTES
        (output / f"CELLS.json.gz.part{index:03d}").write_bytes(
            compressed[offset:offset + RETAINED_PART_BYTES])
    primary_certified = [r for r in records if r["primary"]["certified"]]
    accepted = [r for r in records
                if r["status"] == "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS"]
    summary = {
        "schema": "twistronics_s1b_hard_region_probe_v1",
        "spec_id": spec["spec_id"], "case_id": spec["case_id"],
        "parent_reviewed_commit": spec["parent_reviewed_commit"],
        "status": "HARD_REGION_METHOD_FEASIBILITY_PROBE_COMPLETE",
        "cells": len(records), "primary_factorizations": primary_factors,
        "recomputation_factorizations": recompute_factors,
        "factorizations": total_factors,
        "primary_certified_cells": len(primary_certified),
        "certified_recomputed_cells": len(accepted),
        "certified_by_cutoff": {key: sum(r["cutoff"] == key for r in accepted)
                                for key in spec["cutoff_order"]},
        "minimum_certified_depth_by_cutoff": {
            key: min((r["cell"]["depth"] for r in accepted if r["cutoff"] == key),
                     default=None) for key in spec["cutoff_order"]},
        "parameter_sweeps": 0, "physical_cases": 1,
        "claim_ceiling": spec["claim_ceiling"],
        "interpretation": "Two frozen chains only; the high-coordinate quadrant and full domain are not covered."
    }
    atomic_json(output / "RESULTS.json", summary)
    atomic_json(output / "ENVIRONMENT.json", {
        "python": platform.python_version(), "platform": platform.platform(),
        "precision_bits": spec["precision_bits"], "threads": 1,
        "runtime_provenance": provenance,
        "wall_seconds": time.monotonic() - started
    })
    bound_paths = [SPEC_PATH, Path(__file__).resolve(), HERE / "verify.py", HERE / "README.md",
                   ROOT / "docs/certification-readiness/S1B_METHOD_003.md",
                   BASE_CHECK, BASE / "SPEC.json", CASE_PATH, WHEEL_LOCK_PATH,
                   PARENT_PACKET / "check.py", PARENT_PACKET / "verify.py",
                   PARENT_PACKET / "SPEC.json", PARENT_PACKET / "RUN/RESULTS.json"]
    sources = {str(path.relative_to(ROOT)): sha256(path) for path in bound_paths}
    sources["external-wheel://" + wheel.name] = sha256(wheel)
    atomic_json(output / "SOURCE_BINDINGS.json", sources)
    manifest = {path.name: sha256(path) for path in sorted(output.iterdir())}
    atomic_json(output / "MANIFEST.json", manifest)
    print("HARD_REGION_METHOD_FEASIBILITY_PROBE_COMPLETE")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
