"""Assertion-based regression tests (audit v034, action 4). Expected values are either
exact by symmetry, independently derived, or the recorded v023 baseline at N=4.
Run: python -m pytest test_regression.py -q   (or python test_regression.py)"""
import numpy as np, pytest
from bm_strain import BM, frac_dist, segment_geometry, wrap, sz, sx, sy, s0
from gate import real_basis, real_frame_checked, ortho_checked, classify, GateError
from knobs import add_harmonic

def test_unstrained_dirac_points_exact_by_symmetry():
    m = BM(N=4)
    for f in ([0, 0], [1/3, 1/3]):            # K_M and K'_M: layer-1 and layer-2 Dirac points
        assert m.gaps(m.frac_to_k(np.array(f)))[0] < 1e-6
    assert m.gaps(m.frac_to_k(np.array([2/3, 2/3])))[0] > 5.0   # Gamma_M is gapped

def test_unstrained_flat_bandwidth_and_gamma_gap():
    m = BM(N=4)
    assert 6.0 < m.flat_bandwidth(12) < 9.0          # ~7.4 meV at 1.05 deg, w0/w1=0.8
    assert 18.0 < m.gaps(m.frac_to_k(np.array([2/3, 2/3])))[1] < 23.0

@pytest.mark.parametrize("mat,use_sin,layer_sign", [(s0,False,1),(sx,False,1),(sy,False,1),(sz,True,1),(sz,True,-1),(s0,False,-1)])
def test_allowed_harmonics_preserve_C2zT(mat,use_sin,layer_sign):
    m = BM(N=3, eps=0.003, A_scalar=0.1); add_harmonic(m, 0.2, mat=mat, use_sin=use_sin, layer_sign=layer_sign)
    U = real_basis(m.nG)
    for f in ([0.3,0.2],[0.71,0.64]):
        real_frame_checked(m, U, m.frac_to_k(np.array(f)), m.dim//2-1)   # raises if not real

@pytest.mark.parametrize("mat,use_sin", [(sz,False),(sy,True),(sx,True),(s0,True)])
def test_forbidden_harmonics_break_C2zT(mat,use_sin):
    m = BM(N=3, eps=0.003); add_harmonic(m, 0.2, mat=mat, use_sin=use_sin)
    U = real_basis(m.nG)
    with pytest.raises(GateError):
        real_frame_checked(m, U, m.frac_to_k(np.array([0.3,0.2])), m.dim//2-1)

def test_strained_baseline_nodes_and_remote_gap_v023():
    m = BM(N=4, eps=0.003, phi_deg=0)
    nodes = [f for v, f in m.find_nodes(ngrid=15, nkeep=6) if v < 1e-6]
    assert len(nodes) == 2
    ref = [np.array([0.75641, 0.60857]), np.array([0.57869, 0.72848])]
    assert all(min(frac_dist(n, r) for r in ref) < 2e-3 for n in nodes)
    assert abs(m.min_remote(ngrid=15, nkeep=4)[0] - 5.458) < 0.05

def test_segment_geometry_periodic_example_from_audit():
    t, off, L = segment_geometry([0.99, 0.5], [0.01, 0.5], [0.0, 0.5])
    assert abs(t - 0.5) < 1e-12 and abs(off) < 1e-12 and abs(L - 0.02) < 1e-12
    with pytest.raises(ValueError):
        segment_geometry([0.3, 0.3], [0.3, 0.3], [0.5, 0.5])

def test_ortho_refuses_singular_frame():
    with pytest.raises(GateError):
        ortho_checked(np.diag([1.0, 0.0]))
    q = ortho_checked(np.array([[2.0, 1.0], [0.0, 1.0]]))
    assert np.allclose(q.T @ q, np.eye(2))

def test_classify_never_labels_zero_or_junk():
    assert classify(1.0, -0.98) == 'OPPOSITE'
    assert classify(-1.0, -1.02) == 'SAME'
    assert classify(0.0, 1.0) == 'INDETERMINATE'
    assert classify(0.5, 1.0) == 'INDETERMINATE'
    assert classify(float('nan'), 1.0) == 'INDETERMINATE'

def test_refine_records_optimizer_status():
    m = BM(N=3, eps=0.003)
    f, v, info = m.refine(np.array([0.75, 0.61]), lambda q: m.gaps(m.frac_to_k(q))[0], return_result=True)
    assert info['success'] and v < 1e-6

if __name__ == "__main__":
    import sys; sys.exit(pytest.main([__file__, "-q"]))

def test_tunnelling_strain_law_first_order_cancellation_and_bound():
    """v045: heterostrain modulates w0,w1 only at O(eps^2) in the average law; worst case bounded."""
    m0 = BM(N=3, eps=0.003, kinetic='lab_nn_full', geometry='exact')
    ma = BM(N=3, eps=0.003, kinetic='lab_nn_full', geometry='exact', w_kappa=5.0, w_mode='average')
    mw = BM(N=3, eps=0.003, kinetic='lab_nn_full', geometry='exact', w_kappa=5.0, w_mode='layer1')
    for j in range(3):
        assert np.abs(ma.T[j] - m0.T[j]).max() < 1e-12             # exact cancellation for E_1 = -E_2
        assert 0.99 < np.linalg.norm(mw.T[j]) / np.linalg.norm(m0.T[j]) < 1.0    # <= 0.75% at kappa=5, eps=0.3%

def test_refine_metadata_reflects_final_attempt_and_is_explicit_on_failure():
    """v053 audit target 1: after a wrapped re-refinement, last_refine describes the final attempt; both attempts kept."""
    m = BM(N=3, eps=0.003)
    fn = lambda q: m.gaps(m.frac_to_k(q))[0]
    f, v, info = m.refine(np.array([0.75, 0.61]), fn, return_result=True)
    assert info['success'] and len(info['attempts']) >= 1 and info['attempts'][-1]['value'] == v
    # force a wrap: seed just outside the cell so the first attempt lands at negative coordinates
    f2, v2, info2 = m.refine(np.array([0.75 - 1.0, 0.61]), fn, return_result=True)
    assert np.all((f2 >= 0) & (f2 < 1)) and len(info2['attempts']) == 2 and info2['attempts'][-1]['value'] == v2
    assert abs(v2 - v) < 1e-8 and np.linalg.norm(((f2 - f) + 0.5) % 1 - 0.5) < 1e-5
    # an objective that is non-finite must be reported as failure, never as success
    f3, v3, info3 = m.refine(np.array([0.3, 0.3]), lambda q: float('nan'), return_result=True)
    assert info3['success'] is False

def test_euler_real_frame_guard_is_runtime_not_assert():
    from euler import real_frame
    from gate import real_basis
    from knobs import add_harmonic
    m = BM(N=3, eps=0.003); add_harmonic(m, 0.2, mat=sz, use_sin=False)   # cos*sigma_z breaks C2zT
    with pytest.raises(RuntimeError):
        real_frame(m, real_basis(m.nG), m.frac_to_k(np.array([0.3, 0.2])))
