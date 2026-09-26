"""Fixed synthetic corner repair and seam-budget diagnostics.

Reads hash-bound local text/JSON only. No imports of repository models,
Hamiltonians, production APIs, network or subprocess. Writes a fresh result
directory; failures preserve their result. Analytic proofs are in DERIVATION.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
G = np.array([[0., -1.], [1., 0.]])
I = np.eye(2)


def digest(b):
    return hashlib.sha256(b).hexdigest()


def rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def profile(u):
    return 10*u**3-15*u**4+6*u**5


def profile_d(u):
    return 30*u*u*(1-u)**2


def profile_dd(u):
    return 60*u*(1-u)*(1-2*u)


def principal_defect(a, b, tol, margin):
    for x in (a, b):
        if np.linalg.norm(x.T@x-I, 2) > tol:
            raise ValueError('nonisometry')
        if np.linalg.det(x) <= 0:
            raise ValueError('orientation')
    d = a.T@b
    eta = float(np.linalg.norm(a-b, 2))
    if eta >= 2-margin:
        raise ValueError('branch_cut')
    return float(np.arctan2(d[1, 0], d[0, 0])), eta


def run(out):
    out.mkdir(parents=True, exist_ok=False)
    pb = (HERE/'PLAN.json').read_bytes()
    plan = json.loads(pb)
    for p, expected in plan['sources'].items():
        if digest((ROOT/p).read_bytes()) != expected:
            raise ValueError('source binding: '+p)
    upstream = json.loads((HERE/'UPSTREAM.json').read_text())
    deltas = [0., *upstream['reference_angles'], *plan['additional_angles']]
    tol, margin, length = plan['tolerance'], plan['branch_margin'], plan['length_x']
    checks, repairs, covariant = [], [], []

    def check(name, ok, **ev):
        row = dict(name=name, passed=bool(ok), **ev)
        checks.append(row)
        print(('PASS ' if row['passed'] else 'FAIL ')+name, flush=True)

    check('profile_endpoint_values', profile(0.) == 0 and profile(1.) == 1)
    check('profile_endpoint_jets', all(v == 0 for v in [profile_d(0.), profile_d(1.), profile_dd(0.), profile_dd(1.)]))
    check('profile_analytic_derivative_max', profile_d(.5) == 15/8)
    ucrit = (3-np.sqrt(3))/6
    check('profile_second_derivative_extremum', abs(profile_dd(ucrit)-10*np.sqrt(3)/3) < tol)
    nodes, weights = np.polynomial.legendre.leggauss(plan['quadrature_order'])
    integral = float(sum(w*profile_d((x+1)/2)/2 for x, w in zip(nodes, weights)))
    check('profile_derivative_integral', abs(integral-1) < tol, value=integral)

    j1b, j1t, j20 = rot(.3), rot(-.2), rot(.4)
    b = j1t@j20
    for idx, desired in enumerate(deltas):
        beta0, beta1 = .4, -.1-desired
        a = rot(beta1)@j1b
        delta, eta = principal_defect(a, b, tol, margin)
        repaired = rot(beta1)@rot(delta)@j1b
        closure = float(np.linalg.norm(repaired-b, 2))
        chord = 2*np.sin(abs(delta)/2)
        check(f'principal_angle_{idx}', abs(delta-desired) < tol, angle=delta)
        check(f'chord_identity_{idx}', abs(eta-chord) < tol)
        check(f'exact_corner_repair_{idx}', closure < tol, residual=closure)
        distances, costs, identity_residuals, gauge_residuals = [], [], [], []
        for u in plan['edge_sites']:
            x = length*u
            chi, chix = profile(u), profile_d(u)/length
            beta = beta0+(beta1-beta0)*chi
            beta_d = (beta1-beta0)*chix
            o, q = rot(beta), rot(delta*chi)
            op, qp = beta_d*G@o, delta*chix*G@q
            a0, a1 = .2+.1*x, -.3+.05*x
            dj = op+a1*G@o-o@(a0*G)
            dt = op@q+o@qp+a1*G@o@q-o@q@(a0*G)
            rhs = dj@q+o@qp
            identity_residuals.append(float(np.linalg.norm(dt-rhs, 2)))
            costs.append(float(np.linalg.norm(dt, 2)-np.linalg.norm(dj, 2)-abs(delta*chix)))
            distances.append(float(np.linalg.norm(o@q-o, 2)))
            # Independent endpoint-frame rotations transform both connection and map.
            gamma0, gamma1 = .3*x*x, -.2*np.cos(x)
            gamma0_d, gamma1_d = .6*x, .2*np.sin(x)
            og = rot(-gamma1)@o@q@rot(gamma0)
            ogp = (beta_d+delta*chix+gamma0_d-gamma1_d)*G@og
            dg = ogp+(a1+gamma1_d)*G@og-og@((a0+gamma0_d)*G)
            gauge_residuals.append(float(np.linalg.norm(dg-rot(-gamma1)@dt@rot(gamma0), 2)))
        check(f'uniform_correction_screen_{idx}', max(distances) <= eta+tol and abs(distances[-1]-eta) < tol)
        check(f'covariant_product_rule_{idx}', max(identity_residuals) < tol)
        check(f'connection_cost_screen_{idx}', max(costs) < tol)
        check(f'endpoint_gauge_covariance_{idx}', max(gauge_residuals) < tol)
        repairs.append(dict(delta=delta, eta=eta, closure_residual=closure,
                            correction_sup_bound=eta, added_connection_sup_bound=15*abs(delta)/(8*length),
                            added_connection_integral_bound=abs(delta), sampled_distances=distances))
        covariant.append(dict(max_identity_residual=max(identity_residuals), max_budget_excess=max(costs),
                              max_gauge_residual=max(gauge_residuals)))

    bad = [('reflection', np.diag([1., -1.]), I, 'orientation'),
           ('nonisometry', np.diag([2., 1.]), I, 'nonisometry'),
           ('antipodal', I, rot(np.pi), 'branch_cut')]
    for name, a, b, wanted in bad:
        reason = None
        try:
            principal_defect(a, b, tol, margin)
        except ValueError as exc:
            reason = str(exc)
        check('refuse_'+name, reason == wanted, reason=reason)

    # Direct differential identity with nonzero curvature and seam connection defect.
    # a_x=s*y, a_y=t*x: phi=beta+t*x*Ly, f=t-s, seam=beta'+s*Ly.
    ly, s, t = plan['length_y'], .7, -.2
    delta = upstream['reference_angles'][0]
    strip = []
    for u in plan['edge_sites']:
        x = length*u
        beta_d = .4*np.cos(x)
        chi_d = profile_d(u)/length
        derivative = beta_d+t*ly+delta*chi_d
        via_flux = (t-s)*ly+(beta_d+s*ly)+delta*chi_d
        strip.append(abs(derivative-via_flux))
    check('strip_flux_plus_covariant_seam', max(strip) < tol, residual=max(strip))
    h = length/8
    local_steps = []
    for u in (0., .25, .5, .75):
        x = u*length
        phi = lambda z: .4*np.sin(z)+t*z*ly+delta*profile(z/length)
        bound = (abs(t-s)*ly+.4+abs(s)*ly)*h+abs(delta)*(profile((x+h)/length)-profile(x/length))
        local_steps.append(dict(x=x, actual=abs(phi(x+h)-phi(x)), bound=bound))
    check('strip_variation_screen', all(r['actual'] <= r['bound']+tol for r in local_steps))

    # A complete explicitly glued constant-plane example, not a production Euler API call.
    twists = []
    for m in plan['twists']:
        rate = 2*np.pi*m/length
        endpoint_error = float(np.linalg.norm(rot(rate*length)-I, 2))
        compatibility = []
        singular_errors = []
        for u in plan['edge_sites']:
            x = length*u
            transition = rot(rate*x)
            top_connection = -rate*G
            compatibility.append(float(np.linalg.norm(rate*G@transition+top_connection@transition, 2)))
            singular_errors.append(float(np.max(np.abs(np.linalg.svd(transition, compute_uv=False)-1))))
        # Integral Omega_12/(2pi), with Omega=G*rate/Ly dx wedge dy.
        euler = -rate*length/(2*np.pi)
        raw_backward_winding = rate*length/(2*np.pi)
        check(f'twist_corner_{m}', endpoint_error < tol)
        check(f'twist_all_link_singular_values_{m}', max(singular_errors) < tol)
        check(f'twist_compatible_connection_{m}', max(compatibility) < tol)
        check(f'twist_flux_and_backward_sign_{m}', abs(euler+m) < tol and abs(raw_backward_winding-m) < tol)
        twists.append(dict(m=m, corner_residual=endpoint_error, max_singular_error=max(singular_errors),
                           max_connection_residual=max(compatibility), analytic_euler=euler,
                           analytic_raw_backward_winding=raw_backward_winding))

    alias_m = plan['alias_intervals']
    sampled_distance = max(float(np.linalg.norm(rot(2*np.pi*alias_m*j/alias_m)-I, 2)) for j in range(alias_m+1))
    midpoint_distance = float(np.linalg.norm(rot(2*np.pi*alias_m*(.5/alias_m))-I, 2))
    check('sampled_reference_distance_can_alias', sampled_distance < tol and abs(midpoint_distance-2) < tol,
          sampled_distance=sampled_distance, midpoint_distance=midpoint_distance, analytic_winding=alias_m)
    # A known relative loop avoiding -I has a periodic principal log and zero relative winding.
    amp = plan['relative_loop_amplitude']
    grid = np.linspace(0., 1., 17)
    principal = [float(np.arctan2(rot(amp*np.sin(2*np.pi*u))[1, 0], rot(amp*np.sin(2*np.pi*u))[0, 0])) for u in grid]
    check('relative_principal_log_periodic', abs(principal[-1]-principal[0]) < tol and max(map(abs, principal)) <= amp+tol)
    check('relative_loop_uniform_chord_bound', 2*np.sin(amp/2) < 2 and amp < np.pi)

    result = dict(schema='twistronics_boundary_repair_v1', passed=all(c['passed'] for c in checks),
                  source_sha256=digest(Path(__file__).read_bytes()), plan_sha256=digest(pb),
                  environment=dict(python=platform.python_version(), numpy=np.__version__),
                  checks=checks, repairs=repairs, covariant_checks=covariant,
                  strip_steps=local_steps, twists=twists, alias=dict(intervals=alias_m,
                  sampled_distance=sampled_distance, midpoint_distance=midpoint_distance), limits=plan['limits'])
    (out/'RESULTS.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(f"{sum(c['passed'] for c in checks)}/{len(checks)} checks; overall={result['passed']}")
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    raise SystemExit(run(p.parse_args().output))
