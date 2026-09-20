import numpy as np, sys
from bm_strain import BM
from tbg_ref import TBG
def rem_bm(m):
    return m.min_remote(ngrid=15,nkeep=4)[0]
for kin in ['none','full','lab_nn_full']:
    a=BM(N=4,eps=0.003,kinetic=kin); b=TBG(N=4,eps=0.003,kinetic=kin)
    na=sorted([f for v,f in a.find_nodes(ngrid=15,nkeep=6) if v<1e-6],key=lambda f:f[0]); nb=sorted(b.find_nodes(n=15,keep=6),key=lambda f:f[0])
    dn=max(np.linalg.norm(((x-y)+0.5)%1-0.5) for x,y in zip(na,nb))
    ra=rem_bm(a); rb=b.gap_min(3 if False else 1,n=15,keep=3)  # lower|flat1 minimum in tbg_ref... use remote_gap instead
    seeds=sorted([(b.remote_gap(np.array([p,q])),p,q) for p in np.linspace(0,1,15,endpoint=False) for q in np.linspace(0,1,15,endpoint=False)])[:3]
    rb=min(b.refine(np.array([p,q]),b.remote_gap)[1] for _,p,q in seeds)
    U=b.real_basis(); w1,w2,lab=b.relative_charge(U,nb[0],nb[1],b.dim//2-1)
    print(f"kinetic={kin:12s}: nodes bm {[tuple(np.round(f,5)) for f in na]} | max node diff bm-vs-ref {dn:.1e} | remote gap bm {ra:.4f} ref {rb:.4f} meV | ref charges {w1},{w2} {lab} smin {b.last_smin:.3f}")
