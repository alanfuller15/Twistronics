#!/usr/bin/env python3
"""Replay-free verifier for the retained S1b hard-region feasibility probe."""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sign(endpoint: list[str]) -> int:
    lo, hi = map(Fraction, endpoint)
    if lo > hi:
        raise RuntimeError("REVERSED_INTERVAL")
    if lo > 0:
        return 1
    if hi < 0:
        return -1
    return 0


def require_positive_interval(endpoint: list[str], label: str) -> None:
    lo, hi = map(Fraction, endpoint)
    if lo > hi or lo <= 0:
        raise RuntimeError(label)


def verify_windows(windows: dict, definitions: dict) -> tuple[bool, int]:
    accepted = True
    factors = 0
    for name in ("lower", "upper"):
        window = windows[name]
        definition = definitions[name]
        if Fraction(window["width_meV"]) < Fraction(window["target_lower_meV"]):
            raise RuntimeError("WINDOW_WIDTH_BELOW_TARGET")
        if window["width_meV"] != definition["width_meV"]:
            raise RuntimeError("WINDOW_DEFINITION_MISMATCH")
        if len(window["endpoints"]) != 2:
            raise RuntimeError("ENDPOINT_COUNT_MISMATCH")
        endpoint_ok = True
        for factor in window["endpoints"]:
            factors += 1
            if factor["shift"] != definition[factor["label"]]:
                raise RuntimeError("RECORDED_SHIFT_MISMATCH")
            signs = [sign(pivot) for pivot in factor["pivots"]]
            computed = sum(value < 0 for value in signs)
            if factor["status"] == "CERTIFIED":
                if 0 in signs or computed != factor["negative"]:
                    raise RuntimeError("CERTIFIED_PIVOT_RECORD_INVALID")
                ok = computed == factor["expected_negative"]
            else:
                index = factor.get("pivot_index")
                if index is None or index >= len(signs) or signs[index] != 0:
                    raise RuntimeError("INCONCLUSIVE_PIVOT_RECORD_INVALID")
                ok = False
            endpoint_ok = endpoint_ok and ok
        if window["certified"] != endpoint_ok:
            raise RuntimeError("WINDOW_STATUS_MISMATCH")
        accepted = accepted and endpoint_ok
    return accepted, factors


def main() -> int:
    run = Path(sys.argv[1]).resolve()
    manifest = json.loads((run / "MANIFEST.json").read_text())
    actual = {path.name: sha256(path) for path in sorted(run.iterdir())
              if path.name != "MANIFEST.json"}
    if actual != manifest:
        raise RuntimeError("MANIFEST_MISMATCH")
    sources = json.loads((run / "SOURCE_BINDINGS.json").read_text())
    for name, digest in sources.items():
        if name.startswith("external-wheel://"):
            continue
        path = ROOT / name
        if not path.is_file() or sha256(path) != digest:
            raise RuntimeError("SOURCE_BINDING_MISMATCH:" + name)
    spec = json.loads((HERE / "SPEC.json").read_text())
    results = json.loads((run / "RESULTS.json").read_text())
    parts = sorted(run.glob("CELLS.json.gz.part*"))
    if not parts or [path.name for path in parts] != [f"CELLS.json.gz.part{i:03d}"
                                                      for i in range(len(parts))]:
        raise RuntimeError("CELL_PART_SET_INVALID")
    records = json.loads(gzip.decompress(b"".join(path.read_bytes() for path in parts)))
    expected_cells = {(key, *cell) for key in spec["cutoff_order"]
                      for cell in spec["probe_cells"]}
    seen = {(record["cutoff"], record["cell"]["depth"], record["cell"]["ix"],
             record["cell"]["iy"]) for record in records}
    if seen != expected_cells or len(records) != spec["limits"]["probe_cells_total"]:
        raise RuntimeError("PROBE_CELL_SET_MISMATCH")

    primary_certified = accepted = primary_factors = recompute_factors = 0
    for record in records:
        if record["primary"]["decimal_digits"] != 17:
            raise RuntimeError("PRIMARY_DIGITS_MISMATCH")
        require_positive_interval(record["primary"]["gram_margin_min"],
                                  "PRIMARY_GRAM_CERTIFICATE_INVALID")
        primary_ok, factors = verify_windows(
            record["primary"]["windows"], record["window_definitions"])
        primary_factors += factors
        if record["primary"]["certified"] != primary_ok:
            raise RuntimeError("PRIMARY_STATUS_MISMATCH")
        primary_certified += int(primary_ok)
        recomputation = record["recomputation"]
        final_ok = False
        if primary_ok:
            if recomputation is None or not recomputation["uses_primary_recorded_shifts"]:
                raise RuntimeError("MISSING_ACCEPTED_CELL_RECOMPUTATION")
            if recomputation["decimal_digits"] != spec["recomputation_decimal_digits"]:
                raise RuntimeError("RECOMPUTATION_DIGITS_MISMATCH")
            require_positive_interval(recomputation["gram_margin_min"],
                                      "RECOMPUTATION_GRAM_CERTIFICATE_INVALID")
            recompute_ok, factors = verify_windows(
                recomputation["windows"], record["window_definitions"])
            recompute_factors += factors
            if recomputation["certified"] != recompute_ok:
                raise RuntimeError("RECOMPUTATION_STATUS_MISMATCH")
            final_ok = recompute_ok
        elif recomputation is not None:
            raise RuntimeError("UNNECESSARY_RECOMPUTATION")
        status_ok = record["status"] == "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS"
        if status_ok != final_ok:
            raise RuntimeError("FINAL_CELL_STATUS_MISMATCH")
        accepted += int(final_ok)

    limits = spec["limits"]
    total_factors = primary_factors + recompute_factors
    if primary_factors != limits["primary_factorizations_total"]:
        raise RuntimeError("PRIMARY_FACTORIZATION_COUNT_MISMATCH")
    if recompute_factors > limits["max_recomputation_factorizations"]:
        raise RuntimeError("RECOMPUTATION_CAP_EXCEEDED")
    if total_factors > limits["max_factorizations_total"]:
        raise RuntimeError("TOTAL_FACTORIZATION_CAP_EXCEEDED")
    expected_summary = {
        "cells": len(records), "primary_factorizations": primary_factors,
        "recomputation_factorizations": recompute_factors,
        "factorizations": total_factors,
        "primary_certified_cells": primary_certified,
        "certified_recomputed_cells": accepted,
    }
    for key, value in expected_summary.items():
        if results[key] != value:
            raise RuntimeError("SUMMARY_MISMATCH:" + key)
    if (results["status"] != "HARD_REGION_METHOD_FEASIBILITY_PROBE_COMPLETE" or
            results["parameter_sweeps"] != 0 or results["claim_ceiling"] != spec["claim_ceiling"]):
        raise RuntimeError("CLAIM_CEILING_MISMATCH")
    print("PASS_RETAINED_S1B_HARD_REGION_METHOD_PROBE")
    print(json.dumps(expected_summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
