"""Two-seed check of v047's one-node lower-gap inventory at the shared start."""
import json
from pathlib import Path
import numpy as np
from models import State
from measure import Sample,require
from protocol import match
from checkpoints import save_json,digest
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    rows=[]
    for engine in ['bm_lab','bm_exact','ref_lab']:
        source='ref_lab' if engine=='bm_exact' else engine
        a=json.loads((ROOT/'anchors'/f'early_{source}_N4.json').read_text());targets=[a['nodes'][k] for k in ['L1','L2']]
        s=Sample(engine,4,State(A=.2,B=-.25,T=0,phi=0,ratio=.8));nodes=[s.node(t['f'],2) for t in targets]
        sep=float(np.linalg.norm(np.asarray(nodes[0]['f'])-nodes[1]['f']));require(sep>.001,'duplicate lower roots')
        rows.append(dict(engine=engine,N=4,nodes=nodes,separation=sep,anchor_join=match(nodes,targets),diagnostics=s.metrics))
    save_json(ROOT/'provenance/lower_inventory_probe.json',dict(status='PASS',source_sha256=digest(__file__),scope='At least two distinct lower-gap roots at one N4 state; no inventory completeness or birth location',rows=rows))
    print(json.dumps(rows,indent=2))
