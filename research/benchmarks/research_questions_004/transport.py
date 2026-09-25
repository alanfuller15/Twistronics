"""Check an explicit sphere transport bound against retained and exact controls.

Fresh computation is limited to latitude controls, 14 sphere-transport ODEs,
small link identities, and two original archived 24x24 API calls.
"""
import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import tempfile

import numpy as np
import scipy
from scipy.integrate import solve_ivp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def angle(w):
    return float(np.arctan2(w[1, 0], w[0, 0]))


def circular_error(a, b):
    return float(abs(np.angle(np.exp(1j*(a-b)))))


def ribbon_bound(speed, acceleration, intervals):
    h = 2*np.pi/intervals
    delta = acceleration*h*h/8
    if delta >= 1:
        return dict(valid=False, chord_error_bound=float(delta))
    per_link = speed*acceleration*h**3/(12*(1-delta)**2)
    return dict(valid=True, h=float(h), chord_error_bound=float(delta),
                per_link_angle_error=float(per_link), loop_angle_error=float(intervals*per_link))


def analytic_screen(folds, intervals):
    r = ribbon_bound(1., 4., intervals)  # production loops in y
    flux = 4*np.pi**2*folds/intervals
    combined = flux+2*r['loop_angle_error'] if r['valid'] else None
    acute_x = folds*2*np.pi/intervals < np.pi/2
    acute_y = 2*np.pi/intervals < np.pi/2
    return dict(folds=folds, intervals=intervals, ribbon=r,
                continuous_strip_flux_bound=float(flux), combined_step_bound=combined,
                acute_base_links=acute_x, acute_loop_links=acute_y,
                exact_arithmetic_unwrapping_sufficient=bool(r['valid'] and acute_x and acute_y and combined<np.pi),
                calibrated_phase_policy_sufficient=bool(r['valid'] and acute_x and acute_y and combined<np.pi/2))


def sphere_path(x, m):
    def curve(y):
        d = np.array([np.sin(x), np.sin(y), m+np.cos(x)+np.cos(y)])
        dd = np.array([0., np.cos(y), -np.sin(y)])
        r = np.linalg.norm(d)
        n = d/r
        return n, (dd-n*np.dot(n, dd))/r
    return curve


def continuous_transport(curve, ref, rtol, atol):
    n0, _ = curve(-np.pi)
    frame, _ = ref.frame(n0)
    def rhs(t, flattened):
        n, dn = curve(t)
        v = flattened.reshape(3, 2)
        return (-np.outer(n, dn@v)).ravel()
    sol = solve_ivp(rhs, (-np.pi, np.pi), frame.ravel(), method='DOP853',
                    rtol=rtol, atol=atol)
    if not sol.success:
        raise RuntimeError(sol.message)
    end = sol.y[:, -1].reshape(3, 2)
    forward = frame.T@end
    # The archived overlap product is backward transport in endpoint coordinates.
    return dict(backward_phase=-angle(forward), evaluations=sol.nfev,
                orthogonality_error=float(np.linalg.norm(end.T@end-np.eye(2), 2)),
                tangency_error=float(np.linalg.norm(curve(np.pi)[0]@end)))


def rotation_between(a, b):
    v = np.cross(a, b)
    c = np.dot(a, b)
    if c <= -1+1e-12:
        raise ValueError('antipodal normals')
    vx = np.array([[0., -v[2], v[1]], [v[2], 0., -v[0]], [-v[1], v[0], 0.]])
    return np.eye(3)+vx+vx@vx/(1+c)


def run(out):
    out.mkdir(parents=True, exist_ok=False)
    plan = json.loads((HERE/'PLAN.json').read_text())
    for path, expected in plan['sources'].items():
        if sha(ROOT/path) != expected:
            raise RuntimeError('source mismatch: '+path)
    cal = load(HERE.parent/'research_questions_002/calibrate.py', 'calibration002')
    ref = cal.load_reference()
    old = json.loads((HERE.parent/'research_questions_002/RESULTS.json').read_text())
    old3 = json.loads((HERE.parent/'research_questions_003/RESULTS.json').read_text())
    checks, links, latitudes, ode_rows, comparisons, policies = [], [], [], [], [], []
    def check(name, condition, **evidence):
        checks.append(dict(name=name, passed=bool(condition), **evidence))

    screens = [analytic_screen(a, n) for a in plan['folds'] for n in plan['meshes']]
    for s in screens:
        check(f"screen_{s['folds']}_{s['intervals']}",
              s['exact_arithmetic_unwrapping_sufficient']==(s['folds']==1)
              and s['calibrated_phase_policy_sufficient']==(s['folds']==1 and s['intervals']>=48),
              category='analytic_bound_arithmetic')

    # Distinguish the short oriented-normal arc from merely nonsingular overlap.
    for theta in plan['link_angles']:
        a = np.array([0., 0., 1.])
        b = np.array([np.sin(theta), 0., np.cos(theta)])
        fa = ref.frame(a)[0]@ref.rotation(.37)
        fb = ref.frame(b)[0]@ref.rotation(-.81)
        u, sigma, vt = np.linalg.svd(fa.T@fb)
        polar = u@vt
        backward = fa.T@rotation_between(a, b).T@fb
        error = float(np.linalg.norm(polar-backward, 2))
        acute = bool(np.cos(theta)>0)
        links.append(dict(theta=theta,acute=acute,minimum_overlap=float(sigma[-1]),
                          error=error,polar_determinant=float(np.linalg.det(polar))))
        check(f'polar_arc_{theta}', error<1e-12 if acute else error>1.9,
              category='identity_check' if acute else 'hypothesis_counterexample')

    for theta in plan['latitude_angles']:
        def curve(t):
            return (np.array([np.sin(theta)*np.cos(t),np.sin(theta)*np.sin(t),np.cos(theta)]),
                    np.array([-np.sin(theta)*np.sin(t),np.sin(theta)*np.cos(t),0.]))
        expected = -2*np.pi*(1-np.cos(theta))
        ode = continuous_transport(curve, ref, **plan['ode_tolerances'])
        err = circular_error(ode['backward_phase'], expected)
        check(f'latitude_exact_ODE_{theta}', err<plan['numerical_tolerance'],
              category='exact_solution_control',error=err)
        for mesh in plan['latitude_meshes']:
            frames = np.array([ref.frame(curve(t)[0])[0] for t in np.linspace(-np.pi,np.pi,mesh,endpoint=False)])
            w, minimum = ref.loop(frames)
            error = circular_error(angle(w), expected)
            bound = ribbon_bound(float(np.sin(theta)),float(np.sin(theta)),mesh)
            latitudes.append(dict(theta=theta,mesh=mesh,expected_backward_phase=float(expected),
                                  sampled_phase=angle(w),angular_error=error,bound=bound,minimum_overlap=minimum))
            check(f'latitude_bound_{theta}_{mesh}',error<=bound['loop_angle_error']+1e-12,
                  category='exact_solution_control',error=error,bound=bound['loop_angle_error'])

    for m in plan['sphere_masses']:
        for f in plan['scan_fractions']:
            x=2*np.pi*f-np.pi
            ode=continuous_transport(sphere_path(x,m),ref,**plan['ode_tolerances'])
            ode_rows.append(dict(m=m,fraction=f,x=float(x),**ode))
            check(f'ODE_invariants_{m}_{f}',max(ode['orthogonality_error'],ode['tangency_error'])<plan['numerical_tolerance'],
                  category='numerical_diagnostic')
            for mesh in [48,96]:
                case=next(c for c in old['cases'] if c['name']==f'sphere_m{m}_mesh{mesh}')
                index=round(f*mesh)
                archived=case['base_orientation']*case['result']['phases_rad'][index]
                err=circular_error(archived,ode['backward_phase'])
                bound=ribbon_bound(1.,4.,mesh)['loop_angle_error']
                comparisons.append(dict(m=m,mesh=mesh,row=index,x=float(x),archived_canonical_backward_phase=archived,
                                        ODE_backward_phase=ode['backward_phase'],error=err,bound=bound))
                check(f'archived_vs_continuous_{m}_{mesh}_{index}',err<=bound+plan['numerical_tolerance'],
                      category='numerical_diagnostic',error=err,bound=bound)

    with tempfile.TemporaryDirectory(prefix='twistronics_transport_') as temporary:
        prod=cal.load_production(Path(temporary))
        for label,ceiling in [('calibrated',np.pi/2),('default',3*np.pi/4)]:
            policy=prod.Policy(phase_step_max_rad=float(ceiling))
            trace=cal.Trace();model=cal.Model(ref)
            sampler=prod.Sampler(model,U=np.eye(3),policy=policy,ledger=trace,name='mesh24_'+label)
            record=dict(label=label,mesh=24,policy=asdict(policy))
            try:
                _,F=sampler.frame([0.,0.],0,where='orientation')
                sign=float(np.sign(np.dot(np.cross(F[:,0],F[:,1]),model.normal(model.frac_to_k([0.,0.])))))
                value=prod.euler_wilson(sampler,lo=0,nf1=24,nf2=24,sewings=(np.eye(3),np.eye(3)))
                record.update(status='returned',result=value,oriented_euler=-sign*value['euler_estimate'])
            except prod.Rejected as exc:
                record.update(status='rejected',rejection=exc.record)
            record['diagnostics']=trace.summary();policies.append(record)
            expected=(record['status']=='rejected' and record['rejection']['code']=='phase_resolution') if label=='calibrated' else (record['status']=='returned' and abs(record['oriented_euler']-2)<1e-10)
            check('mesh24_'+label,expected,category='production_policy_control')

    for c in old3['nested_alias_production_cases']:
        s=analytic_screen(97,c['mesh'])
        check('retained_alias_refused_'+str(c['mesh']),abs(c['oriented_euler']-2)<1e-10 and not s['exact_arithmetic_unwrapping_sufficient'],
              category='sampling_limit',analytic_euler=194,retained_sampled_euler=c['oriented_euler'])

    result=dict(schema='twistronics_sphere_transport_bound_v1',passed=all(c['passed'] for c in checks),
                source_sha256=sha(__file__),plan_sha256=sha(HERE/'PLAN.json'),
                environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                checks=checks,analytic_screens=screens,link_controls=links,latitude_controls=latitudes,
                continuous_transport=ode_rows,retained_production_comparisons=comparisons,
                fresh_production_policy_cases=policies,limits=plan['limits'])
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for c in checks: print(('PASS ' if c['passed'] else 'FAIL ')+c['name'])
    print(f"{sum(c['passed'] for c in checks)}/{len(checks)} checks; overall={result['passed']}")
    return 0 if result['passed'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(run(parser.parse_args().output))
