"""Focused replay of the bundle's documented narrow-cone blind spot."""
import json
import time
import numpy as np
from scipy.linalg import eigh
from inputs import ROOT, originals, binding
folder=originals()
import atlas
seed=json.loads((folder/'seeds_legA.json').read_text())[0]
start=time.perf_counter();record=atlas.survey(seed['x'],N=4,n=24);seconds=time.perf_counter()-start
E=atlas.engine(seed['x'],4);f,g,info=E.newton_node(np.array(seed['seeds']['node']),atlas.lo_of(E,'upper'))
assert info['converged']
w=eigh(E.m.H(E.kc(f)),eigvals_only=True,subset_by_index=(E.D//2,E.D//2+1))
distances=[float(np.linalg.norm((np.array(q)-f+.5)%1-.5)) for q in record['upper']]
missing=bool(min(distances,default=float('inf'))>.01 and w[1]-w[0]<1e-8)
out={'source_hashes':binding(['replay_grid.py']),'state':seed['x'],'N':4,'grid':24,'survey':record,'survey_wall_seconds':seconds,
     'tracked_seed_refinement':{'f':f.tolist(),'gap_meV':float(g),'native_gap_meV':float(w[1]-w[0]),'history':info,'survey_upper_distances':distances},
     'known_crossing_node_missed':missing,'scope':'One reproduced grid blind spot. Neither the survey nor this extra seed proves a complete node inventory.'}
(ROOT/'GRID_REPLAY.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('KNOWN NODE MISSED',missing,'survey nodes',{k:len(record[k]) for k in ['flat','upper','lower']},'seconds',seconds)
