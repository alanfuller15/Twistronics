import numpy as np, sys
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS
from braid import adjacent_nodes
x0=np.array([-0.0122,-0.3281,-0.0211,-0.3864,0.1516,6.9472,0.0008])
F1=np.array([0.6538,0.7426]); F3=np.array([0.6211,0.7298])
for B in [-0.328,-0.30,-0.27,-0.24,-0.21,-0.18]:
    x=x0.copy(); x[1]=B; m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
    a,va=m.refine(F1,func); b,vb=m.refine(F3,func)
    adj=adjacent_nodes(m,ngrid=36); fl=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]
    d=b-a; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L
    offs=[(lab,tuple(np.round(q,3)),round(float((((q-a)+0.5)%1-0.5)@d/L**2),2),round(float((((q-a)+0.5)%1-0.5)@n),3)) for lab,lst in (('U',adj['+']),('L',adj['-'])) for _,q in lst]
    print(f"B={B:+.3f}: F1 {tuple(np.round(a,3))} ({va:.0e}) F3 {tuple(np.round(b,3))} ({vb:.0e}) sep={frac_dist(a,b):.3f} | flat total {len(fl)} | adj (label,pos,t,off): {offs}")
    sys.stdout.flush()
    if max(va,vb)<1e-6: F1,F3=a,b
