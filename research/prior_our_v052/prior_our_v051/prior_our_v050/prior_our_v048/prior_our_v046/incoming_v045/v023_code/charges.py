import numpy as np, sys
from bm_strain import BM
from euler import real_frame
from braid import node_winding, transport, adjacent_nodes
A=float(sys.argv[1]); phi=float(sys.argv[2]); N=int(sys.argv[3]) if len(sys.argv)>3 else 4
m=BM(N=N,eps=0.003,phi_deg=phi,A_scalar=A)
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
flat=[f for v,f in m.find_nodes(ngrid=30,nkeep=16) if v<1e-6]
adj=adjacent_nodes(m,ngrid=36); rem=m.min_remote(ngrid=15,nkeep=4)
print(f"A={A} phi={phi} N={N}: flat nodes {len(flat)}, adjacent nodes {len(adj['+'])+len(adj['-'])}, min remote gap {rem[0]:.3e} meV")
r=0.02; starts=[f+np.array([r,0]) for f in flat]
base=real_frame(m,U,m.frac_to_k(starts[0]))
ws=[node_winding(m,U,flat[0],r,64,base)]
for i in range(1,len(flat)):
    ws.append(node_winding(m,U,flat[i],r,64,transport(m,U,[starts[0],starts[i]],base)))
for f,w in zip(flat,ws): print(f"   node {tuple(np.round(f,3))}  w = {w:+.2f}")
print(f"   sum = {sum(round(w) for w in ws):+d}")
