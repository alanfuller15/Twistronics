import numpy as np, sys
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS
x0=np.array([-0.0122,-0.3281,-0.0211,-0.3864,0.1516,6.9472,0.0008])
def inventory(m,fn,lo=(0.56,0.62),hi=(0.74,0.82),n=29):
    pts=sorted((fn(np.array([a,b])),a,b) for a in np.linspace(lo[0],hi[0],n) for b in np.linspace(lo[1],hi[1],n))
    ex=[]
    for v,a,b in pts[:14]:
        f,vv=m.refine(np.array([a,b]),fn)
        if vv<1e-6 and all(frac_dist(f,g)>0.004 for g in ex): ex.append(f)
    return ex, pts[0][0]
for B in [-0.24,-0.225,-0.21,-0.18]:
    x=x0.copy(); x[1]=B; m=make(**dict(zip(KEYS,x)))
    mid=lambda f: m.gaps(m.frac_to_k(f))[0]; lo=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2)); up=lambda f:(lambda w:w[3]-w[2])(m.bands_near_zero(m.frac_to_k(f),2))
    out={nm:inventory(m,fn) for nm,fn in [('mid',mid),('lo',lo),('up',up)]}
    print(f"B={B:+.3f}: "+" | ".join(f"{nm}: {len(ex)} nodes {[tuple(np.round(f,3)) for f in ex]} (grid min {gm:.1e})" for nm,(ex,gm) in out.items()))
    sys.stdout.flush()
