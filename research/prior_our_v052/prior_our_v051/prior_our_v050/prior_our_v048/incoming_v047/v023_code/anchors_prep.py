"""Anchors for the preparation leg A: 0 -> 0.2 (B=T=0, phi=0, ratio=0.8, eps=0.003) under lab_nn_full, both engines.
Reports the flat pair (roots, label), the remote-gap minimum, and upper-gap nodes once they exist."""
import numpy as np, sys, time, json
from bm_strain import BM
from braid import node_winding, transport, adjacent_nodes
from euler import real_frame
from gate import real_basis, classify
from tbg_ref import TBG
N=int(sys.argv[1]) if len(sys.argv)>1 else 4
seeds=[np.array([0.7594,0.6066]),np.array([0.5816,0.7266])]
out=[]
for A in [0.0,0.05,0.10,0.14,0.16,0.20]:
    t=time.time()
    a=BM(N=N,eps=0.003,phi_deg=0,A_scalar=A,kinetic='lab_nn_full',geometry='exact'); fa=lambda f: a.gaps(a.frac_to_k(f))[0]
    ra=[a.refine(s,fa,return_result=True) for s in seeds]; p=[x[0] for x in ra]
    Ua=real_basis(a.nG); r=0.012; sa=p[0]+np.array([r,0]); d=((p[1]-p[0])+0.5)%1-0.5; sb=p[0]+d+np.array([r,0]); base=real_frame(a,Ua,a.frac_to_k(sa))
    wa1=node_winding(a,Ua,p[0],r,80,base); wa2=node_winding(a,Ua,p[0]+d,r,80,transport(a,Ua,[sa,sb],base,nstep=250)); la=classify(wa1,wa2)
    rem=a.min_remote(ngrid=15,nkeep=4); adj=adjacent_nodes(a,ngrid=24)
    b=TBG(N=N,eps=0.003,phi=0,A=A,kinetic='lab_nn_full'); Ub=b.real_basis(); q=[b.refine(s,b.flat_gap)[0] for s in seeds]; wb1,wb2,lb=b.relative_charge(Ub,q[0],q[1],b.dim//2-1)
    rec=dict(A=A,N=N,bm_roots=[x.tolist() for x in p],bm_gaps=[x[1] for x in ra],bm_label=la,ref_roots=[x.tolist() for x in q],ref_label=lb,max_root_diff=float(max(np.linalg.norm(x-y) for x,y in zip(p,q))),
             bm_min_remote=float(rem[0]),bm_min_remote_at=rem[1].tolist(),bm_upper_nodes=[f.tolist() for _,f in adj['+']],bm_lower_nodes=[f.tolist() for _,f in adj['-']])
    out.append(rec)
    print(f"  A={A:.2f}: flat roots {tuple(np.round(p[0],6))} {tuple(np.round(p[1],6))} | bm {la} ref {lb} | root diff {rec['max_root_diff']:.1e} | min remote {rem[0]:.4f} meV at {tuple(np.round(rem[1],3))} | upper nodes {[tuple(np.round(f,3)) for f in rec['bm_upper_nodes']]} lower {[tuple(np.round(f,3)) for f in rec['bm_lower_nodes']]} ({time.time()-t:.0f}s)")
    sys.stdout.flush()
json.dump(out,open(f'anchors_prep_N{N}.json','w'),indent=1)
