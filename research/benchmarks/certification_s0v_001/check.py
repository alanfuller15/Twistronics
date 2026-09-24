"""Contract-bound signed transport with nondegenerate-cluster separation."""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import begin,finish,verify,sha,atomic_json

def need(ok,msg):
    if not ok: raise ValueError(msg)

def build_gap_contract(case_id, derivatives, exercise_refusals=False):
    """Execute one synthetic contour contract and its required refusals."""
    base=dict(
        contract_id=case_id,
        theorem_id='self_adjoint_riesz_contour_differentiation_v1',
        self_adjoint=True,
        cluster_dimension=2,
        cluster_center=0,
        cluster_enclosure_radius=0,
        complement_distance_from_center_lower=3,
        contour_radius=1,
        resolvent_distance=1,
        H_derivative_bounds=derivatives,
        norm='operator',
        fixed_contour=True,
        uniform_over_parameter_domain=True,
        valid_parameter_domain='[0,1/8]',
        required_parameter_domain='[0,1/8]',
    )
    def derive(data):
        need(data.get('theorem_id')=='self_adjoint_riesz_contour_differentiation_v1','MISSING_THEOREM')
        need(data.get('self_adjoint') is True,'SELF_ADJOINT_REQUIRED')
        need(data.get('cluster_dimension')==2,'CLUSTER_DIMENSION_REQUIRED')
        rho=data.get('cluster_enclosure_radius',-1)
        complement=data.get('complement_distance_from_center_lower',0)
        radius=data.get('contour_radius',0);distance=data.get('resolvent_distance',0)
        need(complement>0,'MISSING_COMPLEMENT_DISTANCE')
        need(rho>=0 and radius>rho and complement>radius and distance>0 and
             distance<=min(radius-rho,complement-radius) and data.get('fixed_contour') is True,
             'CONTOUR_SEPARATION_REQUIRED')
        derivatives=data.get('H_derivative_bounds',{})
        need(all(name in derivatives and derivatives[name]>=0 for name in ('H1','H2','H3')),'UNBOUND_DERIVATIVE_INPUT')
        need(data.get('norm')=='operator','OPERATOR_NORM_REQUIRED')
        need(data.get('uniform_over_parameter_domain') is True and
             data.get('valid_parameter_domain')==data.get('required_parameter_domain'),'DOMAIN_MISMATCH')
        h1,h2,h3=(Q(derivatives[name]) for name in ('H1','H2','H3'))
        radius=Q(radius);distance=Q(distance)
        p1=radius*h1/distance**2
        p2=radius*(2*h1**2/distance**3+h2/distance**2)
        p3=radius*(6*h1**3/distance**4+6*h1*h2/distance**3+h3/distance**2)
        need(all(value.denominator==1 for value in (p1,p2,p3,p3+2*p2*p1)),
             'NONINTEGER_SYNTHETIC_BOUND')
        p1,p2,p3=(int(value) for value in (p1,p2,p3))
        return dict(P1=p1,P2=p2,P3=p3,K=p1,K1=p2,K2=p3+2*p2*p1,
                    norm='operator',valid_parameter_domain=data['valid_parameter_domain'])
    output=derive(base)
    mutations=[]
    if exercise_refusals:
        for name,change,expected in (
            ('missing_theorem',lambda d:d.pop('theorem_id'),'MISSING_THEOREM'),
            ('self_adjoint_required',lambda d:d.update(self_adjoint=False),'SELF_ADJOINT_REQUIRED'),
            ('cluster_dimension_required',lambda d:d.update(cluster_dimension=1),'CLUSTER_DIMENSION_REQUIRED'),
            ('missing_complement_distance',lambda d:d.update(complement_distance_from_center_lower=0),'MISSING_COMPLEMENT_DISTANCE'),
            ('contour_separation_required',lambda d:d.update(contour_radius=3),'CONTOUR_SEPARATION_REQUIRED'),
            ('unbound_derivative_input',lambda d:d['H_derivative_bounds'].pop('H3'),'UNBOUND_DERIVATIVE_INPUT'),
            ('operator_norm_required',lambda d:d.update(norm='frobenius'),'OPERATOR_NORM_REQUIRED'),
            ('domain_mismatch',lambda d:d.update(valid_parameter_domain='[0,1/16]'),'DOMAIN_MISMATCH'),
        ):
            trial=json.loads(json.dumps(base));change(trial)
            try: derive(trial)
            except ValueError as exc:
                need(str(exc)==expected,'WRONG_CONTRACT_REFUSAL');mutations.append(dict(id=name,error=expected))
            else: raise ValueError('CONTRACT_MUTATION_ACCEPTED')
    return dict(contract_id=case_id,status='PASS_SYNTHETIC_INTERFACE',
                physical_status='DECLARED_UNEXECUTED',inputs=base,outputs=output,
                refusal_controls=mutations)

def worker():
    from flint import arb,arb_mat,acb,acb_mat,ctx
    ctx.prec=128;ctx.threads=1
    panels=1024;steps=128;h=arb(1)/1024
    I=arb_mat([[1,0,0],[0,1,0],[0,0,1]]);CI=acb_mat(I)
    F0=arb_mat([[1,0],[0,1],[0,0]]);e3=arb_mat([[0],[0],[1]])
    Z=arb_mat([[0,-1,0],[1,0,0],[0,0,0]])
    Y=arb_mat([[0,0,1],[0,0,0],[-1,0,0]])
    def enc(x):
        def ep(v):
            m,e=v.man_exp();return dict(mantissa=str(m),exponent=int(e))
        return dict(lower=ep(x.lower()),upper=ep(x.upper()))
    def norm(m):
        return sum((m[j,k].abs_upper()**2 for j in range(m.nrows()) for k in range(m.ncols())),arb(0)).sqrt().upper()
    def midpoint(m):
        c=arb_mat([[m[j,k].mid() for k in range(m.ncols())] for j in range(m.nrows())]);return c,norm(m-c)
    def wide(m,e):
        return arb_mat([[m[j,k]+arb(0,e.upper()) for k in range(m.ncols())] for j in range(m.nrows())])
    def record(m):
        return [[enc(m[j,k]) for k in range(m.ncols())] for j in range(m.nrows())]
    def rotation(t):
        return arb_mat([[t.cos(),-t.sin()],[t.sin(),t.cos()]])
    def Q(t):
        rz=arb_mat([[t.cos(),-t.sin(),0],[t.sin(),t.cos(),0],[0,0,1]])
        ry=arb_mat([[t.cos(),0,t.sin()],[0,1,0],[-t.sin(),0,t.cos()]])
        return rz*ry
    def model(t,kind):
        if kind=='constant':
            n=arb_mat([[-t.sin()],[0],[t.cos()]]);dn=arb_mat([[-t.cos()],[0],[-t.sin()]])
        else:
            q=Q(t);n=q*e3;dn=Z*n+q*Y*e3
        return n,dn,acb_mat(3*n*n.transpose()),acb_mat(3*(dn*n.transpose()+n*dn.transpose()))
    def oracle(t,kind):
        if kind=='constant': return arb_mat([[t.cos(),0],[0,1],[t.sin(),0]])
        return Q(t)*F0*rotation(-t.sin())
    def contour(t,kind,N=panels):
        n,dn,H,B=model(t,kind);bound=3 if kind=='constant' else 6
        p=acb_mat(3,3);dp=acb_mat(3,3)
        for k in range(N):
            theta=arb.pi()*arb(2*k+1)/N
            z=acb(theta.cos(),theta.sin());R=(z*CI-H).inv()
            p+=z*R/N;dp+=z*(R*B*R)/N
        # Average Taylor remainder: sup ||f''|| * (pi/N)^2 / 6.
        qp=(arb.pi().upper()**2/N**2).upper()
        qdp=(arb(13*bound)*arb.pi().upper()**2/(6*N**2)).upper()
        need(all((p[j,k].imag+arb(0,qp)).contains(0) and (dp[j,k].imag+arb(0,qdp)).contains(0) for j in range(3) for k in range(3)),'REAL_CONTOUR')
        p=wide(arb_mat([[p[j,k].real for k in range(3)] for j in range(3)]),qp)
        dp=wide(arb_mat([[dp[j,k].real for k in range(3)] for j in range(3)]),qdp)
        raw=dp*p-p*dp;kbox=arb_mat(3,3)
        for j in range(3):
            need(raw[j,j].contains(0),'SKEW_DIAGONAL')
            for k in range(j+1,3):
                x=raw[j,k].intersection(-raw[k,j]);kbox[j,k]=x;kbox[k,j]=-x
        return p,dp,kbox,qp,qdp
    contracts=[
        build_gap_contract('constant',dict(H1=3,H2=6,H3=24)),
        build_gap_contract('two_axis',dict(H1=6,H2=48,H3=192),exercise_refusals=True),
    ]
    contract_by_id={c['contract_id']:c for c in contracts}
    cases=[]
    for kind in ('constant','two_axis'):
        output=contract_by_id[kind]['outputs']
        bounds=dict(k=output['K'],k1=output['K1'],k2=output['K2'])
        kbound=arb(bounds['k']);k1=arb(bounds['k1']);k2=arb(bounds['k2'])
        centre=F0;error=arb(0);legacy_error=arb(0);frames=[];ledger=[]
        for k in range(steps):
            _,_,km,qp,qdp=contour((k+arb(1)/2)*h,kind)
            raw,_=midpoint(km);A=(raw-raw.transpose())/2
            need(all((A+A.transpose())[j,l].is_zero() for j in range(3) for l in range(3)),'EXACT_SKEW')
            delta=norm(km-A);cnorm=norm(centre);anorm=norm(A)
            gd=(cnorm*delta*h).upper()
            tube_vd=(cnorm*k1*h*h/4).upper()
            signed_vd=(cnorm*(k2*h**3/24+k1*(kbound+anorm)*h**3/12)).upper()
            u=h/2+arb(0,(h/2)*(1+arb(1)/2**20));extension=(u.abs_upper()-h).abs_upper()
            extra=(cnorm*(delta+k1*(h/2+extension))*extension).upper()
            # Continuum tubes retain the uncancelled first-order debit.  Only the
            # full endpoint recurrence may use the signed centered cancellation.
            tube_radius=(error+gd+tube_vd+extra).upper()
            tube=wide((u*A).exp()*centre,tube_radius);frames.append(tube)
            nxt,rounding=midpoint((h*A).exp()*centre)
            end=(error+gd+signed_vd+rounding).upper()
            legacy_end=(legacy_error+gd+tube_vd+rounding).upper()
            need(norm(nxt-oracle((k+1)*h,kind))<=end,'ENDPOINT_ORACLE')
            for t in (k*h,(k+arb(1)/2)*h,(k+1)*h):
                o=oracle(t,kind)
                need(all(tube[j,l].contains(o[j,l]) for j in range(3) for l in range(2)),'TUBE_ORACLE')
            ledger.append(dict(step=k,start_error=enc(error),legacy_start_error=enc(legacy_error),centre_norm=enc(cnorm),generator_radius=enc(delta),generator_debit=enc(gd),generator_norm_bound=enc(kbound),frozen_generator_norm=enc(anorm),generator_derivative_bound=enc(k1),generator_second_derivative_bound=enc(k2),endpoint_variation_debit=enc(signed_vd),tube_variation_debit=enc(tube_vd),tube_radius=enc(tube_radius),rounding=enc(rounding),end_error=enc(end),legacy_end_error=enc(legacy_end),orthogonality_bound=enc((2*end+end**2).upper()),range_error_bound=enc(end),tube_u=enc(u),tube_extra=enc(extra)))
            centre,error,legacy_error=nxt,end,legacy_end
        R=rotation(arb(1)/5);S=F0*R*F0.transpose();seams=[]
        for k in range(steps//2):
            fs=frames[k];a=frames[2*k];b=frames[2*k+1]
            ft=arb_mat([[a[j,l].union(b[j,l]) for l in range(2)] for j in range(3)])
            t=(k+arb(1)/2)*h+arb(0,h/2)
            need(u.contains(t-k*h),'SOURCE_COVERAGE')
            need(u.contains((2*t).lower()-2*k*h) and u.contains((2*t).upper()-(2*k+1)*h),'TARGET_COVERAGE')
            _,_,ks,_,_=contour(t,kind);_,_,kt,_,_=contour(2*t,kind)
            dfs=ks*fs;dft=2*kt*ft
            m=ft.transpose()*S*fs;dm=dft.transpose()*S*fs+ft.transpose()*S*dfs
            lower=1-norm(m-R);det=m.det()
            need(det>0 and lower>=arb(19)/20,'SEAM_GATE')
            seams.append(dict(cell=k,parameter=enc(t),sigma_lower=enc(lower),determinant=enc(det),polar_derivative_bound=enc((arb(20)/19*norm(dm)).upper()),dM=record(dm)))
        # Numerical K boxes certify noncommutation at separated parameter values.
        _,_,k0,_,_=contour(arb(0),kind);_,_,k1,_,_=contour(arb(1)/8,kind)
        comm=k0*k1-k1*k0
        if kind=='two_axis':
            need(any(not comm[j,l].contains(0) for j in range(3) for l in range(3)),'NONCOMMUTATION')
            tau=arb(1)/8
            order=(tau*k1).exp()*(tau*k0).exp()-(tau*k0).exp()*(tau*k1).exp()
            need(any(not order[j,l].contains(0) for j in range(3) for l in range(3)),'ORDER_CONTROL')
            frozen=(tau*k0).exp()*F0-oracle(tau,kind)
            need(any(frozen[j,l].abs_lower()>error for j in range(3) for l in range(2)),'FROZEN_GENERATOR_CONTROL')
        else:
            order=arb_mat(3,3);frozen=arb_mat(3,2)
        # Exact synthetic P and P' are controls, never inputs to contour/transport.
        calibration=[]
        for N in (512,1024):
            t=arb(1)/16;p,dp,kbox,pe,de=contour(t,kind,N);n,dn,_,_=model(t,kind)
            exactp=I-n*n.transpose();exactdp=-(dn*n.transpose()+n*dn.transpose())
            need(all(p[j,l].contains(exactp[j,l]) and dp[j,l].contains(exactdp[j,l]) for j in range(3) for l in range(3)),'QUADRATURE_ORACLE')
            calibration.append(dict(panels=N,projector_debit=enc(pe),derivative_debit=enc(de),P=record(p),dP=record(dp)))
        need(error<legacy_error,'SIGNED_IMPROVEMENT')
        cases.append(dict(id=kind,contract_id=kind,bounds=bounds,steps=ledger,seams=seams,final_error=enc(error),legacy_final_error=enc(legacy_error),improvement=enc((legacy_error-error).lower()),commutator=record(comm),order_difference=record(order),frozen_difference=record(frozen),calibration=calibration))
    return dict(status='PASS_BOUND_CONTRACT_TRANSPORT',cases=cases,
                gap_to_derivative_contracts=contracts,pi=enc(arb.pi()),panels=panels,
                precision=128,step_size='1/1024',source_domain='[0,1/16]',
                target_domain='[0,1/8]',physical_evaluations=0)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',action='store_true');ap.add_argument('--wheel',type=Path);ap.add_argument('--output',type=Path);args=ap.parse_args()
    if args.worker:
        resource.setrlimit(resource.RLIMIT_AS,(1073741824,)*2)
        start=time.monotonic();r=worker();r['wall_seconds']=time.monotonic()-start;print(json.dumps(r));return
    need(args.wheel is not None and args.output is not None,'WHEEL_AND_OUTPUT_REQUIRED')
    from run_calibration import environment
    spec=json.loads((HERE/'SPEC.json').read_text())
    for path,digest in spec['dependencies'].items(): need(sha(HERE.parent/path)==digest,'DEPENDENCY_HASH')
    env=environment(args.wheel,spec);out=begin(args.output)
    for path in list(spec['dependencies'])+[f'certification_s0v_001/{n}' for n in ('check.py','verify.py','SPEC.json')]:
        dest=out/'SOURCE'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE.parent/path,dest)
    shutil.copyfile(HERE.parents[2]/'docs/certification-readiness/S0V_BOUND_CONTRACT.md',out/'S0V_BOUND_CONTRACT.md')
    atomic_json(out/'ENVIRONMENT.json',env)
    run=subprocess.run([sys.executable,'-B',str(out/'SOURCE/certification_s0v_001/check.py'),'--worker'],capture_output=True,text=True,timeout=40)
    need(run.returncode==0,run.stderr);r=json.loads(run.stdout);finish(out,r)
    print(json.dumps(verify(out)));print(json.dumps(dict(status=r['status'],cases=len(r['cases']),wall_seconds=r['wall_seconds'])))

if __name__=='__main__': main()
