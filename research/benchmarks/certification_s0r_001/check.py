"""Fixed restarted Kato transport driven by numerical contour enclosures."""
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
    panels=2048;steps=128;h=arb(1)/1024
    I=arb_mat([[1,0,0],[0,1,0],[0,0,1]]);CI=acb_mat(I)
    F0=arb_mat([[1,0],[0,1],[0,0]])
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
    def contour(t):
        n=arb_mat([[-t.sin()],[0],[t.cos()]]);dn=arb_mat([[-t.cos()],[0],[-t.sin()]])
        H=acb_mat(3*n*n.transpose());dH=acb_mat(3*(dn*n.transpose()+n*dn.transpose()))
        p=acb_mat(3,3);dp=acb_mat(3,3)
        for k in range(panels):
            theta=2*arb.pi()*(arb(2*k+1)/(2*panels)+arb(0,arb(1)/(2*panels)))
            z=acb(theta.cos(),theta.sin());R=(z*CI-H).inv()
            p+=z*R/panels;dp+=z*(R*dH*R)/panels
        need(all(p[j,k].imag.contains(0) and dp[j,k].imag.contains(0) for j in range(3) for k in range(3)),'REAL_CONTOUR')
        p=arb_mat([[p[j,k].real for k in range(3)] for j in range(3)])
        dp=arb_mat([[dp[j,k].real for k in range(3)] for j in range(3)])
        return p,dp*p-p*dp
    def oracle(t):
        return arb_mat([[t.cos(),0],[0,1],[t.sin(),0]])
    centre=F0;error=arb(0);frames=[];step_records=[]
    for k in range(steps):
        tmid=(k+arb(1)/2)*h
        pm,km=contour(tmid)
        raw,_=midpoint(km)
        A=(raw-raw.transpose())/2
        need(all((A+A.transpose())[j,l].is_zero() for j in range(3) for l in range(3)),'EXACT_SKEW_REQUIRED')
        delta=norm(km-A)
        cnorm=norm(centre)
        generator_debit=(cnorm*delta*h).upper()
        variation_debit=(cnorm*48*h*h/4).upper()
        local=(generator_debit+variation_debit).upper()
        # Pad tube endpoints beyond downstream t -> 2t radius rounding.
        u=h/2+arb(0,(h/2)*(1+arb(1)/2**20))
        # Rounded u may extend minutely beyond [0,h]. Charge that extension.
        extension=(u.abs_upper()-h).abs_upper()
        tube_extra=(cnorm*(delta+48*(h/2+extension))*extension).upper()
        tube=wide((u*A).exp()*centre,error+local+tube_extra)
        frames.append(tube)
        y=(h*A).exp()*centre
        nextcentre,rounding=midpoint(y)
        next_error=(error+local+rounding).upper()
        # Norm-defect and range bounds use the exact Kato frame as reference.
        ortho=(2*next_error+next_error**2).upper()
        need(norm(nextcentre-oracle((k+1)*h))<=next_error,'ENDPOINT_ORACLE')
        for v in (k*h,tmid,(k+1)*h):
            o=oracle(v)
            need(all(tube[j,l].contains(o[j,l]) for j in range(3) for l in range(2)),'TUBE_ORACLE')
        step_records.append(dict(step=k,start_error=enc(error),centre_norm=enc(cnorm),generator_radius=enc(delta),generator_debit=enc(generator_debit),variation_debit=enc(variation_debit),rounding=enc(rounding),end_error=enc(next_error),orthogonality_bound=enc(ortho),range_error_bound=enc(next_error),tube_u=enc(u),tube_extra=enc(tube_extra)))
        centre,error=nextcentre,next_error
    angle=arb(1)/5
    R=arb_mat([[angle.cos(),-angle.sin()],[angle.sin(),angle.cos()]])
    S=F0*R*F0.transpose()
    def hull(a,b):
        return arb_mat([[a[j,k].union(b[j,k]) for k in range(a.ncols())] for j in range(a.nrows())])
    seam_records=[]
    for k in range(steps//2):
        fs=frames[k];ft=hull(frames[2*k],frames[2*k+1])
        t=(k+arb(1)/2)*h+arb(0,h/2)
        need(u.contains(t-k*h),'SOURCE_TUBE_COVERAGE')
        need(u.contains((2*t).lower()-2*k*h) and u.contains((2*t).upper()-(2*k+1)*h),'TARGET_TUBE_COVERAGE')
        ps,ks=contour(t);pt,kt=contour(2*t)
        dfs=ks*fs;dft=2*kt*ft
        m=ft.transpose()*S*fs;dm=dft.transpose()*S*fs+ft.transpose()*S*dfs
        lower=1-norm(m-R)
        need(m.det()>0 and lower>=arb(19)/20,'SEAM_GATE')
        amp=(arb(20)/19*norm(dm)).upper()
        seam_records.append(dict(cell=k,parameter=enc(t),sigma_lower=enc(lower),polar_derivative_bound=enc(amp),dM=record(dm)))
    # Geometric failure control: at source 1/4, target 1/2, test first-column norm.
    bad=oracle(arb(1)/2).transpose()*S*oracle(arb(1)/4)
    badcol=norm(arb_mat([[bad[0,0]],[bad[1,0]]]))
    need(badcol<arb(19)/20,'GEOMETRIC_REFUSAL')
    # Domain extension is checked against the frozen single-origin debit.
    old=42*arb(2).sqrt()*(arb(1)/8)**2
    need(error<old,'RESTART_IMPROVEMENT')
    # A symmetric perturbation must never use the no-amplification lemma.
    non_skew=I/100
    need(not all((non_skew+non_skew.transpose())[j,l].is_zero() for j in range(3) for l in range(3)),'SKEW_CONTROL')
    return dict(status='PASS_RESTARTED_TRANSPORT',steps=step_records,seams=seam_records,panels=panels,step_size='1/1024',source_domain='[0,1/16]',target_domain='[0,1/8]',final_frame_error=enc(error),single_origin_remainder=enc(old),geometric_refusal_column_upper=enc(badcol),controls=['non_skew_refused','geometric_seam_refused'],physical_evaluations=0,precision=128)

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
    for path in list(spec['dependencies'])+[f'certification_s0r_001/{n}' for n in ('check.py','verify.py','SPEC.json')]:
        dest=out/'SOURCE'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE.parent/path,dest)
    shutil.copyfile(HERE.parents[2]/'docs/certification-readiness/S0R_RESTARTED_TRANSPORT.md',out/'S0R_RESTARTED_TRANSPORT.md')
    atomic_json(out/'ENVIRONMENT.json',env)
    run=subprocess.run([sys.executable,'-B',str(out/'SOURCE/certification_s0r_001/check.py'),'--worker'],capture_output=True,text=True,timeout=40)
    need(run.returncode==0,run.stderr);r=json.loads(run.stdout);finish(out,r)
    print(json.dumps(verify(out)));print(json.dumps({k:v for k,v in r.items() if k not in ('steps','seams')}))

if __name__=='__main__': main()
