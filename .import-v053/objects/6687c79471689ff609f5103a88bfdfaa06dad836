"""Anchor roots and labels for the braid-1 / deepening / unlinking route under the declared model, both engines.
States (A=0.20, phi=0, ratio=0.8, eps=0.003, theta=1.05): B=-0.25, -0.30 (braid-1 window); B=-0.40 (deepened); B=-0.40,T=-0.40 (v028 checkpoint)."""
import numpy as np, sys, time
from bm_strain import BM, sz
from knobs import add_harmonic
from braid import node_winding, transport
from euler import real_frame
from gate import real_basis, classify
from tbg_ref import TBG
N=int(sys.argv[1]) if len(sys.argv)>1 else 4
STATES=[dict(B=-0.25,T=0.0),dict(B=-0.30,T=0.0),dict(B=-0.40,T=0.0),dict(B=-0.40,T=-0.40)]
seeds=[np.array([0.744,0.612]),np.array([0.516,0.828])]
print(f"N={N} kinetic=lab_nn_full geometry=exact (bm) | anchor roots in unwrapped fractional coordinates")
for st in STATES:
    t=time.time()
    # --- bm engine
    a=BM(N=N,eps=0.003,phi_deg=0,A_scalar=0.20,kinetic='lab_nn_full',geometry='exact'); add_harmonic(a,st['B'],mat=sz,use_sin=True)
    if st['T']: add_harmonic(a,st['T'],mat=sz,use_sin=True,layer_sign=-1)
    fa=lambda f: a.gaps(a.frac_to_k(f))[0]; ra=[a.refine(s,fa,return_result=True) for s in seeds]
    Ua=real_basis(a.nG); lo=a.dim//2-1; r=0.012
    p=[x[0] for x in ra]; sa=p[0]+np.array([r,0]); d=((p[1]-p[0])+0.5)%1-0.5; sb=p[0]+d+np.array([r,0]); base=real_frame(a,Ua,a.frac_to_k(sa))
    wa1=node_winding(a,Ua,p[0],r,80,base); wa2=node_winding(a,Ua,p[0]+d,r,80,transport(a,Ua,[sa,sb],base,nstep=250))
    # --- ref engine
    b=TBG(N=N,eps=0.003,phi=0,A=0.20,B=st['B'],Bt=st['T'],kinetic='lab_nn_full'); Ub=b.real_basis()
    q=[b.refine(s,b.flat_gap)[0] for s in seeds]; wb1,wb2,labb=b.relative_charge(Ub,q[0],q[1],b.dim//2-1)
    print(f"  B={st['B']:+.2f} T={st['T']:+.2f}: bm roots {tuple(np.round(p[0],6))} {tuple(np.round(p[1],6))} gaps {ra[0][1]:.0e},{ra[1][1]:.0e} w {wa1:+.2f},{wa2:+.2f} -> {classify(wa1,wa2)} | ref roots {tuple(np.round(q[0],6))} {tuple(np.round(q[1],6))} w {wb1},{wb2} -> {labb} smin {b.last_smin:.3f} | max root diff {max(np.linalg.norm(x-y) for x,y in zip(p,q)):.1e} ({time.time()-t:.0f}s)")
    sys.stdout.flush()
