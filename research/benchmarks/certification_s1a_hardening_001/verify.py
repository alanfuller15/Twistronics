#!/usr/bin/env python3
"""Independent retained-evidence verifier for the bounded S1a hardening packet."""
from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise SystemExit("VERIFY_REFUSED: " + message)


here = Path(__file__).resolve()
packet = here.parent
remote_root = here.parents[3] if len(here.parents) > 3 else here.parents[1]
root = remote_root if (remote_root / "docs/certification-readiness/CASE.json").exists() else here.parents[1]
run = Path(sys.argv[1] if len(sys.argv) > 1 else packet / "RUN")
manifest = json.loads((run / "MANIFEST.json").read_text())
require(set(manifest) == {"ENVIRONMENT.json", "RESULTS.json", "SOURCE_BINDINGS.json"}, "manifest key set")
for name, digest in manifest.items():
    require(sha256(run / name) == digest, "manifest digest " + name)

bindings = json.loads((run / "SOURCE_BINDINGS.json").read_text())
closure = {"bm_strain.py", "knobs.py", "braid.py", "euler.py", "gate.py", "fast_engine.py", "tbg_ref.py"}
required = {
    "docs/certification-readiness/CASE.json",
    "research/benchmarks/migration_contract_review/partner_v078p.zip",
    *{"research/benchmarks/migration_contract_review/partner_v078p.zip!partner_v074p.zip!" + n for n in closure},
    "research/benchmarks/certification_s1a_hardening_001/check.py",
    "research/benchmarks/certification_s1a_hardening_001/verify.py",
    "research/benchmarks/certification_s1a_hardening_001/README.md",
    "research/benchmarks/certification_s1a_hardening_001/WHEEL_LOCK.json",
    "external-wheel://python_flint-0.9.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl",
}
require(set(bindings) == required, "source binding set")


def bound_bytes(rel):
    if rel.startswith("external-wheel://"):
        lock = json.loads((packet / "WHEEL_LOCK.json").read_text())
        require(rel == "external-wheel://" + lock["filename"], "wheel URI")
        require(bindings[rel] == lock["sha256"], "wheel detached digest")
        return None
    if rel == "docs/certification-readiness/CASE.json" and not (root / rel).exists():
        return (root / "CASE.json").read_bytes()
    if rel == "research/benchmarks/migration_contract_review/partner_v078p.zip" and not (root / rel).exists():
        return (root / "partner_v078p.zip").read_bytes()
    if rel.startswith("research/benchmarks/certification_s1a_hardening_001/"):
        return (packet / rel.rsplit("/", 1)[1]).read_bytes()
    if "!" not in rel:
        return (root / rel).read_bytes()
    outer_rel, nested_name, member = rel.split("!")
    outer = (root / outer_rel) if (root / outer_rel).exists() else root / "partner_v078p.zip"
    with zipfile.ZipFile(outer) as z:
        nested = z.read(nested_name)
    with zipfile.ZipFile(io.BytesIO(nested)) as z:
        return z.read(member)


for rel, digest in bindings.items():
    data = bound_bytes(rel)
    if data is not None:
        require(hashlib.sha256(data).hexdigest() == digest, "source binding " + rel)

r = json.loads((run / "RESULTS.json").read_text())
env = json.loads((run / "ENVIRONMENT.json").read_text())
lock = json.loads((packet / "WHEEL_LOCK.json").read_text())
require(r["schema"] == "twistronics_s1a_hardening_v1", "schema")
require(r["status"] == "PASS_PHYSICAL_AFFINE_ASSEMBLY_BRIDGE", "status")
require(r["claim_ceiling"] == "PHYSICAL_AFFINE_ASSEMBLY_ONLY_NO_UNIFORM_ISOLATION_OR_TOPOLOGY", "claim ceiling")
require(all(r["checks"].values()), "all declared checks")
require(r["runtime_binding"] == lock, "result runtime binding")
require(env["python_flint_wheel"] == lock, "environment wheel binding")
require(env["python_flint"] == lock["python_flint_version"], "python-flint version")
require(env["native_flint"] == lock["native_flint_version"], "native FLINT version")
binding = r["case_binding"]
require(binding["constants"] == {"HBARV_meV_angstrom": "5944", "A_LAT_angstrom": "2.46"}, "case constants")
require(binding["B"] == "-0.25", "harmonic amplitude")
require(binding["harmonic"] == {"mat": "sz", "use_sin": True, "layer_sign": 1, "which": [0, 1, 2]}, "harmonic semantics")
require(binding["archived_helper"] == "knobs.add_harmonic", "archived helper")
require(len(binding["guard_mutation_controls"]) == 10 and all(binding["guard_mutation_controls"].values()), "refusal controls")
require(r["nested_identity"]["nonoverlap_count"] == 0, "nested identity")
require(r["nested_identity"]["worst_difference_abs_upper_meV"] < 1e-25, "nested identity width")
for key, dim in (("a", 196), ("b", 308)):
    rec = r["cutoffs"][key]
    require(rec["dimension"] == dim, "dimension " + key)
    require(rec["whole_domain_arithmetic_radius_upper_meV"] <= 1e-8, "assembly radius " + key)
    require(len(rec["coefficient_ball_sha256"]) == 64, "coefficient digest " + key)
    require([x["point"] for x in rec["diagnostic_bridge"]] == [[0, 0], [1, 0], [0, 1]], "bridge points " + key)
    for point in rec["diagnostic_bridge"]:
        require(point["max_abs_midpoint_difference_meV"] <= 1e-9, "float bridge " + key)
        require(point["archived_imaginary_residual_meV"] <= 1e-9, "real residual " + key)
        require(point["diagnostic_lower_external_gap_meV"] >= 0, "diagnostic lower ordering " + key)
        require(point["diagnostic_upper_external_gap_meV"] >= 0, "diagnostic upper ordering " + key)
require(any("No interval inertia" in x for x in r["limits"]), "uniform-isolation limitation")
require(any("No projector" in x for x in r["limits"]), "topology limitation")
print("PASS_RETAINED_S1A_HARDENING_EVIDENCE")
