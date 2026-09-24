#!/usr/bin/env python3
"""Replay-free verifier for the retained S1b method-feasibility probe."""
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


def main() -> int:
    run = Path(sys.argv[1]).resolve()
    manifest = json.loads((run / "MANIFEST.json").read_text())
    actual = {p.name: sha256(p) for p in sorted(run.iterdir()) if p.name != "MANIFEST.json"}
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
    if not parts or [p.name for p in parts] != [f"CELLS.json.gz.part{i:03d}"
                                                for i in range(len(parts))]:
        raise RuntimeError("CELL_PART_SET_INVALID")
    records = json.loads(gzip.decompress(b"".join(p.read_bytes() for p in parts)))
    expected_cells = {(k, *cell) for k in spec["cutoff_order"] for cell in spec["probe_cells"]}
    seen = {(r["cutoff"], r["cell"]["depth"], r["cell"]["ix"], r["cell"]["iy"])
            for r in records}
    if seen != expected_cells or len(records) != spec["limits"]["cells_total"]:
        raise RuntimeError("PROBE_CELL_SET_MISMATCH")
    certified = 0
    factors = 0
    for record in records:
        cell_ok = True
        for name in ("lower", "upper"):
            window = record["windows"][name]
            if Fraction(window["width_meV"]) < Fraction(window["target_lower_meV"]):
                raise RuntimeError("WINDOW_WIDTH_BELOW_TARGET")
            if len(window["endpoints"]) != 2:
                raise RuntimeError("ENDPOINT_COUNT_MISMATCH")
            endpoint_ok = True
            for factor in window["endpoints"]:
                factors += 1
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
            cell_ok = cell_ok and endpoint_ok
        if (record["status"] == "CERTIFIED_FIXED_CELL_WINDOWS") != cell_ok:
            raise RuntimeError("CELL_STATUS_MISMATCH")
        certified += int(cell_ok)
    if factors != spec["limits"]["factorizations_total"]:
        raise RuntimeError("FACTORIZATION_COUNT_MISMATCH")
    if results["certified_probe_cells"] != certified:
        raise RuntimeError("SUMMARY_CERTIFIED_COUNT_MISMATCH")
    if results["status"] != "METHOD_FEASIBILITY_PROBE_COMPLETE" or results["parameter_sweeps"] != 0:
        raise RuntimeError("CLAIM_CEILING_MISMATCH")
    print("PASS_RETAINED_S1B_CELL_INTRINSIC_METHOD_PROBE")
    print(json.dumps({"cells": len(records), "factorizations": factors,
                      "certified_probe_cells": certified}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
