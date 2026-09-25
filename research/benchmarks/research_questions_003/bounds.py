"""Bound unsampled variation; replay a nested-grid alias on archived code.

No edits to the retained model, archived production code, or earlier evidence.
Only the explicitly declared synthetic runs and fixed 4x4 witnesses are used.
"""
import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import tempfile

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def projected_representation(model, k, Q):
    """Exact reduction of direct_projection to its nonzero projected rows."""
    x, y = k
    p = model.p
    I, X = np.eye(2), np.array([[0., 1.], [1., 0.]])
    Y, Z = np.array([[0., -1j], [1j, 0.]]), np.diag([1., -1.])
    z = np.array([x+Q/2+1j*y, x+Q/2-1j*y,
                  -x+Q/2+1j*y, -x+Q/2-1j*y])
    C = np.diag(1 / np.sqrt(1 + np.abs(z)**2))
    V = np.vstack([C, -np.diag(z) @ C])
    cf = -1j*p['cpp']*model.eps*np.kron(Z, Z)
    A = np.block([[p['M']*np.kron(I, X)+model.hc, cf],
                  [cf.conj().T, model.delta*np.kron(Z, Y)+model.hf]])
    return A, V


def analytic_constant(parameters, shift):
    """Rational triangle bound; round upward to an integer, not a fitted norm."""
    p = {k: Fraction(str(v)) for k, v in parameters.items()}
    c = Fraction(str(shift))
    eps = -(1+p['poisson'])*p['strain']/2
    alpha = abs(p['M']) + abs(-2*p['W3']-c) + abs(p['J'])/2
    beta = abs(p['Mf']*eps) + abs(-2*(p['U1']+6*p['U2'])-c) + abs(p['U1'])/2
    cross = abs(p['cpp']*eps)
    rational_bound = max(alpha, beta) + cross
    R = math.ceil(rational_bound)
    return dict(shift_meV=float(c), alpha_meV=float(alpha), beta_meV=float(beta),
                cross_meV=float(cross), rational_R=str(rational_bound),
                unrounded_R_meV=float(rational_bound), R_meV=R,
                L_K_meV=2*R, L_Q_meV=R,
                rule='R=ceil(max(alpha,beta)+abs(cpp*eps)); L_K=2R, L_Q=R')


def gap_and_projector(h):
    eigenvalues, vectors = np.linalg.eigh(h)
    frame = vectors[:, 1:3]  # fixed middle pair, zero-based indices [1, 2]
    gap = min(eigenvalues[1]-eigenvalues[0], eigenvalues[3]-eigenvalues[2])
    residual = np.linalg.norm(h@vectors-vectors@np.diag(eigenvalues), 2)
    return float(gap), frame@frame.conj().T, eigenvalues, float(residual)


def run(out):
    out.mkdir(parents=True, exist_ok=False)
    plan = json.loads((HERE/'PLAN.json').read_text())
    for path, expected in plan['sources'].items():
        if sha(ROOT/path) != expected:
            raise RuntimeError('source identity mismatch: '+path)
    calibration = load(HERE.parent/'research_questions_002/calibrate.py', 'calibration002')
    reference = calibration.load_reference()
    source = load(HERE.parent/'vafek_2025/model.py', 'retained_vafek_model')
    checks, aliases, screens = [], [], []

    def check(name, condition, **evidence):
        checks.append(dict(name=name, passed=bool(condition), **evidence))

    # These are full-cell diameter bounds in radians, not sampled derivatives.
    for folds in plan['reference_folds']:
        for mesh in plan['meshes']:
            eta = 2*np.pi*(folds+1)/mesh
            bounded = eta < 1
            screens.append(dict(folds=folds, mesh=mesh, analytic_euler=2*folds,
                                normal_and_projector_variation_bound=float(eta),
                                H_variation_bound=float(2*eta),
                                certified_local_chart=bounded,
                                overlap_lower_bound=float(np.sqrt(1-eta*eta)) if bounded else None,
                                scope='Each cell relative to any of its corners; not an Euler certificate'))
            check(f'variation_screen_fold{folds}_mesh{mesh}', bounded == (folds == 1),
                  category='analytic_screen_arithmetic', eta=float(eta), local_chart=bounded)

    with tempfile.TemporaryDirectory(prefix='twistronics_bounds_') as temporary:
        production = calibration.load_production(Path(temporary))
        policy = production.Policy(phase_step_max_rad=float(np.pi/2))
        for mesh in plan['meshes']:
            fast = calibration.Model(reference, folds=97)
            slow = calibration.Model(reference, folds=1)
            maximum = 0.
            for f1 in np.linspace(0., 1., mesh+1):
                for f2 in np.linspace(0., 1., mesh+1):
                    k = fast.frac_to_k([f1, f2])
                    maximum = max(maximum, float(np.max(np.abs(fast.H(k)-slow.H(k)))))
            trace = calibration.Trace()
            sampler = production.Sampler(fast, U=np.eye(3), policy=policy,
                                         ledger=trace, name=f'alias97_mesh{mesh}')
            record = dict(mesh=mesh, folds=97, analytic_euler=194,
                          maximum_sampled_H_difference=maximum)
            try:
                _, frame = sampler.frame([0., 0.], 0, where='adapter:orientation')
                orientation = float(np.sign(np.dot(np.cross(frame[:, 0], frame[:, 1]),
                                                   fast.normal(fast.frac_to_k([0., 0.])))))
                value = production.euler_wilson(sampler, lo=0, nf1=mesh, nf2=mesh,
                                               sewings=(np.eye(3), np.eye(3)))
                record.update(status='returned', result=value,
                              fibre_orientation_at_origin=orientation,
                              oriented_euler=-orientation*value['euler_estimate'])
            except production.Rejected as exc:
                record.update(status='rejected', rejection=exc.record)
            record['diagnostics'] = trace.summary()
            aliases.append(record)
            check(f'nested_alias_grid_identity_{mesh}', maximum < 1e-10,
                  category='sampling_limit', maximum=maximum)
            check(f'nested_alias_false_acceptance_{mesh}', record['status'] == 'returned'
                  and abs(record.get('oriented_euler', 999)-2) < 1e-10,
                  category='sampling_limit', analytic_euler=194,
                  sampled_euler=record.get('oriented_euler'),
                  interpretation='Expected wrong classification by sampled guards; new variation screen refuses certification')

    model = source.Model()
    constant = analytic_constant(model.p, plan['scalar_shift_meV'])
    witnesses = []
    directions = [np.array(v, dtype=float)/np.linalg.norm(v) for v in plan['directions']]
    Q = plan['Q']
    for k in plan['centres_K']:
        A, V = projected_representation(model, k, Q)
        h = model.direct_projection(k, Q)
        assembly_error = float(np.linalg.norm(h-V.conj().T@A@V, 2))
        isometry_error = float(np.linalg.norm(V.conj().T@V-np.eye(4), 2))
        actual_norm = float(np.linalg.norm(A-constant['shift_meV']*np.eye(8), 2))
        check(f'projected_assembly_{k}', max(assembly_error, isometry_error) < 1e-10
              and actual_norm <= constant['R_meV'], category='implementation_check',
              assembly_error=assembly_error, isometry_error=isometry_error,
              measured_shifted_A_norm=actual_norm, analytic_R=constant['R_meV'])
        g0, P0, eigenvalues, residual = gap_and_projector(h)
        for radius in plan['radii_K']:
            epsilon = constant['L_K_meV']*radius
            gap_lower = g0-2*epsilon
            projector_bound = min(1., np.sqrt(2)*epsilon/(g0-epsilon)) if epsilon < g0 else 1.
            neighbours = []
            for direction in directions:
                destination = np.asarray(k)+radius*direction
                hp = model.direct_projection(destination, Q)
                gp, Pp, _, _ = gap_and_projector(hp)
                neighbours.append(dict(K=destination.tolist(), gap_meV=gp,
                                       H_difference=float(np.linalg.norm(hp-h, 2)),
                                       projector_difference=float(np.linalg.norm(Pp-P0, 2))))
            record = dict(centre_K=k, Q=Q, radius_K=radius, centre_eigenvalues_meV=eigenvalues.tolist(),
                          centre_gap_meV=g0, centre_eigendecomposition_residual=residual,
                          uniform_H_difference_bound_meV=epsilon,
                          uniform_gap_lower_bound_meV=gap_lower,
                          uniform_projector_difference_bound=float(projector_bound),
                          ambient_projector_difference_bound=float(min(1., projector_bound+2*radius)),
                          isolation_screen='positive_bound' if gap_lower > 0 else 'not_certified',
                          numerical_witnesses=neighbours)
            witnesses.append(record)
            check(f'local_model_bound_{k}_{radius}',
                  all(v['H_difference'] <= epsilon+1e-10 and v['gap_meV'] >= gap_lower-1e-10
                      and v['projector_difference'] <= projector_bound+1e-10 for v in neighbours),
                  category='implementation_check', gap_lower=gap_lower,
                  note='Finite witnesses check implementation only; uniform statement follows from DERIVATION.md')
    check('small_cells_isolated', all(w['isolation_screen']=='positive_bound' for w in witnesses if w['radius_K']==.001),
          category='declared_screen_outcome')
    check('large_cells_not_certified', all(w['isolation_screen']=='not_certified' for w in witnesses if w['radius_K']==.1),
          category='declared_screen_outcome', interpretation='Failure of this sufficient bound does not prove gap closure')

    result = dict(schema='twistronics_unsampled_variation_v1', passed=all(c['passed'] for c in checks),
                  source_sha256=sha(__file__), plan_sha256=sha(HERE/'PLAN.json'),
                  environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                  policy=asdict(policy), checks=checks, reference_screens=screens,
                  nested_alias_production_cases=aliases, projected_model_parameters=model.p,
                  projected_model_constant=constant, projected_model_cells=witnesses,
                  limits=plan['limits'])
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    for c in checks:
        print(('PASS ' if c['passed'] else 'FAIL ')+c['name'])
    print(f"{sum(c['passed'] for c in checks)}/{len(checks)} checks; overall={result['passed']}")
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.output))
