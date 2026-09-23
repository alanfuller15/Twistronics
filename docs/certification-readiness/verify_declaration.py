#!/usr/bin/env python3
"""Read-only declaration verifier. No archived imports or model evaluation.
Run from any directory; stdout is the reproducible declaration receipt.
This checks integrity and exact finite-set/rational declarations, not theorems.
"""
import ast
import hashlib
import io
import json
import sys
import zipfile
from decimal import Decimal
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/certification-readiness"
checks = {}

def check(name, condition):
    checks[name] = bool(condition)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def canonical(value):
    return digest(json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode())

def read_json(path):
    return json.loads(path.read_text())

def binding(path):
    data = (ROOT / path).read_bytes()
    return {"path": path, "sha256": digest(data), "bytes": len(data)}

def spans(source):
    result = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result[node.name] = (node.lineno, node.end_lineno)
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result[node.name + "." + child.name] = (child.lineno, child.end_lineno)
    return result

def main():
    case = read_json(DOC / "CASE.json")
    plan = read_json(DOC / "PLAN.json")
    sources = read_json(DOC / "SOURCE_BINDINGS.json")
    contract = read_json(ROOT / "research/benchmarks/migration_contract_review/CONTRACT_EXPECTATIONS.json")
    archive = (ROOT / sources["archive"]["path"]).read_bytes()
    check("archive_binding", digest(archive) == sources["archive"]["sha256"]
          == contract["archive_sha256"] == case["basis_of_declaration"]["archive_sha256"]
          and len(archive) == sources["archive"]["bytes"])
    for row in sources["files"]:
        check("file:" + row["path"], binding(row["path"]) == row)
    with zipfile.ZipFile(io.BytesIO(archive)) as outer:
        nested_data = outer.read("partner_v074p.zip")
        with zipfile.ZipFile(io.BytesIO(nested_data)) as nested:
            for row in sources["archive_members"]:
                container = nested if "!" in row["container"] else outer
                data = container.read(row["member"])
                check("member:" + row["member"],
                      digest(data) == row["sha256"] and len(data) == row["bytes"])
                if "inspected_definitions" in row:
                    located = spans(data.decode())
                    check("spans:" + row["member"], all(
                        located.get(s["name"]) == (s["first_line"], s["last_line"])
                        for s in row["inspected_definitions"]))
            check("contract_outer_sources", all(
                digest(outer.read(name)) == sha
                for name, sha in contract["source_sha256"].items()))
        basis = json.loads(outer.read("RUN/BASIS.json"))
        models = json.loads(outer.read("RUN/MODELS.json"), parse_float=Decimal)
    retained = models["discovery_B-0.25"]
    a, b = case["cutoffs"]["a"], case["cutoffs"]["b"]
    aa, bb = list(map(tuple, a["ordered_indices"])), list(map(tuple, b["ordered_indices"]))
    stencil = list(map(tuple, b["stencil"]))
    check("retained_order", a["ordered_indices"] == basis["ordered_indices"])
    expected_b = sorted({(x + dx, y + dy) for x, y in aa for dx, dy in stencil})
    check("exact_neighbor_shell", bb == expected_b)
    check("basis_counts_nesting", len(aa) == len(set(aa)) == a["vectors"] == 49
          and len(bb) == len(set(bb)) == b["vectors"] == 77 and set(aa) <= set(bb))
    check("dimensions_and_pairs", (a["dimension"], b["dimension"]) == (196, 308)
          and a["selected_bands_zero_based"] == [97, 98]
          and b["selected_bands_zero_based"] == [153, 154])
    pos = [bb.index(index) for index in aa]
    mapping = [2 * len(bb) * layer + 2 * pos[i] + s
               for layer in range(2) for i in range(len(aa)) for s in range(2)]
    check("embedding_and_isometry", pos == case["inclusion"]["index_position_map"]
          and mapping == case["inclusion"]["column_to_row"]
          and len(set(mapping)) == 196 and min(mapping) >= 0 and max(mapping) < 308)
    check("canonical_array_hashes",
          canonical(a["ordered_indices"]) == a["ordered_indices_sha256"]
          and canonical(b["ordered_indices"]) == b["ordered_indices_sha256"]
          and canonical(mapping) == case["inclusion"]["column_to_row_sha256"])
    fixed = case["orientation"]["fixed_pivot"]
    check("fixed_pivot_coordinates", aa[fixed["index_position"]] == (0, 0)
          and fixed["layer"] == 0 and fixed["real_coordinates"] ==
          [2 * aa.index((0, 0)), 2 * aa.index((0, 0)) + 1]
          and F(fixed["gram_determinant_lower"]) == F(1, 10**12))
    defaults_match = set(case["model"]["constructor"]) == set(retained["defaults"])
    for key, value in retained["defaults"].items():
        declared = case["model"]["constructor"][key]
        defaults_match &= declared == value if isinstance(value, str) else F(str(declared)) == F(str(value))
    check("retained_constructor_literals", defaults_match)
    check("retained_harmonic_and_case", case["model"]["valley"] == retained["valley"] == 1
          and F(case["model"]["B"]) == F(str(retained["B"])) == F(-1, 4)
          and all(case["model"]["harmonic"][k] == retained["harmonic"][k]
                  for k in ["mat", "use_sin", "layer_sign"])
          and case["model"]["harmonic"]["which"] == [0, 1, 2])
    check("source_to_target_shifts", case["seams"]["d1"] == [-1, 0] and case["seams"]["d2"] == [0, -1])
    ranks = {name: [sum((x + dx, y + dy) in set(indices) for x, y in indices)
                   for dx, dy in [(-1, 0), (0, -1)]]
             for name, indices in [("a", aa), ("b", bb)]}
    check("partial_shift_ranks", ranks == {"a": [42, 40], "b": [68, 66]})
    chi = list(map(F, case["repair"]["chi_coefficients_ascending"]))
    endpoint_jets = []
    for _ in range(3):
        endpoint_jets.append([chi[0], sum(chi)])
        chi = [i * chi[i] for i in range(1, len(chi))]
    check("repair_endpoint_jets", endpoint_jets == [[0, 1], [0, 0], [0, 0]])
    t = case["targets"]
    check("rational_thresholds", F(t["seam_restricted_singular_value_min"]) == F(19, 20)
          and 1 - F(t["seam_restricted_singular_value_min"])**2 == F(39, 400)
          and F(case["identification"]["uniform_restricted_singular_value_min"]) == F(1, 2)
          and F(t["external_gap_lower_meV"]) == F(1, 10**5)
          and F(t["hamiltonian_assembly_error_meV"]) == F(1, 10**8)
          and F(t["final_q_interval_max_half_width"]) == F(1, 8))
    check("case_plan_and_budget_binding", case["case_id"] == plan["case_id"]
          and case["arithmetic"]["backend"] == plan["backend"]["package"] + "==" + plan["backend"]["version"]
          and sum(s["wall_seconds"] for s in plan["stages"]) == plan["global_limits"]["wall_seconds"] == 2220
          and plan["backend"]["precision_bits"] == [128, 256, 512])
    check("unexecuted_and_dependency_lock_open", case["status"] == "DECLARED_UNEXECUTED"
          and all(v["status"] == "NOT_RUN" for v in case["current_outcomes"].values())
          and plan["execution_status"] == "NOT_RUN"
          and plan["implementation_status"] == "NOT_IMPLEMENTED"
          and plan["backend"]["native_flint_version"] is None
          and not plan["stages"][0]["physical_model_evaluation"])
    documents = [binding("docs/certification-readiness/" + name) for name in
                 ["README.md", "CASE.md", "CASE.json", "IMPLEMENTATION_PLAN.md", "PLAN.json",
                  "verify_declaration.py", "SOURCE_BINDINGS.json"]]
    passed = all(checks.values())
    receipt = {
        "schema": "twistronics_static_declaration_checks_v2", "date": "2026-09-23",
        "case_id": case["case_id"], "plan_id": plan["plan_id"],
        "outcome": "PASS_STATIC_INTEGRITY_AND_FINITE_SET_CHECKS_ONLY" if passed else "FAIL",
        "method": "Read-only Python standard-library verifier; no archived imports or numerical model execution.",
        "documents": documents, "checks": checks,
        "counts": {"retained_indices": len(aa), "comparison_indices": len(bb),
                   "dimensions": [a["dimension"], b["dimension"]], "inclusion_columns": len(mapping),
                   "shift_index_ranks": ranks, "archive_members_bound": len(sources["archive_members"])},
        "execution": {"archived_modules_imported": False, "hamiltonian_assemblies": 0,
                      "eigensolver_runs": 0, "parameter_sweeps": 0, "physical_case_outcome": None},
        "limitations": ["Integrity checks do not validate the proposed numerical methods or prove their hypotheses.",
                       "Independent revision/design review and a locked, audited implementation remain required."]
    }
    print(json.dumps(receipt, indent=2))
    return 0 if passed else 1

if __name__ == "__main__":
    sys.exit(main())
