import numpy as np, time
from bm_strain import BM, sz
from knobs import add_harmonic
from braid import node_winding, transport
from euler import real_frame
from gate import real_basis, classify
def measure(kw, mode, B=0.0, A=0.0):
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=A,kinetic='lab_nn_full',geometry='exact',w_kappa=kw,w_mode=mode)
    if B: add_harmonic(m,B,mat=sz,use_sin=True)
    nodes=[f for v,f in m.find_nodes(ngrid=15,nkeep=6) if v<1e-6]
    if len(nodes)!=2: return f"{len(nodes)} nodes"
    rem=m.min_remote(ngrid=15,nkeep=4)[0]; U=real_basis(m.nG); r=0.012
    a=nodes[0]+np.array([r,0]); d=((nodes[1]-nodes[0])+0.5)%1-0.5; b=nodes[0]+d+np.array([r,0]); base=real_frame(m,U,m.frac_to_k(a))
    w1=node_winding(m,U,nodes[0],r,80,base); w2=node_winding(m,U,nodes[0]+d,r,80,transport(m,U,[a,b],base,nstep=250))
    Tscale=[abs(np.linalg.norm(m.T[j])/np.linalg.norm(BM(N=3).T[j])) for j in range(3)]
    return f"T_j scale {np.round(Tscale,5).tolist()} | nodes {[tuple(np.round(f,4)) for f in nodes]} sep {np.linalg.norm(d):.4f} | remote gap {rem:.4f} meV | {classify(w1,w2)}"
print("baseline (0.3% heterostrain, lab_nn_full, exact):")
for mode,kw in [('average',0.0),('average',5.0),('average',-5.0),('layer1',5.0),('layer1',-5.0)]:
    t=time.time(); print(f"  w_mode={mode:8s} kappa={kw:+.1f}: {measure(kw,mode)} ({time.time()-t:.0f}s)")
print("braid-1 window (A=0.2, B_sym=-0.25 / -0.30), worst case layer1 kappa=+-5:")
for kw in (5.0,-5.0):
    for B in (-0.25,-0.30):
        t=time.time(); print(f"  kappa={kw:+.1f} B={B:+.2f}: {measure(kw,'layer1',B=B,A=0.20)} ({time.time()-t:.0f}s)")
