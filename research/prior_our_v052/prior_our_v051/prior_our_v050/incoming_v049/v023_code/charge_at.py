import numpy as np, sys, json
from bm_strain import BM, frac_dist
from euler import real_frame
from braid import node_winding, transport
from sep import make
from descend import KEYS
x=json.loads(sys.argv[1]); F1=np.array(json.loads(sys.argv[2])); F3=np.array(json.loads(sys.argv[3]))
m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
F1,v1=m.refine(F1,func); F3,v3=m.refine(F3,func); assert max(v1,v3)<1e-6
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
r=0.008; a=F1+np.array([r,0]); b=F3+np.array([r,0]); base=real_frame(m,U,m.frac_to_k(a))
w1=node_winding(m,U,F1,r,80,base); w3=node_winding(m,U,F3,r,80,transport(m,U,[a,b],base,nstep=200))
print(f"x={np.round(x,4).tolist()}: F1 {tuple(np.round(F1,3))} w={w1:+.2f}  F3 {tuple(np.round(F3,3))} w={w3:+.2f}  sep={frac_dist(F1,F3):.3f}  -> {'SAME' if w1*w3>0 else 'OPPOSITE'}")
