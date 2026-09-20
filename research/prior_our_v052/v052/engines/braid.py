import numpy as np, sys
from scipy.linalg import eigh
from bm_strain import BM, frac_dist
from euler import real_frame
from gate import ortho_checked as ortho, classify
def node_winding(m,U,center,radius,npts,base):
    ts=np.linspace(0,2*np.pi,npts+1)
    frames=[real_frame(m,U,m.frac_to_k(center+radius*np.array([np.cos(t),np.sin(t)]))) for t in ts]
    e=frames[0].copy()
    if np.linalg.det(base.T@e)<0: e=e@np.diag([1,-1])
    u=frames[0][:,0]; alpha=np.arctan2(e[:,1]@u,e[:,0]@u); tot=0.0
    for j in range(1,npts+1):
        e=ortho((frames[j]@frames[j].T)@e); v=frames[j][:,0]
        if v@u<0: v=-v
        u=v; a=np.arctan2(e[:,1]@u,e[:,0]@u); tot+=(a-alpha+np.pi)%(2*np.pi)-np.pi; alpha=a
    return tot/np.pi
def transport(m,U,pts,base,nstep=60):
    """carry 2-frame orientation along the polyline pts; returns the oriented frame at the end."""
    prev=base
    for a,b in zip(pts[:-1],pts[1:]):
        for s in np.linspace(0,1,nstep)[1:]:
            fr=real_frame(m,U,m.frac_to_k(a+s*(b-a)))
            if np.linalg.det(prev.T@fr)<0: fr=fr@np.diag([1,-1])
            prev=fr
    return prev
def adjacent_nodes(m,ngrid=30):
    """exact crossings between upper flat band and the band above (gap +), and lower flat and band below (gap -)."""
    out={}
    for lab,idx in [('+',(2,3)),('-',(0,1))]:
        func=lambda f: (lambda w: w[idx[1]]-w[idx[0]])(m.bands_near_zero(m.frac_to_k(f),2))
        fs,vals=m.grid(ngrid,func); res=[]
        for v,f1,f2 in m.local_minima(fs,vals,12):
            f,val=m.refine(np.array([f1,f2]),func,tol=1e-10)
            if val<1e-6 and all(frac_dist(f,g)>0.01 for _,g in res): res.append((val,f))
        out[lab]=res
    return out
if __name__=="__main__":
    A=float(sys.argv[1]); N=int(sys.argv[2])
    m=BM(N=N,eps=0.003,A_scalar=A)
    u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
    flat=[f for v,f in m.find_nodes(ngrid=30,nkeep=14) if v<1e-6]
    adj=adjacent_nodes(m)
    print(f"A={A} N={N}")
    print("  flat-gap nodes:",[np.round(f,4) for f in flat])
    print("  upper adjacent-gap nodes:",[np.round(f,4) for _,f in adj['+']])
    print("  lower adjacent-gap nodes:",[np.round(f,4) for _,f in adj['-']])
    r=0.02
    # windings of all flat-gap nodes with orientation transported along straight paths from node 0
    starts=[f+np.array([r,0]) for f in flat]
    base=real_frame(m,U,m.frac_to_k(starts[0]))
    ws=[node_winding(m,U,flat[0],r,64,base)]
    for i in range(1,len(flat)):
        b=transport(m,U,[starts[0],starts[i]],base); ws.append(node_winding(m,U,flat[i],r,64,b))
    print("  windings (straight paths from node 0):",[f"{w:+.2f}" for w in ws])
    # path-dependence test: node 0 -> node 1 along two paths that together encircle a chosen adjacent-gap node
    adjpts=[f for _,f in adj['+']]+[f for _,f in adj['-']]
    if len(flat)>=2 and adjpts:
        p0,p1=starts[0],starts[1]
        for q in adjpts:
            # detour waypoint: reflect the adjacent node across the straight segment so path A passes one side, path B the other
            d=p1-p0; d/=np.linalg.norm(d); n=np.array([-d[1],d[0]])
            off=(q-p0)@n
            wA=q+ n*0.06*np.sign(off) if off!=0 else q+n*0.06   # same side as q, beyond it
            wB=q- n*0.06*np.sign(off) if off!=0 else q-n*0.06   # other side of q
            bA=transport(m,U,[p0,wA,p1],base); bB=transport(m,U,[p0,wB,p1],base)
            w1A=node_winding(m,U,flat[1],r,64,bA); w1B=node_winding(m,U,flat[1],r,64,bB)
            print(f"  node1 winding via path around adjacent node {np.round(q,3)}:  side A {w1A:+.2f}   side B {w1B:+.2f}   (orientation flip: {np.linalg.det(bA.T@bB):+.2f})")
