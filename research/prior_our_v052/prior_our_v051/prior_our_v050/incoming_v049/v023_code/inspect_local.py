import numpy as np, sys, json, os
from bm_strain import BM, frac_dist
from check_iso import mk, gapfn, base
c=np.array(json.loads(os.environ.get('C','[0.62,0.90]'))); R=float(os.environ.get('R','0.08'))
def inv(m,i,n=25):
    fn=gapfn(m,i); pts=sorted((fn(np.array([a,b])),a,b) for a in np.linspace(c[0]-R,c[0]+R,n) for b in np.linspace(c[1]-R,c[1]+R,n)); ex=[]
    for v,a,b in pts[:8]:
        f,vv=m.refine(np.array([a,b]),fn)
        if vv<1e-6 and all(frac_dist(f,g)>0.003 for g in ex) and frac_dist(f,c)<R*1.5: ex.append(f)
    return ex,pts[0][0]
key=sys.argv[1]
for v in [float(x) for x in sys.argv[2:]]:
    p=dict(base); p[key]=v; m=mk(p); out=[]
    for i,lab in enumerate(['f1|f2','f2|up','up|nx']):
        ex,gm=inv(m,i+1); out.append(f"{lab}: {len(ex)} nodes {[tuple(np.round(f,4)) for f in ex]} (box grid min {gm:.2e})")
    print(f"{key}={v:.3f} | "+" | ".join(out)); sys.stdout.flush()
