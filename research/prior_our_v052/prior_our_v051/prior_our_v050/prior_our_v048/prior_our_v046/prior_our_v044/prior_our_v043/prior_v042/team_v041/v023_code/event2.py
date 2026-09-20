import numpy as np, sys
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS
from braid import adjacent_nodes
xa=np.array([-0.0014,-0.3358,-0.0126,-0.3396,0.1222,6.8518,0.0013]); xb=np.array([-0.0104,-0.3294,-0.0197,-0.3786,0.1467,6.9313,0.0009])
m=make(**dict(zip(KEYS,xa))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
fl=[f for v,f in m.find_nodes(ngrid=40,nkeep=20) if v<1e-6]; adj=adjacent_nodes(m,ngrid=36)
print("x_a: flat nodes",[tuple(np.round(f,3)) for f in fl],"adj",len(adj['+']),"+",len(adj['-']),"bw",round(m.flat_bandwidth(10)))
# identify the two originals as the closest pair
import itertools
pair=min(itertools.combinations(fl,2),key=lambda p:frac_dist(*p)); print("closest pair",[tuple(np.round(f,3)) for f in pair],"sep",round(frac_dist(*pair),4))
F1,F3=pair
for lam in [0.2,0.4,0.6,0.8,1.0]:
    x=xa+lam*(xb-xa); m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
    a,va=m.refine(F1,func); b,vb=m.refine(F3,func)
    mid=(F1+F3)/2; c,vc=m.refine(mid,func)
    print(f"lam={lam:.1f}: F1 {tuple(np.round(a,3))} ({va:.1e}) F3 {tuple(np.round(b,3))} ({vb:.1e}) sep={frac_dist(a,b):.4f} | from midpoint -> {tuple(np.round(c,3))} gap {vc:.2e}")
    if max(va,vb)<1e-6 and frac_dist(a,b)>0.005: F1,F3=a,b
    sys.stdout.flush()
m=make(**dict(zip(KEYS,xb)))
fl=[f for v,f in m.find_nodes(ngrid=40,nkeep=20) if v<1e-6]; adj=adjacent_nodes(m,ngrid=36); rem=m.min_remote(ngrid=15,nkeep=4)
print("x_b: flat nodes",[tuple(np.round(f,3)) for f in fl],"adj",len(adj['+']),"+",len(adj['-']),"minrem",f"{rem[0]:.2e}","bw",round(m.flat_bandwidth(10)))
