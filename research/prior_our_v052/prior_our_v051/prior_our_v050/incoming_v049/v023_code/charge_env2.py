import numpy as np, sys, json, os
from bm_strain import BM, frac_dist, sz, s0, sx, sy
from knobs import add_harmonic
from braid import node_winding, transport, adjacent_nodes
from euler import real_frame
MATS={'sz':sz,'s0':s0,'sx':sx,'sy':sy}
BASES=json.loads(os.environ.get('BASE_KNOBS','[]')); A=float(os.environ.get('A','0.20')); phi=float(os.environ.get('PHI','0')); N=int(os.environ.get('NN','4'))
m=BM(N=N,eps=0.003,phi_deg=phi,A_scalar=A)
for amp,sp in BASES:
    sp=dict(sp); add_harmonic(m,amp,mat=MATS[sp.pop('mat')],**sp)
func=lambda f: m.gaps(m.frac_to_k(f))[0]
F1,v1=m.refine(np.array(json.loads(sys.argv[1])),func); F3,v3=m.refine(np.array(json.loads(sys.argv[2])),func); assert max(v1,v3)<1e-6
adj=adjacent_nodes(m,ngrid=30)
print("flat:",[tuple(np.round(f,3)) for v,f in m.find_nodes(ngrid=30,nkeep=12) if v<1e-6],"upper:",[tuple(np.round(f,3)) for _,f in adj['+']],"lower:",[tuple(np.round(f,3)) for _,f in adj['-']])
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
r=0.012; a=F1+np.array([r,0]); b=F3+np.array([r,0]); base=real_frame(m,U,m.frac_to_k(a))
w1=node_winding(m,U,F1,r,80,base); w3=node_winding(m,U,F3,r,80,transport(m,U,[a,b],base,nstep=200))
print(f"N={N}: F1 {tuple(np.round(F1,4))} w={w1:+.2f}  F3 {tuple(np.round(F3,4))} w={w3:+.2f}  sep={frac_dist(F1,F3):.3f} -> {'SAME' if w1*w3>0 else 'OPPOSITE'}")
