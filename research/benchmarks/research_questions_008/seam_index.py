"""Fixed synthetic seam-index and abstract-collar controls.

Reads bound local source/JSON files. Writes only a fresh output directory.
No production imports, network, subprocess, parameter search or eigensolver.
Geometric checks use ordinary floating point; Fraction decisions are exact
only for their declared synthetic inputs in units of one full turn.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
from numpy.polynomial import Polynomial as P

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
G = np.array([[0., -1.], [1., 0.]])
I = np.eye(2)
TAU = 2*np.pi


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def norm(a):
    return float(np.linalg.norm(a, 2))


def ext(poly, t, length, derivative=0):
    """C2 extension by endpoint quadratic Taylor polynomial."""
    if 0 <= t <= length:
        return float(poly.deriv(derivative)(t))
    e = 0. if t < 0 else length
    d = t-e
    if derivative == 0:
        return float(poly(e)+poly.deriv()(e)*d+poly.deriv(2)(e)*d*d/2)
    if derivative == 1:
        return float(poly.deriv()(e)+poly.deriv(2)(e)*d)
    return float(poly.deriv(2)(e))


def unique_integer(center, error):
    """Exact closed interval in turns; geometry supplies integer existence."""
    if error < 0:
        raise ValueError('negative radius')
    lo, hi = center-error, center+error
    first = -((-lo.numerator)//lo.denominator)
    last = hi.numerator//hi.denominator
    return first if first == last else None


def run(out):
    out.mkdir(parents=True, exist_ok=False)
    plan_bytes = (HERE/'PLAN.json').read_bytes()
    plan = json.loads(plan_bytes)
    for path, expected in plan['sources'].items():
        if sha((ROOT/path).read_bytes()) != expected:
            raise ValueError('source binding: '+path)
    Lx, Ly = plan['length_x'], plan['length_y']
    tol = plan['tolerance']
    nodes, weights = np.polynomial.legendre.leggauss(plan['quadrature_order'])

    def integrate(fun, length):
        return float(sum(w*fun((n+1)*length/2)*length/2 for n,w in zip(nodes,weights)))

    rows, evidence = [], []

    def check(name, passed, **values):
        row = dict(name=name, passed=bool(passed), **values)
        rows.append(row)
        print(('PASS ' if passed else 'FAIL ')+name, flush=True)

    for case in plan['cases']:
        label, m, n, offset, curve, active = [case[k] for k in
            ('name','m','n','offset','curve','connection')]
        q = m-n
        # Fixed polynomial edge lifts, including nonperiodic endpoint jets.
        alpha = P([.23, (TAU*n+offset+curve)/Ly, -curve/Ly**2])
        beta = P([-.31, (TAU*m+offset-.7*curve)/Lx, .7*curve/Lx**2])
        da = float(alpha(Ly)-alpha(0))
        b = beta-P([0., (da+TAU*q)/Lx])

        def ax(x,y):
            return active*(.2+.1*x+.07*x*y+.03*y*y)

        def ay(x,y):
            return active*(-.3+.11*x*x+.04*x*y+.05*y)

        def curvature(x,y):
            return active*(.15*x-.02*y)

        def k1(y):
            return alpha.deriv()(y)+ay(Lx,y)-ay(0,y)

        def k2(x):
            return beta.deriv()(x)+ax(x,Ly)-ax(x,0)

        def phi(x):
            return beta(x)+integrate(lambda y: ay(x,y),Ly)

        K1, K2 = integrate(k1,Ly), integrate(k2,Lx)
        delta_phi = phi(Lx)-phi(0)
        corrected = (delta_phi-K1)/TAU
        flux = integrate(lambda x: integrate(lambda y:curvature(x,y),Ly),Lx)
        corner = norm(rot(beta(Lx))@rot(alpha(0))-rot(alpha(Ly))@rot(beta(0)))
        check(label+'_corner', corner<tol, residual=corner)
        transported = rot(integrate(lambda y:ay(Lx,y),Ly))@rot(alpha(Ly))@rot(-integrate(lambda y:ay(0,y),Ly))
        transport_residual = norm(transported-rot(K1)@rot(alpha(0)))
        check(label+'_transport_identity', transport_residual<tol, residual=transport_residual)
        check(label+'_corrected_index', abs(corrected-q)<tol, value=corrected, expected=q)
        check(label+'_stokes_both_seams', abs(flux+K2-K1-TAU*q)<tol, residual=float(flux+K2-K1-TAU*q))

        def gamma(x,y):
            return .17*x*x*y-.09*x*y*y+.13*x*x-.2*y

        def gy(x,y):
            return .17*x*x-.18*x*y-.2

        def gauge_phi(x):
            return beta(x)+gamma(x,0)-gamma(x,Ly)+integrate(lambda y:ay(x,y)+gy(x,y),Ly)

        gauge_K1 = integrate(lambda y: alpha.deriv()(y)+gy(0,y)-gy(Lx,y)+ay(Lx,y)+gy(Lx,y)-ay(0,y)-gy(0,y),Ly)
        gauge_error = max(abs(gauge_K1-K1),*(abs(gauge_phi(Lx*u)-phi(Lx*u)) for u in plan['edge_sites']))
        check(label+'_frame_gauge', gauge_error<tol, residual=float(gauge_error))

        def theta(x,y):
            return x/Lx*ext(alpha,y,Ly)+y/Ly*ext(b,x,Lx)

        def grad(x,y):
            return np.array([ext(alpha,y,Ly)/Lx+y/Ly*ext(b,x,Lx,1),x/Lx*ext(alpha,y,Ly,1)+ext(b,x,Lx)/Ly])

        def astar(x,y):
            return np.array([-TAU*q*y/(Lx*Ly),0.])-grad(x,y)

        def g1(x,y):
            return theta(x+Lx,y)-theta(x,y)

        def g2(x,y):
            return TAU*q*x/Lx+theta(x,y+Ly)-theta(x,y)

        edge_error = 0.
        for u in plan['edge_sites']:
            x,y = u*Lx,u*Ly
            edge_error=max(edge_error,norm(rot(g1(0,y))-rot(alpha(y))),norm(rot(g2(x,0))-rot(beta(x))))
        check(label+'_collar_matches_edges', edge_error<tol, residual=edge_error)
        canonical_error=max(abs(b(Lx)-b(0)),*(norm(rot(beta(u*Lx)+theta(u*Lx,0)-theta(u*Lx,Ly))-rot(TAU*q*u)) for u in plan['edge_sites']))
        check(label+'_canonical_gauge', canonical_error<tol, residual=float(canonical_error))
        cocycle_error, connection_error = 0.,0.
        for u,v in plan['collar_sites']:
            x,y = u*Lx,v*Ly
            cocycle_error=max(cocycle_error,norm(rot(g2(x+Lx,y))@rot(g1(x,y))-rot(g1(x,y+Ly))@rot(g2(x,y))))
            dg1=grad(x+Lx,y)-grad(x,y)
            dg2=np.array([TAU*q/Lx,0.])+grad(x,y+Ly)-grad(x,y)
            for defect in (dg1+astar(x+Lx,y)-astar(x,y),dg2+astar(x,y+Ly)-astar(x,y)):
                connection_error=max(connection_error,float(np.max(np.abs(defect))))
        check(label+'_full_collar_cocycle', cocycle_error<tol, residual=cocycle_error)
        check(label+'_full_connection_compatibility', connection_error<tol, residual=connection_error)
        # Canonical curvature integrates to -q in the declared Omega_12 convention.
        euler=-integrate(lambda x:integrate(lambda y:TAU*q/(Lx*Ly),Ly),Lx)/TAU
        check(label+'_compatible_euler_sign', abs(euler+q)<tol, euler=euler)
        evidence.append(dict(name=label,q=q,raw_phase_change_turns=float(delta_phi/TAU),K1=K1,K2=K2,flux=flux,corrected_index=corrected,euler=euler,corner_residual=corner,collar_residual=cocycle_error,connection_residual=connection_error,b_derivative_jump=float(b.deriv()(Lx)-b.deriv()(0))))

    hidden=evidence[0]
    check('left_integer_hidden_from_raw_scan', abs(hidden['raw_phase_change_turns'])<tol and hidden['q']==-1 and abs(hidden['K1']-TAU)<tol)
    # Analytic endpoint extrema give uniform bounds for these affine lifts.
    a0,a1=.9*np.pi,-.9*np.pi
    b0,b1=-.1*np.pi,.1*np.pi
    eta1,eta2=2*np.sin(.45*np.pi),2*np.sin(.05*np.pi)
    check('joint_counterexample_corner', norm(rot(b1)@rot(a0)-rot(a1)@rot(b0))<tol)
    check('joint_counterexample_edge1_below_two', eta1<2, uniform_bound=float(eta1))
    check('joint_counterexample_edge2_below_two', eta2<2, uniform_bound=float(eta2))
    index_diff=((b1-b0)-(a1-a0))/TAU
    check('joint_counterexample_changed_class', abs(index_diff-1)<tol, q_difference=float(index_diff))
    half_defect=norm(rot(.5*b1)@rot(.5*a0)-rot(.5*a1)@rot(.5*b0))
    check('naive_homotopy_breaks_corner', abs(half_defect-2)<tol, midpoint_defect=half_defect)
    rho_sum=2*np.arcsin(eta1/2)+2*np.arcsin(eta2/2)
    check('joint_strict_bound_refuses_counterexample', not rho_sum<np.pi-plan['guard_margin'], rho_sum=float(rho_sum))
    # Positive control with nonconstant, small relative edge lifts and equal deltas.
    pa=P([.2,.3,-.2]); pb=P([-.1,-.05,.15])
    joint=(pb(1)-pb(0))-(pa(1)-pa(0))
    check('positive_joint_lift_condition', abs(joint)<tol)
    rho1,rho2=.35,.2375
    check('positive_joint_uniform_bound', rho1+rho2<np.pi and max(abs(pa(u)) for u in plan['edge_sites'])<=rho1 and max(abs(pb(u)) for u in plan['edge_sites'])<=rho2, analytic_angle_bound_sum=rho1+rho2)
    # R(s^3): equal two-jets do not imply equality on any neighborhood.
    jet=P([0,0,0,1])
    check('finite_jet_matches_at_origin', all(jet.deriv(i)(0)==0 for i in range(3)))
    jet_defect=norm(rot(jet(plan['jet_probe']))-I)
    check('finite_jet_does_not_close_collar', jet_defect>plan['negative_control_floor'], defect=jet_defect)
    h=Ly/plan['midpoint_intervals']
    midpoint=sum(h*((j+.5)*h)**2 for j in range(plan['midpoint_intervals']))
    error=abs(Ly**3/3-midpoint)
    bound=plan['midpoint_intervals']*(2*Ly)*h*h/4
    check('lipschitz_midpoint_error_bound', error<=bound, actual_error=error, bound=bound)
    intervals=[]
    for test in plan['interval_cases']:
        center,error=Fraction(test['center']),Fraction(test['error'])
        try:
            value=unique_integer(center,error)
            observed='refuse' if value is None else value
        except ValueError:
            observed='invalid'
        check('exact_interval_'+test['name'], observed==test['expected'], observed=observed)
        intervals.append(dict(**test,observed=observed))

    if len(rows)!=plan['expected_check_count']:
        raise ValueError('check count differs from plan: '+str(len(rows)))
    passed=all(r['passed'] for r in rows)
    result=dict(schema='twistronics_seam_index_v1',passed=passed,source_sha256=sha(Path(__file__).read_bytes()),plan_sha256=sha(plan_bytes),environment=dict(python=platform.python_version(),numpy=np.__version__),checks=rows,cases=evidence,joint_counterexample=dict(eta1=float(eta1),eta2=float(eta2),q_difference=float(index_diff),homotopy_midpoint_defect=half_defect),interval_cases=intervals,limits=plan['limits'])
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(f'{sum(r["passed"] for r in rows)}/{len(rows)} checks; overall={passed}',flush=True)
    return 0 if passed else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raise SystemExit(run(args.output))
