#!/usr/bin/env python3
"""Freeze diagnostic specimens using retained JSON only; no numerical model imports."""
import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

RAW_BYTES = 196613136
RAW_SHA256 = "328b42afbdb508b631fbccbaf13afbdf5197824ab97822a7c5a4aa755b674679"
SOURCE_COMMIT = "ad18d34ef0bf3b5d4ec7a4d2e27ba954f2fd0492"
RULES = [
    ("upper_left", "upper.left", "largest_failed_pivot_width"),
    ("upper_right", "upper.right", "smallest_proposed_upper_width"),
    ("upper_both", "upper.left+upper.right", "smallest_proposed_upper_width"),
    ("lower_left", "lower.left", "largest_failed_pivot_width"),
    ("lower_both", "lower.left+lower.right", "smallest_proposed_lower_width"),
    ("accepted_upper", "accepted", "smallest_proposed_upper_width"),
    ("accepted_lower", "accepted", "smallest_proposed_lower_width"),
]


def width(row, name):
    return F(row["windows"][name]["width_meV"])


def key(row):
    return tuple(row["cell"][n] for n in ("depth", "ix", "iy"))


def freeze(raw):
    groups = {}; accepted = {}; digest = hashlib.sha256(); size = 0
    for line in raw.open("rb"):
        digest.update(line); size += len(line)
        r = json.loads(line)
        if r["kind"] == "header":
            continue
        e = r["full_interval_evidence"]
        row = {"cell": r["cell"], "source_sequence": r["sequence"],
               "source_record_sha256": r["record_sha256"], "windows": e["window_definitions"]}
        d = row["cell"]["depth"]
        if r["outcome"] == "CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS":
            accepted.setdefault(d, []).append(row)
            if d == 9:
                groups.setdefault("accepted", []).append(row)
        elif d == 9:
            failures = []
            for name, w in e["primary"]["windows"].items():
                for ep in w["endpoints"]:
                    if ep["status"] != "CERTIFIED":
                        lo, hi = map(F, ep["pivots"][ep["pivot_index"]])
                        if not lo <= 0 <= hi:
                            raise ValueError("INVALID_FAILED_PIVOT")
                        failures.append((name + "." + ep["label"], hi - lo))
            signature = "+".join(sorted(name for name, _ in failures))
            row["max_failed_pivot_interval_width"] = str(max(w for _, w in failures))
            groups.setdefault(signature, []).append(row)
    if (size, digest.hexdigest()) != (RAW_BYTES, RAW_SHA256):
        raise ValueError("RAW_INPUT_IDENTITY_MISMATCH")
    specimens = []
    for identifier, signature, rule in RULES:
        candidates = groups[signature]
        if rule == "largest_failed_pivot_width":
            ranking = lambda r: (-F(r["max_failed_pivot_interval_width"]), key(r))
        else:
            window = "lower" if "lower" in rule else "upper"
            ranking = lambda r: (width(r, window), key(r))
        chosen = dict(min(candidates, key=ranking))
        chosen.update(id=identifier, historical_signature=signature, selection_rule=rule)
        d, ix, iy = key(chosen)
        chosen["center"] = [str(F(2 * ix + 1, 2 ** (d + 1))), str(F(2 * iy + 1, 2 ** (d + 1)))]
        chosen["original_half_width"] = str(F(1, 2 ** (d + 1)))
        specimens.append(chosen)
    if len({key(r) for r in specimens}) != 7:
        raise ValueError("SPECIMENS_NOT_DISTINCT")
    failed_upper = [r for s, rs in groups.items() if s.startswith("upper") for r in rs]
    failed_lower = [r for s, rs in groups.items() if s.startswith("lower") for r in rs]
    accepted_min = {n: min(width(r, n) for r in accepted[9]) for n in ("upper", "lower")}
    failed_upper_min = min(width(r, "upper") for r in failed_upper)
    failed_upper_max = max(width(r, "upper") for r in failed_upper)
    stats = {
        "upper_failures": len(failed_upper), "lower_failures": len(failed_lower),
        "upper_failures_below_accepted_depth9_minimum": sum(width(r, "upper") < accepted_min["upper"] for r in failed_upper),
        "lower_failures_below_accepted_depth9_minimum": sum(width(r, "lower") < accepted_min["lower"] for r in failed_lower),
        "accepted_depth9_upper_widths_inside_failed_range": [str(w) for w in sorted(width(r, "upper") for r in accepted[9] if failed_upper_min <= width(r, "upper") <= failed_upper_max)],
        "accepted_depth9_lower_minimum_meV": str(accepted_min["lower"]),
        "accepted_upper_minimum_by_depth": {str(d): {"width_meV": str(min(width(r, "upper") for r in rs)),
            "width_times_2_to_depth_meV": str(2 ** d * min(width(r, "upper") for r in rs))} for d, rs in sorted(accepted.items())},
        "historical_depth9_signatures": {k: len(v) for k, v in sorted(groups.items())},
    }
    return {"schema_version": 1, "packet_id": "S1B-DIAGNOSTIC-001", "source_commit": SOURCE_COMMIT,
            "raw_log_bytes": RAW_BYTES, "raw_log_sha256": RAW_SHA256,
            "selection_ties": "ascending (depth, ix, iy), exact rational comparison",
            "specimens": specimens, "retained_width_statistics": stats,
            "scope": "Retained-record selection and arithmetic only; no new physical or certification evidence."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_log", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    content = (json.dumps(freeze(args.raw_log), indent=2, sort_keys=True) + "\n").encode()
    if args.check:
        if args.check.read_bytes() != content:
            raise ValueError("FROZEN_INPUTS_MISMATCH")
        print("PASS_FROZEN_RETAINED_INPUTS")
    else:
        sys.stdout.buffer.write(content)
