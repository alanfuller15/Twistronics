"""Direct evaluation of arXiv-v2 Eq73/B28 against the retained projection.

The printed formula does not call the projection or negate a derived scalar.
The projection helpers are shared with the earlier, hash-checked audit: this
is a separate transcription, not independent scientific validation.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "source_audit"
REPO = HERE.parents[3]
TOL = 1e-10
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
FROZEN = {
    OLD / "reproduce.py": "429b8a26af9c1f45af2c0ff5e19ff08ea2281ac76fb22d0848b89a2cf7ea9aa4",
    OLD / "SOURCE_RECEIPT.json": "25af2d9b90bb58ade14d7a9322bada9aae5c5e98a9b89bd32c26a62fb75b98af",
    OLD / "RESULTS.json": "6cf7380081f1ea33fc81afab95910691aa3902139566973c6b3b075573f33b41",
    REPO / "research/benchmarks/vafek_2025/model.py": "28af2f9c143252a8422e2993bda1f5fca937445636adf5456a059fda706ed0b3",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def printed_eq73(k, p):
    """Fresh physical-unit transcription of the RHS, including both diagonals.

    Source: SOURCE_EXTRACTS.json, A2.E73 (PDF B28).
    No derived projection, dimensionless Model.valley, or computed sign input.
    """
    kx, ky = k
    v, gamma, cpp, mf, mass = (p[n] for n in
                              ("v_meV_A", "gamma", "cpp", "Mf", "M"))
    eps = -(1 + p["poisson"]) * p["strain"] / 2
    denominator = v**2 * (kx**2 + ky**2) + gamma**2
    strain_matrix = np.array([
        [2*gamma*cpp*v*ky, -1j*mf*v**2*(kx-1j*ky)**2],
        [1j*mf*v**2*(kx+1j*ky)**2, 2*gamma*cpp*v*ky],
    ], dtype=complex)
    return eps/denominator * strain_matrix + gamma**2*mass/denominator * X


def mx(a):
    return float(np.max(np.abs(a)))


def traceless(a):
    return a - np.trace(a)/2 * I


def pack(a):
    return {"real": a.real.tolist(), "imag": a.imag.tolist()}


def trace_difference(a, b):
    delta = np.trace(a-b)
    if not np.isfinite(delta) or abs(delta.imag) > TOL:
        raise ValueError("Trace difference is not finite and real")
    return float(delta.real)


def main(output):
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    for path, expected in FROZEN.items():
        if digest(path) != expected:
            raise ValueError(f"Frozen input differs: {path}")
    receipt = json.loads((OLD / "SOURCE_RECEIPT.json").read_text())
    extracts = json.loads((HERE / "SOURCE_EXTRACTS.json").read_text())
    if extracts["source_sha256"] != receipt["resources"][0]["sha256"]:
        raise ValueError("HTML resource hashes differ")
    hashes = {r["html_anchor"]: r["html_math_alttext_joined_sha256"]
              for r in receipt["equation_crosswalk"]}
    if [r["html_anchor"] for r in extracts["equations"]] != [
            "A1.E35", "A2.E71", "A2.E72", "A2.E73"]:
        raise ValueError("Unexpected equation inventory")
    for row in extracts["equations"]:
        raw = ("\n".join(row["math_alttext"]) + "\n").encode()
        actual = hashlib.sha256(raw).hexdigest()
        if actual != row["sha256_newline_joined"] or actual != hashes[row["html_anchor"]]:
            raise ValueError("Equation excerpt differs from frozen receipt")

    audit = load(OLD / "reproduce.py", "frozen_source_audit")
    model = load(REPO / "research/benchmarks/vafek_2025/model.py", "frozen_model")
    retained = json.loads((OLD / "RESULTS.json").read_text())
    old_rows = {r["id"]: r for r in retained["cases"]}
    predicates, rows = {}, []

    for name, K, Q, overrides in audit.CASES:
        p = dict(audit.PARAMETERS, **overrides)
        k = np.asarray(K) * p["gamma"] / p["v_meV_A"]
        u = audit.source_columns(k, p)
        phase = audit.source_to_code_phase(k, p)
        _, perturbation, cf = audit.physical_blocks(k, p)
        raw = u.conj().T @ perturbation @ u
        rephased = phase @ raw @ phase.conj().T
        printed = printed_eq73(k, p)
        um = audit.code_gauge_columns(-k, p)
        _, hm, _ = audit.physical_blocks(-k, p)
        other_valley = (um.conj().T @ hm @ um).conj()
        trace_delta = trace_difference(printed, raw)
        old_trace = old_rows[name]["single_valley_cf_trace_difference_printed_minus_projected_meV"]
        residuals = {
            "printed_matrix_hermitian": mx(printed-printed.conj().T),
            "printed_equals_existing_literal": mx(printed-model.Model(overrides).valley(*K)),
            "traceless_agrees_after_phase_conversion": mx(traceless(printed)-traceless(rephased)),
            "printed_scalar_plus_projected_cf_scalar_zero": abs(float(np.trace(printed).real/2)
                + float(np.trace(u.conj().T @ cf @ u).real/2)),
            "trace_witness_matches_retained_value": abs(trace_delta-old_trace),
            "valley_exchange_and_column_swap": mx(printed-X@other_valley@X),
        }
        for label, value in residuals.items():
            predicates[f"{name}:{label}"] = bool(np.isfinite(value) and value <= TOL)
        rows.append({"id": name, "K_dimensionless": K, "physical_k_A_inverse": k.tolist(),
                     "overrides": overrides, "printed_eq73": pack(printed),
                     "raw_projection_using_printed_columns": pack(raw),
                     "projection_after_explicit_phase_conversion": pack(rephased),
                     "trace_printed_minus_raw_meV": trace_delta,
                     "raw_traceless_difference_meV": mx(traceless(printed)-traceless(raw)),
                     "residuals_meV": residuals})

    # Focused falsification controls at the existing witness; not source choices.
    p = dict(audit.PARAMETERS)
    k = np.array([.23, -.17]) * p["gamma"] / p["v_meV_A"]
    u = audit.source_columns(k, p)
    phase = audit.source_to_code_phase(k, p)
    _, dh, cf = audit.physical_blocks(k, p)
    printed = printed_eq73(k, p)
    direct = phase @ (u.conj().T @ dh @ u) @ phase.conj().T
    diagonal_flipped = printed.copy()
    diagonal_flipped[0, 0] *= -1
    diagonal_flipped[1, 1] *= -1
    adjoint_block = phase @ (u.conj().T @ (dh-2*cf) @ u) @ phase.conj().T
    expected_trace = old_rows["retained_witness"]["single_valley_cf_trace_difference_printed_minus_projected_meV"]
    def witness_accepts(a, b):
        return bool(abs(trace_difference(a, b)-expected_trace) <= TOL)
    controls = {
        "unmodified_trace_gate_accepts": witness_accepts(printed, direct),
        "printed_diagonal_flip_rejected": not witness_accepts(diagonal_flipped, direct),
        "upper_block_adjoint_rejected": not witness_accepts(printed, adjoint_block),
        "printed_diagonal_flip_eliminates_difference": mx(diagonal_flipped-direct) <= TOL,
        "upper_block_adjoint_eliminates_difference": mx(printed-adjoint_block) <= TOL,
    }
    predicates.update({f"control:{key}": bool(value) for key, value in controls.items()})
    good = all(predicates.values())
    result = {
        "status": "DIRECT_TRANSCRIPTION_CHECKED_CONVENTION_UNRESOLVED" if good else "CHECK_FAILED",
        "runtime": {"python": platform.python_version(), "numpy": np.__version__},
        "tolerance_meV": TOL,
        "sources": {str(path.relative_to(REPO)): digest(path) for path in
                    [*FROZEN, HERE/"reproduce.py", HERE/"SOURCE_EXTRACTS.json"]},
        "predicates": predicates, "cases": rows, "controls": controls,
        "control_trace_differences_meV": {
            "printed_diagonal_flipped": trace_difference(diagonal_flipped, direct),
            "upper_block_replaced_by_adjoint": trace_difference(printed, adjoint_block)},
        "limitations": ["The printed formula has a separate code path, but the same author transcribed it.",
                        "Projection helpers are shared with the earlier audit.",
                        "Supplied source excerpts do not prove independent retrieval or author intent.",
                        "Raw column phases differ; phase conversion is explicit, not attributed to the paper.",
                        "Later journal equations remain unchecked; no production convention selected.",
                        "Fixed matrix diagnostics only; no new topology or experimental result."]}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write("\n")
    print(json.dumps({"status": result["status"], "predicates": len(predicates),
                      "failed": [key for key, value in predicates.items() if not value],
                      "max_residual_meV": max(v for row in rows for v in row["residuals_meV"].values()),
                      "witness_trace_difference_meV": rows[0]["trace_printed_minus_raw_meV"],
                      "witness_raw_traceless_difference_meV": rows[0]["raw_traceless_difference_meV"],
                      "controls": controls}, indent=2))
    return 0 if good else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    sys.exit(main(parser.parse_args().output.resolve()))
