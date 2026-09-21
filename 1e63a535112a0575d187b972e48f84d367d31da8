import numpy as np, json, sys, time
from fold_track import track, bm_model, gapfn, local_roots
from braid import adjacent_nodes
from bm_strain import frac_dist
out=[]; t=time.time()
out.append(track('extra_flat_birth',2,[[0.565,0.573],[0.509,0.568]],[0.180,0.179,0.178,0.177,0.176,0.1755],'A',dict(B=0.0)))
# extra-pair annihilation on the B leg at A=0.2: identify the non-original pair at B=0
m=bm_model(0.20,0.0); fn=gapfn(m,2); ex=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]
orig=[np.array([0.7745,0.6507]),np.array([0.5924,0.7995])]; extra=[f for f in ex if min(frac_dist(f,o) for o in orig)>0.05]
print("flat nodes at (A=0.2,B=0):",[tuple(np.round(f,4)) for f in ex],"| extra pair:",[tuple(np.round(f,4)) for f in extra])
out.append(track('extra_flat_ann',2,[x.tolist() for x in extra[:2]],[0.0,-0.01,-0.02,-0.025,-0.03,-0.032,-0.034,-0.036],'B',dict(A=0.20)))
# lower-pair birth on the B leg: seat the two lower roots at B=-0.25, track upward
m=bm_model(0.20,-0.25); fl=gapfn(m,1); adj=adjacent_nodes(m,ngrid=30); lows=[f for _,f in adj['-']]
if len(lows)<2:
    ex2,bmin=local_roots(m,fl,lows[0] if lows else np.array([0.5,0.5]),R=0.08,n=25); lows=ex2
print("lower roots at (A=0.2,B=-0.25):",[tuple(np.round(f,4)) for f in lows])
if len(lows)>=2:
    out.append(track('lower_birth',1,[lows[0].tolist(),lows[1].tolist()],[-0.25,-0.22,-0.20,-0.18,-0.16,-0.15,-0.14,-0.13,-0.12,-0.11],'B',dict(A=0.20)))
json.dump(out,open('fold_track_prep_B.json','w'),indent=1); print(f"({time.time()-t:.0f}s)")
