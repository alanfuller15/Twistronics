import numpy as np, json, sys
from bm_strain import BM, frac_dist
from sep import make
from braid import adjacent_nodes
from descend import KEYS
x3=np.array([0.1326,-0.3661,0.0045,-0.02,0.0113,84.3659,0.003]); x4=np.array([0.1103,-0.3994,0.0232,-0.0382,0.0036,86.8956,0.0028])
F1=np.array([0.70,0.68]); F3=np.array([0.62,0.53])
for lam in [0.0,0.25,0.5,0.75,1.0]:
    x=x3+lam*(x4-x3); m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
    a,va=m.refine(F1,func); b,vb=m.refine(F3,func)
    # local minimum of mid gap in the box around the pair
    f1s=np.linspace(0.55,0.80,14); f2s=np.linspace(0.45,0.75,14)
    vals=[(func(np.array([p,q])),p,q) for p in f1s for q in f2s]; vmin=min(vals)
    fmin,vm=m.refine(np.array(vmin[1:]),func)
    print(f"lam={lam:.2f}: tracker F1 {tuple(np.round(a,3))} ({va:.1e}) F3 {tuple(np.round(b,3))} ({vb:.1e}) sep={frac_dist(a,b):.4f} | box min gap {vm:.2e} at {tuple(np.round(fmin,3))}")
    if lam in (0.0,1.0):
        fl=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]; adj=adjacent_nodes(m,ngrid=36); rem=m.min_remote(ngrid=15,nkeep=4)
        print(f"     all flat nodes: {[tuple(np.round(f,3)) for f in fl]} | adj {len(adj['+'])}+{len(adj['-'])} | minrem {rem[0]:.2e} | bw {m.flat_bandwidth(10):.0f}")
    sys.stdout.flush()
