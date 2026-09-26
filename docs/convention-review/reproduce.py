"""Small-matrix check: the two existing projected assemblies agree after Q -> -Q.

Tests, for the unchanged research/benchmarks/vafek_2025/model.py, that
U H_literal(K,Q) U^dag = H_direct(K,-Q) with U = tau_x (x) sigma_x, together
with the block identities used in the derivation, the exact c'' sign identity,
and the retained same-Q adjacent-gap discrepancy. Only 4x4 matrices are built.
No root search, transport, sweep or convention choice. Refuses to overwrite
an existing output file.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
import numpy as np

REPO = Path(__file__).resolve().parents[2]
MODEL = REPO / 'research/benchmarks/vafek_2025/model.py'
MODEL_SHA256 = '28af2f9c143252a8422e2993bda1f5fca937445636adf5456a059fda706ed0b3'
TOL = 1e-10  # meV, and dimensionless for block identities
POINTS = [((0.23, -0.17), 0.5), ((-0.11, 0.19), 0.8), ((0.37, 0.05), -0.3), ((0.0, 0.4), 1.1)]
PARAMETER_SETS = [{}, {'strain': 0.004}, {'cpp': 1000.0, 'M': -2.0}]
WITNESS = ((0.23, -0.17), 0.5)
RETAINED_WITNESS_GAP_DIFFERENCE = 1.5320713555991716  # PR #4 caa700b RESULTS.json

I2 = np.eye(2); X = np.array([[0, 1], [1, 0]]); Y = np.array([[0, -1j], [1j, 0]]); Z = np.diag([1, -1])
PAULI = {'I': I2, 'X': X, 'Y': Y, 'Z': Z}
U = np.kron(X, X)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blocks(k, Q):
    """C and F exactly as written inside model.h (restated for the block identities)."""
    x, y = k; xp, xm = x + Q/2, x - Q/2
    np_, nm = np.sqrt(1 + xp*xp + y*y), np.sqrt(1 + xm*xm + y*y)
    C = np.diag([1/np_, 1/np_, 1/nm, 1/nm])
    F = np.diag([-(xp + 1j*y)/np_, -(xp - 1j*y)/np_, (xm - 1j*y)/nm, (xm + 1j*y)/nm])
    return C, F


def valley_blocks(model, k, Q):
    x, y = k; z = np.zeros((2, 2))
    return np.block([[model.valley(x + Q/2, y), z], [z, model.valley(-(x - Q/2), -y).conj()]])


def mx(a):
    return float(np.max(np.abs(a)))


def main(output):
    if output.exists():
        raise FileExistsError('Refusing to replace retained output: ' + str(output))
    if sha(MODEL) != MODEL_SHA256:
        raise RuntimeError('model.py does not match the reviewed baseline')
    sys.path.insert(0, str(MODEL.parent))
    from model import Model
    ev = np.linalg.eigvalsh
    checks = {}
    m0 = Model()
    checks['U_unitary'] = mx(U @ U.conj().T - np.eye(4))
    checks['U_hc_Udag_minus_hc'] = mx(U @ m0.hc @ U.conj().T - m0.hc)
    checks['U_hf_Udag_minus_hf'] = mx(U @ m0.hf @ U.conj().T - m0.hf)
    block_rows, identity_rows, cpp_rows, spectral_rows = [], [], [], []
    for k, Q in POINTS:
        Cq, Fq = blocks(k, Q); Cm, Fm = blocks(k, -Q)
        block_rows.append({'K': list(k), 'Q': Q,
                           'U_C_Udag_minus_C_minusQ': mx(U @ Cq @ U.T - Cm),
                           'U_F_Udag_plus_F_minusQ': mx(U @ Fq @ U.T + Fm),
                           # Confirms the restated C, F are the ones inside model.h.
                           'restated_blocks_reproduce_model_h_cc_ff_terms': mx(
                               Cq @ m0.hc @ Cq + Fq.conj().T @ m0.hf @ Fq - (m0.h(k, Q) - valley_blocks(m0, k, Q)))})
    for params in PARAMETER_SETS:
        m = Model(params); mneg = Model(dict(params, cpp=-m.p['cpp']))
        for k, Q in POINTS:
            L, Dq, Dm = m.h(k, Q), m.direct_projection(k, Q), m.direct_projection(k, -Q)
            identity_rows.append({'parameters': params, 'K': list(k), 'Q': Q,
                                  'same_Q_matrix_difference_meV': mx(L - Dq),
                                  'U_Hlit_Udag_minus_Hdir_minusQ_meV': mx(U @ L @ U.conj().T - Dm)})
            cpp_rows.append({'parameters': params, 'K': list(k), 'Q': Q,
                             'Hlit_cpp_minus_Hdir_neg_cpp_meV': mx(L - mneg.direct_projection(k, Q))})
            if not params:
                x, y = k
                spectral_rows.append({'K': list(k), 'Q': Q,
                                      'spec_lit_KQ_vs_dir_K_minusQ_meV': mx(ev(L) - ev(Dm)),
                                      'spec_lit_KQ_vs_dir_minusK_minusQ_meV': mx(ev(L) - ev(m.direct_projection((-x, -y), -Q))),
                                      'spec_lit_KQ_vs_lit_K_minusQ_meV': mx(ev(L) - ev(m.h(k, -Q))),
                                      'max_adjacent_gap_difference_same_KQ_meV': mx(np.diff(ev(L)) - np.diff(ev(Dq)))})
    search = {'same_KQ': [], 'Q_reversed': []}
    for (a, A), (b, B) in itertools.product(PAULI.items(), repeat=2):
        V = np.kron(A, B)
        for conj in (False, True):
            def same(target_Q_sign):
                return all(mx(V @ (m0.h(k, Q).conj() if conj else m0.h(k, Q)) @ V.conj().T -
                              m0.direct_projection(k, target_Q_sign * Q)) <= TOL for k, Q in POINTS)
            label = a + b + (' with complex conjugation' if conj else '')
            if same(1): search['same_KQ'].append(label)
            if same(-1): search['Q_reversed'].append(label)
    witness = next(r for r in spectral_rows if r['K'] == list(WITNESS[0]) and r['Q'] == WITNESS[1])
    predicates = {
        'U_unitary_and_hc_hf_invariant': max(checks.values()) <= TOL,
        'block_identities': all(max(r['U_C_Udag_minus_C_minusQ'], r['U_F_Udag_plus_F_minusQ'],
                                    r['restated_blocks_reproduce_model_h_cc_ff_terms']) <= TOL for r in block_rows),
        'Q_reversed_unitary_identity': all(r['U_Hlit_Udag_minus_Hdir_minusQ_meV'] <= TOL for r in identity_rows),
        'same_Q_matrices_differ_off_axis': all(r['same_Q_matrix_difference_meV'] > 1e-3 for r in identity_rows if r['K'][1] != 0),
        'cpp_sign_identity': all(r['Hlit_cpp_minus_Hdir_neg_cpp_meV'] <= TOL for r in cpp_rows),
        'Q_reversal_not_a_symmetry_of_literal': all(r['spec_lit_KQ_vs_lit_K_minusQ_meV'] > 1e-3 for r in spectral_rows if r['Q'] != 0 and r['K'][1] != 0),
        'retained_same_Q_gap_witness_reproduced': abs(witness['max_adjacent_gap_difference_same_KQ_meV'] - RETAINED_WITNESS_GAP_DIFFERENCE) <= 1e-9,
        'no_same_KQ_pauli_product_equivalence': search['same_KQ'] == [],
        'tau_x_sigma_x_found_for_Q_reversal': 'XX' in search['Q_reversed'],
    }
    ok = all(predicates.values())
    result = {
        'status': 'Q_REVERSAL_EQUIVALENCE_REPRODUCED_CONVENTION_UNRESOLVED' if ok else 'CHECK_FAILED',
        'sources': {'research/benchmarks/vafek_2025/model.py': sha(MODEL), 'docs/convention-review/reproduce.py': sha(__file__)},
        'runtime': {'python': platform.python_version(), 'numpy': np.__version__},
        'tolerance': TOL, 'unitary': 'tau_x (x) sigma_x = kron(X, X)',
        'invariance_checks': checks, 'block_identities': block_rows, 'Q_reversal_identity': identity_rows,
        'cpp_sign_identity': cpp_rows, 'spectral_comparisons': spectral_rows, 'pauli_product_search': search,
        'predicates': predicates,
        'limitations': ['Implemented model only; the paper\'s signed boost/coordinate/coupling convention is not checked (primary source not reachable from the reviewing environment).',
                        'Both assemblies were authored within this project; not independent validation.',
                        'No root search, transport, braid, Euler-class or sweep; 4x4 matrices at fixed points only.'],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as handle:
        handle.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'failed': [k for k, v in predicates.items() if not v],
                      'max_Q_reversal_residual_meV': max(r['U_Hlit_Udag_minus_Hdir_minusQ_meV'] for r in identity_rows),
                      'witness_same_Q_gap_difference_meV': witness['max_adjacent_gap_difference_same_KQ_meV'],
                      'Q_reversed_pauli_matches': search['Q_reversed']}, indent=2))
    return 0 if ok else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    sys.exit(main(parser.parse_args().output.resolve()))
