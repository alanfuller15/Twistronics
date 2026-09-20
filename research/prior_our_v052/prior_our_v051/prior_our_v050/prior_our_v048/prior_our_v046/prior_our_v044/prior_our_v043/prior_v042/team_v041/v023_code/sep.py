import numpy as np, sys
from bm_strain import BM, frac_dist
from knobs import add_harmonic, KNOBS
def make(A=0.20,Bz=-0.30,eps=0.003,phi=0.0,Bt=0.0,Bx=0.0,ratio=0.8,theta=1.05,Bz_single=0.0):
    m=BM(N=4,theta_deg=theta,ratio=ratio,eps=eps,phi_deg=phi,A_scalar=A)
    add_harmonic(m,Bz,**KNOBS['sz_sin'])
    if Bt: add_harmonic(m,Bt,**KNOBS['tauz'])
    if Bx: add_harmonic(m,Bx,**KNOBS['sx'])
    if Bz_single: add_harmonic(m,Bz_single,mat=__import__('bm_strain').sz,use_sin=True,which=(0,))
    return m
import json,os
BASE=json.loads(os.environ.get('BASE','{}'))
def track(param,values,F1=np.array(json.loads(os.environ.get('F1','[0.738,0.611]'))),F3=np.array(json.loads(os.environ.get('F3','[0.518,0.827]')))):
    for v in values:
        kw=dict(BASE); kw[param]=v; m=make(**kw); func=lambda f: m.gaps(m.frac_to_k(f))[0]
        F1,v1=m.refine(F1,func); F3,v3=m.refine(F3,func)
        print(f"  {param}={v:+.3f}: F1 {tuple(np.round(F1,3))} ({v1:.0e})  F3 {tuple(np.round(F3,3))} ({v3:.0e})  sep={frac_dist(F1,F3):.3f}")
        sys.stdout.flush()
        if v1>1e-6 or v3>1e-6:
            print(f"     -> gap opened: refined points coincide? dist={frac_dist(F1,F3):.4f}, min mid gap there {min(v1,v3):.2e}"); break
if __name__=="__main__":
    param=sys.argv[1]; vals=[float(x) for x in sys.argv[2:]]
    track(param,vals)
