#!/usr/bin/env python3
"""Verify retained S1b interval-inertia evidence without rerunning physics."""
from __future__ import annotations

import hashlib
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "RUN")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise SystemExit("FAIL: " + message)


def fraction(text: str):
    from fractions import Fraction
    return Fraction(text)


def signed_pivots(record: dict, expected_count=None) -> int:
    require(record["status"] == "CERTIFIED", "uncertified inertia record")
    negative = 0
    for lower, upper in record["pivots"]:
        lo, hi = fraction(lower), fraction(upper)
        require(hi < 0 or lo > 0, "zero-containing pivot")
        negative += hi < 0
    require(negative == record["negative"], "recorded inertia count")
    if expected_count is not None:
        require(negative == expected_count, "expected inertia count")
    return len(record["pivots"])


def load_cutoff(key: str):
    parts = sorted(RUN.glob(f"{key}_cells.json.gz.part*"))
    require(parts, "missing cutoff parts " + key)
    payload = b"".join(part.read_bytes() for part in parts)
    return json.loads(gzip.decompress(payload))


manifest = json.loads((RUN / "MANIFEST.json").read_text())
for name, digest in manifest.items():
    require((RUN / name).is_file(), "missing manifest file " + name)
    require(sha(RUN / name) == digest, "manifest hash " + name)

sources = json.loads((RUN / "SOURCE_BINDINGS.json").read_text())
for name, digest in sources.items():
    if name.startswith("external-wheel://"):
        lock = json.loads((ROOT / "research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json").read_text())
        require(name == "external-wheel://" + lock["filename"], "wheel URI")
        require(digest == lock["sha256"], "wheel digest")
    else:
        require((ROOT / name).is_file(), "missing bound source " + name)
        require(sha(ROOT / name) == digest, "bound source hash " + name)

spec = json.loads((HERE / "SPEC.json").read_text())
case = json.loads((ROOT / spec["case_path"]).read_text())
results = json.loads((RUN / "RESULTS.json").read_text())
environment = json.loads((RUN / "ENVIRONMENT.json").read_text())
require(results["spec_id"] == spec["spec_id"], "spec binding")
require(results["case_id"] == case["case_id"], "case binding")
require(results["parent_reviewed_commit"] == spec["parent_reviewed_commit"], "parent binding")
require(results["global_counters"]["inertia_factorizations"] <= spec["limits"]["max_inertia_factorizations_total"], "global factor cap")
require(results["global_counters"]["physical_cases"] == 1, "physical case count")
require(results["global_counters"]["parameter_sweeps"] == 0, "sweep count")

provenance = environment["runtime_provenance"]
require(provenance["proc_maps_checked"] is True, "proc maps gate")
require(provenance["loaded_extension_bound_to_wheel"] is True, "loaded extension binding")
require(provenance["mapped_native_library_count"] >= 3, "mapped native library count")
require(provenance["mapped_native_libraries_bound_to_wheel"] is True, "mapped native bindings")
require(provenance["installed_native_member_count"] >= 3, "native member count")

total_pivots = 0
cutoff_statuses = []
for key in spec["cutoff_order"]:
    parts = sorted(RUN.glob(f"{key}_cells.json.gz.part*"))
    if not parts:
        require(results["cutoffs"][key]["status"] == "INCONCLUSIVE", "missing cutoff status")
        continue
    record = load_cutoff(key)
    cutoff_statuses.append(record["status"])
    require(record["cutoff"] == key, "cutoff key")
    require(record["dimension"] == case["cutoffs"][key]["dimension"], "dimension")
    require(record["selected_bands_zero_based"] == case["cutoffs"][key]["selected_bands_zero_based"], "band pair")
    require(record["counters"]["attempted_cells"] <= spec["subdivision"]["max_attempted_cells_per_cutoff"], "cell cap")
    require(record["counters"]["factorizations"] <= spec["limits"]["max_inertia_factorizations_per_cutoff"], "factor cap")
    require(record["counters"]["max_depth_attempted"] <= spec["subdivision"]["max_depth"], "depth cap")
    require(len(record["cell_attempts"]) == record["counters"]["attempted_cells"], "attempt retention")
    certified_factorizations = 0
    for attempt in record["cell_attempts"]:
        require(attempt["precisions"], "precision attempt retention")
        for trial in attempt["precisions"]:
            for window in trial.get("windows", {}).values():
                for side in ("left", "right"):
                    inertia = window[side]
                    if inertia.get("status") == "CERTIFIED":
                        total_pivots += signed_pivots(inertia)
                        certified_factorizations += 1
    require(certified_factorizations == record["counters"]["factorizations"], "factorization retention")
    target = fraction(spec["target_external_gap_lower_meV"])
    coverage = [[False] * 256 for _ in range(256)]
    partition = [[False] * 256 for _ in range(256)]

    def mark(grid, c, message):
        scale = 1 << (8 - c["depth"])
        for i in range(c["ix"] * scale, (c["ix"] + 1) * scale):
            for j in range(c["iy"] * scale, (c["iy"] + 1) * scale):
                require(not grid[i][j], message)
                grid[i][j] = True

    for cell in record["accepted_cells"]:
        require(cell["status"] == "CERTIFIED", "accepted cell status")
        for window in cell["windows"].values():
            expected = window["expected_count"]
            total_pivots += signed_pivots(window["left"], expected)
            total_pivots += signed_pivots(window["right"], expected)
            require(window["count_certified"] is True, "count flag")
            require(window["target_met"] is True, "target flag")
            require(fraction(window["cell_gap_lower_meV"][0]) >= target, "cell margin")
        c = cell["cell"]
        mark(coverage, c, "overlapping accepted interiors")
        mark(partition, c, "overlapping partition cells")
    for unresolved in record["unresolved"]:
        cells = unresolved.get("frontier", [])
        if unresolved.get("cell"):
            cells.append(unresolved["cell"])
        for c in cells:
            mark(partition, c, "overlapping partition cells")
    complete = all(all(row) for row in coverage)
    require(all(all(row) for row in partition), "accepted/unresolved partition coverage")
    require((record["status"] == "CERTIFIED_UNIFORM_EXTERNAL_ISOLATION") == complete,
            "coverage/status equivalence")
    if not complete:
        require(record["status"] == "INCONCLUSIVE" and record["unresolved"], "inconclusive evidence")

if all(s == "CERTIFIED_UNIFORM_EXTERNAL_ISOLATION" for s in cutoff_statuses) and len(cutoff_statuses) == 2:
    require(results["status"] == "CERTIFIED_UNIFORM_EXTERNAL_ISOLATION", "global certified status")
else:
    require(results["status"] == "INCONCLUSIVE", "global inconclusive status")
require("NO_PROJECTOR_TRANSPORT_SEAM_OR_TOPOLOGY" in results["claim_ceiling"], "claim ceiling")
print(json.dumps({"status": "PASS_RETAINED_S1B_INTERVAL_INERTIA_EVIDENCE",
                  "result_status": results["status"], "files": len(manifest),
                  "signed_pivots_checked": total_pivots,
                  "runtime_native_members": provenance["installed_native_member_count"]}, sort_keys=True))
