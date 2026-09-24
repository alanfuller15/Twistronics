#!/usr/bin/env python3
"""Run the fixed S1b cell-intrinsic method-feasibility probe."""
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
from flint import arb_mat, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SPEC_PATH = HERE / "SPEC.json"
PARENT = ROOT / "research/benchmarks/certification_s1b_001"
PARENT_CHECK = PARENT / "check.py"
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


def exact_box(parent, lo: Fraction, hi: Fraction):
    if not lo <= hi:
        raise RuntimeError("INVALID_EXACT_BOX")
    return parent.exact_arb(lo).union(parent.exact_arb(hi))


def probe_cell(parent, assembly, coefficients, cutoff: dict, spec: dict, cell: list[int]) -> dict:
    depth, ix, iy = cell
    den = 1 << depth
    x0, x1 = Fraction(ix, den), Fraction(ix + 1, den)
    y0, y1 = Fraction(iy, den), Fraction(iy + 1, den)
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    center = parent.matrix_from_coefficients(coefficients, xc, yc)
    midpoint = assembly.mid_float([[center[i, j] for j in range(center.ncols())]
                                   for i in range(center.nrows())])
    eigenvalues, vectors = np.linalg.eigh(midpoint)
    V = parent.decimal_matrix(vectors)
    gram, margins, minimum = parent.gram_certificate(V)
    VT = V.transpose()
    transformed = VT * center * V
    dx = exact_box(parent, x0 - xc, x1 - xc)
    dy = exact_box(parent, y0 - yc, y1 - yc)
    boxed = (transformed + dx * (VT * arb_mat(coefficients[1]) * V) +
             dy * (VT * arb_mat(coefficients[2]) * V))
    parent_spec = json.loads((PARENT / "SPEC.json").read_text())
    parent_spec["_cutoff"] = cutoff
    lo, hi = cutoff["selected_bands_zero_based"]
    windows = parent.candidate_windows(eigenvalues, lo, hi, parent_spec)
    records = {}
    accepted = True
    for name, (left, right, expected) in windows.items():
        endpoints = []
        for label, shift in (("left", left), ("right", right)):
            result = parent.interval_ldl(boxed - parent.exact_arb(shift) * gram)
            result["label"] = label
            result["shift"] = parent.rational_text(shift)
            result["expected_negative"] = expected
            endpoints.append(result)
        width = right - left
        target = Fraction(parent_spec["target_external_gap_lower_meV"])
        ok = (width >= target and
              all(r["status"] == "CERTIFIED" and r["negative"] == expected
                  for r in endpoints))
        accepted = accepted and ok
        records[name] = {"expected_negative": expected, "certified": ok,
                         "width_meV": parent.rational_text(width),
                         "target_lower_meV": parent.rational_text(target),
                         "endpoints": endpoints}
    return {
        "cell": {"depth": depth, "ix": ix, "iy": iy,
                 "x": [parent.rational_text(x0), parent.rational_text(x1)],
                 "y": [parent.rational_text(y0), parent.rational_text(y1)]},
        "precision_bits": spec["precision_bits"],
        "dimension": cutoff["dimension"],
        "gram_margin_min": minimum,
        "gram_margins": margins,
        "windows": records,
        "status": "CERTIFIED_FIXED_CELL_WINDOWS" if accepted else "INCONCLUSIVE"
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
    parent = load_module(PARENT_CHECK, "reviewed_s1b")
    assembly = parent.load_parent()
    lock = json.loads(WHEEL_LOCK_PATH.read_text())
    provenance = parent.runtime_provenance(wheel, lock)
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
            record = probe_cell(parent, assembly, coefficients, cutoff, spec, cell)
            record["cutoff"] = key
            records.append(record)
            if time.monotonic() - started > spec["limits"]["wall_seconds"]:
                raise RuntimeError("DETERMINISTIC_WALL_CAP_EXCEEDED")
    factor_count = sum(4 for _ in records)
    if len(records) != spec["limits"]["cells_total"]:
        raise RuntimeError("CELL_CAP_MISMATCH")
    if factor_count != spec["limits"]["factorizations_total"]:
        raise RuntimeError("FACTORIZATION_CAP_MISMATCH")
    output.mkdir(parents=True)
    raw = (json.dumps(records, indent=2, sort_keys=True) + "\n").encode()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    for offset in range(0, len(compressed), RETAINED_PART_BYTES):
        index = offset // RETAINED_PART_BYTES
        (output / f"CELLS.json.gz.part{index:03d}").write_bytes(
            compressed[offset:offset + RETAINED_PART_BYTES])
    certified = [r for r in records if r["status"] == "CERTIFIED_FIXED_CELL_WINDOWS"]
    summary = {
        "schema": "twistronics_s1b_cell_intrinsic_probe_v1",
        "spec_id": spec["spec_id"], "case_id": spec["case_id"],
        "parent_reviewed_commit": spec["parent_reviewed_commit"],
        "status": "METHOD_FEASIBILITY_PROBE_COMPLETE",
        "cells": len(records), "factorizations": factor_count,
        "certified_probe_cells": len(certified),
        "certified_by_cutoff": {key: sum(r["cutoff"] == key for r in certified)
                                for key in spec["cutoff_order"]},
        "deepest_probe": max(r["cell"]["depth"] for r in records),
        "parameter_sweeps": 0, "physical_cases": 1,
        "claim_ceiling": spec["claim_ceiling"],
        "interpretation": "Selected cells demonstrate method feasibility only; the parameter domain is not covered."
    }
    atomic_json(output / "RESULTS.json", summary)
    atomic_json(output / "ENVIRONMENT.json", {
        "python": platform.python_version(), "platform": platform.platform(),
        "precision_bits": spec["precision_bits"], "threads": 1,
        "runtime_provenance": provenance,
        "wall_seconds": time.monotonic() - started
    })
    sources = {str(p.relative_to(ROOT)): sha256(p) for p in
               [SPEC_PATH, Path(__file__).resolve(), HERE / "verify.py", HERE / "README.md",
                ROOT / "docs/certification-readiness/S1B_METHOD_002.md",
                PARENT_CHECK, PARENT / "SPEC.json", CASE_PATH, WHEEL_LOCK_PATH]}
    sources["external-wheel://" + wheel.name] = sha256(wheel)
    atomic_json(output / "SOURCE_BINDINGS.json", sources)
    manifest = {p.name: sha256(p) for p in sorted(output.iterdir())}
    atomic_json(output / "MANIFEST.json", manifest)
    print("METHOD_FEASIBILITY_PROBE_COMPLETE")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
