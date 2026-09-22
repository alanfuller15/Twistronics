"""Analytic and adversarial controls before the R1 calculation."""
import json
import numpy as np
from scipy.linalg import eigh
from bounds import ROOT, sha, center_data, certificate, enclosure, containment

class Toy:
    dim = 4
    def __init__(self, curved=False, rotation=None, closure=False, singular=False):
        self.h0 = np.diag([-10., 0., 0., 10.])
        x = np.diag([0., 1., -1., 0.])
        y = np.zeros((4, 4)); y[1, 2] = y[2, 1] = 1.
        d = np.zeros((4, 4))
        if curved:
            d[1, 3] = d[3, 1] = 1.
        else:
            d = -.02*x+.03*y+.1*np.eye(4)
        if closure:
            d[3, 3] = -40.
        self.h0 -= .4*x+.6*y
        self.A = [x, np.zeros_like(y) if singular else y, d]
        if rotation is not None:
            self.h0 = rotation.T @ self.h0 @ rotation
            self.A = [rotation.T @ a @ rotation for a in self.A]
        self.curved = curved

    def H(self, v):
        return self.h0+v[0]*self.A[0]+v[1]*self.A[1]+(v[2]-38)*self.A[2]

    def exact(self, D):
        d = D-38
        if self.curved:
            x = np.sqrt(25+.5*d*d)-5
            return np.array([.4+x, .6, -x])
        return np.array([.4+.02*d, .6-.03*d, .1*d])

def check_path(toy, a, b):
    D = (a+b)/2
    raw, _ = center_data(toy, D, 1, toy.exact(D)[:2])
    cert = certificate(raw, (b-a)/2)
    distances, gaps = [], []
    for d in np.linspace(a, b, 101):
        lo, hi = enclosure(raw, cert, d)
        y = toy.exact(d)
        distances.append(float(np.min(np.r_[y-lo, hi-y])))
        w = eigh(toy.H([*y[:2], d]), eigvals_only=True)
        gaps.append(float(w[2]-w[1]))
    return raw, cert, {'minimum_containment_margin': min(distances), 'maximum_exact_root_gap_meV': max(gaps)}

def main():
    records = []
    def add(name, ok, **evidence):
        records.append({'name': name, 'pass': bool(ok), **evidence})
    rng = np.random.default_rng(104729)
    rotation = np.linalg.qr(rng.normal(size=(4, 4)))[0]
    for name, toy in [('translating_node', Toy()), ('constant_real_basis_change', Toy(rotation=rotation)), ('curved_schur_root', Toy(curved=True))]:
        raw, cert, measured = check_path(toy, 37.75, 38.25)
        add(name, cert['pass'] and measured['minimum_containment_margin'] > 0 and measured['maximum_exact_root_gap_meV'] < 1e-10,
            center=raw, certificate=cert, analytic_samples=measured)
    toy = Toy(curved=True)
    raw, cert, _ = check_path(toy, 37.75, 38.25)
    tiny = certificate(raw, .25, radius_override=np.array(cert['radii'])*.01)
    lo, hi = enclosure(raw, tiny, 38.25)
    actual_outside = bool(np.any(toy.exact(38.25) < lo) or np.any(toy.exact(38.25) > hi))
    add('undersized_radius_rejected', not tiny['pass'] and actual_outside, certificate=tiny, analytic_endpoint_outside=actual_outside)
    raw, _ = center_data(Toy(curved=True, closure=True), 38, 1, [.4, .6])
    closed = certificate(raw, .3)
    add('complement_closure_rejected', not closed['pass'] and closed['reason'] == 'complement_line_or_inertia', certificate=closed)
    failure = None
    try:
        center_data(Toy(singular=True), 38, 1, [.4, .6])
    except ValueError as e:
        failure = str(e)
    add('singular_momentum_map_rejected', failure == 'singular_projected_map', reason=failure)
    point, _ = center_data(toy, 38, 1, [.4, .6])
    pc = certificate(point, 0)
    joins = []
    for D in [37.875, 38.125]:
        r, _ = center_data(toy, D, 1, toy.exact(D)[:2])
        t = certificate(r, .125)
        joins.append(containment(point, pc, r, t, 38))
    add('common_endpoint_root_contained', pc['pass'] and all(j['pass'] for j in joins), joins=joins)
    fake_point = {'y': [0., 0., 0.], 'D_meV': 38., 'velocity': [0., 0., 0.]}
    fake_tube = dict(fake_point, y=[1.5, 0., 0.])
    point_cert = {'pass': True, 'inner_radii': [.1, .1, .1]}
    tube_cert = {'pass': True, 'radii': [1., 1., 1.]}
    bad = containment(fake_point, point_cert, fake_tube, tube_cert, 38)
    # [-1,1] and [.5,2.5] overlap, but a root in [-.1,.1] is not in the latter.
    add('outer_overlap_insufficient', not bad['pass'], outer_boxes_overlap=True, containment=bad)
    out = {'plan_sha256': sha(ROOT/'PLAN.json'), 'source_hashes': {n: sha(ROOT/n) for n in ['bounds.py', 'controls.py']},
           'controls': records, 'all_controls_pass': all(r['pass'] for r in records)}
    (ROOT/'CONTROLS.json').write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    for r in records:
        print(r['name'], r['pass'])
    return 0 if out['all_controls_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
