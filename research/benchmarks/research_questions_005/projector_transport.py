"""Fixed controls for a general polar/Kato bound and affine-spinor constants.

No physical parameter sweep, production API run, source mutation or network.
The mathematical statements are in DERIVATION.md; ODEs are diagnostics only.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.linalg import expm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def adj(a):
    return a.conj().T


def polar(a):
    u, s, vh = np.linalg.svd(a)
    return u@vh, float(s[-1])


def link_bound(p, q, h):
    d = p*p*h*h/2
    return dict(p=p, q=q, h=h, d=d, valid=bool(d<1),
                overlap_lower=1-d if d<1 else None,
                error_bound=p*(q+p*p)*h**3/(6*(1-d)) if d<1 else None)


def screen(a, n):
    h = 2*np.pi/n
    y = link_bound(1., 10., float(h))
    x_d = a*a*h*h/2
    e = n*y['error_bound']
    flux = 2*a*2*np.pi*h
    value = flux+2*e
    return dict(fold=a, intervals=n, loop_error=e, strip_flux=flux,
                combined_step_bound=value, base_d=float(x_d), loop_d=y['d'],
                overlap_floor_sufficient=bool(x_d<=.5 and y['d']<=.5),
                unwrap=bool(x_d<1 and y['valid'] and value<np.pi),
                calibrated_policy=bool(x_d<1 and y['valid'] and value<np.pi/2))


def spinor(z, u):
    w = np.array([1., -z], dtype=complex)
    dw = np.array([0., -u], dtype=complex)
    r = np.sqrt(1+abs(z)**2)
    c = float(np.real(np.conj(z)*u))
    a = abs(u)**2
    v = w/r
    dv = dw/r-w*c/r**3
    ddv = -2*dw*c/r**3-w*a/r**3+3*w*c*c/r**5
    return v, dv, ddv


def spinor_exact_norm2(z, u):
    if abs(u)==0:
        return 0.
    zp = z*np.conj(u)/abs(u)
    C = 1+zp.imag**2
    s = zp.real
    return float(abs(u)**4*C*(C+4*s*s)/(C+s*s)**4)


def basis_derivatives(k, Q, direction, dq):
    x,y = k
    dx,dy = direction
    zs = [x+Q/2+1j*y, x+Q/2-1j*y, -x+Q/2+1j*y, -x+Q/2-1j*y]
    us = [dx+dq/2+1j*dy, dx+dq/2-1j*dy, -dx+dq/2+1j*dy, -dx+dq/2-1j*dy]
    mats = [np.zeros((8,4),complex) for _ in range(3)]
    for j,(z,u) in enumerate(zip(zs,us)):
        for mat,value in zip(mats,spinor(z,u)):
            mat[[j,j+4],j] = value
    return mats


def generator(dim, terms):
    g = np.zeros((dim,dim))
    for i,j,v in terms:
        g[j,i] += v
        g[i,j] -= v
    return g


def moving_plane(dim, rank, complex_case=False):
    at = [(0,2,.8)] if dim==4 else [(0,3,.8),(2,4,.5)]
    bt = [(1,2,.6),(0,3,.4)] if dim==4 else [(1,3,.6),(2,5,.4)]
    A,B = generator(dim,at), generator(dim,bt)
    W = np.diag(np.exp(1j*np.arange(dim)*.31)) if complex_case else np.eye(dim)
    F0 = np.eye(dim)[:,:rank]
    def curve(t):
        ea = expm(t*A)
        R = ea@expm(t*B)
        F = W@R@F0
        C = W@(A+ea@B@ea.T)@adj(W)
        P = F@adj(F)
        D = C@P-P@C
        return P,D,F
    return curve,dict(dim=dim,rank=rank,A_terms=at,B_terms=bt,
                      complex_fixed_phases=complex_case,p=1.4,q=4.88)


def compare_link(curve, start, h, rtol, atol):
    P0,_,F0 = curve(start)
    _,_,F1 = curve(start+h)
    def rhs(t,y):
        P,D,_ = curve(t)
        return ((D@P-P@D)@y.reshape(F0.shape)).ravel()
    sol = solve_ivp(rhs,(start,start+h),F0.ravel(),method='DOP853',rtol=rtol,atol=atol)
    if not sol.success:
        raise RuntimeError(sol.message)
    Y = sol.y[:,-1].reshape(F0.shape)
    exact = adj(Y)@F1
    sampled,minimum = polar(adj(F0)@F1)
    A = adj(F0)@Y
    k_measured = float(np.linalg.norm((A-adj(A))/2,2))
    error = float(np.linalg.norm(sampled-exact,2))
    endpointP = curve(start+h)[0]
    invariant = float(max(np.linalg.norm(adj(Y)@Y-np.eye(Y.shape[1]),2),
                          np.linalg.norm(endpointP@Y-Y,2)))
    angle_error = float(abs(np.arctan2((sampled@adj(exact))[1,0],(sampled@adj(exact))[0,0]))) if not np.iscomplexobj(F0) else None
    # Independent endpoint gauges, including a reflection in the real case.
    r = F0.shape[1]
    G0 = np.diag(np.exp(.19j*np.arange(1,r+1))) if np.iscomplexobj(F0) else np.diag([1.,-1.])
    G1 = np.diag(np.exp(-.47j*np.arange(1,r+1))) if np.iscomplexobj(F0) else np.array([[.8,-.6],[.6,.8]])
    gauged = polar(adj(F0@G0)@(F1@G1))[0]
    covariance = float(np.linalg.norm(gauged-adj(G0)@sampled@G1,2))
    return dict(start=start,h=h,operator_error=error,angle_error=angle_error,
                minimum_overlap=minimum,skew_overlap_norm=k_measured,
                ODE_invariant_error=invariant,ODE_evaluations=sol.nfev,
                endpoint_gauge_covariance_error=covariance)


def run(out):
    out.mkdir(parents=True,exist_ok=False)
    plan = json.loads((HERE/'PLAN.json').read_text())
    for path,expected in plan['sources'].items():
        if sha(ROOT/path)!=expected:
            raise RuntimeError('source mismatch: '+path)
    checks=[]
    def check(name,passed,**evidence):
        checks.append(dict(name=name,passed=bool(passed),**evidence))
    spins=[]
    for xy in plan['spinor_z']:
        z=complex(*xy)
        for uv in plan['spinor_u']:
            u=complex(*uv)
            _,dv,ddv=spinor(z,u)
            actual=float(np.vdot(ddv,ddv).real)
            exact=spinor_exact_norm2(z,u)
            row=dict(z=xy,u=uv,norm_first=float(np.linalg.norm(dv)),norm_second_squared=actual,
                     exact_norm_second_squared=exact,upper_second_squared=abs(u)**4)
            spins.append(row)
            check('spinor_'+str(xy)+'_'+str(uv),abs(actual-exact)<1e-12 and actual<=abs(u)**4+1e-12,
                  category='analytic_identity_witness')
    check('spinor_bound_attained',all(abs(s['norm_second_squared']-s['upper_second_squared'])<1e-12 for s in spins if s['z']==[0.,0.]),category='sharpness_control')

    bounds3=load(HERE.parent/'research_questions_003/bounds.py','bound003')
    model=load(HERE.parent/'vafek_2025/model.py','vafek').Model()
    model_rows=[]
    for k in plan['model_centres']:
        for direction,dq in [(d,0.) for d in plan['K_directions']]+[([0.,0.],1.)]:
            Q=plan['model_Q']
            A,_=bounds3.projected_representation(model,k,Q)
            V,D,DD=basis_derivatives(k,Q,direction,dq)
            Ac=A-plan['scalar_shift']*np.eye(8)
            H=adj(V)@A@V
            H1=adj(D)@Ac@V+adj(V)@Ac@D
            H2=adj(DD)@Ac@V+2*adj(D)@Ac@D+adj(V)@Ac@DD
            step=plan['finite_difference_step']
            dest=np.array(direction)*step
            hp=model.direct_projection(np.array(k)+dest,Q+dq*step)
            hm=model.direct_projection(np.array(k)-dest,Q-dq*step)
            fd1=(hp-hm)/(2*step); fd2=(hp-2*model.direct_projection(k,Q)+hm)/step**2
            err1=float(np.linalg.norm(H1-fd1,2));err2=float(np.linalg.norm(H2-fd2,2))
            L,M=(94.,188.) if dq==0 else (47.,47.)
            row=dict(K=k,Q=Q,direction=direction,dQ=dq,H_first_norm=float(np.linalg.norm(H1,2)),
                     H_second_norm=float(np.linalg.norm(H2,2)),L=L,M=M,
                     assembly_error=float(np.linalg.norm(H-model.direct_projection(k,Q),2)),
                     finite_difference_first_error=err1,finite_difference_second_error=err2)
            model_rows.append(row)
            check('H_derivatives_'+str(k)+'_'+str(direction)+'_'+str(dq),
                  row['assembly_error']<1e-10 and row['H_first_norm']<=L+1e-10 and row['H_second_norm']<=M+1e-10
                  and err1<plan['fd_tolerance'] and err2<plan['fd_tolerance'],category='fixed_model_diagnostic')

    links=[];definitions=[]
    for dim,rank,complex_case,starts in [(4,2,False,plan['real_starts']),(6,3,True,plan['complex_starts'])]:
        curve,spec=moving_plane(dim,rank,complex_case)
        definitions.append(spec)
        for start in starts:
            for h in plan['edge_lengths']:
                row=compare_link(curve,start,h,**plan['ode_tolerances'])
                b=link_bound(spec['p'],spec['q'],h)
                row.update(dim=dim,rank=rank,complex_case=complex_case,bound=b)
                links.append(row)
                tol=plan['ODE_diagnostic_tolerance']
                check(f'Kato_link_{dim}_{start}_{h}',row['operator_error']<=b['error_bound']+tol
                      and (row['angle_error'] is None or row['angle_error']<=b['error_bound']+tol)
                      and row['skew_overlap_norm']<=spec['p']*(spec['q']+spec['p']**2)*h**3/6+tol
                      and row['minimum_overlap']>=b['overlap_lower']-tol and row['ODE_invariant_error']<tol,
                      category='numerical_transport_diagnostic')
                check(f'gauge_covariance_{dim}_{start}_{h}',row['endpoint_gauge_covariance_error']<1e-12,
                      category='endpoint_gauge_control')
    check('nonzero_general_link_error',max(r['operator_error'] for r in links)>1e-5,
          category='nontriviality_control')

    geodesics=[]
    G=generator(4,[(0,2,.7),(1,3,.4)]);F0=np.eye(4)[:,:2]
    for h in plan['geodesic_lengths']:
        F1=expm(h*G)@F0
        U,s=polar(F0.T@F1)
        row=dict(h=h,minimum_overlap=s,operator_error=float(np.linalg.norm(U-np.eye(2),2)))
        geodesics.append(row)
        check('exact_geodesic_'+str(h),row['operator_error']<1e-12,category='exact_transport_control')
    cut_h=np.pi/(2*.7)
    cut=link_bound(.7,.98,float(cut_h))
    cut['measured_minimum_overlap']=polar(F0.T@expm(cut_h*G)@F0)[1]
    check('orthogonal_endpoint_refused',not cut['valid'] and cut['measured_minimum_overlap']<1e-12,
          category='hypothesis_boundary_control')

    screens=[screen(a,n) for a in plan['folds'] for n in plan['screen_meshes']]
    for s in screens:
        check(f"generic_screen_{s['fold']}_{s['intervals']}",s['unwrap']==(s['fold']==1 and s['intervals']>=48)
              and s['calibrated_policy']==(s['fold']==1 and s['intervals']>=96),category='analytic_bound_arithmetic')
    old4=json.loads((HERE.parent/'research_questions_004/RESULTS.json').read_text())
    for n in [48,96]:
        s=screen(1,n)
        observed=max(r['error'] for r in old4['retained_production_comparisons'] if r['mesh']==n)
        check('retained_loop_error_'+str(n),observed<=s['loop_error'],category='retained_evidence_comparison',
              observed_max=observed,new_general_bound=s['loop_error'])

    old3=json.loads((HERE.parent/'research_questions_003/RESULTS.json').read_text())
    conditional=[]
    for c in old3['projected_model_cells']:
        if c['radius_K']!=.001: continue
        g=c['uniform_gap_lower_bound_meV'];p1=np.sqrt(2)*94/g
        oldp2=np.sqrt(2)*470/g+12*94**2/g**2
        newp2=np.sqrt(2)*188/g+12*94**2/g**2
        row=dict(centre_K=c['centre_K'],assumed_gap=g,p1=float(p1),old_p2=float(oldp2),new_p2=float(newp2),
                 relative_p2_reduction=float((oldp2-newp2)/oldp2),embedded_K_p2=float(newp2+4*p1+4),
                 status='conditional_on_uncertified_float_gap_not_a_certificate')
        conditional.append(row)
        check('conditional_projector_bound_'+str(c['centre_K']),newp2<oldp2,category='conditional_arithmetic')

    result=dict(schema='twistronics_general_projector_transport_v1',passed=all(c['passed'] for c in checks),
                source_sha256=sha(Path(__file__)),plan_sha256=sha(HERE/'PLAN.json'),
                environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                checks=checks,spinors=spins,model_derivatives=model_rows,path_definitions=definitions,
                general_links=links,exact_geodesics=geodesics,orthogonal_endpoint=cut,
                generic_sphere_screens=screens,conditional_projector_bounds=conditional,limits=plan['limits'])
    for c in checks: print(('PASS ' if c['passed'] else 'FAIL ')+c['name'])
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(f"{sum(c['passed'] for c in checks)}/{len(checks)} checks; overall={result['passed']}")
    return 0 if result['passed'] else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    raise SystemExit(run(parser.parse_args().output))
