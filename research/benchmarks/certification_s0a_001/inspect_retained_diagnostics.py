#!/usr/bin/env python3
"""Read retained floating diagnostics; never import or execute archived code."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT/"research/benchmarks/migration_contract_review/partner_v078p.zip"
EXPECTED = "d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e"
raw = ARCHIVE.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != EXPECTED:
    raise ValueError("archive hash mismatch")
with zipfile.ZipFile(ARCHIVE) as z:
    data = z.read("RUN/DIAGNOSTICS.jsonl")
rows = [json.loads(line) for line in data.splitlines() if line.strip()]
selected = [r for r in rows if r.get("kind") == "frame"
            and str(r.get("case", "")).startswith("B-0.25_v+1_") and r.get("lo") == 97]
print(json.dumps({
    "schema": "retained_diagnostic_inspection_v1", "date": "2026-09-23",
    "archive": str(ARCHIVE.relative_to(ROOT)), "archive_sha256": sha,
    "member": "RUN/DIAGNOSTICS.jsonl", "member_sha256": hashlib.sha256(data).hexdigest(),
    "filter": {"kind": "frame", "case_prefix": "B-0.25_v+1_", "lo": 97},
    "rows": len(selected), "unique_coordinates": len({tuple(r["f"]) for r in selected}),
    "cases": sorted({r["case"] for r in selected}),
    "upper_external_gap_meV": {"min": min(r["upper_external_gap_meV"] for r in selected),
                               "max": max(r["upper_external_gap_meV"] for r in selected)},
    "physical_evaluations": 0,
    "limitations": "Retained floating loop diagnostics only; not a rectangle cover, center-gap certificate or interval bound."
}, indent=2, sort_keys=True))
