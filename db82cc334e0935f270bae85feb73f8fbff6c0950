"""Scope-selection pilot only; no ACCEPT labels and no event certification."""
import argparse,json,time
from pathlib import Path
import numpy as np
from models import State
from measure import Sample
from local_domain import bounded_node
from boundary_audit import seeds as edges
from checkpoints import save_json
ROOT=Path(__file__).resolve().parent

def run(engine):
    path=ROOT/'provenance'/f'pilot_{engine}_N4.json'
    if path.exists(): raise ValueError('pilot already exists')
    a=json.loads((ROOT/'anchors'/f'unlink_{engine}_N4.json').read_text())
    starts=[a['nodes'][k]['f'] for k in ['L1','L2']]
    record=dict(scope='DIAGNOSTIC_PILOT_ONLY',engine=engine,N=4,roots=[],opening=[])
    save_json(path,record)
    for T in [0.,-.1,-.2,-.25,-.30,-.31]:
        s=Sample(engine,4,State(A=.2,B=-.4,T=T,phi=0,ratio=.8))
        nodes=[bounded_node(s,f,2,[[0,1],[0,1]]) for f in starts]
        sep=float(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f']))
        record['roots'].append(dict(T=T,nodes=nodes,separation=sep,diagnostics=s.metrics))
        starts=[n['f'] for n in nodes];save_json(path,record)
        print(engine,'ROOT',T,sep,flush=True)
    for T in [-.32,-.4]:
        s=Sample(engine,4,State(A=.2,B=-.4,T=T,phi=0,ratio=.8))
        trials=[s.minimum(2,g,extra=edges(s,2,starts)) for g in [12,18]]
        record['opening'].append(dict(T=T,trials=trials,diagnostics=s.metrics));save_json(path,record)
        print(engine,'OPEN',T,[x['minimum']['gap'] for x in trials],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True)
    run(p.parse_args().engine)
