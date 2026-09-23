"""Regression tests for the reviewed failures and the narrowed API contracts."""
import json
from pathlib import Path
import numpy as np
import pytest
from scipy.linalg import eigh
import guarded_topology as gt
import guarded_sparse as gs
from bm_strain import BM
from gate import real_basis

PLAN = json.loads((Path(__file__).parent/'PLAN.json').read_text())


class Toy:
    dim = 4
    valley = 1
    def frac_to_k(self, f): return np.asarray(f)
    def H(self, k): return np.diag([-3., -1., 1., 3.]).astype(complex)


class Smooth(Toy):
    def H(self, k):
        a = 2*np.pi*k[0]; c, s = np.cos(a), np.sin(a)
        R = np.eye(4); R[:2, :2] = [[c, -s], [s, c]]
        return (R @ super().H(k) @ R.T).astype(complex)


def sampler(model=None, **policy):
    return gt.Sampler(Toy() if model is None else model, gt.Policy(**policy), U=np.eye(4))


def assert_code(code, call):
    with pytest.raises(gt.Rejected) as ex: call()
    assert ex.value.record['code'] == code


@pytest.mark.parametrize('name,value', [('external_gap_meV', 0), ('overlap_min', 0), ('reality_meV', float('nan')), ('root_gap_meV', -1), ('overlap_min', 1.1), ('phase_step_max_rad', np.pi)])
def test_invalid_policy_refused(name, value):
    with pytest.raises(gt.Rejected): gt.Policy(**{name: value})


@pytest.mark.parametrize('lo', [1.2, float('nan'), True, -1, 4])
def test_invalid_band_refused(lo):
    with pytest.raises(gt.Rejected): sampler().frame([0, 0], lo)


@pytest.mark.parametrize('lo', [0, 2])
def test_both_external_edges_accounted_and_enforced(lo):
    S = sampler(); S.frame([0, 0], lo)
    row = S.records[-1]
    assert row['external_gap_meV'] == 2
    assert (row['lower_external_gap_meV'] is None) == (lo == 0)
    assert (row['upper_external_gap_meV'] is None) == (lo == 2)
    assert_code('external_gap', lambda: sampler(external_gap_meV=3).frame([0, 0], lo))


def test_full_space_external_is_not_applicable():
    S = sampler(); S.frame([0, 0], 0, 4)
    assert S.records[-1]['external_status'] == 'NOT_APPLICABLE_FULL_SPACE'
    assert S.records[-1]['external_gap_meV'] is None


def test_negative_loop_start_and_exact_mirror():
    nodes = [[.3, .4], [.6, .6]]
    for direction in ([1, 0], [-1, 0]):
        g = gt.geometry(nodes, .012, 96, 300, direction)
        assert np.array_equal(g['transport'][0], g['loops'][0][0])
        assert np.array_equal(g['transport'][-1], g['loops'][1][0])
        assert np.allclose(np.array(g['loops'][0][0])-nodes[0], np.array(direction)*.012, atol=1e-16)
        for key in ('nodes', 'loops', 'transport'):
            assert np.array_equal(gt.mirror(g)[key], -np.asarray(g[key]))


def test_mismatched_base_refused_before_frame():
    g = gt.geometry([[.3, .4], [.6, .6]], .012, 8, 8)
    g['transport'][0][0] += .024
    S = sampler()
    assert_code('base_path_mismatch', lambda: gt.pair_charges(S, g))
    assert not any(x['kind'] == 'frame' for x in S.records)


def test_nonroot_centers_refused():
    g = gt.geometry([[.3, .4], [.6, .6]], .012, 8, 8)
    assert_code('unverified_node', lambda: gt.pair_charges(sampler(), g))


def test_zero_pair_overlap_refused():
    class Jump(Toy):
        def H(self, k):
            return np.diag([-3., -1., 1., 3.] if round(4*k[1]) % 2 == 0 else [-1., -3., 3., 1.]).astype(complex)
    assert_code('overlap', lambda: gt.euler_wilson(sampler(Jump()), nf1=4, nf2=4, sewings=(np.eye(4), np.eye(4))))


def test_smooth_band_coarse_refusal_and_refined_acceptance():
    assert_code('overlap', lambda: gt.band_sign_holonomy(sampler(Smooth()), 1, 0, 0, n=4, sewing_matrix=np.eye(4)))
    r = gt.band_sign_holonomy(sampler(Smooth()), 1, 0, 0, n=32, sewing_matrix=np.eye(4))
    assert r['sign'] == 1


@pytest.mark.parametrize('axis', [0, 1])
def test_both_sewing_directions_enforced(axis):
    sew = [np.eye(4), np.eye(4)]; sew[axis] *= .9
    assert_code('sewing_loss', lambda: gt.euler_wilson(sampler(), nf1=4, nf2=4, sewings=sew))


def test_zero_sewing_refused():
    assert_code('overlap', lambda: gt.band_sign_holonomy(sampler(), 1, 0, 0, n=4, sewing_matrix=np.zeros((4, 4))))


def test_positive_wilson_and_boundary_bands():
    for lo in [0, 1, 2]:
        r = gt.euler_wilson(sampler(), lo=lo, nf1=4, nf2=4, sewings=(np.eye(4), np.eye(4)))
        assert r['euler_estimate'] == 0
    for band in [0, 3]:
        assert gt.band_sign_holonomy(sampler(), band, 0, 0, n=4, sewing_matrix=np.eye(4))['sign'] == 1


def test_degenerate_band_rejected():
    class Degenerate(Toy):
        def H(self, k): return np.diag([-2., 0., 0., 2.]).astype(complex)
    assert_code('external_gap', lambda: gt.band_sign_holonomy(sampler(Degenerate()), 1, 0, 0, n=4, sewing_matrix=np.eye(4)))


def test_native_reality_and_realify_binding():
    m = BM(N=2, eps=.003, kinetic='lab_nn_full', geometry='exact')
    f = np.array([.31, .27]); H = m.H(m.frac_to_k(f)); U = real_basis(m.nG)
    assert np.max(np.abs(gs.realify(H)-U.conj().T @ H @ U)) < 1e-9
    m2 = BM(N=2, eps=.003, mass=1, kinetic='lab_nn_full', geometry='exact')
    assert_code('matrix_precondition', lambda: gt.Sampler(m2).frame(f, m2.dim//2-1))


@pytest.mark.parametrize('idx', [[[1.9, 0]], [[float('nan'), 0]], [[True, 0]], [['1', 0]], [[0, 0], [0, 0]], [1, 2], []])
def test_bad_basis_rejected_before_constructor(idx):
    with pytest.raises(gt.Rejected): gs.fixed_bm(idx)


def model_and_checker():
    kw = dict(N=3, eps=.003, kinetic='lab_nn_full', geometry='exact')
    idx = BM(**kw).idx
    m = gs.fixed_bm(idx, **kw)
    return m, gs.CheckedSparse(m, idx, PLAN['sparse'])


def test_implicit_basis_not_supported():
    m = BM(N=2)
    assert_code('fixed_declared_basis_required', lambda: gs.CheckedSparse(m, m.idx, PLAN['sparse']))


def test_sparse_mandatory_native_match_and_work_accounting():
    m, C = model_and_checker(); lo = m.dim//2-3; f = [.31, .27]
    w, V = C.window(f, lo, 6)
    expected = eigh(m.H(m.frac_to_k(np.array(f))), eigvals_only=True, subset_by_index=(lo, lo+5))
    assert np.max(abs(w-expected)) < 1e-8
    counts = C.ledger.counts()
    assert counts == {'setup': 1, 'native_assembly': 1, 'candidate_assembly': 1, 'native_dense_eigh': 1, 'lu_factorization': 1, 'arpack': 1, 'validation': 1}
    assert len([x for x in C.ledger.entries if x['kind'] == 'attempt']) == 1
    assert all('inclusive_wall_seconds' not in x for x in C.ledger.entries if x['kind'] == 'component')


def test_wrong_absolute_bands_rejected_even_with_good_residual(monkeypatch):
    m, C = model_and_checker(); lo = m.dim//2-3
    def wrong(S, k, **kw):
        # Exact eigenpairs from the wrong absolute window: residual alone passes.
        return eigh(S.toarray(), subset_by_index=(lo+2, lo+2+k-1))
    monkeypatch.setattr(gs, 'eigsh', wrong)
    assert_code('absolute_window_not_matched', lambda: C.window([.31, .27], lo, 6))
    assert C.ledger.entries[-1]['status'] == 'REJECTED'
    assert not any(x['kind'] == 'accepted' for x in C.ledger.entries)


def test_far_shift_missing_window_refused():
    m, C = model_and_checker()
    assert_code('absolute_window_not_matched', lambda: C.window([.31, .27], m.dim//2-3, 6, sigma=10000, request_k=8))


def test_changed_static_model_cannot_use_stale_fast_snapshot():
    m, C = model_and_checker(); m.Hstat[0, 0] += 1; m.Hstat[1, 1] += 1
    assert_code('sparse_comparison', lambda: C.window([.31, .27], m.dim//2-3, 6))


def test_general_lu_used_only_as_solver_on_inertia_counterexample():
    # The original signed-U-diagonal count is demonstrably wrong. The replacement
    # uses LU only for inverse application; the ordered reference is dense eigh.
    A = np.array([[0., 1.], [1., 0.]])
    lu = gs.splu(gs.sp.csc_matrix(A), diag_pivot_thresh=0., options={'SymmetricMode': True})
    assert np.count_nonzero(lu.U.diagonal() < 0) == 0
    assert np.count_nonzero(eigh(A, eigvals_only=True) < 0) == 1
    assert np.allclose(A @ lu.solve(np.eye(2)), np.eye(2))
