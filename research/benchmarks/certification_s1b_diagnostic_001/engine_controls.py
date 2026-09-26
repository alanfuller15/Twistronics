"""Small synthetic/mocked controls; never load CASE or evaluate its model.

Controls exercise the reviewed interval backend on matrices of dimension 2/3.
PhysicalEngine is allocated without its constructor and receives mock affine
assembly and mock eigensolver objects. No physical basis, model or endpoint is
computed. Run as a script to emit a machine-readable control report.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import engine


def run() -> dict:
    results = {}
    results["engine_import_has_no_numeric_imports"] = (
        "numpy" not in sys.modules and "flint" not in sys.modules)
    import numpy as np
    from flint import arb, arb_mat, ctx

    base = engine.load_module(engine.BASE_CHECK, "synthetic_reviewed_interval_ldl")
    ctx.prec, ctx.threads = 128, 1

    def check(name, condition):
        results[name] = bool(condition)

    def rejects(name, operation, expected):
        try:
            operation()
        except RuntimeError as exc:
            check(name, str(exc) == expected)
        else:
            check(name, False)

    known = base.interval_ldl(arb_mat([[-3, 0, 0], [0, 2, 0], [0, 0, 4]]))
    check("known_signed_inertia", known == {
        "status": "CERTIFIED", "negative": 1,
        "pivots": [["-3", "-3"], ["2", "2"], ["4", "4"]]})
    zero = base.interval_ldl(arb_mat([[-2, 0], [0, arb(0, 1)]]))
    check("zero_containing_pivot_stops_with_partial_count",
          zero["status"] == "INCONCLUSIVE" and zero["pivot_index"] == 1 and
          zero["negative"] == 1 and len(zero["pivots"]) == 2 and
          Fraction(zero["pivots"][-1][0]) < 0 < Fraction(zero["pivots"][-1][1]))
    other = base.interval_ldl(arb_mat([[-2, 0], [0, -1]]))
    check("wrong_expected_count_remains_certified_other_inertia",
          other["status"] == "CERTIFIED" and other["negative"] == 2 and
          other["negative"] != 1 and len(other["pivots"]) == 2)
    matrix = arb_mat([[-2, 1], [1, 3]])
    reversed_matrix = engine.permute_matrix(matrix, [1, 0], arb_mat)
    reversed_result = base.interval_ldl(reversed_matrix)
    check("actual_synthetic_reversal_preserves_inertia",
          reversed_result["status"] == "CERTIFIED" and
          reversed_result["negative"] == base.interval_ldl(matrix)["negative"] == 1 and
          reversed_result["pivots"] != base.interval_ldl(matrix)["pivots"])
    rejects("invalid_permutation_rejected",
            lambda: engine.permute_matrix(matrix, [0, 0], arb_mat),
            "INVALID_MATRIX_PERMUTATION")
    rejects("nonfinite_interval_matrix_rejected",
            lambda: engine.matrix_evidence(arb_mat([[arb("nan")]]), base),
            "NONFINITE_INTERVAL_MATRIX")
    values = [[0.1, -0.3], [-0.0, 1e-15]]
    frozen = engine.serialize_basis(values, 2)
    expected = [["10000000000000001/100000000000000000",
                 "-29999999999999999/100000000000000000"],
                ["0", "10000000000000001/10000000000000000000000000000000"]]
    check("basis_serialization_uses_exact_17g_including_negatives", frozen == expected)
    reloaded = arb_mat([[base.exact_arb(Fraction(v)) for v in row] for row in frozen])
    check("basis_reload_encloses_exact_retained_rationals",
          all(Fraction(base.endpoint(reloaded[i, j])[0]) <= Fraction(frozen[i][j]) <=
              Fraction(base.endpoint(reloaded[i, j])[1])
              for i in range(2) for j in range(2)))
    check("basis_json_roundtrip_preserves_hash",
          engine.canonical_sha256(frozen) == engine.canonical_sha256(
              engine.validate_basis(json.loads(json.dumps(frozen)), 2)))
    rejects("nonfinite_float_basis_rejected",
            lambda: engine.serialize_basis([[math.inf]], 1), "NONFINITE_BASIS")
    rejects("float_input_to_retained_basis_rejected",
            lambda: engine.validate_basis([[1.0]], 1),
            "BASIS_REQUIRES_EXACT_RATIONAL_STRINGS")
    rejects("unreduced_basis_rational_rejected",
            lambda: engine.validate_basis([["2/4"]], 1),
            "BASIS_RATIONAL_NOT_CANONICAL")

    specimen = {
        "id": "synthetic", "center": ["1/4", "3/4"],
        "original_half_width": "1/8", "windows": {
            "lower": {"left": "-5", "right": "-4"},
            "upper": {"left": "5", "right": "6"}}}
    arms = [
        {"id": "original_128", "precision_bits": 128,
         "radius_multiplier": "1", "column_order": "identity"},
        {"id": "original_256", "precision_bits": 256,
         "radius_multiplier": "1", "column_order": "identity"},
        {"id": "original_reverse_128", "precision_bits": 128,
         "radius_multiplier": "1", "column_order": "reverse_195_to_0"},
        {"id": "point_128", "precision_bits": 128,
         "radius_multiplier": "0", "column_order": "identity"}]
    calls = {"validation_precisions": [], "assembly_precisions": [], "eigen": 0}

    def validate_case(case):
        if case["case_id"] != "SYNTHETIC_ONLY":
            raise RuntimeError("CONTROL_PHYSICAL_MODEL_FORBIDDEN")
        calls["validation_precisions"].append(ctx.prec)

    def assemble_coefficients(indices, case):
        if case["case_id"] != "SYNTHETIC_ONLY":
            raise RuntimeError("CONTROL_PHYSICAL_MODEL_FORBIDDEN")
        calls["assembly_precisions"].append(ctx.prec)
        return ([[arb(-3), arb(0)], [arb(0), arb(4)]],
                [[arb(0), arb(1) / 3], [arb(1) / 3, arb(0)]],
                [[arb(1) / 7, arb(0)], [arb(0), -arb(2) / 7]]), {}

    def eigensolver(midpoint):
        # A spy only: never invoke numpy.linalg.eigh in these controls.
        calls["eigen"] += 1
        if ctx.prec != 128 or midpoint.shape != (2, 2):
            raise RuntimeError("BASIS_GENERATOR_SETUP_MISMATCH")
        return np.array([-3.0, 4.0]), np.array([[0.8, -0.6], [0.6, 0.8]])

    instance = object.__new__(engine.PhysicalEngine)
    instance.np = SimpleNamespace(isfinite=np.isfinite,
                                  linalg=SimpleNamespace(eigh=eigensolver))
    instance.arb, instance.arb_mat, instance.ctx = arb, arb_mat, ctx
    instance.base = base
    instance.assembly = SimpleNamespace(
        validate_case=validate_case, assemble_coefficients=assemble_coefficients,
        mid_float=lambda matrix: np.array([[float(v.mid()) for v in row] for row in matrix]))
    instance.dimension = 2
    instance.case = {"case_id": "SYNTHETIC_ONLY", "cutoffs": {
        "a": {"ordered_indices": [[0, 0]], "dimension": 2}}}
    instance.specimens = {specimen["id"]: specimen}
    instance.arms = {arm["id"]: arm for arm in arms}
    ctx.prec = 53
    basis = instance.make_basis(specimen)
    check("mock_basis_generation_sets_precision_before_assembly",
          calls["validation_precisions"] == [128] and
          calls["assembly_precisions"] == [128] and calls["eigen"] == 1)
    original = instance.prepare(specimen, arms[0], basis)
    repeated = instance.prepare(specimen, arms[0], json.loads(json.dumps(basis)))
    high = instance.prepare(specimen, arms[1], basis)
    reverse = instance.prepare(specimen, arms[2], basis)
    point = instance.prepare(specimen, arms[3], basis)
    check("each_prepare_reassembles_at_requested_precision",
          calls["validation_precisions"] == [128, 128, 128, 256, 128, 128] and
          calls["assembly_precisions"] == [128, 128, 128, 256, 128, 128])
    check("arms_never_regenerate_basis", calls["eigen"] == 1)
    check("fresh_same_runtime_reconstruction_identical", original["evidence"] == repeated["evidence"])
    check("higher_precision_rebuilt_enclosures",
          high["evidence"]["assembly_precision_bits"] == 256 and
          high["evidence"]["unpermuted_K_sha256"] != original["evidence"]["unpermuted_K_sha256"])
    check("reverse_uses_formed_canonical_matrices",
          reverse["evidence"]["unpermuted_K_sha256"] == original["evidence"]["unpermuted_K_sha256"] and
          reverse["evidence"]["unpermuted_gram_sha256"] == original["evidence"]["unpermuted_gram_sha256"] and
          reverse["evidence"]["permutation"] == [1, 0] and
          all(base.endpoint(reverse["matrices"][k][i, j]) ==
              base.endpoint(original["matrices"][k][1-i, 1-j])
              for k in range(4) for i in range(2) for j in range(2)))
    check("point_arm_removes_box_variation",
          point["evidence"]["unpermuted_K_sha256"] != original["evidence"]["unpermuted_K_sha256"])
    check("all_arms_keep_same_exact_retained_basis",
          all(p["evidence"]["basis_roundtrip_sha256"] == engine.canonical_sha256(basis)
              for p in (original, repeated, high, reverse, point)))
    check("recorded_shifts_are_reused_unchanged", original["shifts"] == ["-5", "-4", "5", "6"])
    check("fresh_factor_repeat_uses_actual_reviewed_ldl",
          all(instance.factor(original, i) == instance.factor(repeated, i) for i in range(4)))
    singular = instance.prepare(specimen, arms[0], [["1", "1"], ["0", "0"]])
    check("uncertified_gram_is_retained_without_raise",
          not singular["gram_certified"] and
          any(Fraction(pair[0]) <= 0 for pair in singular["evidence"]["gram_margins"]))
    rejects("uncertified_gram_cannot_enter_factor",
            lambda: instance.factor(singular, 0), "FACTOR_WITH_UNCERTIFIED_GRAM")
    rejects("unfrozen_specimen_rejected",
            lambda: instance.make_basis({**specimen, "center": ["0", "0"]}),
            "SPECIMEN_NOT_FROZEN_INPUT")
    rejects("unfrozen_arm_rejected",
            lambda: instance.prepare(specimen, {**arms[0], "precision_bits": 64}, basis),
            "ARM_NOT_FROZEN_PROTOCOL")
    rejects("endpoint_index_out_of_range_rejected",
            lambda: instance.factor(original, 4), "INVALID_ENDPOINT_INDEX")
    return {
        "schema": "s1b_diagnostic_engine_controls_v1",
        "scope": "Synthetic 2x2/3x3 arithmetic and mock assembly/eigensolver only; no CASE evaluation",
        "controls": results, "passed": sum(results.values()), "total": len(results),
        "physical_model_evaluations": 0, "physical_eigensolver_calls": 0,
        "physical_endpoint_factorizations": 0,
        "status": "PASS" if all(results.values()) else "FAIL",
    }


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, sort_keys=True, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)
