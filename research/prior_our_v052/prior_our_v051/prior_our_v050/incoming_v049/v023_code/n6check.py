import numpy as np
from scipy.linalg import eigh
from bm_strain import BM, frac_dist, sz
from knobs import add_harmonic
from final_check import winding, transport2, frame
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
def mk(Bt):
    m=BM(N=6,eps=0.003,phi_deg=65,A_scalar=0.0); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,Bt,mat=sz,use_sin=True,layer_sign=-1); return m
m=mk(-0.70); U=np.kron(np.eye(2*m.nG),u2); D=m.dim; func=lambda f: m.gaps(m.frac_to_k(f))[0]
F1,v1=m.refine(np.array([0.6495,0.8384]),func); F3,v3=m.refine(np.array([0.6283,0.8343]),func)
r=0.004; a=F1+np.array([r,0]); b=F3+np.array([r,0]); base=frame(m,U,m.frac_to_k(a),D//2-1)
w1=winding(m,U,F1,r,96,base,D//2-1); w3=winding(m,U,F3,r,96,transport2(m,U,[a,b],base,D//2-1),D//2-1)
print(f"N=6 Btau=-0.70: F1 {tuple(np.round(F1,4))} ({v1:.0e}) w={w1:+.2f}; F3 {tuple(np.round(F3,4))} ({v3:.0e}) w={w3:+.2f}; sep {frac_dist(F1,F3):.4f} -> {'SAME' if w1*w3>0 else 'OPPOSITE'}")
m=mk(-0.74); fl=m.find_nodes(ngrid=30,nkeep=16); ex=[f for v,f in fl if v<1e-6]
print(f"N=6 Btau=-0.74: exact flat-gap nodes {len(ex)}; global min mid gap {fl[0][0]:.3f} meV at {tuple(np.round(fl[0][1],3))}")
