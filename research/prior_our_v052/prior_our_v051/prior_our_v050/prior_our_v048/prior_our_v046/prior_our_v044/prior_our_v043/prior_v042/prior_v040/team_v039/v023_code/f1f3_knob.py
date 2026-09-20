import numpy as np, sys
from bm_strain import BM, frac_dist
from euler import real_frame
from braid import node_winding, transport
from knobs import add_harmonic, KNOBS
name=sys.argv[1]
for B in [float(x) for x in sys.argv[2:]]:
    m=BM(N=int(__import__("os").environ.get("NN","4")),eps=0.003,phi_deg=0,A_scalar=0.20); add_harmonic(m,B,**KNOBS[name])
    u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
    func=lambda f: m.gaps(m.frac_to_k(f))[0]
    F1,v1=m.refine(np.array([0.75,0.62]),func); F3,v3=m.refine(np.array([0.52,0.83]),func)
    assert v1<1e-6 and v3<1e-6,(v1,v3)
    r=0.012; a=F1+np.array([r,0]); b=F3+np.array([r,0])
    base=real_frame(m,U,m.frac_to_k(a))
    w1=node_winding(m,U,F1,r,80,base); w3=node_winding(m,U,F3,r,80,transport(m,U,[a,b],base,nstep=250))
    print(f"{name} B={B:+.2f}: F1 {tuple(np.round(F1,3))} w={w1:+.2f}; F3 {tuple(np.round(F3,3))} w={w3:+.2f}  straight segment -> {'SAME' if w1*w3>0 else 'OPPOSITE'}")
    sys.stdout.flush()
