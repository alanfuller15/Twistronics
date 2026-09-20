import numpy as np, sys, json, os
from scipy.linalg import eigh
from bm_strain import BM, frac_dist
from check_iso import mk, base, gapfn, inv
from euler import shift_matrix
from final_check import winding, transport2, frame
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
p=dict(base); p.update(json.loads(os.environ.get('P','{}'))); N=int(os.environ.get('NN','4'))
import check_iso; check_iso.N=N
m=mk(p); U=np.kron(np.eye(2*m.nG),u2); D=m.dim; lo=D//2-1
gaps=[inv(m,i)[1] for i in range(4)]; fl=[f for v,f in m.find_nodes(ngrid=30,nkeep=12) if v<1e-6]
print(f"N={N} params {p}\n  gap minima lo|f1 {gaps[0]:.2f}  f1|f2 {gaps[1]:.2e}  f2|up {gaps[2]:.2f}  up|nx {gaps[3]:.2f} meV | flat nodes {[tuple(np.round(f,3)) for f in fl]}")
def euler(lo,nf1=24,nf2=40):
    S2=shift_matrix(m,(0,-1)); S1=shift_matrix(m,(-1,0)); bp=None; b0=None; phis=[]; dets=[]
    for f1 in np.linspace(0,1,nf1,endpoint=False):
        fr=[frame(m,U,m.frac_to_k(np.array([f1,f2])),lo) for f2 in np.linspace(0,1,nf2,endpoint=False)]
        b=fr[0]
        if bp is not None and np.linalg.det(bp.T@b)<0: b=b@np.diag([1,-1]); fr[0]=b
        if b0 is None: b0=b
        bp=b; W=np.eye(2)
        for j in range(nf2-1): W=W@(fr[j].T@fr[j+1])
        W=W@(fr[-1].T@(S2@fr[0])); u,s,vt=np.linalg.svd(W); O=u@vt; dets.append(np.linalg.det(O)); phis.append(np.arctan2(O[1,0],O[0,0]))
    ext=np.unwrap(np.append(np.unwrap(phis),phis[0])); return (ext[-1]-ext[0])/(2*np.pi), np.linalg.det(bp.T@(S1@b0)), min(dets)
e,cl,md=euler(lo); print(f"  Wilson-loop Euler class of the flat pair: e2 = {e:+.3f} (orientation closure {cl:+.2f}, min det {md:+.2f})")
if len(fl)==2:
    r=0.012; a=fl[0]+np.array([r,0]); d=((fl[1]-fl[0])+0.5)%1-0.5; b=fl[0]+d+np.array([r,0]); bf=frame(m,U,m.frac_to_k(a),lo)
    wa=winding(m,U,fl[0],r,80,bf,lo); wb=winding(m,U,fl[0]+d,r,80,transport2(m,U,[a,b],bf,lo),lo)
    print(f"  flat nodes: w={wa:+.2f}, {wb:+.2f} (sep {np.linalg.norm(d):.3f}) -> {'SAME' if wa*wb>0 else 'OPPOSITE'}")
