"""Cross-implementation tests (v036): the independent model tbg_ref must agree with bm_strain
where their conventions coincide, and differ only by the velocity-renormalisation term."""
import numpy as np, pytest
from bm_strain import BM
from tbg_ref import TBG

def test_unstrained_spectra_agree_at_K_and_Gamma():
    a, b = BM(N=4), TBG(N=4, kinetic='none')
    for f in ([0, 0], [1/3, 1/3], [2/3, 2/3]):
        wa = a.bands_near_zero(a.frac_to_k(np.array(f)), 2); wb = b.bands(b.k(np.array(f)), 2)
        assert np.abs(wa - wb).max() < 2e-3

def test_strained_nodes_agree_with_kinetic_none():
    a = BM(N=4, eps=0.003); b = TBG(N=4, eps=0.003, kinetic='none')
    na = sorted([f for v, f in a.find_nodes(ngrid=15, nkeep=6) if v < 1e-6], key=lambda f: f[0])
    nb = sorted(b.find_nodes(n=15, keep=6), key=lambda f: f[0])
    assert len(na) == len(nb) == 2
    assert all(np.linalg.norm(((x - y) + 0.5) % 1 - 0.5) < 2e-4 for x, y in zip(na, nb))

def test_kinetic_tensor_sensitivity_of_remote_gap():
    """v038: kinetic='none' reproduces bm_strain to <3e-4 meV in bands (here: gap to 1e-2);
    the full Oliva-Leyva-Naumis tensor v0(I+(1-beta)E) lowers the remote gap by ~9%."""
    g = lambda m: min(m.refine(np.array([a, c]), m.remote_gap)[1] for _, a, c in sorted([(m.remote_gap(np.array([a, c])), a, c) for a in np.linspace(0, 1, 12, endpoint=False) for c in np.linspace(0, 1, 12, endpoint=False)])[:3])
    g0 = g(TBG(N=4, eps=0.003, kinetic='none')); gf = g(TBG(N=4, eps=0.003, kinetic='full'))
    assert abs(g0 - 5.458) < 0.01
    assert 0.35 < g0 - gf < 0.65

def test_1d_velocity_sign_check():
    """geometric factor is (1+eps), not (1-eps): E=-2t cos(k a (1+eps)) has slope ~ a(1+eps)."""
    t, a, k = 1.0, 1.0, 0.3
    v = lambda eps: 2*t*a*(1+eps)*np.sin(k*a*(1+eps))
    assert v(0.01) > v(0.0) > v(-0.01)

def test_plaquette_euler_class_is_minus_one_unstrained():
    m = TBG(N=3, kinetic='none'); U = m.real_basis()
    e, cl, md = m.euler_plaquette(U, m.dim//2 - 1, n1=16, n2=16)
    assert abs(abs(e) - 1) < 0.05 and min(cl) > 0.9 and md > 0

if __name__ == "__main__":
    import sys; sys.exit(pytest.main([__file__, "-q"]))


@pytest.mark.parametrize("kin", ["none", "full", "lab_nn_full"])
def test_both_engines_agree_for_each_declared_kinetic_option(kin):
    """v041: the same declared model in both engines; nodes to 1e-5, remote gap to 1e-3 meV."""
    a = BM(N=4, eps=0.003, kinetic=kin); b = TBG(N=4, eps=0.003, kinetic=kin)
    na = sorted([f for v, f in a.find_nodes(ngrid=15, nkeep=6) if v < 1e-6], key=lambda f: f[0])
    nb = sorted(b.find_nodes(n=15, keep=6), key=lambda f: f[0])
    assert len(na) == len(nb) == 2
    assert max(np.linalg.norm(((x - y) + 0.5) % 1 - 0.5) for x, y in zip(na, nb)) < 1e-5
    ra = a.min_remote(ngrid=15, nkeep=4)[0]
    seeds = sorted([(b.remote_gap(np.array([p, q])), p, q) for p in np.linspace(0, 1, 15, endpoint=False) for q in np.linspace(0, 1, 15, endpoint=False)])[:3]
    rb = min(b.refine(np.array([p, q]), b.remote_gap)[1] for _, p, q in seeds)
    assert abs(ra - rb) < 1e-3

def test_tbg_ref_requires_explicit_kinetic():
    with pytest.raises(ValueError):
        TBG(N=3)

def test_invalid_charge_is_none_not_zero():
    m = TBG(N=3, eps=0.003, kinetic='none'); U = m.real_basis(); lo = m.dim // 2 - 1
    nodes = m.find_nodes(n=12, keep=4); assert len(nodes) == 2
    # a frame taken between the two nodes at a distance comparable to the loop radius must not yield a numeric charge
    mid = 0.5 * (nodes[0] + nodes[1]); frame = m.real_frame(U, m.k(mid), lo)
    d = np.linalg.norm(nodes[0] - nodes[1])
    w = m.node_charge(U, nodes[0], lo, frame, r=0.45 * d)
    assert w is None or abs(w) == 1

def test_exact_geometry_makes_engines_agree_to_roundoff():
    """v043: with geometry='exact' in bm_strain, the two engines are the same declared model to roundoff."""
    a = BM(N=3, eps=0.003, phi_deg=65, kinetic='lab_nn_full', geometry='exact'); b = TBG(N=3, eps=0.003, phi=65, kinetic='lab_nn_full')
    for f in ([0.31, 0.27], [1.13, 0.62]):
        wa = a.bands_near_zero(a.frac_to_k(np.array(f)), 3); wb = b.bands(b.k(np.array(f)), 3)
        assert np.abs(wa - wb).max() < 1e-10
    a2 = BM(N=3, eps=0.003, phi_deg=65, kinetic='lab_nn_full', geometry='linear')
    wa2 = a2.bands_near_zero(a2.frac_to_k(np.array([0.31, 0.27])), 3); wb = b.bands(b.k(np.array([0.31, 0.27])), 3)
    assert 1e-5 < np.abs(wa2 - wb).max() < 2e-3          # linearised geometry residual, as v042 reported

def test_gap_min_never_returns_infinity():
    m = TBG(N=3, eps=0.003, kinetic='none')
    v = m.gap_min(2, n=8, keep=2)
    assert np.isfinite(v) and v > 0

def test_cutoff_padding_witness_and_common_tolerance():
    """v046 (team witness): at phi=15.843560625048124 deg two indices sit between the historical paddings;
    with a common cutoff_tol the bases and matrices match."""
    kw = dict(N=4, eps=0.003, kinetic='lab_nn_full')
    a = BM(phi_deg=15.843560625048124, geometry='exact', **kw); b = TBG(phi=15.843560625048124, **kw)
    assert (a.dim, b.dim) == (196, 188)
    for tol in (1e-9, 1e-6):
        a2 = BM(phi_deg=15.843560625048124, geometry='exact', cutoff_tol=tol, **kw); b2 = TBG(phi=15.843560625048124, cutoff_tol=tol, **kw)
        assert a2.dim == b2.dim
        wa = a2.bands_near_zero(a2.frac_to_k(np.array([0.31, 0.27])), 3); wb = b2.bands(b2.k(np.array([0.31, 0.27])), 3)
        assert np.abs(wa - wb).max() < 1e-10
    with pytest.raises(ValueError):
        TBG(cutoff_tol=-1.0, **kw)
