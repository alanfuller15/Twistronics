import numpy as np, sys, json
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS
from braid import adjacent_nodes
x0=np.array([-0.0122,-0.3281,-0.0211,-0.3864,0.1516,6.9472,0.0008])
for dA in [0.0,0.0025,0.005,0.0078,0.010,0.015]:
    x=x0.copy(); x[0]+=dA; m=make(**dict(zip(KEYS,x)))
    box=lambda fn: min((fn(np.array([a,b])),a,b) for a in np.linspace(0.58,0.70,13) for b in np.linspace(0.68,0.80,13))
    mid=lambda f: m.gaps(m.frac_to_k(f))[0]; lo=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2)); up=lambda f:(lambda w:w[3]-w[2])(m.bands_near_zero(m.frac_to_k(f),2))
    res={}
    for nm,fn in [('mid',mid),('lo',lo),('up',up)]:
        v,a,b=box(fn); f,vv=m.refine(np.array([a,b]),fn); res[nm]=(vv,f)
    # count exact mid nodes in box via fine local grid
    pts=[]
    for a in np.linspace(0.58,0.70,25):
        for b in np.linspace(0.68,0.80,25):
            pts.append((mid(np.array([a,b])),a,b))
    pts.sort(); ex=[]
    for v,a,b in pts[:12]:
        f,vv=m.refine(np.array([a,b]),mid)
        if vv<1e-6 and all(frac_dist(f,g)>0.004 for g in ex): ex.append(f)
    print(f"dA={dA:+.4f}: box-min gaps  mid {res['mid'][0]:.2e} @{tuple(np.round(res['mid'][1],4))}  lo {res['lo'][0]:.2e} @{tuple(np.round(res['lo'][1],4))}  up {res['up'][0]:.2e} @{tuple(np.round(res['up'][1],4))} | exact mid nodes in box: {[tuple(np.round(f,4)) for f in ex]}")
    sys.stdout.flush()
