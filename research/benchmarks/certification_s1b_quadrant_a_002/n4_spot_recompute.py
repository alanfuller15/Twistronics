#!/usr/bin/env python3
"""Deterministic post-run N4 third-congruence spot recomputation.

This is review evidence only.  It reads an already packaged packet-002 run,
selects five accepted durable records without inspecting their margins, and
recomputes the recorded shifts using a structurally different congruence.
It never changes the search partition or runs an additional cell search.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from flint import ctx
from scipy.linalg import eigh


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE_PATH = ROOT / "research/benchmarks/certification_s1b_001/check.py"
METHOD_PATH = ROOT / "research/benchmarks/certification_s1b_method_004/check.py"
CASE_PATH = ROOT / "docs/certification-readiness/CASE.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def accepted_records(log_path: Path) -> tuple[dict, list[dict]]:
    with log_path.open() as stream:
        header = json.loads(next(stream))
        records = [
            json.loads(line) for line in stream
            if line.strip()
        ]
    accepted = [
        item for item in records
        if item["outcome"] == "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS"
    ]
    if not accepted:
        raise RuntimeError("NO_ACCEPTED_RECORDS")
    return header, accepted


def deterministic_selection(accepted: list[dict]) -> list[dict]:
    """Earliest accepted record at each depth, plus latest deepest record."""
    first_by_depth = {}
    for item in accepted:
        first_by_depth.setdefault(item["cell"]["depth"], item)
    selected = [first_by_depth[depth] for depth in sorted(first_by_depth)]
    deepest = max(first_by_depth)
    latest_deepest = max(
        (item for item in accepted if item["cell"]["depth"] == deepest),
        key=lambda item: item["sequence"],
    )
    if latest_deepest not in selected:
        selected.append(latest_deepest)
    if len(selected) != 5:
        raise RuntimeError(f"EXPECTED_FIVE_SELECTED_RECORDS_GOT_{len(selected)}")
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("OUTPUT_ALREADY_EXISTS")

    receipt = json.loads((run / "SUPERVISOR_RECEIPT.json").read_text())
    results = json.loads((run / "RESULTS.json").read_text())
    log_path = run / "ATTEMPTS.ndjson"
    observed_log_sha = sha256(log_path)
    if observed_log_sha != receipt["durable_log_sha256"]:
        raise RuntimeError("DURABLE_LOG_SHA256_MISMATCH")
    if results["status"] != "INCONCLUSIVE_WATCHDOG_TIMEOUT":
        raise RuntimeError("UNEXPECTED_PACKET_STATUS")

    header, accepted = accepted_records(log_path)
    selected = deterministic_selection(accepted)
    if header["implementation_commit"] != results["implementation_commit"]:
        raise RuntimeError("IMPLEMENTATION_BINDING_MISMATCH")

    base = load_module(BASE_PATH, "packet002_n4_base")
    method = load_module(METHOD_PATH, "packet002_n4_method")
    assembly = base.load_parent()
    case = json.loads(CASE_PATH.read_text())
    assembly.validate_case(case)
    cutoff = case["cutoffs"]["a"]
    coefficients, _ = assembly.assemble_coefficients(
        cutoff["ordered_indices"], case)
    ctx.prec = 128
    ctx.threads = 1

    checked = []
    for item in selected:
        cell = item["cell"]
        depth, ix, iy = cell["depth"], cell["ix"], cell["iy"]
        den = 1 << depth
        x0, x1 = Fraction(ix, den), Fraction(ix + 1, den)
        y0, y1 = Fraction(iy, den), Fraction(iy + 1, den)
        xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
        center = base.matrix_from_coefficients(coefficients, xc, yc)
        midpoint = assembly.mid_float([
            [center[i, j] for j in range(center.ncols())]
            for i in range(center.nrows())
        ])
        _, vectors = eigh(midpoint, driver="evx", check_finite=True)
        seed = int.from_bytes(
            hashlib.sha256(item["record_sha256"].encode()).digest()[:8], "big")
        rng = np.random.default_rng(seed)
        perturbation = np.eye(vectors.shape[1]) + 1e-9 * rng.standard_normal(
            (vectors.shape[1], vectors.shape[1]))
        third_vectors = vectors @ perturbation
        orthogonality_defect = float(np.linalg.norm(
            third_vectors.T @ third_vectors - np.eye(vectors.shape[1]), ord="fro"))
        if not orthogonality_defect > 0:
            raise RuntimeError("THIRD_CONGRUENCE_NOT_PERTURBED")

        dx = method.exact_box(base, x0 - xc, x1 - xc)
        dy = method.exact_box(base, y0 - yc, y1 - yc)
        _, gram, margins, minimum, boxed = method.certified_congruence(
            base, coefficients, center, third_vectors, dx, dy, 12)
        definitions = item["full_interval_evidence"]["window_definitions"]
        windows, certified = method.run_windows(base, boxed, gram, definitions)
        observed_counts = {
            name: [endpoint["negative"] for endpoint in data["endpoints"]]
            for name, data in windows.items()
        }
        if not certified or observed_counts != {"lower": [97, 97], "upper": [99, 99]}:
            raise RuntimeError("THIRD_CONGRUENCE_DID_NOT_CERTIFY")
        checked.append({
            "source_sequence": item["sequence"],
            "source_record_sha256": item["record_sha256"],
            "cell": cell,
            "selection_role": (
                "latest_deepest" if item is selected[-1]
                else f"earliest_accepted_depth_{depth}"
            ),
            "seed_from_source_record_sha256": seed,
            "lapack_driver": "evx",
            "right_perturbation": "I + 1e-9 * N(0,1)",
            "decimal_digits": 12,
            "orthogonality_defect_fro_before_decimal_rounding":
                format(orthogonality_defect, ".17g"),
            "gram_margin_min": minimum,
            "gram_margins": margins,
            "recorded_window_definitions": definitions,
            "windows": windows,
            "certified": True,
        })

    payload = {
        "schema_version": 1,
        "evidence_id": "S1B-QUADRANT-A-002-N4-SPOT-001",
        "audit_requirement": "N4 third-congruence spot recomputation",
        "scope": "five already-accepted cutoff-a cells only; no search or parameter sweep",
        "selection": (
            "earliest accepted durable record at every observed accepted depth, "
            "plus the latest durable record at the maximum accepted depth"
        ),
        "approved_protocol_commit": results["approved_protocol_commit"],
        "implementation_commit": results["implementation_commit"],
        "packet_status": results["status"],
        "packet_attempts": results["attempted_cells"],
        "durable_log_sha256": observed_log_sha,
        "results_sha256": sha256(run / "RESULTS.json"),
        "partition_sha256": sha256(run / "PARTITION.json"),
        "runtime_provenance_digest": header["runtime_provenance_digest"],
        "precision_bits": 128,
        "cutoff": "a",
        "factorizations": 4 * len(checked),
        "selected_cells": len(checked),
        "all_certified": all(item["certified"] for item in checked),
        "records": checked,
        "limitations": [
            "This spot check is not a coverage extension and changes no partition cell.",
            "It checks a third fixed congruence at retained shifts, not an independent LDL implementation.",
            "No full-quadrant, full-domain, cutoff-b/agreement, topology, transport, seam, cutoff-convergence, v078, or experimental claim follows.",
        ],
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": "PASS_N4_THIRD_CONGRUENCE_SPOT",
        "selected": [item["cell"] for item in checked],
        "factorizations": payload["factorizations"],
        "output_sha256": sha256(output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
