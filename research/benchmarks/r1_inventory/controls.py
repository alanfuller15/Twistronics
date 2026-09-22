"""Known affine multiband families, including a hidden second double root."""
import json
import numpy as np
from scipy.linalg import eigh, qr
from inventory import ROOT, sha, components, primitives, correction, core_capture, outer_guard, cover, strips

class Toy:
    dim = 5
    def __init__(self, alpha=0., moving=False, rotated=False, closing=False):
        x = np.diag([0., 1., -1., 0., 0.]); y = np.zeros((5, 5)); y[1, 2] = y[2, 1] = 1.
        x[1, 3] = x[3, 1] = alpha
        self.h0 = np.diag([-20., 0., 0., 10., 30.])-.4*x-.6*y
        d = -.02*x+.03*y+.1*np.eye(5) if moving else np.zeros((5, 5))
        if closing:
            d[3, 3] -= 40.
        self.A = [x, y, d]
        if rotated:
            rng = np.random.default_rng(314159)
            O = np.linalg.qr(rng.normal(size=(5, 5)))[0]
            self.h0 = O.T @ self.h0 @ O
            self.A = [O.T @ a @ O for a in self.A]
    def H(self, v):
        return self.h0+v[0]*self.A[0]+v[1]*self.A[1]+(v[2]-38)*self.A[2]

def reference(family):
    H = family.H([.4, .6, 38.]); w, V = eigh(H)
    F = qr(V[:, 1:3], mode='full')[0][:, :2]; Q = qr(F, mode='full')[0][:, 2:]
    E = float(np.trace(F.T @ H @ F)/2)
    J = np.column_stack([components(F.T @ a @ F) for a in family.A[:2]]+[components(-np.eye(2))])
    velocity = -np.linalg.solve(J, components(F.T @ family.A[2] @ F))
    raw = {'D_meV': 38., 'lo': 1, 'y': [.4, .6, E], 'velocity': velocity.tolist(),
           'complement_eigenvalues_meV': eigh(Q.T @ H @ Q-E*np.eye(3), eigvals_only=True).tolist()}
    return primitives(family, raw, F)

def main():
    records = []
    def add(name, passed, **evidence):
        records.append({'name': name, 'pass': bool(passed), **evidence})
    for name, family in [('isolated_linear_node', Toy()), ('translating_node', Toy(moving=True)),
                         ('constant_real_basis_change', Toy(moving=True, rotated=True)), ('nonzero_remote_coupling', Toy(alpha=2.))]:
        p = reference(family); rows, result = cover(p, [.1, .1], [.02, .02], .25)
        bridge = core_capture(p, [.02, .02, .1], .25); other = outer_guard(p, [.1, .1], .25)
        add(name, result['pass'] and bridge['pass'] and other['pass'], cover=result, core=bridge, other_gaps=other)
    family = Toy(alpha=10.); p = reference(family)
    rows, result = cover(p, [.25, .25], [.01, .01], .01, {'maximum_depth': 10, 'maximum_split_nodes_per_reference': 400})
    extra = np.array([20/(100-2), 0., 0.])
    w = eigh(family.H([.4+extra[0], .6, 38.]), eigvals_only=True)
    leaves = rows[rows[:, 10] != 0]
    containing = leaves[np.all(leaves[:, :3] <= extra, axis=1) & np.all(leaves[:, 3:6] >= extra, axis=1)]
    add('second_analytic_node_not_excluded', not result['pass'] and w[2]-w[1] < 1e-10 and len(containing) > 0 and np.all(containing[:, 10] != 1),
        cover=result, second_node_offset=extra.tolist(), second_node_gap_meV=float(w[2]-w[1]), containing_leaf_states=containing[:, 10].tolist())
    bridge = core_capture(reference(Toy(alpha=2.)), [.02, .02, 1e-12], .25)
    add('projected_core_requires_energy_capture', not bridge['pass'], core=bridge)
    p = reference(Toy(closing=True)); c = correction(p, [-.1, -.1, -.3], [.1, .1, .3])
    add('closing_complement_rejected', c['eta'] >= 1 and c['correction_upper'] is None, bound=c)
    p = reference(Toy(alpha=10.)); rows, result = cover(p, [.25, .25], [.01, .01], .01, {'maximum_split_nodes_per_reference': 0})
    add('exhausted_budget_retains_unresolved', not result['pass'] and result['split_nodes'] == 0 and np.any(rows[:, 10] == -2), cover=result)
    R, core, h = np.array([.11, .17]), np.array([.02, .03]), .25
    regions = strips(R, core, h)
    volume = sum(float(np.prod(b-a)) for a, b in regions)+float(8*np.prod(core)*h)
    exact = float(8*np.prod(R)*h)
    disjoint = all(np.any(np.minimum(b, d) <= np.maximum(a, c)) for i, (a, b) in enumerate(regions) for c, d in regions[i+1:])
    add('four_strip_partition', abs(volume-exact) < 1e-15 and disjoint, reconstructed_volume=volume, exact_volume=exact, disjoint_interiors=disjoint)
    result = {'plan_sha256': sha(ROOT/'PLAN.json'), 'source_hashes': {n: sha(ROOT/n) for n in ['inventory.py', 'controls.py']},
              'controls': records, 'all_controls_pass': all(r['pass'] for r in records)}
    (ROOT/'CONTROLS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for r in records:
        print(r['name'], r['pass'])
    return 0 if result['all_controls_pass'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
