import numpy as np
from tbg_ref import TBG
for N,vr in [(4,True),(4,False),(6,True),(6,False)]:
    m=TBG(N=N,eps=0.003,vrenorm=vr)
    seeds=sorted([(m.remote_gap(np.array([a,b])),a,b) for a in np.linspace(0,1,15,endpoint=False) for b in np.linspace(0,1,15,endpoint=False)])[:3]
    rem=min(m.refine(np.array([a,b]),m.remote_gap)[1] for _,a,b in seeds)
    nodes=m.find_nodes(n=15,keep=6)
    print(f"N={N} velocity-renormalisation={vr}: remote gap {rem:.4f} meV; nodes {[tuple(np.round(f,5)) for f in nodes]}")
