import numpy as np, sys
from scipy.linalg import eigh
from bm_strain import BM, frac_dist, sz
from knobs import add_harmonic
from braid import adjacent_nodes, transport
from euler import real_frame
def mk(Bt): 
    m=BM(N=4,eps=0.003,phi_deg=65,A_scalar=0.0); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,Bt,mat=sz,use_sin=True,layer_sign=-1); return m
from gate import real_frame_checked, ortho_checked as ortho, classify
def frame(m,U,k,lo):
    return real_frame_checked(m,U,k,lo)
def winding(m,U,center,radius,npts,base,lo):
    ts=np.linspace(0,2*np.pi,npts+1); fr=[frame(m,U,m.frac_to_k(center+radius*np.array([np.cos(t),np.sin(t)])),lo) for t in ts]
    e=fr[0].copy()
    if np.linalg.det(base.T@e)<0: e=e@np.diag([1,-1])
    u=fr[0][:,0]; al=np.arctan2(e[:,1]@u,e[:,0]@u); tot=0
    for j in range(1,npts+1):
        e=ortho((fr[j]@fr[j].T)@e); v=fr[j][:,0]
        if v@u<0: v=-v
        u=v; a=np.arctan2(e[:,1]@u,e[:,0]@u); tot+=(a-al+np.pi)%(2*np.pi)-np.pi; al=a
    return tot/np.pi
def transport2(m,U,pts,base,lo,n=200):
    prev=base
    for a,b in zip(pts[:-1],pts[1:]):
        for s in np.linspace(0,1,n)[1:]:
            f=frame(m,U,m.frac_to_k(a+s*(b-a)),lo)
            if np.linalg.det(prev.T@f)<0: f=f@np.diag([1,-1])
            prev=f
    return prev
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
if __name__=='__main__':
    # (1) F pair charge at -0.70 with correct seeds
    m=mk(-0.70); U=np.kron(np.eye(2*m.nG),u2); D=m.dim; func=lambda f: m.gaps(m.frac_to_k(f))[0]
    F1,v1=m.refine(np.array([0.6495,0.8384]),func); F3,v3=m.refine(np.array([0.6283,0.8343]),func)
    r=0.004; a=F1+np.array([r,0]); b=F3+np.array([r,0]); base=frame(m,U,m.frac_to_k(a),D//2-1)
    w1=winding(m,U,F1,r,96,base,D//2-1); w3=winding(m,U,F3,r,96,transport2(m,U,[a,b],base,D//2-1),D//2-1)
    print(f"Btau=-0.70: F1 {tuple(np.round(F1,4))} ({v1:.0e}) w={w1:+.2f}  F3 {tuple(np.round(F3,4))} ({v3:.0e}) w={w3:+.2f} sep={frac_dist(F1,F3):.4f} -> {classify(w1,w3)}")
    # (2) global inventory at -0.74
    m=mk(-0.74); U=np.kron(np.eye(2*m.nG),u2)
    fl=m.find_nodes(ngrid=36,nkeep=18); ex=[f for v,f in fl if v<1e-6]; adj=adjacent_nodes(m,ngrid=36)
    up=lambda f:(lambda w:w[3]-w[2])(m.bands_near_zero(m.frac_to_k(f),2)); lo_=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2))
    fs,vals=m.grid(15,lo_); lomin=min(m.refine(np.array(c[1:]),lo_)[1] for c in m.local_minima(fs,vals,3))
    print(f"Btau=-0.74: flat-gap nodes {len(ex)} (global min mid gap {fl[0][0]:.3f} meV at {tuple(np.round(fl[0][1],3))}) | upper nodes {[tuple(np.round(f,3)) for _,f in adj['+']]} | lower nodes {len(adj['-'])} (min {lomin:.2f} meV) | bw {m.flat_bandwidth(10):.0f}")
    # (3) U pair relative charge in the (flat2, upper) frame
    Uz=[f for _,f in adj['+']]
    if len(Uz)==2:
        lo=D//2; a=Uz[0]+np.array([0.012,0]); b=Uz[1]+np.array([0.012,0]); base=frame(m,U,m.frac_to_k(a),lo)
        wa=winding(m,U,Uz[0],0.012,80,base,lo); wb=winding(m,U,Uz[1],0.012,80,transport2(m,U,[a,b],base,lo),lo)
        print(f"   U pair (upper-gap 2-frame): w={wa:+.2f}, {wb:+.2f} along straight segment (sep {frac_dist(*Uz):.3f}) -> {classify(wa,wb)}")
