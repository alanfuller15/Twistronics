import numpy as np, time, sys
from tbg_ref import TBG
vr = sys.argv[1]=='1' if len(sys.argv)>1 else True
print(f"v026 braid test, second implementation, velocity-renormalisation={vr}")
for B in [-0.25,-0.30]:
    t=time.time(); m=TBG(N=4,eps=0.003,phi=0.0,A=0.20,B=B,vrenorm=vr); U=m.real_basis(); lo=m.dim//2-1
    nodes=m.find_nodes(n=24,keep=8)
    if len(nodes)!=2: print(f"  B={B:+.2f}: {len(nodes)} nodes found {[tuple(np.round(f,3)) for f in nodes]} -> not a clean pair, skipping"); continue
    w1,w2,lab=m.relative_charge(U,nodes[0],nodes[1],lo)
    print(f"  B={B:+.2f}: nodes {tuple(np.round(nodes[0],4))} {tuple(np.round(nodes[1],4))} | charges {w1:+d},{w2:+d} -> {lab}   (bm_strain: {'SAME' if B==-0.25 else 'OPPOSITE'})  ({time.time()-t:.0f}s)")
