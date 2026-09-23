"""Fixed small-matrix checks for the boundary review note (docs/boundary-review).

Synthetic 3x3 and small random matrices only: no Hamiltonian from the
repository, no production code, no sweep. Refuses to overwrite its output
and exits 1 if any predicate fails.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np

TOL = 1e-12


def polar(m):
    u, _, vt = np.linalg.svd(m)
    return u @ vt


def orth(a):
    q, _ = np.linalg.qr(a)
    return q


def smin(m):
    return float(np.linalg.svd(m, compute_uv=False).min())


def selected_polar(s, e0, e1):
    """Selected-fibre polar isometry J as an ambient map on range(e0)."""
    return e1 @ polar(e1.T @ s @ e0) @ e0.T


def corner_case(c):
    # Explicit orthonormal basis of span{(1,1,0),(0,1,1)}, as used in review 5288150576.
    f0 = np.column_stack([np.array([1., 1., 0.]) / np.sqrt(2), np.array([-1., 1., 2.]) / np.sqrt(6)])
    s1, s2 = np.diag([1., c, 1.]), np.diag([1., 1., c])
    e1, e2, e3 = orth(s1 @ f0), orth(s2 @ f0), orth(s1 @ s2 @ f0)  # exact-image fibres
    j1b, j2l = selected_polar(s1, f0, e1), selected_polar(s2, f0, e2)
    j2r, j1t = selected_polar(s2, e1, e3), selected_polar(s1, e2, e3)
    path_a, path_b = j2r @ j1b @ f0, j1t @ j2l @ f0
    d = (e3.T @ path_a).T @ (e3.T @ path_b)
    edges = [(s1, f0, e1, j1b), (s2, f0, e2, j2l), (s2, e1, e3, j2r), (s1, e2, e3, j1t)]
    lam = [1 - smin(e.T @ s @ f) for s, f, e, _ in edges]
    eps = [float(np.linalg.norm((j - s) @ f, 2)) for s, f, _, j in edges]
    return dict(c=c, commute=float(np.abs(s1 @ s2 - s2 @ s1).max()),
                link_loss=lam, max_link_loss=max(lam), epsilon=eps,
                defect_norm=float(np.linalg.norm(path_a - path_b, 2)),
                telescoping_bound=float(sum(eps)),
                corner_angle=float(np.arctan2(d[1, 0], d[0, 0])), corner_det=float(np.linalg.det(d)))


def main(out):
    if out.exists():
        raise FileExistsError('refusing to overwrite ' + str(out))
    checks = []

    def check(name, ok, **ev):
        checks.append(dict(name=name, passed=bool(ok), **ev))

    corners = [corner_case(c) for c in (0.5, 0.95)]
    for r in corners:
        check(f'commuting_maps_c{r["c"]}', r['commute'] == 0.0, value=r['commute'])
        check(f'corner_defect_nonzero_c{r["c"]}', abs(r['corner_angle']) > 1e-5 and abs(r['corner_det'] - 1) < 1e-10,
              angle=r['corner_angle'])
        check(f'exact_image_epsilon_le_lambda_c{r["c"]}', all(e <= l + TOL for e, l in zip(r['epsilon'], r['link_loss'])),
              epsilon=r['epsilon'], link_loss=r['link_loss'])
        check(f'epsilon_le_sqrt2lambda_c{r["c"]}', all(e <= np.sqrt(2 * l) + TOL for e, l in zip(r['epsilon'], r['link_loss'])))
        check(f'telescoping_bound_c{r["c"]}', r['defect_norm'] <= r['telescoping_bound'] + TOL,
              defect_norm=r['defect_norm'], bound=r['telescoping_bound'])
    check('c095_passes_0.05_sewing_gate', corners[1]['max_link_loss'] <= 0.05, value=corners[1]['max_link_loss'])

    # Constant commuting orthogonal control: exact equivariant fibres close the corner.
    rng = np.random.default_rng(20260923)
    t1 = np.linalg.qr(rng.normal(size=(4, 4)))[0]
    t2 = t1 @ t1
    f0 = orth(rng.normal(size=(4, 2)))
    e1, e2, e3 = t1 @ f0, t2 @ f0, t1 @ t2 @ f0
    a = selected_polar(t2, e1, e3) @ selected_polar(t1, f0, e1) @ f0
    b = selected_polar(t1, e2, e3) @ selected_polar(t2, f0, e2) @ f0
    ortho_defect = float(np.linalg.norm(a - b, 2))
    check('orthogonal_commuting_control_closes', ortho_defect < 1e-12, value=ortho_defect)

    # Residual counterexample: on-target projected residual is blind to off-target mismatch.
    th = 0.2
    h = np.diag([0., 0., 1.]); p = np.diag([1., 1., 0.]); q = np.eye(3) - p; f = np.eye(3)[:, :2]
    s = np.array([[np.cos(th), 0, -np.sin(th)], [0, 1, 0], [np.sin(th), 0, np.cos(th)]])
    projected = float(np.abs(p @ (h @ s - s @ h) @ p).max())
    offtarget = float(np.linalg.norm(q @ s @ p, 2))
    loss = 1 - smin(f.T @ s @ f)
    bperp = float(np.linalg.norm(q @ (h @ s - s @ h) @ f))
    check('projected_residual_zero', projected == 0.0, value=projected)
    check('offtarget_mismatch_nonzero', abs(offtarget - np.sin(th)) < TOL, value=offtarget)
    check('sewing_loss_small', abs(loss - (1 - np.cos(th))) < TOL, value=loss)
    check('complementary_residual_detects', abs(bperp - np.sin(th)) < TOL, value=bperp)

    # Sylvester bound ||R||_F <= ||B_perp||_F / delta on random spectral data.
    worst = 0.
    for _ in range(200):
        n, r = 6, 2
        w0 = np.sort(rng.normal(size=n)); w1 = np.sort(rng.normal(size=n))
        u0 = np.linalg.qr(rng.normal(size=(n, n)))[0]; u1 = np.linalg.qr(rng.normal(size=(n, n)))[0]
        h0 = u0 @ np.diag(w0) @ u0.T; h1 = u1 @ np.diag(w1) @ u1.T
        f0 = u0[:, 2:4]; a0 = np.diag(w0[2:4]); p1 = u1[:, 2:4] @ u1[:, 2:4].T
        sm = np.linalg.qr(rng.normal(size=(n, n)))[0] * 0.9
        rr = (np.eye(n) - p1) @ sm @ f0
        bp = (np.eye(n) - p1) @ (h1 @ sm - sm @ h0) @ f0
        others = np.r_[w1[:2], w1[4:]]
        delta = min(abs(x - y) for x in others for y in w0[2:4])
        if delta > 1e-3:
            worst = max(worst, np.linalg.norm(rr) - np.linalg.norm(bp) / delta)
    check('sylvester_bound_random', worst <= TOL, max_violation=float(worst))

    ok = all(c['passed'] for c in checks)
    result = dict(schema='twistronics_boundary_review_v1', passed=ok,
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  environment=dict(python=platform.python_version(), numpy=np.__version__),
                  corner_cases=corners, orthogonal_control_defect=ortho_defect,
                  residual_counterexample=dict(theta=th, projected_residual=projected, offtarget=offtarget,
                                               sewing_loss=loss, complementary_residual=bperp),
                  checks=checks,
                  limits=['Synthetic fixed matrices and seeded random spectral data only',
                          'No repository Hamiltonian, production API, cutoff comparison or physical claim',
                          'Floating-point checks of stated identities; not interval enclosures'])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x') as fh:
        fh.write(json.dumps(result, indent=2) + '\n')
    for c in checks:
        print(('PASS ' if c['passed'] else 'FAIL ') + c['name'])
    print(f"{sum(c['passed'] for c in checks)}/{len(checks)} checks; overall={ok}")
    return 0 if ok else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    sys.exit(main(ap.parse_args().output.resolve()))
