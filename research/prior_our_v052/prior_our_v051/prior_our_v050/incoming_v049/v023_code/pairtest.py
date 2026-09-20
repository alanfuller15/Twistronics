import numpy as np, sys
from bm_strain import BM, frac_dist
from euler import real_frame
from braid import node_winding, transport, adjacent_nodes
A=0.20; phi=float(sys.argv[1]); N=int(sys.argv[2]) if len(sys.argv)>2 else 4
m=BM(N=N,eps=0.003,phi_deg=phi,A_scalar=A)
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
func=lambda f: m.gaps(m.frac_to_k(f))[0]
# the two close nodes near (0.52,0.88): refine from seeds
pair=[]
for seed in [(0.525,0.871),(0.507,0.895),(0.537,0.868),(0.516,0.903)]:
    f,v=m.refine(np.array(seed),func)
    if v<1e-6 and all(frac_dist(f,g)>0.003 for g in pair): pair.append(f)
adj=adjacent_nodes(m,ngrid=36)
print(f"phi={phi} N={N}: close pair {[tuple(np.round(f,4)) for f in pair]}  sep={frac_dist(pair[0],pair[1]):.4f}; adjacent nodes {[tuple(np.round(f,3)) for _,f in adj['+']+adj['-']]}")
r=0.006
s0=pair[0]+np.array([r,0]); s1=pair[1]+np.array([r,0])
base=real_frame(m,U,m.frac_to_k(s0))
w0=node_winding(m,U,pair[0],r,96,base)
w1=node_winding(m,U,pair[1],r,96,transport(m,U,[s0,s1],base,nstep=200))
print(f"   relative charge along the direct segment: w0={w0:+.2f}, w1={w1:+.2f}  ->  {'SAME' if w0*w1>0 else 'OPPOSITE'}")
