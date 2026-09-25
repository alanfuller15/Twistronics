"""Lazy physical arithmetic for the frozen S1B-DIAGNOSTIC-001 protocol.

Importing this module performs no numerical imports or model evaluation.
Only the supervised worker may construct PhysicalEngine after the separate
implementation audit gate. The engine owns no loop, retry, budget or output.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE_CHECK = ROOT / "research/benchmarks/certification_s1b_001/check.py"
ASSEMBLY_CHECK = ROOT / "research/benchmarks/certification_s1a_hardening_001/check.py"


def canonical_sha256(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def rational_text(value) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("NUMERICAL_SOURCE_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def serialize_basis(vectors, dimension: int) -> list[list[str]]:
    """Freeze the specified .17g decimal rationals, not binary-float ratios."""
    if len(vectors) != dimension or any(len(row) != dimension for row in vectors):
        raise RuntimeError("BASIS_DIMENSION_MISMATCH")
    result = []
    for row in vectors:
        retained = []
        for item in row:
            value = float(item)
            if not math.isfinite(value):
                raise RuntimeError("NONFINITE_BASIS")
            retained.append(rational_text(Fraction(format(value, ".17g"))))
        result.append(retained)
    return result


def validate_basis(basis, dimension: int) -> list[list[str]]:
    if (not isinstance(basis, list) or len(basis) != dimension or
            any(not isinstance(row, list) or len(row) != dimension for row in basis)):
        raise RuntimeError("BASIS_DIMENSION_MISMATCH")
    normalized = []
    for row in basis:
        normalized_row = []
        for value in row:
            if not isinstance(value, str):
                raise RuntimeError("BASIS_REQUIRES_EXACT_RATIONAL_STRINGS")
            try:
                rational = rational_text(value)
            except (ValueError, ZeroDivisionError) as exc:
                raise RuntimeError("INVALID_BASIS_RATIONAL") from exc
            if rational != value:
                raise RuntimeError("BASIS_RATIONAL_NOT_CANONICAL")
            normalized_row.append(rational)
        normalized.append(normalized_row)
    return normalized


def matrix_evidence(matrix, base) -> list[list[list[str]]]:
    """Exact outward endpoints, never midpoint/float diagnostic hashes."""
    rows = []
    for i in range(matrix.nrows()):
        row = []
        for j in range(matrix.ncols()):
            value = matrix[i, j]
            if not value.is_finite():
                raise RuntimeError("NONFINITE_INTERVAL_MATRIX")
            row.append(base.endpoint(value))
        rows.append(row)
    return rows


def permute_matrix(matrix, permutation, arb_mat):
    n = matrix.nrows()
    if matrix.ncols() != n or sorted(permutation) != list(range(n)):
        raise RuntimeError("INVALID_MATRIX_PERMUTATION")
    return arb_mat([[matrix[i, j] for j in permutation] for i in permutation])


class PhysicalEngine:
    """Evaluate one explicitly supplied specimen/arm; never select more work."""

    def __init__(self, wheel: Path):
        import numpy as np
        from flint import arb, arb_mat, ctx
        import runtime_identity

        self.np, self.arb, self.arb_mat, self.ctx = np, arb, arb_mat, ctx
        self.base = load_module(BASE_CHECK, "diagnostic_reviewed_interval_ldl")
        self.assembly = load_module(ASSEMBLY_CHECK, "diagnostic_reviewed_assembly")
        self.spec = json.loads((HERE / "SPEC.json").read_text())
        self.inputs = json.loads((HERE / "INPUTS.json").read_text())
        self.case = json.loads((ROOT / self.spec["case_path"]).read_text())
        self.dimension = self.spec["dimension"]
        if (self.dimension != 196 or self.spec["cutoff"] != "a" or
                self.case["case_id"] != self.spec["case_id"] or
                self.case["cutoffs"]["a"]["dimension"] != self.dimension):
            raise RuntimeError("FROZEN_MODEL_IDENTITY_MISMATCH")
        self.specimens = {s["id"]: s for s in self.inputs["specimens"]}
        self.arms = {a["id"]: a for a in self.spec["arms_in_order"]}
        self.ctx.prec = 128
        self.ctx.threads = 1
        self.assembly.validate_case(self.case)
        self.runtime_provenance = runtime_identity.collect(Path(wheel))

    def _require_specimen(self, specimen):
        if (not isinstance(specimen, dict) or
                self.specimens.get(specimen.get("id")) != specimen):
            raise RuntimeError("SPECIMEN_NOT_FROZEN_INPUT")

    def _require_arm(self, arm):
        if not isinstance(arm, dict) or self.arms.get(arm.get("id")) != arm:
            raise RuntimeError("ARM_NOT_FROZEN_PROTOCOL")

    def _fresh_coefficients(self, precision):
        # Precision must be installed before every CASE-based operation. No
        # coefficient cache exists, including between primary/repeat stages.
        if type(precision) is not int or precision not in (128, 256):
            raise RuntimeError("UNSUPPORTED_ASSEMBLY_PRECISION")
        self.ctx.prec = precision
        self.ctx.threads = 1
        self.assembly.validate_case(self.case)
        cutoff = self.case["cutoffs"]["a"]
        coefficients, _ = self.assembly.assemble_coefficients(
            cutoff["ordered_indices"], self.case)
        if len(coefficients) != 3:
            raise RuntimeError("AFFINE_COEFFICIENT_COUNT_MISMATCH")
        for matrix in coefficients:
            if len(matrix) != self.dimension or any(len(r) != self.dimension for r in matrix):
                raise RuntimeError("AFFINE_COEFFICIENT_DIMENSION_MISMATCH")
            if any(not x.is_finite() for row in matrix for x in row):
                raise RuntimeError("NONFINITE_AFFINE_COEFFICIENT")
        return coefficients

    def make_basis(self, specimen: dict) -> list[list[str]]:
        self._require_specimen(specimen)
        coefficients = self._fresh_coefficients(128)
        x, y = map(Fraction, specimen["center"])
        center = self.base.matrix_from_coefficients(coefficients, x, y)
        midpoint = self.assembly.mid_float([
            [center[i, j] for j in range(self.dimension)]
            for i in range(self.dimension)])
        if not self.np.isfinite(midpoint).all():
            raise RuntimeError("NONFINITE_CENTER_MIDPOINT")
        # Exactly one eigensolver call. Counting/durable starts are the worker's
        # responsibility; failure propagates without a retry.
        eigenvalues, vectors = self.np.linalg.eigh(midpoint)
        if not self.np.isfinite(eigenvalues).all():
            raise RuntimeError("NONFINITE_CENTER_EIGENVALUES")
        return serialize_basis(vectors, self.dimension)

    def prepare(self, specimen: dict, arm: dict, basis: list[list[str]]) -> dict:
        self._require_specimen(specimen)
        self._require_arm(arm)
        retained_basis = validate_basis(basis, self.dimension)
        coefficients = self._fresh_coefficients(arm["precision_bits"])
        V = self.arb_mat([[self.base.exact_arb(Fraction(value)) for value in row]
                          for row in retained_basis])
        VT = V.transpose()
        gram = VT * V
        gram_endpoints = matrix_evidence(gram, self.base)
        gram_margins = []
        for i in range(self.dimension):
            off = sum((abs(gram[i, j]) for j in range(self.dimension) if i != j),
                      self.arb(0))
            margin = gram[i, i] - off
            if not margin.is_finite():
                raise RuntimeError("NONFINITE_GRAM_MARGIN")
            gram_margins.append(self.base.endpoint(margin))
        gram_certified = all(Fraction(pair[0]) > 0 for pair in gram_margins)
        x, y = map(Fraction, specimen["center"])
        radius = Fraction(specimen["original_half_width"]) * Fraction(arm["radius_multiplier"])
        if radius < 0:
            raise RuntimeError("NEGATIVE_BOX_RADIUS")
        delta = self.base.exact_arb(-radius).union(self.base.exact_arb(radius))
        center = self.base.matrix_from_coefficients(coefficients, x, y)
        boxed = (VT * center * V + delta * (VT * self.arb_mat(coefficients[1]) * V) +
                 delta * (VT * self.arb_mat(coefficients[2]) * V))
        shifts = [specimen["windows"][name][endpoint]
                  for name in ("lower", "upper") for endpoint in ("left", "right")]
        matrices = [boxed - self.base.exact_arb(Fraction(shift)) * gram for shift in shifts]
        unpermuted_k = [canonical_sha256(matrix_evidence(K, self.base)) for K in matrices]
        unpermuted_gram = canonical_sha256(gram_endpoints)
        permutation = list(range(self.dimension))
        if arm["column_order"] == "reverse_195_to_0":
            permutation.reverse()
        elif arm["column_order"] != "identity":
            raise RuntimeError("UNSUPPORTED_COLUMN_ORDER")
        # Always form canonical products in the original column order first.
        # Reversal only indexes already formed intervals, preserving endpoints.
        if arm["column_order"] != "identity":
            matrices = [permute_matrix(K, permutation, self.arb_mat) for K in matrices]
            gram = permute_matrix(gram, permutation, self.arb_mat)
            gram_margins = [gram_margins[i] for i in permutation]
        evidence = {
            "assembly_precision_bits": self.ctx.prec,
            "basis_roundtrip_sha256": canonical_sha256(retained_basis),
            "gram_margins": gram_margins,
            "unpermuted_gram_sha256": unpermuted_gram,
            "gram_matrix_sha256": canonical_sha256(matrix_evidence(gram, self.base)),
            "unpermuted_K_sha256": unpermuted_k,
            "K_sha256": [canonical_sha256(matrix_evidence(K, self.base)) for K in matrices],
            "permutation": permutation,
        }
        return {"evidence": evidence, "matrices": matrices, "gram_certified": gram_certified,
                "precision_bits": arm["precision_bits"], "shifts": shifts}

    def factor(self, prepared: dict, index: int) -> dict:
        if type(index) is not int or index not in range(4):
            raise RuntimeError("INVALID_ENDPOINT_INDEX")
        if not prepared["gram_certified"]:
            raise RuntimeError("FACTOR_WITH_UNCERTIFIED_GRAM")
        self.ctx.prec = prepared["precision_bits"]
        self.ctx.threads = 1
        result = self.base.interval_ldl(prepared["matrices"][index])
        # The reviewed routine emits exact rational pivot endpoints; all must
        # remain finite and ordered before the record can be retained.
        for low, high in result["pivots"]:
            if Fraction(low) > Fraction(high):
                raise RuntimeError("INVALID_RETAINED_PIVOT")
        return result
