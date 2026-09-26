#!/usr/bin/env python3
from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SPEC = HERE / "SPEC.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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


def cell_tuple(value: dict[str, Any]) -> tuple[int, int, int]:
    return int(value["depth"]), int(value["ix"]), int(value["iy"])


def cell_ref(value: tuple[int, int, int]) -> dict[str, int]:
    return {"depth": value[0], "ix": value[1], "iy": value[2]}


def children(cell: tuple[int, int, int]):
    d, ix, iy = cell
    for xb in (0, 1):
        for yb in (0, 1):
            yield d + 1, 2 * ix + xb, 2 * iy + yb


def area_fraction(cells: list[dict[str, int]]) -> Fraction:
    return sum((Fraction(4 ** (1 - int(c["depth"]))) for c in cells), Fraction(0))


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def histogram(cells: list[dict[str, int]]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(int(c["depth"]) for c in cells).items())}


def verify_manifest() -> None:
    manifest = json.loads((HERE / "MANIFEST.sha256.json").read_text())
    if manifest["packet_id"] != json.loads(SPEC.read_text())["packet_id"]:
        raise RuntimeError("MANIFEST_PACKET_MISMATCH")
    for item in manifest["sources"]:
        path = ROOT / item["path"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            raise RuntimeError("SOURCE_BINDING_MISMATCH:" + item["path"])
    expected_generated = {item["path"]: item for item in manifest["generated"]}
    actual_names = {"RESULTS.json", "PARTITION.json"} | {p.name for p in HERE.glob("CELLS.json.gz.part*")}
    if set(expected_generated) != actual_names:
        raise RuntimeError("GENERATED_FILE_SET_MISMATCH")
    for name, item in expected_generated.items():
        path = HERE / name
        if path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            raise RuntimeError("GENERATED_BINDING_MISMATCH:" + name)


def verify_partition_raster(accepted: list[dict], unresolved: list[dict], frontier: list[dict], max_depth: int) -> None:
    side = 1 << (max_depth - 1)
    raster = bytearray(side * side)
    for kind, cells in enumerate((accepted, unresolved, frontier), start=1):
        for ref in cells:
            d, ix, iy = cell_tuple(ref)
            if d < 1 or d > max_depth:
                raise RuntimeError("PARTITION_DEPTH_INVALID")
            scale = 1 << (max_depth - d)
            x0 = ix * scale - side
            y0 = iy * scale - side
            if x0 < 0 or y0 < 0 or x0 + scale > side or y0 + scale > side:
                raise RuntimeError("PARTITION_CELL_OUTSIDE_QUADRANT")
            for x in range(x0, x0 + scale):
                offset = x * side
                for y in range(y0, y0 + scale):
                    index = offset + y
                    if raster[index] != 0:
                        raise RuntimeError("PARTITION_OVERLAP")
                    raster[index] = kind
    if any(value == 0 for value in raster):
        raise RuntimeError("PARTITION_GAP")


def main() -> int:
    verify_manifest()
    spec = json.loads(SPEC.read_text())
    results = json.loads((HERE / "RESULTS.json").read_text())
    partition = json.loads((HERE / "PARTITION.json").read_text())
    parts = sorted(HERE.glob("CELLS.json.gz.part*"))
    if not parts or [p.name for p in parts] != [f"CELLS.json.gz.part{i:03d}" for i in range(len(parts))]:
        raise RuntimeError("PART_SET_INVALID")
    compressed = b"".join(p.read_bytes() for p in parts)
    payload = gzip.decompress(compressed)
    if len(payload) != results["records"]["uncompressed_bytes"] or hashlib.sha256(payload).hexdigest() != results["records"]["uncompressed_sha256"]:
        raise RuntimeError("RECORD_PAYLOAD_BINDING_MISMATCH")
    if results["records"]["parts"] != [
        {"path": p.name, "bytes": p.stat().st_size, "sha256": sha256(p)} for p in parts
    ]:
        raise RuntimeError("RECORD_PART_BINDING_MISMATCH")
    records = json.loads(payload)

    queue: deque[tuple[int, int, int]] = deque([tuple(spec["algorithm"]["root_cell"])])
    accepted: list[dict[str, int]] = []
    unresolved: list[dict[str, int]] = []
    primary_factors = recompute_factors = 0
    for sequence, record in enumerate(records):
        if not queue:
            raise RuntimeError("BFS_RECORD_AFTER_TERMINATION")
        expected = queue.popleft()
        actual = cell_tuple(record["cell"])
        if actual != expected or record["sequence"] != sequence or record["cutoff"] != "a":
            raise RuntimeError("BFS_ORDER_MISMATCH")
        d, ix, iy = actual
        den = 1 << d
        if ([Fraction(v) for v in record["cell"]["x"]] != [Fraction(ix, den), Fraction(ix + 1, den)] or
                [Fraction(v) for v in record["cell"]["y"]] != [Fraction(iy, den), Fraction(iy + 1, den)]):
            raise RuntimeError("EXACT_CELL_BOX_MISMATCH")
        if record["precision_bits"] != spec["precision_bits"] or record["primary"]["decimal_digits"] != 17:
            raise RuntimeError("PRECISION_MISMATCH")
        require_positive_interval(record["primary"]["gram_margin_min"], "PRIMARY_GRAM_INVALID")
        primary_ok, factors = verify_windows(record["primary"]["windows"], record["window_definitions"])
        primary_factors += factors
        if factors != 4 or record["primary"]["certified"] != primary_ok:
            raise RuntimeError("PRIMARY_STATUS_MISMATCH")
        recomputation = record["recomputation"]
        final_ok = False
        if primary_ok:
            if recomputation is None or not recomputation["uses_primary_recorded_shifts"]:
                raise RuntimeError("MISSING_RECOMPUTATION")
            if recomputation["decimal_digits"] != spec["recomputation_decimal_digits"]:
                raise RuntimeError("RECOMPUTATION_DIGITS_MISMATCH")
            require_positive_interval(recomputation["gram_margin_min"], "RECOMPUTATION_GRAM_INVALID")
            recompute_ok, factors = verify_windows(recomputation["windows"], record["window_definitions"])
            recompute_factors += factors
            if factors != 4 or recomputation["certified"] != recompute_ok:
                raise RuntimeError("RECOMPUTATION_STATUS_MISMATCH")
            final_ok = recompute_ok
        elif recomputation is not None:
            raise RuntimeError("UNNECESSARY_RECOMPUTATION")
        if (record["status"] == "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS") != final_ok:
            raise RuntimeError("FINAL_STATUS_MISMATCH")
        if final_ok:
            accepted.append(cell_ref(actual))
        elif d < spec["algorithm"]["max_depth"]:
            queue.extend(children(actual))
        else:
            unresolved.append(cell_ref(actual))

    frontier = [cell_ref(c) for c in queue]
    if partition["accepted_cells"] != accepted or partition["unresolved_max_depth_cells"] != unresolved or partition["unprocessed_frontier_cells"] != frontier:
        raise RuntimeError("TERMINAL_SET_MISMATCH")
    verify_partition_raster(accepted, unresolved, frontier, spec["algorithm"]["max_depth"])
    if not partition["complete_disjoint_partition"]:
        raise RuntimeError("PARTITION_FLAG_MISMATCH")

    af, uf, ff = map(area_fraction, (accepted, unresolved, frontier))
    if af + uf + ff != 1:
        raise RuntimeError("PARTITION_AREA_MISMATCH")
    expected_partition_summary = {
        "accepted_depth_histogram": histogram(accepted),
        "unresolved_depth_histogram": histogram(unresolved),
        "frontier_depth_histogram": histogram(frontier),
        "accepted_area_fraction_of_quadrant": fraction_text(af),
        "unresolved_area_fraction_of_quadrant": fraction_text(uf),
        "frontier_area_fraction_of_quadrant": fraction_text(ff),
    }
    for key, value in expected_partition_summary.items():
        if partition[key] != value:
            raise RuntimeError("PARTITION_SUMMARY_MISMATCH:" + key)

    expected_status = "CERTIFIED_CUTOFF_A_HARD_QUADRANT_COVERAGE" if not unresolved and not frontier else "INCONCLUSIVE_BOUNDED_COVERAGE"
    summary = {
        "attempted_cells": len(records),
        "accepted_cells": len(accepted),
        "unresolved_max_depth_cells": len(unresolved),
        "unprocessed_frontier_cells": len(frontier),
        "primary_factorizations": primary_factors,
        "recomputation_factorizations": recompute_factors,
        "total_factorizations": primary_factors + recompute_factors,
    }
    for key, value in summary.items():
        if results[key] != value:
            raise RuntimeError("RESULT_SUMMARY_MISMATCH:" + key)
    limits = spec["limits"]
    if (len(records) > limits["max_attempted_cells"] or primary_factors > limits["max_primary_factorizations"] or
            recompute_factors > limits["max_recomputation_factorizations"] or
            primary_factors + recompute_factors > limits["max_total_factorizations"]):
        raise RuntimeError("DETERMINISTIC_CAP_EXCEEDED")
    if (results["packet_id"] != spec["packet_id"] or results["status"] != expected_status or
            results["cutoff"] != "a" or results["domain"] != spec["domain"] or
            results["precision_bits"] != 128 or results["max_depth"] != 9 or
            results["limits"] != limits or results["claim_ceiling"] != spec["claim_ceiling"] or
            results["partition"]["sha256"] != sha256(HERE / "PARTITION.json")):
        raise RuntimeError("RESULT_BINDING_MISMATCH")
    if partition["stop_reason"] != results["stop_reason"]:
        raise RuntimeError("STOP_REASON_MISMATCH")
    print("PASS_RETAINED_S1B_CUTOFF_A_QUADRANT_PACKET")
    print(json.dumps({**summary, "status": expected_status,
                      "accepted_area_fraction": fraction_text(af)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
