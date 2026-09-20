import numpy as np, sys
from tbg_ref import TBG
kin=sys.argv[1] if len(sys.argv)>1 else 'full'
for Bt in [-0.66,-0.69,-0.70,-0.71]:
    m=TBG(N=4,eps=0.003,phi=65,A=0.0,B=-0.40,Bt=Bt,kinetic=kin); U=m.real_basis(); lo=m.dim//2-1; fn=m.flat_gap
    c=np.array([0.64,0.836]); pts=sorted((fn(np.array([a,b])),a,b) for a in np.linspace(c[0]-0.05,c[0]+0.05,25) for b in np.linspace(c[1]-0.04,c[1]+0.04,25))
    ex=[]
    for v,a,b in pts[:10]:
        f,val=m.refine(np.array([a,b]),fn)
        if val<1e-6 and all(np.linalg.norm(f-g)>0.002 for g in ex): ex.append(f)
    line=f"kinetic={kin} Btau={Bt:+.2f}: exact flat nodes {[tuple(np.round(f,4)) for f in ex]} (box min {pts[0][0]:.2e})"
    if len(ex)==2:
        w1,w2,lab=m.relative_charge(U,ex[0],ex[1],lo); line+=f" sep {np.linalg.norm(ex[0]-ex[1]):.4f} charges {w1:+d},{w2:+d} -> {lab}"
    print(line); sys.stdout.flush()
