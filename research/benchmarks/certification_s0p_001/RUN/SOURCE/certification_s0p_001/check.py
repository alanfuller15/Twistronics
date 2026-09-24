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
            if v['edge']==1 and v['k']==128:
                captured.update(dp=v['Dp'],term=v['ja']*v['G']*v['angular'](a),bound=v['L2']/8192)
        return trace
    sys.settrace(trace)
    try: screen=relative(a,b,256,2)
    finally: sys.settrace(None)
    need(screen['status']=='CERTIFIED' and captured,'capture')
    # Edge 1 D is identically zero. Negate only Ja', not the cancelling sum.
    mutant=captured['dp']-2*captured['term']
    need(frobenius(captured['dp'])<arb('1e-28'),'edge1 cancellation')
    need(frobenius(mutant)>captured['bound'],'edge1 single-term refusal')
    rows=[dict(id='edge1_single_term_refused',passed=True,mutant_F=enclosure(frobenius(mutant)),allowance=enclosure(captured['bound']))]

    def polar_cell(m,dm):
        need(m.det()>0,'POSITIVE_DETERMINANT_REQUIRED')
        x,y=m[0,0]+m[1,1],m[1,0]-m[0,1]
        dx,dy=dm[0,0]+dm[1,1],dm[1,0]-dm[0,1]
        s=(x*x+y*y).sqrt();need(s>0,'POLAR_DENOMINATOR_REQUIRED')
        A=arb_mat([[x,-y],[y,x]]);dA=arb_mat([[dx,-dy],[dy,dx]])
        du=dA/s-A*((x*dx+y*dy)/s**3)
        amp=2*frobenius(dm)/s.lower()
        return du,s,amp
    def frame(t):
        base=arb_mat([[t.cos(),0],[t.sin(),0],[0,1]])
        db=arb_mat([[-t.sin(),0],[t.cos(),0],[0,0]])
        r=rot(t*t)
        return base*r,db*r+base*r*G*(2*t)
    S=arb_mat([[1,0,0],[0,1,0],[0,0,arb(49)/50]])
    def overlap(t):
        fs,dfs=frame(t);ft,dft=frame(2*t);dft=dft*2
        return ft.transpose()*S*fs,dft.transpose()*S*fs+ft.transpose()*S*dfs
    def matrix_record(m):
        return [[enclosure(m[r,c]) for c in range(m.ncols())] for r in range(m.nrows())]
    radius=arb(1)/256
    for numerator in (1,3,5,7):
        mid=arb(numerator)/8;t=mid+arb(0,radius)
        m,dm=overlap(t);du,s,amp=polar_cell(m,dm)
        point_checks=[]
        for offset in (-1,0,1):
            v=mid+offset*radius;mp,dmp=overlap(v);dup,sp,ap=polar_cell(mp,dmp)
            oracle=rot(-3*v*v)*G*(-6*v)
            residual=dup-oracle
            need(all(residual[r,c].contains(0) and residual[r,c].abs_upper()<arb('1e-28') for r in range(2) for c in range(2)),'point oracle')
            need(all(du[r,c].contains(oracle[r,c]) for r in range(2) for c in range(2)),'cell containment')
            need(frobenius(oracle)<=amp,'uniform amplification')
            point_checks.append(dict(offset=offset,oracle_residual_F=enclosure(frobenius(residual))))
        rows.append(dict(id=f'cell_{numerator}_8',passed=True,parameter=enclosure(t),determinant=enclosure(m.det()),s=enclosure(s),
                         dM_F_bound=enclosure(frobenius(dm)),amplification_F_bound=enclosure(amp),dU=matrix_record(du),point_checks=point_checks))
    for name,m in [('uncertain',arb_mat([[arb(0,arb(1)/10),0],[0,1]])),('singular',arb_mat([[0,0],[0,1]])),('reflection',arb_mat([[1,0],[0,-1]]))]:
        try: polar_cell(m,G)
        except ValueError as exc: need(str(exc)=='POSITIVE_DETERMINANT_REQUIRED','refusal reason')
        else: raise ValueError('unsafe determinant accepted')
        rows.append(dict(id=name+'_refused',passed=True,reason='POSITIVE_DETERMINANT_REQUIRED'))
    return dict(status='PASS_CELL_DERIVATIVE_CONTROLS',records=rows,checks=len(rows),physical_evaluations=0,
                scope='Four declared synthetic cells; interval seam-overlap derivatives and polar amplification; no numerical projector certificate')

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
    sources=list(spec['dependencies'])+['certification_s0n_001/combined.py','certification_s0n_001/SPEC.json','certification_s0p_001/check.py']
    for path in sources:
        dest=out/'SOURCE'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE.parent/path,dest)
    atomic_json(out/'ENVIRONMENT.json',env)
    shutil.copyfile(HERE.parents[2]/'docs/certification-readiness/S0P_CELL_DERIVATIVES.md',out/'S0P_CELL_DERIVATIVES.md')
    run=subprocess.run([sys.executable,'-B',str(out/'SOURCE/certification_s0p_001/check.py'),'--worker'],capture_output=True,text=True,timeout=40)
    need(run.returncode==0,run.stderr)
    summary=json.loads(run.stdout);finish(out,summary);print(json.dumps(verify(out)));print(run.stdout)

if __name__=='__main__': main()
