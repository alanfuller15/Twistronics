import numpy as np, sys
from scipy.linalg import eigh
from bm_strain import BM
from euler import real_frame
from gate import ortho_checked as ortho, classify
def node_winding(m,U,center,radius,npts,base):
    """Rotation angle (units of pi) of the lower flat-band real eigenvector inside the parallel-
    transported, orientation-fixed 2-band frame, around a circle about 'center'."""
    ts=np.linspace(0,2*np.pi,npts+1)
    frames=[real_frame(m,U,m.frac_to_k(center+radius*np.array([np.cos(t),np.sin(t)]))) for t in ts]
    e=frames[0].copy()
    if np.linalg.det(base.T@e)<0: e=e@np.diag([1,-1])
    u=frames[0][:,0]; alpha0=np.arctan2(e[:,1]@u,e[:,0]@u); alpha=alpha0; tot=0.0
    for j in range(1,npts+1):
        P=frames[j]@frames[j].T
        e=ortho(P@e)               # parallel transport of the 2-frame
        v=frames[j][:,0]
        if v@u<0: v=-v             # continuity of the eigenvector sign
        u=v
        a=np.arctan2(e[:,1]@u,e[:,0]@u)
        d=(a-alpha+np.pi)%(2*np.pi)-np.pi; tot+=d; alpha=a
    hol=np.arctan2((e.T@frames[0])[1,0],(e.T@frames[0])[0,0])  # residual holonomy of the frame
    return tot/np.pi, hol/np.pi
eps=0.003; N=int(sys.argv[1]); A=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
m=BM(N=N,eps=eps,A_scalar=A)
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
nodes=[f for v,f in m.find_nodes(ngrid=15,nkeep=6) if v<1e-6]
print("A=",A,"N=",N,"nodes:",[np.round(f,4) for f in nodes])
r=0.02
starts=[f+np.array([r,0]) for f in nodes]
base=real_frame(m,U,m.frac_to_k(starts[0]))
w1,h1=node_winding(m,U,nodes[0],r,64,base)
prev=base
for s in np.linspace(0,1,80)[1:]:
    fr=real_frame(m,U,m.frac_to_k(starts[0]+s*(starts[1]-starts[0])))
    if np.linalg.det(prev.T@fr)<0: fr=fr@np.diag([1,-1])
    prev=fr
w2,h2=node_winding(m,U,nodes[1],r,64,prev)
print(f"  node1: eigenvector rotation = {w1:+.3f} pi (frame holonomy {h1:+.3f} pi)")
print(f"  node2: eigenvector rotation = {w2:+.3f} pi (frame holonomy {h2:+.3f} pi)")
print(f"  -> windings w1={round(w1):+d}, w2={round(w2):+d}, sum={round(w1)+round(w2):+d}  (theorem: sum = 2 e2)")
