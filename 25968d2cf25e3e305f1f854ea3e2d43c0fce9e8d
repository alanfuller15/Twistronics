"""Lower un-link collision (v052): track the lower pair through T: 0 -> -0.40 at (A=0.2, B=-0.40), lab_nn_full, bm exact,
tbg_ref cross-check; at every step also record the flat pair roots and each lower node's (t, offset) relative to the
flat pair's straight segment (shortest periodic lift), so a segment crossing on this leg would be visible."""
import numpy as np, json, sys, time
from fold_track import track, bm_model, gapfn, local_roots
from bm_strain import frac_dist, segment_geometry
from braid import adjacent_nodes
t0=time.time()
m=bm_model(0.20,-0.40,0.0); fl=gapfn(m,1); adj=adjacent_nodes(m,ngrid=30); lows=[f for _,f in adj['-']]
if len(lows)<2:
    ex,bmin=local_roots(m,fl,lows[0] if lows else np.array([0.6,0.6]),R=0.08,n=25); lows=ex
print("lower roots at (A=0.2,B=-0.40,T=0):",[tuple(np.round(f,4)) for f in lows])
Ts=[0.0,-0.02,-0.05,-0.08,-0.10,-0.12,-0.14,-0.16,-0.18,-0.20,-0.25,-0.30,-0.40]
res=track('lower_unlink_ann',1,[lows[0].tolist(),lows[1].tolist()],Ts,'T',dict(A=0.20,B=-0.40))
# segment offsets pass: flat pair roots and lower-node geometry at each alive step
flat_seeds=[np.array([0.7319,0.6092]),np.array([0.5272,0.8306])]   # v044 anchors at B=-0.40, T=0
print("flat-segment geometry of the lower nodes (t along F1->F3, offset):")
for row in res['rows']:
    if not row['alive']: break
    mm=bm_model(0.20,-0.40,row['T']); ff=gapfn(mm,2); F=[mm.refine(s,ff)[0] for s in flat_seeds]; flat_seeds=F
    geo=[segment_geometry(F[0],F[1],np.array(q))[:2] for q in row['bm_roots']]
    row['flat_roots']=[x.tolist() for x in F]; row['lower_offsets']=[[float(a),float(b)] for a,b in geo]
    print(f"  T={row['T']:+.2f}: flat {tuple(np.round(F[0],4))} {tuple(np.round(F[1],4))} | lower (t,off) {[(round(a,3),round(b,4)) for a,b in geo]} | lower sep {row['sep']:.4f}")
json.dump(res,open('fold_track_unlink.json','w'),indent=1); print(f"({time.time()-t0:.0f}s)")
