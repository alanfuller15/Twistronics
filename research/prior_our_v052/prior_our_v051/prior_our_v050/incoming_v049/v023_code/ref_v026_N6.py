import numpy as np, time
from tbg_ref import TBG
for B in [-0.25,-0.30]:
    t=time.time(); m=TBG(N=6,eps=0.003,A=0.20,B=B); U=m.real_basis(); lo=m.dim//2-1
    fn=m.flat_gap; seeds=[np.array([0.516,0.828]),np.array([0.742,0.612])]
    nodes=[m.refine(s,fn)[0] for s in seeds]; gaps=[fn(f) for f in nodes]
    w1,w2,lab=m.relative_charge(U,nodes[0],nodes[1],lo)
    print(f"N=6 B={B:+.2f}: nodes {tuple(np.round(nodes[0],4))} ({gaps[0]:.0e}) {tuple(np.round(nodes[1],4))} ({gaps[1]:.0e}) | charges {w1:+d},{w2:+d} -> {lab} ({time.time()-t:.0f}s)")
