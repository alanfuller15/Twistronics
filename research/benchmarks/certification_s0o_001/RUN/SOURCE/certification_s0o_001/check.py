"""Fixed derivative controls; no physical models or adaptive search."""
import argparse
import inspect
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
for name in ('certification_s0f_001','certification_s0b_001','certification_s0n_001'):
    sys.path.insert(0,str(HERE.parent/name))
from runner_io import begin,finish,verify,sha,atomic_json

def need(ok,message):
    if not ok: raise ValueError(message)

def worker():
    from flint import arb,arb_mat,ctx
    from combined import Combined,relative,i,rot,frobenius,enclosure
    ctx.prec=128;ctx.threads=1
    G=arb_mat([[0,-1],[1,0]])
    a,b=Combined(128,1),Combined(160,1,bump='361/500')
    a.repair();b.repair()
    captured={}
    lines,start=inspect.getsourcelines(relative)
    line=start+next(k for k,s in enumerate(lines) if 'affine=max(' in s)
    def trace(frame,event,arg):
        if frame.f_code is relative.__code__ and event=='line' and frame.f_lineno==line:
            v=frame.f_locals
            if v['k'] in (32,128,224):
                captured[(v['edge'],v['k'])]=(v['t'],v['Dp'],v['L2'])
        return trace
    # Observe the actual frozen S0n Dp, without modifying its code or branches.
    sys.settrace(trace)
    try: result=relative(a,b,256,2)
    finally: sys.settrace(None)
    need(result['status']=='CERTIFIED' and len(captured)==6,'frozen capture')
    def D(edge,t):
        target,source=a.ends(edge,t)
        def q(x,y): return i.polar(b.frame(x,y).transpose()*a.frame(x,y))
        return a.repaired(edge,t)-q(*target).transpose()*b.repaired(edge,t)*q(*source)
    records=[]
    step=arb(1)/4096
    for (edge,k),(t,dp,L2) in sorted(captured.items()):
        def rates(g):
            if edge==1: return arb.pi()/g.d,arb(0),arb(0)
            return ((2*arb.pi()*g.w-arb.pi()/g.d+g.defect).abs_upper()+4*g.bump.abs_upper()+g.delta.abs_upper()*arb(15)/8,
                    8*g.bump.abs_upper()+6*g.delta.abs_upper(),60*g.delta.abs_upper())
        va,aa,ja=rates(a);vb,ab,jb=rates(b)
        if edge==1:
            vq=2*arb.pi()*((b.c(arb(1))-a.c(arb(1))).abs_upper()+(b.c(arb(0))-a.c(arb(0))).abs_upper())
        else: vq=arb.pi()*(arb(1)/a.d-arb(1)/b.d).abs_upper()
        L3=arb(2).sqrt()*(ja+3*va*aa+va**3+jb+3*(vb+vq)*ab+(vb+vq)**3)
        secant=(D(edge,t+step)-D(edge,t-step))/(2*step)
        error=frobenius(secant-dp)
        first=L2*step/2;second=L3*step**2/6
        need(error<=first and error<=second,'central difference consistency')
        row=dict(id=f'derivative_{edge}_{k}',passed=True,error_F=enclosure(error),L2=enclosure(L2),L3=enclosure(L3),first_bound=enclosure(first),second_bound=enclosure(second))
        if edge==2:
            mutant=frobenius(secant+dp)
            need(mutant>second,'sign mutation must fail')
            row['negated_Dp_refused']=True;row['mutant_error_F']=enclosure(mutant)
        records.append(row)

    # Frechet derivative from entries of a general positive-determinant 2x2 M.
    # No angle oracle is consumed by this operation.
    def polar_derivative(m,dm):
        need(m.det()>0,'POSITIVE_DETERMINANT_REQUIRED')
        x,y=m[0,0]+m[1,1],m[1,0]-m[0,1]
        dx,dy=dm[0,0]+dm[1,1],dm[1,0]-dm[0,1]
        s=(x*x+y*y).sqrt();need(s>0,'POLAR_DENOMINATOR_REQUIRED')
        A=arb_mat([[x,-y],[y,x]]);dA=arb_mat([[dx,-dy],[dy,dx]])
        return dA/s-A*((x*dx+y*dy)/s**3)
    for num,den in ((1,7),(1,2),(6,7)):
        t=arb(num)/den
        left,right=rot(t*t),rot(3*t)
        diag=arb_mat([[2+t,0],[0,1+t*t]])
        ddiag=arb_mat([[1,0],[0,2*t]])
        m=left*diag*right
        dm=(left*G*(2*t))*diag*right+left*ddiag*right+left*diag*(right*G*3)
        du=polar_derivative(m,dm)
        oracle=rot(t*t+3*t)*G*(2*t+3)
        residual=du-oracle
        need(all(residual[r,c].contains(0) and residual[r,c].abs_upper()<arb('1e-28') for r in range(2) for c in range(2)),'polar derivative oracle')
        tangent=i.polar(m).transpose()*du+du.transpose()*i.polar(m)
        need(all(tangent[r,c].contains(0) for r in range(2) for c in range(2)),'polar tangent')
        records.append(dict(id=f'polar_{num}_{den}',passed=True,residual_F=enclosure(frobenius(residual))))
    try: polar_derivative(arb_mat([[1,0],[0,-1]]),G)
    except ValueError as exc: need(str(exc)=='POSITIVE_DETERMINANT_REQUIRED','refusal reason')
    else: raise ValueError('reflection accepted')
    records.append(dict(id='polar_reflection_refused',passed=True))
    # f(t)=t^3 at zero: central error=h^2, while local sup |f''|=6h.
    need(step**2>6*step*step**2/6,'counterexample')
    records.append(dict(id='L2_quadratic_remainder_counterexample',passed=True,error=enclosure(step**2),invalid_bound=enclosure(step**3)))
    return dict(status='PASS_FIXED_DERIVATIVE_CONTROLS',records=records,checks=14,physical_evaluations=0,
                scope='Synthetic derivative checks and entrywise polar Frechet primitive; no numerical projector or transport certificate')

def main():
    p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true');p.add_argument('--output',type=Path);p.add_argument('--wheel',type=Path);args=p.parse_args()
    if args.worker:
        resource.setrlimit(resource.RLIMIT_AS,(1073741824,)*2)
        start=time.monotonic();r=worker();r['wall_seconds']=time.monotonic()-start
        print(json.dumps(r));return
    if args.output is None or args.wheel is None: p.error('--output and --wheel required')
    from run_calibration import environment
    spec=json.loads((HERE.parent/'certification_s0n_001/SPEC.json').read_text())
    for path,digest in spec['dependencies'].items(): need(sha(HERE.parent/path)==digest,'dependency hash')
    env=environment(args.wheel.resolve(),spec)
    out=begin(args.output)
    sources=list(spec['dependencies'])+['certification_s0n_001/combined.py','certification_s0n_001/SPEC.json','certification_s0o_001/check.py']
    for path in sources:
        dest=out/'SOURCE'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE.parent/path,dest)
    atomic_json(out/'ENVIRONMENT.json',env)
    shutil.copyfile(HERE.parents[2]/'docs/certification-readiness/S0O_DERIVATIVES.md',out/'S0O_DERIVATIVES.md')
    run=subprocess.run([sys.executable,'-B',str(out/'SOURCE/certification_s0o_001/check.py'),'--worker'],capture_output=True,text=True,timeout=40)
    need(run.returncode==0,run.stderr)
    summary=json.loads(run.stdout);finish(out,summary);print(json.dumps(verify(out)));print(run.stdout)

if __name__=='__main__': main()
