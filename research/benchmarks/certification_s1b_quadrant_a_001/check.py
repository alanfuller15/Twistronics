#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import resource
import sys
import time
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
from typing import Any

from flint import ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
METHOD_DIR = ROOT / "research" / "benchmarks" / "certification_s1b_method_004"
METHOD_CHECK = METHOD_DIR / "check.py"
BASE_DIR = ROOT / "research" / "benchmarks" / "certification_s1b_001"
CASE = ROOT / "docs" / "certification-readiness" / "CASE.json"
LOCK = ROOT / "research" / "benchmarks" / "certification_s1a_hardening_001" / "WHEEL_LOCK.json"
SPEC = HERE / "SPEC.json"
PART_BYTES = 500_000

NOTE = ROOT / "docs" / "certification-readiness" / "S1B_QUADRANT_A_001.md"
SOURCE_PATHS = [
    CASE,
    LOCK,
    SPEC,
    NOTE,
    HERE / "check.py",
    HERE / "verify.py",
    METHOD_DIR / "SPEC.json",
    METHOD_DIR / "check.py",
    METHOD_DIR / "verify.py",
    METHOD_DIR / "RUN" / "RESULTS.json",
    BASE_DIR / "SPEC.json",
    BASE_DIR / "check.py",
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def cell_ref(cell: tuple[int, int, int] | list[int]) -> dict[str, int]:
    d, ix, iy = map(int, cell)
    return {"depth": d, "ix": ix, "iy": iy}


def cell_tuple(ref: dict[str, Any]) -> tuple[int, int, int]:
    return int(ref["depth"]), int(ref["ix"]), int(ref["iy"])


def children(cell: tuple[int, int, int]):
    d, ix, iy = cell
    for xb in (0, 1):
        for yb in (0, 1):
            yield d + 1, 2 * ix + xb, 2 * iy + yb


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def area_fraction_of_quadrant(cells: list[dict[str, int]]) -> Fraction:
    return sum((Fraction(4 ** (1 - int(c["depth"]))) for c in cells), Fraction(0))


def depth_histogram(cells: list[dict[str, int]]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(int(c["depth"]) for c in cells).items())}


def write_parts(payload: bytes) -> list[dict[str, Any]]:
    compressed = gzip.compress(payload, compresslevel=9, mtime=0)
    for old in HERE.glob("CELLS.json.gz.part*"):
        old.unlink()
    out = []
    for i, offset in enumerate(range(0, len(compressed), PART_BYTES)):
        name = f"CELLS.json.gz.part{i:03d}"
        path = HERE / name
        path.write_bytes(compressed[offset : offset + PART_BYTES])
        out.append({"path": name, "bytes": path.stat().st_size, "sha256": sha256(path)})
    return out


def finalize_manifest() -> None:
    results = json.loads((HERE / "RESULTS.json").read_text())
    parts = [HERE / item["path"] for item in results["records"]["parts"]]
    sources = []
    for path in SOURCE_PATHS:
        sources.append({"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256(path)})
    generated = [HERE / "RESULTS.json", HERE / "PARTITION.json"] + parts
    manifest = {
        "schema_version": 1,
        "packet_id": results["packet_id"],
        "sources": sources,
        "generated": [
            {"path": str(path.relative_to(HERE)), "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in generated
        ],
    }
    (HERE / "MANIFEST.sha256.json").write_bytes(canonical_bytes(manifest))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", nargs="?", type=Path)
    parser.add_argument("--finalize-existing", action="store_true")
    args = parser.parse_args()
    if args.finalize_existing:
        finalize_manifest()
        print("FINALIZED_EXISTING_RETAINED_RUN")
        return 0
    if args.wheel is None:
        parser.error("wheel is required unless --finalize-existing is used")
    wheel = args.wheel.resolve()
    spec = json.loads(SPEC.read_text())
    if spec["precision_bits"] != 128 or spec["algorithm"]["max_depth"] != 9:
        raise RuntimeError("frozen precision/depth mismatch")
    if spec["cutoff"] != "a" or spec["domain"] != {"x": ["1/2", "1"], "y": ["1/2", "1"]}:
        raise RuntimeError("frozen cutoff/domain mismatch")
    limits = spec["limits"]
    if limits["physical_cases"] != 1 or limits["parameter_sweeps"] != 0 or limits["workers"] != 1:
        raise RuntimeError("frozen execution-count mismatch")

    method = load_module(METHOD_CHECK, "reviewed_s1b_method004")
    base = method.load_module(method.BASE_CHECK, "reviewed_s1b_base_for_quadrant")
    assembly = base.load_parent()
    case = json.loads(CASE.read_text())
    lock = json.loads(LOCK.read_text())
    provenance = base.runtime_provenance(wheel, lock)
    assembly.validate_case(case)
    cutoff = case["cutoffs"]["a"]
    resource.setrlimit(resource.RLIMIT_AS,
                       (limits["address_space_bytes"], limits["address_space_bytes"]))
    ctx.prec = spec["precision_bits"]
    ctx.threads = 1
    coefficients, _ = assembly.assemble_coefficients(cutoff["ordered_indices"], case)

    queue: deque[tuple[int, int, int]] = deque([tuple(spec["algorithm"]["root_cell"])])
    records: list[dict[str, Any]] = []
    accepted: list[dict[str, int]] = []
    unresolved: list[dict[str, int]] = []
    primary_factors = 0
    recompute_factors = 0
    stop_reason: str | None = None
    started = time.monotonic()

    while queue:
        elapsed = time.monotonic() - started
        if len(records) >= limits["max_attempted_cells"]:
            stop_reason = "MAX_ATTEMPTED_CELLS"
            break
        if primary_factors + 4 > limits["max_primary_factorizations"]:
            stop_reason = "MAX_PRIMARY_FACTORIZATIONS"
            break
        if elapsed >= limits["wall_seconds"]:
            stop_reason = "WALL_SECONDS_ADMISSION_CAP"
            break

        cell = queue.popleft()
        record = method.probe_cell(base, assembly, coefficients, cutoff, spec, list(cell))
        record["sequence"] = len(records)
        record["cutoff"] = "a"
        records.append(record)
        primary_factors += 4
        if record["primary"]["certified"]:
            recompute_factors += 4
        if recompute_factors > limits["max_recomputation_factorizations"]:
            raise RuntimeError("recomputation factor cap exceeded")

        if record["status"] == "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS":
            accepted.append(cell_ref(cell))
        elif cell[0] < spec["algorithm"]["max_depth"]:
            queue.extend(children(cell))
        else:
            unresolved.append(cell_ref(cell))

    frontier = [cell_ref(cell) for cell in queue]
    if not frontier and unresolved and stop_reason is None:
        stop_reason = "MAX_DEPTH_UNRESOLVED"

    accepted_fraction = area_fraction_of_quadrant(accepted)
    unresolved_fraction = area_fraction_of_quadrant(unresolved)
    frontier_fraction = area_fraction_of_quadrant(frontier)
    if accepted_fraction + unresolved_fraction + frontier_fraction != 1:
        raise RuntimeError("terminal cells do not cover the quadrant exactly")

    status = (
        "CERTIFIED_CUTOFF_A_HARD_QUADRANT_COVERAGE"
        if not unresolved and not frontier
        else "INCONCLUSIVE_BOUNDED_COVERAGE"
    )
    elapsed_seconds = time.monotonic() - started
    records_payload = canonical_bytes(records)
    parts = write_parts(records_payload)
    partition = {
        "schema_version": 1,
        "root_cell": cell_ref(tuple(spec["algorithm"]["root_cell"])),
        "accepted_cells": accepted,
        "unresolved_max_depth_cells": unresolved,
        "unprocessed_frontier_cells": frontier,
        "accepted_depth_histogram": depth_histogram(accepted),
        "unresolved_depth_histogram": depth_histogram(unresolved),
        "frontier_depth_histogram": depth_histogram(frontier),
        "accepted_area_fraction_of_quadrant": fraction_text(accepted_fraction),
        "unresolved_area_fraction_of_quadrant": fraction_text(unresolved_fraction),
        "frontier_area_fraction_of_quadrant": fraction_text(frontier_fraction),
        "complete_disjoint_partition": True,
        "stop_reason": stop_reason,
    }
    (HERE / "PARTITION.json").write_bytes(canonical_bytes(partition))

    results = {
        "schema_version": 1,
        "packet_id": spec["packet_id"],
        "status": status,
        "cutoff": "a",
        "domain": spec["domain"],
        "precision_bits": spec["precision_bits"],
        "max_depth": spec["algorithm"]["max_depth"],
        "attempted_cells": len(records),
        "accepted_cells": len(accepted),
        "unresolved_max_depth_cells": len(unresolved),
        "unprocessed_frontier_cells": len(frontier),
        "primary_factorizations": primary_factors,
        "recomputation_factorizations": recompute_factors,
        "total_factorizations": primary_factors + recompute_factors,
        "elapsed_seconds": elapsed_seconds,
        "stop_reason": stop_reason,
        "partition": {
            "path": "PARTITION.json",
            "sha256": sha256(HERE / "PARTITION.json"),
        },
        "records": {
            "encoding": "canonical_json_then_gzip_mtime_0_then_fixed_parts",
            "uncompressed_bytes": len(records_payload),
            "uncompressed_sha256": hashlib.sha256(records_payload).hexdigest(),
            "parts": parts,
        },
        "runtime_provenance": provenance,
        "limits": limits,
        "claim_ceiling": spec["claim_ceiling"],
        "limitations": [
            "Only cutoff a on [1/2,1]^2 was attempted.",
            "Any unresolved or unprocessed retained cell makes the coverage result inconclusive.",
            "No full-domain, cutoff-b, cutoff-agreement, topology, transport, seam, cutoff-convergence, or experimental claim follows.",
        ],
    }
    (HERE / "RESULTS.json").write_bytes(canonical_bytes(results))

    finalize_manifest()
    print(json.dumps({
        "status": status,
        "attempted_cells": len(records),
        "accepted_cells": len(accepted),
        "unresolved_max_depth_cells": len(unresolved),
        "frontier_cells": len(frontier),
        "accepted_area_fraction": fraction_text(accepted_fraction),
        "elapsed_seconds": elapsed_seconds,
    }, sort_keys=True))
    return 0 if status == "CERTIFIED_CUTOFF_A_HARD_QUADRANT_COVERAGE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
