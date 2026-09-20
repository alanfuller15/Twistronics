"""Targeted seed-coverage check, not a fresh global inventory or charge gate."""
import json
from pathlib import Path
import numpy as np
from models import State
from measure import Sample,require
from checkpoints import save_json
ROOT=Path(__file__).resolve().parent
prior_root=ROOT.parent/'closing-v048' if (ROOT.parent/'closing-v048').is_dir() else ROOT.parent/'prior_our_v048/v048'
prior=prior_root/'results/flat_birth_ref_lab_N4_refined.json'
r=json.loads(prior.read_text());require(r['status']=='ACCEPT','prior fold not accepted')
f=np.array(r['event']['f']);n=np.array(r['event']['fold_trials'][-1]['null_direction'])
coef=r['nondegeneracy']['trials'][-1]['squared_separation_coefficient']
offset=np.sqrt(coef*(1.054-r['event']['parameter']))/2
seeds=[f-offset*n,f+offset*n];rows=[]
for engine in ['bm_exact','ref_lab']:
 s=Sample(engine,4,State(A=-.35,B=-.4,T=-1.8,phi=80,ratio=1.054))
 nodes=[s.node(z,3) for z in seeds];sep=float(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f']))
 require(sep>.001,'duplicate root');rows.append(dict(engine=engine,N=4,nodes=nodes,separation=sep,diagnostics=s.metrics))
diff=max(float(np.linalg.norm(np.array(rows[0]['nodes'][i]['f'])-rows[1]['nodes'][i]['f'])) for i in range(2))
require(diff<1e-6,'cross-engine mismatch')
save_json(ROOT/'provenance/ratio_1054.json',dict(status='ACCEPT',scope='two local roots only; no new charge claim',ratio=1.054,seeds=[z.tolist() for z in seeds],rows=rows,max_root_difference=diff))
print(json.dumps(dict(rows=rows,max_root_difference=diff),indent=2))
