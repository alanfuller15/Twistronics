import numpy as np, sys
from bm_strain import BM, frac_dist
from euler import real_frame
from braid import adjacent_nodes
def orientation_holonomy(m,U,center,radius,npts=200):
    ts=np.linspace(0,2*np.pi,npts+1)
    prev=None; first=None
    for t in ts:
        fr=real_frame(m,U,m.frac_to_k(center+radius*np.array([np.cos(t),np.sin(t)])))
        if prev is not None and np.linalg.det(prev.T@fr)<0: fr=fr@np.diag([1,-1])
        if first is None: first=fr
        prev=fr
    return np.linalg.det(first.T@prev)
if __name__=="__main__":
    A=float(sys.argv[1]); N=int(sys.argv[2])
    m=BM(N=N,eps=0.003,A_scalar=A)
    u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
    flat=[f for v,f in m.find_nodes(ngrid=30,nkeep=14) if v<1e-6]
    adj=adjacent_nodes(m,ngrid=36)
    print(f"A={A} N={N}: flat-gap nodes {len(flat)}, upper-gap nodes {len(adj['+'])}, lower-gap nodes {len(adj['-'])}")
    for lab,lst in [('flat',flat),('upper',[f for _,f in adj['+']]),('lower',[f for _,f in adj['-']])]:
        for f in lst:
            print(f"   {lab:5s} node {np.round(f,4)}: orientation holonomy of the flat 2-frame around it = {orientation_holonomy(m,U,f,0.03):+.2f}")
