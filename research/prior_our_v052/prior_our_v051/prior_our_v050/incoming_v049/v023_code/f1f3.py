import numpy as np, sys
from bm_strain import BM, frac_dist
from euler import real_frame
from braid import node_winding, transport
A=float(sys.argv[1]); phi=float(sys.argv[2]); s1=eval(sys.argv[3]); s3=eval(sys.argv[4])
m=BM(N=4,eps=0.003,phi_deg=phi,A_scalar=A)
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
func=lambda f: m.gaps(m.frac_to_k(f))[0]
F1,v1=m.refine(np.array(s1),func); F3,v3=m.refine(np.array(s3),func)
assert v1<1e-6 and v3<1e-6
r=0.015; a=F1+np.array([r,0]); b=F3+np.array([r,0])
base=real_frame(m,U,m.frac_to_k(a))
w1=node_winding(m,U,F1,r,64,base); w3=node_winding(m,U,F3,r,64,transport(m,U,[a,b],base,nstep=150))
print(f"A={A} phi={phi}: F1 {tuple(np.round(F1,3))} w={w1:+.2f}; F3 {tuple(np.round(F3,3))} w={w3:+.2f} along straight F1-F3 segment -> {'SAME' if w1*w3>0 else 'OPPOSITE'}")
