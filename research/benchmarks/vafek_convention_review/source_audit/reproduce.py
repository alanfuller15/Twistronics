"""Fixed-point, gauge-aware audit of arXiv:2502.08700v2 conventions.

Transcribes the physical-unit six-component Hamiltonian and printed flat-band
columns, then compares their projection with the two unchanged project models.
No roots, parameter sweep, transport, or selected production convention.
The formulas are a human transcription, not an automated source validation.
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
REPO = HERE.parents[3]
MODEL = REPO / "research/benchmarks/vafek_2025/model.py"
MODEL_SHA = "28af2f9c143252a8422e2993bda1f5fca937445636adf5456a059fda706ed0b3"
TOL = 1e-10
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1., -1.]).astype(complex)

# Declared rounded benchmark, including Table 1's signed v and gamma.
PARAMETERS = dict(gamma=-24.8, v_meV_A=-4300., M=3.7, Mf=4380.,
                  strain=.0015, poisson=.16, U1=58., U2=2.3, W3=50.2,
                  J=16.4, cpp=-3362.)
CASES = [
    ("retained_witness", [.23, -.17], .5, {}),
    ("retained_opposite_y", [-.11, .19], .8, {}),
    ("retained_axis", [.2, 0.], .5, {}),
    ("retained_gamma", [0., 0.], .5, {}),
    ("retained_zero_cpp", [.23, -.17], .5, {"cpp": 0.}),
    ("retained_zero_strain", [.23, -.17], .5, {"strain": 0.}),
    # Artificial control, not a second choice of the paper's parameters.
    ("artificial_positive_gamma", [.23, -.17], .5, {"gamma": 24.8}),
]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mx(a):
    return float(np.max(np.abs(a)))


def pack(a):
    a = np.asarray(a)
    return {"real": a.real.tolist(), "imag": a.imag.tolist()}


def blockdiag(*matrices):
    nr, nc = sum(a.shape[0] for a in matrices), sum(a.shape[1] for a in matrices)
    out = np.zeros((nr, nc), complex)
    r = c = 0
    for a in matrices:
        out[r:r+a.shape[0], c:c+a.shape[1]] = a
        r += a.shape[0]
        c += a.shape[1]
    return out


def physical_blocks(k, p):
    """HTML 26/35 = PDF A1/A10; retain only M, Mf, c'' perturbations."""
    kx, ky = k
    v, g = p["v_meV_A"], p["gamma"]
    e = -(1 + p["poisson"]) * p["strain"] / 2
    h0 = np.zeros((6, 6), complex)
    h0[:2, 2:4] = v * (kx * I + 1j * ky * Z)
    h0[2:4, :2] = h0[:2, 2:4].conj().T
    h0[:2, 4:] = g * I
    h0[4:, :2] = g * I
    perturbation = np.zeros_like(h0)
    perturbation[2:4, 2:4] = p["M"] * X
    perturbation[4:, 4:] = p["Mf"] * e * Y
    cf_only = np.zeros_like(h0)
    cf_only[2:4, 4:] = -1j * p["cpp"] * e * Z
    cf_only[4:, 2:4] = cf_only[2:4, 4:].conj().T
    return h0, perturbation + cf_only, cf_only


def source_columns(k, p):
    """HTML 70-72 = PDF B25-B27, including the printed angular phases."""
    r = float(np.linalg.norm(k))
    theta = float(np.arctan2(k[1], k[0])) if r else 0.
    v, g = p["v_meV_A"], p["gamma"]
    phases = np.exp(1j * theta * np.array([1, 2, 0, 3, 1, 2]))
    norm = np.sqrt(2 * (v*v*r*r + g*g))
    plus = phases * np.array([0, 0, g, g, -v*r, -v*r]) / norm
    minus = phases * np.array([0, 0, g, -g, -v*r, v*r]) / norm
    return np.column_stack([(plus + minus)/np.sqrt(2),
                            (plus - minus)/np.sqrt(2)])


def code_gauge_columns(k, p):
    x, y = np.array(k) * p["v_meV_A"] / p["gamma"]
    n = np.sqrt(1 + x*x + y*y)
    return np.vstack([np.zeros((2, 2)), I, -(x*I + 1j*y*Z)]) / n


def source_to_code_phase(k, p):
    theta = float(np.arctan2(k[1], k[0])) if np.linalg.norm(k) else 0.
    return np.sign(p["gamma"]) * np.diag([1., np.exp(3j*theta)])


def interactions(p):
    """HTML 57 and 74; Of is transposed to get P. One spin, nu_f=-2."""
    of = (np.eye(4) + np.kron(X, X) - np.kron(Y, Z) - np.kron(Z, Y))/4
    a = of.T - np.eye(4)/2
    tz, sz = np.kron(Z, I), np.kron(I, Z)
    hc = -2*p["W3"]*np.eye(4) - p["J"]*(tz@a@tz + sz@a@sz)/2
    hf = -p["U1"]*a - 2*(p["U1"] + 6*p["U2"])*np.eye(4)
    return of.T, hc, hf


def run_case(name, K, Q, overrides, Model):
    p = dict(PARAMETERS, **overrides)
    m = Model(overrides)
    e = -(1+p["poisson"])*p["strain"]/2
    scale = p["gamma"]/p["v_meV_A"]
    k = np.array(K)*scale
    q = np.array([Q*scale, 0.])
    h0, dh, cf = physical_blocks(k, p)
    u = source_columns(k, p)
    uc = code_gauge_columns(k, p)
    phase = source_to_code_phase(k, p)
    cf_projected = u.conj().T @ cf @ u
    N = p["gamma"]**2 + p["v_meV_A"]**2 * float(k@k)
    derived_scalar = -2*p["gamma"]*p["cpp"]*e*p["v_meV_A"]*k[1]/N
    printed_scalar = -derived_scalar
    one_rephased = phase @ (u.conj().T@dh@u) @ phase.conj().T
    literal_valley = m.valley(*K)
    expected_difference = 4*p["cpp"]*e*K[1]/(1+float(np.dot(K,K))) * I

    kp, minus_argument = k+q/2, -(k-q/2)
    hp0, hp1, _ = physical_blocks(kp, p)
    hm0, hm1, _ = physical_blocks(minus_argument, p)
    hp = blockdiag(hp0+hp1, (hm0+hm1).conj())
    up = blockdiag(source_columns(kp, p), source_columns(minus_argument, p).conj())
    # valley-major six-component blocks -> sector-major twelve components.
    perm = [0, 1, 6, 7, 2, 3, 8, 9, 4, 5, 10, 11]
    hp = hp[np.ix_(perm, perm)]
    up = up[perm, :]
    parent, hc, hf = interactions(p)
    hp[4:8, 4:8] += hc
    hp[8:, 8:] += hf
    d = blockdiag(source_to_code_phase(kp, p),
                  source_to_code_phase(minus_argument, p).conj())
    projected = d @ (up.conj().T@hp@up) @ d.conj().T
    direct = m.direct_projection(K, Q)
    literal = m.h(K, Q)
    ev = np.linalg.eigvalsh
    z = np.array([1, 1j, 1j, 1])/2
    checks = {
        "source_columns_orthonormal": mx(u.conj().T@u-I),
        "source_columns_kernel_meV": mx(h0@u),
        "source_columns_equal_code_columns_times_phase": mx(u-uc@phase),
        "cf_projection_equals_negative_scalar_meV": mx(cf_projected-derived_scalar*I),
        "literal_minus_rephased_projection_equals_formula_meV": mx(literal_valley-one_rephased-expected_difference),
        "parent_projector_from_source_equals_code": mx(parent-np.outer(z,z.conj())),
        "source_hc_equals_code_meV": mx(hc-m.hc),
        "source_hf_equals_code_meV": mx(hf-m.hf),
        "source_full_projection_equals_direct_meV": mx(projected-direct),
        "source_full_projection_hermitian_meV": mx(projected-projected.conj().T),
    }
    return {
        "id": name, "K": K, "Q": Q, "overrides": overrides,
        "physical_k_A_inverse": k.tolist(), "physical_q_A_inverse": q.tolist(),
        "single_valley_cf_scalar_from_projection_meV": float(np.trace(cf_projected).real/2),
        "single_valley_cf_scalar_from_printed_E73_meV": float(printed_scalar),
        "single_valley_cf_trace_difference_printed_minus_projected_meV": float(2*printed_scalar-np.trace(cf_projected).real),
        "checks": checks,
        "source_full_projection_in_code_gauge": pack(projected),
        "literal_spectrum_meV": ev(literal).tolist(),
        "source_projected_spectrum_meV": ev(projected).tolist(),
        "same_Q_gap_difference_meV": mx(np.diff(ev(literal))-np.diff(ev(projected))),
    }


def main(output):
    if output.exists():
        raise FileExistsError(f"Refusing to replace {output}")
    if digest(MODEL) != MODEL_SHA:
        raise RuntimeError("Model hash differs from reviewed source")
    spec = importlib.util.spec_from_file_location("reviewed_vafek_model", MODEL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.PARAMETERS != PARAMETERS:
        raise RuntimeError("Declared parameters differ from benchmark")
    rows = [run_case(*case, module.Model) for case in CASES]
    predicates = {f"{r['id']}:{k}": bool(np.isfinite(v) and v <= TOL)
                  for r in rows for k,v in r["checks"].items()}
    predicates["witness_gap_reproduced"] = abs(rows[0]["same_Q_gap_difference_meV"]-1.5320713555991716) <= 1e-9
    predicates["single_valley_trace_witness_nonzero"] = abs(rows[0]["single_valley_cf_trace_difference_printed_minus_projected_meV"]) > 1e-3
    for name in ["retained_axis", "retained_gamma", "retained_zero_cpp", "retained_zero_strain"]:
        row = next(r for r in rows if r["id"] == name)
        predicates[name+":zero_control"] = abs(row["single_valley_cf_trace_difference_printed_minus_projected_meV"]) <= TOL
    good = all(predicates.values())
    result = {
        "status": "SOURCE_SIGN_DISCREPANCY_REPRODUCED_CONVENTION_UNRESOLVED" if good else "CHECK_FAILED",
        "tolerance": TOL,
        "runtime": {"python": platform.python_version(), "numpy": np.__version__},
        "sources": {str(MODEL.relative_to(REPO)): digest(MODEL),
                    str(Path(__file__).resolve().relative_to(REPO)): digest(__file__),
                    str((HERE/'SOURCE_RECEIPT.json').relative_to(REPO)): digest(HERE/'SOURCE_RECEIPT.json')},
        "predicates": predicates, "cases": rows,
        "limitations": ["Human transcription of arXiv v2 only; later journal equations not checked.",
                        "Fixed small-matrix diagnostics; not an independent physical validation.",
                        "No selected convention, model repair, node search, transport, sweep or braid claim."],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write('\n')
    print(json.dumps({"status": result['status'], "predicates": len(predicates),
                      "failed": [k for k,v in predicates.items() if not v],
                      "max_check_residual": max(v for r in rows for v in r['checks'].values()),
                      "witness_gap_difference_meV": rows[0]['same_Q_gap_difference_meV'],
                      "witness_trace_difference_meV": rows[0]['single_valley_cf_trace_difference_printed_minus_projected_meV']}, indent=2))
    return 0 if good else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    sys.exit(main(parser.parse_args().output.resolve()))
