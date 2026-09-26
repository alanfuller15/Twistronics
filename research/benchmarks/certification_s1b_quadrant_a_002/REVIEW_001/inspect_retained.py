#!/usr/bin/env python3
"""Extract exact diagnostics from the fixed, previously reviewed packet.

Standard library only. No model, eigensolver, interval arithmetic backend,
factorization, or search is called. The input hashes select one historical
packet; this is a diagnostic extractor, not a replacement for verify.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path

SOURCE_COMMIT = "fd98e033d479c69709d7e434d0b527115c6a9ecd"
INPUTS = {
    "ATTEMPTS.ndjson": (196613136, "328b42afbdb508b631fbccbaf13afbdf5197824ab97822a7c5a4aa755b674679"),
    "PARTITION.json": (64698, "23f2cb6797a36839d78dcbd86a46dfe55d1580ef1fb9e775d493ea3d45bac63d"),
    "RESULTS.json": (18411, "04979988d505bb1a454fa803b11de94901797738a3dac3ef16eea833d8232fc1"),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def check_bytes(name, count, digest):
    require((count, digest) == INPUTS[name], "INPUT_IDENTITY_MISMATCH:" + name)


def read_json(folder, name):
    data = (folder / name).read_bytes()
    check_bytes(name, len(data), hashlib.sha256(data).hexdigest())
    return json.loads(data)


def cell_key(cell):
    return tuple(cell[k] for k in ("depth", "ix", "iy"))


def interval(pair):
    lo, hi = map(F, pair)
    require(lo <= hi, "REVERSED_INTERVAL")
    return lo, hi


def zero_distance(pair):
    lo, hi = interval(pair)
    return lo if lo > 0 else -hi if hi < 0 else F(0)


def range_text(values):
    return {"min": str(min(values)), "max": str(max(values))}


def extract(folder):
    partition = read_json(folder, "PARTITION.json")
    results = read_json(folder, "RESULTS.json")
    unresolved = {cell_key(c) for c in partition["unresolved_max_depth_cells"]}
    rows, seen = [], set()
    depths = defaultdict(Counter)
    signatures = Counter()
    groups = defaultdict(lambda: defaultdict(list))
    accepted_d9_widths = defaultdict(list)
    endpoint_status = Counter()
    factor_counts = Counter()
    raw_hash, raw_bytes = hashlib.sha256(), 0
    previous = None
    with (folder / "ATTEMPTS.ndjson").open("rb") as stream:
        for sequence, line in enumerate(stream, start=-1):
            raw_hash.update(line)
            raw_bytes += len(line)
            r = json.loads(line)
            require(r["sequence"] == sequence, "SEQUENCE_MISMATCH")
            if sequence >= 0:
                require(r["previous_record_sha256"] == previous, "CHAIN_MISMATCH")
            canonical = json.dumps({k: v for k, v in r.items() if k != "record_sha256"},
                                   sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                                   allow_nan=False).encode()
            require(hashlib.sha256(canonical).hexdigest() == r["record_sha256"], "RECORD_HASH")
            previous = hashlib.sha256(line.rstrip(b"\n")).hexdigest()
            if sequence == -1:
                require(r["kind"] == "header" and r["test_mode"] is False, "HEADER")
                continue
            cell = r["cell"]
            key = cell_key(cell)
            require(key not in seen, "DUPLICATE_CELL")
            seen.add(key)
            e = r["full_interval_evidence"]
            p = e["primary"]
            require(cell_key(e["cell"]) == key, "CELL_MISMATCH")
            require(e["dimension"] == 196 and e["precision_bits"] == 128, "CASE_MISMATCH")
            accepted = r["outcome"] == "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS"
            depths[str(cell["depth"])]["attempted"] += 1
            depths[str(cell["depth"])]["accepted" if accepted else "inconclusive"] += 1
            for kind in ("primary", "recomputation"):
                factor_counts[kind] += r[kind + "_factorizations"]
                if e.get(kind):
                    endpoint_status[kind + "_certified_records"] += int(e[kind]["certified"])
            widths = {name: F(w["width_meV"]) for name, w in e["window_definitions"].items()}
            if accepted and cell["depth"] == 9:
                for name, width in widths.items():
                    accepted_d9_widths[name].append(width)
            if key not in unresolved:
                continue
            require(cell["depth"] == 9 and not p["certified"] and not accepted,
                    "UNRESOLVED_STATUS_MISMATCH")
            require(r["recomputation_factorizations"] == 0 and not e.get("recomputation"),
                    "UNEXPECTED_RECOMPUTATION")
            gram = interval(p["gram_margin_min"])
            require(gram[0] > 0, "GRAM_NOT_POSITIVE")
            failures = []
            for name, w in p["windows"].items():
                require(widths[name] >= F(w["target_lower_meV"]), "WINDOW_BELOW_TARGET")
                for ep in w["endpoints"]:
                    if ep["status"] == "CERTIFIED":
                        continue
                    index = ep["pivot_index"]
                    pivots = ep["pivots"]
                    require(len(pivots) == index + 1, "FAILURE_NOT_TERMINAL")
                    lo, hi = interval(pivots[index])
                    require(lo <= 0 <= hi, "FAILURE_PIVOT_EXCLUDES_ZERO")
                    signed = [zero_distance(v) for v in pivots[:index]]
                    require(all(v > 0 for v in signed), "EARLIER_AMBIGUOUS_PIVOT")
                    failures.append({
                        "endpoint": name + "." + ep["label"],
                        "shift": ep["shift"], "pivot_index_zero_based": index,
                        "zero_containing_pivot": pivots[index],
                        "pivot_interval_width": str(hi - lo),
                        "minimum_preceding_pivot_distance_from_zero": str(min(signed)) if signed else None,
                    })
            require(failures, "MISSING_FAILURE")
            signature = "+".join(sorted(f["endpoint"] for f in failures))
            signatures[signature] += 1
            group = "+".join(sorted({f["endpoint"].split(".")[0] for f in failures}))
            for name, value in widths.items():
                groups[group][name + "_window_width_meV"].append(value)
            groups[group]["gram_margin_lower"].append(gram[0])
            rows.append({"cell": cell, "sequence": sequence, "record_sha256": r["record_sha256"],
                         "gram_margin_min": p["gram_margin_min"],
                         "proposed_window_width_meV": {n: str(v) for n, v in widths.items()},
                         "failed_endpoints": failures})
    check_bytes("ATTEMPTS.ndjson", raw_bytes, raw_hash.hexdigest())
    require({cell_key(row["cell"]) for row in rows} == unresolved, "UNRESOLVED_MEMBERSHIP")
    require(len(rows) == 40 and len(seen) == 714, "COUNT_MISMATCH")
    return {
        "schema_version": 1, "analysis_id": "S1B-QUADRANT-A-002-REVIEW-001",
        "source_commit": SOURCE_COMMIT,
        "inputs": {name: {"bytes": size, "sha256": digest} for name, (size, digest) in INPUTS.items()},
        "method": "Exact rational inspection of retained records only; zero new factorizations or coverage attempts.",
        "terminal_status": results["status"],
        "retained_factorizations": dict(factor_counts),
        "retained_certified_record_counts": dict(endpoint_status),
        "attempt_outcomes_by_depth": {d: {k: depths[d][k] for k in ("attempted", "accepted", "inconclusive")}
                                      for d in sorted(depths)},
        "unresolved_failed_endpoint_signatures": dict(sorted(signatures.items())),
        "unresolved_ranges_by_failed_window": {g: {n: range_text(v) for n, v in sorted(values.items())}
                                               for g, values in sorted(groups.items())},
        "accepted_depth9_proposed_window_width_ranges_meV": {n: range_text(v) for n, v in sorted(accepted_d9_widths.items())},
        "unresolved_cells": rows,
        "limitations": [
            "This extracts diagnostics from the fixed reviewed artifact; it does not independently reconstruct interval-LDL enclosures.",
            "Proposed windows and pivot magnitudes are not certified physical gap measurements.",
            "Zero-containing pivots do not prove gap closure or the success or necessity of a finer depth.",
            "Depth summaries are priority-selected conditional samples, not same-cell convergence or future yield estimates.",
            "Coverage, partition, protocol, runtime provenance, and certification claim ceiling are unchanged.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="Previously materialized exact packet directory")
    parser.add_argument("--check", type=Path, help="Check a retained JSON report byte-for-byte; otherwise write JSON to stdout")
    args = parser.parse_args()
    output = (json.dumps(extract(args.packet), indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    if args.check:
        require(args.check.read_bytes() == output, "REPORT_MISMATCH")
        print("PASS_RETAINED_DIAGNOSTICS")
    else:
        sys.stdout.buffer.write(output)


if __name__ == "__main__":
    main()
