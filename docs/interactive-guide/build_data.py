"""Export pinned, retained observations for reader education; never run an engine.

Requires Python standard library and a git checkout containing the two source
commits. Fetch the exact mapping commit explicitly if it is not present.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAPPING = "3f174f19b3ed5d57598accd1d7b1550fc7c9eeff"
NODES = "4c43a663d9212ffaaa5e6bad9b5a9d831bf31b62"
bindings = []


def retained(commit, path, expected=None):
    raw = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{commit}:{path}"])
    digest = hashlib.sha256(raw).hexdigest()
    if expected and digest != expected:
        raise ValueError(f"Retained source hash mismatch: {path}")
    bindings.append({"commit": commit, "path": path, "sha256": digest})
    return json.loads(raw)


summary = retained(MAPPING, "research/benchmarks/momentum_mapping_summary_001/OUTPUT/SUMMARY.json")
coverage_results = retained(MAPPING, "research/benchmarks/certification_s1b_quadrant_a_002/RUN/RESULTS.json")
partition = retained(MAPPING, "research/benchmarks/certification_s1b_quadrant_a_002/RUN/PARTITION.json",
                     coverage_results["partition"]["sha256"])
if (partition["accepted_area_fraction_of_quadrant"] != "29663/65536"
        or len(partition["accepted_cells"]) != 590
        or coverage_results["status"] != "INCONCLUSIVE_WATCHDOG_TIMEOUT"):
    raise ValueError("Unexpected retained quadrant coverage")
points = []
for batch, label in [("001", "Coarse 001"), ("002", "Refined 002")]:
    records = retained(MAPPING, f"research/benchmarks/momentum_mapping_scout_{batch}/RUN/RESULTS.json",
                       summary["batches"][label]["input_files"]["RESULTS.json"]["sha256"])
    if len(records["points"]) != 64 or records["status"] != "EXPLORATORY_COMPLETE":
        raise ValueError("Unexpected retained point count or status")
    for row in records["points"]:
        p, d = row["point"], row["diagnostic"]
        x, y = map(Fraction, p["center"])
        if [x, y] != [Fraction(2*p["cell"][a]+1, 2**(p["cell"]["depth"]+1)) for a in ("ix", "iy")]:
            raise ValueError("Center/cell disagreement")
        points.append({"batch": batch, "index": p["index"], "cell": p["cell"],
                       "center": p["center"], "x": float(x), "y": float(y),
                       "u": float(512*x-351), "v": float(512*y-368),
                       "upper": float(Fraction(d["local_gap_estimates_meV"]["upper"])),
                       "upper_exact": d["local_gap_estimates_meV"]["upper"],
                       "lower": float(Fraction(d["local_gap_estimates_meV"]["lower"])),
                       "energies": d["band_energies_meV"]})
    minimum = min(p["upper"] for p in points if p["batch"] == batch)
    if minimum != float(Fraction(summary["batches"][label]["statistics"]["gaps"]["upper"]["minimum_meV"])):
        raise ValueError("Summary minimum disagreement")

manifest = retained(NODES, "docs/visual-guide/sources.json")
engines = {}
for engine in ("bm_lab", "ref_lab"):
    path = f"research/v062/results/second_{engine}_N8.json"
    records = retained(NODES, path, manifest["inputs"][path])
    if len(records["states"]) != 11:
        raise ValueError("Unexpected continuation length")
    engines[engine] = []
    for s in records["states"]:
        if s["label"] != "OPPOSITE" or not all(n["success"] for n in s["nodes"].values()):
            raise ValueError("Unexpected node outcome")
        engines[engine].append({"ratio": s["ratio"], "label": s["label"],
                                "nodes": {k:n["f"] for k,n in s["nodes"].items()}})

data = {"snapshot": "2026-09-25 UTC", "mapping_commit": MAPPING, "nodes_commit": NODES,
        "points": points, "engines": engines, "sources": bindings,
        "coverage": {"numerator": 29663, "denominator": 65536,
                     "scope": "Historical normalized S1b quadrant-area fraction; unchanged by point mapping."}}
payload = "window.TWISTRONICS_DATA = " + json.dumps(data, separators=(",", ":"), allow_nan=False) + ";\n"
(HERE / "data.js").write_text(payload)
(HERE / "sources.json").write_text(json.dumps({"inputs": bindings, "data_js_sha256": hashlib.sha256(payload.encode()).hexdigest()}, indent=2)+"\n")
print("Exported 128 retained point spectra and 22 retained six-node states; checked source hashes and summary minima. No research engine executed.")
