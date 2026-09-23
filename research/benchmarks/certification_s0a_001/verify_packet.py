#!/usr/bin/env python3
"""Verify retained hashes, exact dyadic signs and fixed acceptance predicates.

Standard library only. This does not rerun numerics or validate the proofs.
"""
import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(p):
    return json.loads(p.read_text())


def endpoint(x):
    return Fraction(int(x["mantissa"]))*Fraction(2)**x["exponent"]


def bounds(x):
    lo, hi = endpoint(x["lower"]), endpoint(x["upper"])
    if lo > hi:
        raise AssertionError("reversed endpoints")
    return lo, hi


def main():
    packet = read(HERE/"PACKET_MANIFEST.json")
    for row in packet["files"]+packet["unchanged_prior_packet"]:
        data = (ROOT/row["path"]).read_bytes()
        assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"], row["path"]
    run = read(HERE/"RUN/MANIFEST.json")
    for row in run["files"]:
        data = (HERE/row["path"]).read_bytes()
        assert len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"], row["path"]
    spec = read(HERE/"SPEC.json")
    result = read(HERE/"RUN/RESULTS.json")
    assert result["status"] == "PASS" and result["passed_jobs"] == result["completed_jobs"] == len(spec["jobs"]) == 10
    assert result["physical_evaluations"] == 0 and result["wall_seconds"] < spec["limits"]["global_wall_seconds"]
    checked_pivots = 0
    for job in spec["jobs"]:
        r = read(HERE/"RUN"/(job["id"]+".json"))
        assert r["job"] == job and r["status"] == "PASS" and r["physical_evaluations"] == 0
        assert r["wall_seconds"] < spec["limits"]["job_wall_seconds"]
        if job["kind"] == "inertia":
            signs = []
            for p in r["pivots"]:
                lo, hi = bounds(p)
                assert hi < 0 or lo > 0
                signs.append(hi < 0)
            assert len(signs) == job["dimension"] and sum(signs) == r["negative"] == r["expected_negative"]
            assert bounds(r["Gram_defect_F_bound"])[1] < 1
            assert bounds(r["sigma_min_V_lower_bound"])[0] > 0
            checked_pivots += len(signs)
        elif job["kind"] == "transport":
            b = r["bounds"]
            assert bounds(b["bound"])[1] < Fraction(job["acceptance_error"])
            assert bounds(b["reference_discrepancy_bound"])[1] < bounds(b["bound"])[0]
            assert bounds(b["uncertain_rate_total_bound"])[0] > Fraction(job["acceptance_error"])
        else:
            assert r["checks_passed"] == len(r["checks"]) == 7 and all(c["pass"] for c in r["checks"])
    print(json.dumps({"status": "PASS_RETAINED_INTEGRITY_AND_PREDICATES_ONLY",
                      "packet_files": len(packet["files"]), "unchanged_prior_files": len(packet["unchanged_prior_packet"]),
                      "run_hash_bindings": len(run["files"]), "signed_pivots_checked": checked_pivots,
                      "synthetic_jobs": 10, "physical_evaluations": 0}, indent=2))


if __name__ == "__main__":
    main()
