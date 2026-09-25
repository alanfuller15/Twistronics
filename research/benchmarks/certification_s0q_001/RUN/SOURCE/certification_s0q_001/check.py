"""Fixed synthetic interval-resolvent -> Kato-frame -> seam derivative packet."""
import argparse
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'certification_s0b_001'))
from runner_io import begin, finish, verify, sha, atomic_json

def need(ok, message):
    if not ok:
        raise ValueError(message)

def worker():
    from flint import arb, arb_mat, acb, acb_mat, ctx
    ctx.prec = 128
    ctx.threads = 1
    N = 1024
    I = arb_mat([[1,0,0],[0,1,0],[0,0,1]])
    CI = acb_mat(I)
    F0 = arb_mat([[1,0],[0,1],[0,0]])
    G = arb_mat([[0,-1],[1,0]])
    def enc(x):
        def endpoint(v):
            m,e = v.man_exp()
            return dict(mantissa=str(m), exponent=int(e))
        return dict(lower=endpoint(x.lower()), upper=endpoint(x.upper()))
    def mat(m):
        return [[enc(m[j,k]) for k in range(m.ncols())] for j in range(m.nrows())]
    def norm(m):
        return sum((m[j,k].abs_upper()**2 for j in range(m.nrows()) for k in range(m.ncols())),arb(0)).sqrt().upper()
    def contains(a,b):
        return all(a[j,k].contains(b[j,k]) for j in range(a.nrows()) for k in range(a.ncols()))
    def overlap_zero(a):
        return all(a[j,k].contains(0) for j in range(a.nrows()) for k in range(a.ncols()))
    def model(t):
        # H=3nn^T, n=(-sin t,0,cos t); spectrum {0,0,3} for real t.
        n=arb_mat([[-t.sin()],[0],[t.cos()]])
        dn=arb_mat([[-t.cos()],[0],[-t.sin()]])
        return 3*n*n.transpose(), 3*(dn*n.transpose()+n*dn.transpose())
    def contour(t, radius=1):
        r=arb(radius)
        need(r>0 and r<3,'CONTOUR_SEPARATION_REQUIRED')
        h,dh=model(t)
        p=acb_mat(3,3); dp=acb_mat(3,3)
        # Each box contains its entire arc, so the average encloses the integral.
        for k in range(N):
            theta=2*arb.pi()*(arb(2*k+1)/(2*N)+arb(0,arb(1)/(2*N)))
            z=acb(theta.cos(),theta.sin())*r
            res=(CI*z-acb_mat(h)).inv()
            p += res*z/N
            dp += (res*acb_mat(dh)*res)*z/N
        need(all(p[j,k].imag.contains(0) and dp[j,k].imag.contains(0) for j in range(3) for k in range(3)),'REAL_PROJECTOR_REQUIRED')
        return arb_mat([[p[j,k].real for k in range(3)] for j in range(3)]),arb_mat([[dp[j,k].real for k in range(3)] for j in range(3)])
    p0,dp0=contour(arb(0))
    K0=dp0*p0-p0*dp0
    # Resolvent bounds at radius 1: ||P'||<=3, ||P''||<=2*3^2+6=24.
    # ||K||<=6, ||K'||<=48, hence ||F''||F<=84 sqrt(2).
    second=84*arb(2).sqrt()
    def numerical_frame(t):
        p,dp=contour(t)
        K=dp*p-p*dp
        remainder=(second*t.abs_upper()**2/2).upper()
        f=F0+t*K0*F0
        f=arb_mat([[f[j,k]+arb(0,remainder) for k in range(2)] for j in range(3)])
        df=K*f
        return f,df,p,dp,remainder
    angle=arb(1)/5
    R=arb_mat([[angle.cos(),-angle.sin()],[angle.sin(),angle.cos()]])
    # Rank-two partial isometry, with S^T S=diag(1,1,0). Not a lattice translation.
    S=F0*R*F0.transpose()
    def polar(m,dm):
        need(m.det()>0,'POSITIVE_DETERMINANT_REQUIRED')
        lower=1-norm(m-R)
        need(lower>=arb(19)/20,'SEAM_SINGULAR_GATE')
        x,y=m[0,0]+m[1,1],m[1,0]-m[0,1]
        dx,dy=dm[0,0]+dm[1,1],dm[1,0]-dm[0,1]
        s=(x*x+y*y).sqrt()
        need(s>0,'POLAR_DENOMINATOR_REQUIRED')
        A=arb_mat([[x,-y],[y,x]]);dA=arb_mat([[dx,-dy],[dy,dx]])
        du=dA/s-A*((x*dx+y*dy)/s**3)
        return du,lower,arb(20)/19*norm(dm)
    def oracle_frame(t):
        return arb_mat([[t.cos(),0],[0,1],[t.sin(),0]]),arb_mat([[-t.sin(),0],[0,0],[t.cos(),0]])
    rows=[]
    for cell in range(4):
        mid=arb(2*cell+1)/1024
        t=mid+arb(0,arb(1)/1024)
        fs,dfs,ps,dps,es=numerical_frame(t)
        ft,dft,pt,dpt,et=numerical_frame(2*t)
        dft=2*dft
        m=ft.transpose()*S*fs
        dm=dft.transpose()*S*fs+ft.transpose()*S*dfs
        du,sg,amp=polar(m,dm)
        for offset in (-1,0,1):
            v=mid+arb(offset)/1024
            os,dos=oracle_frame(v);ot,dot=oracle_frame(2*v);dot=2*dot
            need(contains(fs,os) and contains(ft,ot),'FRAME_ORACLE')
            need(contains(dfs,dos) and contains(dft,dot),'FRAME_DERIVATIVE_ORACLE')
            po=os*os.transpose();dpo=dos*os.transpose()+os*dos.transpose()
            need(contains(ps,po) and contains(dps,dpo),'PROJECTOR_ORACLE')
            mo=ot.transpose()*S*os;dmo=dot.transpose()*S*os+ot.transpose()*S*dos
            need(contains(m,mo) and contains(dm,dmo),'SEAM_ORACLE')
            # Independent scalar angle derivative for the 2x2 polar factor.
            x,y=mo[0,0]+mo[1,1],mo[1,0]-mo[0,1]
            dx,dy=dmo[0,0]+dmo[1,1],dmo[1,0]-dmo[0,1]
            u=arb_mat([[x,-y],[y,x]])/(x*x+y*y).sqrt()
            duo=u*G*((x*dy-y*dx)/(x*x+y*y))
            need(contains(du,duo) and norm(duo)<amp,'POLAR_ORACLE')
        rows.append(dict(id=f'cell_{cell}',status='CERTIFIED',parameter=enc(t),P=mat(ps),dP=mat(dps),F=mat(fs),dF=mat(dfs),M=mat(m),dM=mat(dm),dU=mat(du),source_remainder=enc(es),target_remainder=enc(et),sigma_lower=enc(sg),polar_derivative_bound=enc(amp),oracle_points=3))
    for label,fn,reason in [
        ('contour_contact',lambda:contour(arb(0),3),'CONTOUR_SEPARATION_REQUIRED'),
        ('seam_loss',lambda:polar(R*(arb(9)/10),G),'SEAM_SINGULAR_GATE'),
        ('orientation',lambda:polar(arb_mat([[1,0],[0,-1]]),G),'POSITIVE_DETERMINANT_REQUIRED')]:
        try: fn()
        except ValueError as exc: need(str(exc)==reason,'WRONG_REFUSAL')
        else: raise ValueError('UNSAFE_ACCEPTANCE')
        rows.append(dict(id=label,status='INCONCLUSIVE',reason=reason))
    _,oracle_d=oracle_frame(arb(0))
    need(not overlap_zero(-K0*F0-oracle_d),'KATO_SIGN_MUTATION_ACCEPTED')
    need(not overlap_zero(K0*F0-2*oracle_d),'TARGET_CHAIN_MUTATION_ACCEPTED')
    rows.extend([dict(id='kato_sign',status='MUTATION_REFUSED'),dict(id='target_chain',status='MUTATION_REFUSED')])
    return dict(status='PASS_RESOLVENT_KATO_SEAM',records=rows,checks=len(rows),physical_evaluations=0,panels=N,precision=128,coverage='t in [0,1/128], target parameter 2t in [0,1/64]',bounds=dict(P_prime_operator=3,P_second_operator=24,K_operator=6,K_prime_operator=48,F_second_frobenius=enc(second)))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',action='store_true');ap.add_argument('--wheel',type=Path);ap.add_argument('--output',type=Path);args=ap.parse_args()
    if args.worker:
        resource.setrlimit(resource.RLIMIT_AS,(1073741824,)*2)
        start=time.monotonic();result=worker();result['wall_seconds']=time.monotonic()-start
        print(json.dumps(result));return
    need(args.output is not None and args.wheel is not None,'WHEEL_AND_OUTPUT_REQUIRED')
    from run_calibration import environment
    spec=json.loads((HERE/'SPEC.json').read_text())
    for path,digest in spec['dependencies'].items(): need(sha(HERE.parent/path)==digest,'DEPENDENCY_HASH')
    env=environment(args.wheel,spec);out=begin(args.output)
    for path in list(spec['dependencies'])+['certification_s0q_001/check.py','certification_s0q_001/verify.py','certification_s0q_001/SPEC.json']:
        dest=out/'SOURCE'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(HERE.parent/path,dest)
    shutil.copyfile(HERE.parents[2]/'docs/certification-readiness/S0Q_RESOLVENT_KATO.md',out/'S0Q_RESOLVENT_KATO.md')
    atomic_json(out/'ENVIRONMENT.json',env)
    run=subprocess.run([sys.executable,'-B',str(out/'SOURCE/certification_s0q_001/check.py'),'--worker'],capture_output=True,text=True,timeout=40)
    need(run.returncode==0,run.stderr)
    result=json.loads(run.stdout);finish(out,result);print(json.dumps(verify(out)));print(json.dumps({k:v for k,v in result.items() if k!='records'}))

if __name__=='__main__': main()
