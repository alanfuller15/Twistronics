import numpy as np, sys
from bm_strain import BM, frac_dist
from euler import real_frame
from braid import node_winding, transport, adjacent_nodes
from sep import make
from descend import KEYS
xa=np.array([-0.0014,-0.3358,-0.0126,-0.3396,0.1222,6.8518,0.0013]); xb=np.array([-0.0104,-0.3294,-0.0197,-0.3786,0.1467,6.9313,0.0009])
x=xa+1.2*(xb-xa); m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
F1,v1=m.refine(np.array([0.654,0.743]),func); F3,v3=m.refine(np.array([0.621,0.730]),func); assert max(v1,v3)<1e-6
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
r=0.006; a=F1+np.array([r,0]); b=F3+np.array([r,0]); base=real_frame(m,U,m.frac_to_k(a))
w1=node_winding(m,U,F1,r,96,base); w3=node_winding(m,U,F3,r,96,transport(m,U,[a,b],base,nstep=200))
print(f"close pair: F1 {tuple(np.round(F1,4))} w={w1:+.2f}  F3 {tuple(np.round(F3,4))} w={w3:+.2f}  sep={frac_dist(F1,F3):.4f} -> {'SAME' if w1*w3>0 else 'OPPOSITE'}")
