"""Anchors for NEXT_SEQUENCE items 1-2 under lab_nn_full, both engines (bm exact), N=4.
(1) flat birth: A=-0.35, B=-0.40, T=-1.8, phi=80, ratio 1.10 -> 1.00 (track the two flat nodes down from 1.10)
(2) final annihilation: ratio 1.10, A -0.35 -> -0.30 (track the pair until it vanishes)"""
import numpy as np, sys, json, time
from bm_strain import BM, sz, frac_dist
from knobs import add_harmonic
from braid import node_winding, transport
from euler import real_frame
from gate import real_basis, classify
from tbg_ref import TBG
def bm(A,ratio):
    m=BM(N=4,ratio=ratio,eps=0.003,phi_deg=80,A_scalar=A,kinetic='lab_nn_full',geometry='exact'); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,-1.8,mat=sz,use_sin=True,layer_sign=-1); return m
def ref(A,ratio): return TBG(N=4,eps=0.003,phi=80,A=A,B=-0.40,Bt=-1.8,w0=110.0*ratio,kinetic='lab_nn_full')
def pair_bm(m,seeds):
    fa=lambda f: m.gaps(m.frac_to_k(f))[0]; rs=[m.refine(s,fa,return_result=True) for s in seeds]; p=[r[0] for r in rs]; g=[r[1] for r in rs]
    if max(g)>1e-6 or frac_dist(p[0],p[1])<2e-3: return p,g,None
    U=real_basis(m.nG); d=((p[1]-p[0])+0.5)%1-0.5; r=min(0.012,0.3*np.linalg.norm(d)); sa=p[0]+np.array([r,0]); sb=p[0]+d+np.array([r,0]); base=real_frame(m,U,m.frac_to_k(sa))
    w1=node_winding(m,U,p[0],r,80,base); w2=node_winding(m,U,p[0]+d,r,80,transport(m,U,[sa,sb],base,nstep=250)); return p,g,classify(w1,w2)
rec=[]
print("(1) flat birth window, ratio 1.10 -> 1.00 at A=-0.35:")
seeds=[np.array([0.681,0.967]),np.array([0.682,0.875])]
for ratio in [1.10,1.08,1.06,1.05,1.04,1.03,1.02,1.00]:
    t=time.time(); m=bm(-0.35,ratio); p,g,lab=pair_bm(m,seeds); b=ref(-0.35,ratio); q=[b.refine(s,b.flat_gap)[0] for s in seeds]; gq=[b.flat_gap(x) for x in q]
    sep=frac_dist(p[0],p[1]); print(f"  ratio={ratio:.2f}: bm roots {tuple(np.round(p[0],5))} {tuple(np.round(p[1],5))} gaps {g[0]:.0e},{g[1]:.0e} sep {sep:.4f} label {lab} | ref roots diff {max(np.linalg.norm(x-y) for x,y in zip(p,q)):.1e} gaps {gq[0]:.0e},{gq[1]:.0e} ({time.time()-t:.0f}s)"); sys.stdout.flush()
    rec.append(dict(window='flat_birth',ratio=ratio,A=-0.35,bm_roots=[x.tolist() for x in p],bm_gaps=g,sep=float(sep),label=lab,ref_roots=[x.tolist() for x in q],ref_gaps=gq))
    if max(g)>1e-6: print("     -> pair gone (gap opened): birth is above this ratio"); break
    seeds=p
print("(2) final annihilation window, A -0.35 -> -0.30 at ratio 1.10:")
seeds=[np.array([0.681,0.967]),np.array([0.682,0.875])]
for A in [-0.35,-0.34,-0.33,-0.32,-0.31,-0.30]:
    t=time.time(); m=bm(A,1.10); p,g,lab=pair_bm(m,seeds); b=ref(A,1.10); q=[b.refine(s,b.flat_gap)[0] for s in seeds]; gq=[b.flat_gap(x) for x in q]
    sep=frac_dist(p[0],p[1]); print(f"  A={A:+.2f}: bm roots {tuple(np.round(p[0],5))} {tuple(np.round(p[1],5))} gaps {g[0]:.0e},{g[1]:.0e} sep {sep:.4f} label {lab} | ref roots diff {max(np.linalg.norm(x-y) for x,y in zip(p,q)):.1e} gaps {gq[0]:.0e},{gq[1]:.0e} ({time.time()-t:.0f}s)"); sys.stdout.flush()
    rec.append(dict(window='final_ann',ratio=1.10,A=A,bm_roots=[x.tolist() for x in p],bm_gaps=g,sep=float(sep),label=lab,ref_roots=[x.tolist() for x in q],ref_gaps=gq))
    if max(g)>1e-6: print("     -> pair gone (gap opened): annihilation is below this A"); break
    seeds=p
json.dump(rec,open('anchors_final_N4.json','w'),indent=1)
