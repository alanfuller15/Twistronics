"""Bounded synthetic quadrature and noncommuting Kato transport calibration."""
import argparse
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

def worker():
    from flint import arb,arb_mat,acb,acb_mat,ctx
    ctx.prec=128;ctx.threads=1
    panels=512;steps=128;h=arb(1)/1024
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
    cases=[]
    for kind,lipschitz in [('constant',24),('two_axis',120)]:
        centre=F0;error=arb(0);frames=[];ledger=[]
        for k in range(steps):
            _,_,km,qp,qdp=contour((k+arb(1)/2)*h,kind)
            raw,_=midpoint(km);A=(raw-raw.transpose())/2
            need(all((A+A.transpose())[j,l].is_zero() for j in range(3) for l in range(3)),'EXACT_SKEW')
            delta=norm(km-A);cnorm=norm(centre)
            gd=(cnorm*delta*h).upper();vd=(cnorm*lipschitz*h*h/4).upper();local=(gd+vd).upper()
            u=h/2+arb(0,(h/2)*(1+arb(1)/2**20));extension=(u.abs_upper()-h).abs_upper()
            extra=(cnorm*(delta+lipschitz*(h/2+extension))*extension).upper()
            tube=wide((u*A).exp()*centre,error+local+extra);frames.append(tube)
            nxt,rounding=midpoint((h*A).exp()*centre);end=(error+local+rounding).upper()
            need(norm(nxt-oracle((k+1)*h,kind))<=end,'ENDPOINT_ORACLE')
            for t in (k*h,(k+arb(1)/2)*h,(k+1)*h):
                o=oracle(t,kind)
                need(all(tube[j,l].contains(o[j,l]) for j in range(3) for l in range(2)),'TUBE_ORACLE')
            ledger.append(dict(step=k,start_error=enc(error),centre_norm=enc(cnorm),generator_radius=enc(delta),generator_debit=enc(gd),variation_debit=enc(vd),rounding=enc(rounding),end_error=enc(end),orthogonality_bound=enc((2*end+end**2).upper()),range_error_bound=enc(end),tube_u=enc(u),tube_extra=enc(extra)))
            centre,error=nxt,end
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
        for N in (256,512):
            t=arb(1)/16;p,dp,kbox,pe,de=contour(t,kind,N);n,dn,_,_=model(t,kind)
            exactp=I-n*n.transpose();exactdp=-(dn*n.transpose()+n*dn.transpose())
            need(all(p[j,l].contains(exactp[j,l]) and dp[j,l].contains(exactdp[j,l]) for j in range(3) for l in range(3)),'QUADRATURE_ORACLE')
            calibration.append(dict(panels=N,projector_debit=enc(pe),derivative_debit=enc(de),P=record(p),dP=record(dp)))
        cases.append(dict(id=kind,lipschitz=lipschitz,steps=ledger,seams=seams,final_error=enc(error),commutator=record(comm),order_difference=record(order),frozen_difference=record(frozen),calibration=calibration))
    return dict(status='PASS_TAYLOR_NONCOMMUTING_TRANSPORT',cases=cases,pi=enc(arb.pi()),panels=panels,precision=128,step_size='1/1024',source_domain='[0,1/16]',target_domain='[0,1/8]',physical_evaluations=0)

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
    for path in list(spec['dependencies'])+[f'certification_s0s_001/{n}' for n in ('check.py','verify.py','SPEC.json')]:
        dest=out/'SOURCE'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE.parent/path,dest)
    shutil.copyfile(HERE.parents[2]/'docs/certification-readiness/S0S_TAYLOR_NONCOMMUTING.md',out/'S0S_TAYLOR_NONCOMMUTING.md')
    atomic_json(out/'ENVIRONMENT.json',env)
    run=subprocess.run([sys.executable,'-B',str(out/'SOURCE/certification_s0s_001/check.py'),'--worker'],capture_output=True,text=True,timeout=40)
    need(run.returncode==0,run.stderr);r=json.loads(run.stdout);finish(out,r)
    print(json.dumps(verify(out)));print(json.dumps(dict(status=r['status'],cases=len(r['cases']),wall_seconds=r['wall_seconds'])))

if __name__=='__main__': main()
