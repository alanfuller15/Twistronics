"""Refine the rounded v047 start seeds and compare matched versus mismatched geometry."""
import json,itertools
from pathlib import Path
import numpy as np
from models import State
from measure import Sample,require
from protocol import match
from checkpoints import save_json,digest
ROOT=Path(__file__).resolve().parent

def error(a,b):return min(max(float(np.linalg.norm(np.asarray(x['f'])-y['f'])) for x,y in zip(a,perm)) for perm in itertools.permutations(b))
def main():
    p=State(A=.2,B=-.25,T=0,phi=0,ratio=.8);rounded=[[.7459,.6123],[.5172,.8278]];rows=[];roots={}
    for engine in ['bm_lab','bm_exact','ref_lab']:
        s=Sample(engine,4,p);nodes=[s.node(seed,3) for seed in rounded];roots[engine]=nodes
        source='ref_lab' if engine=='bm_exact' else engine
        anchor=json.loads((ROOT/'anchors'/f'early_{source}_N4.json').read_text());wanted=[anchor['nodes'][k] for k in ['F1','F3']]
        rows.append(dict(engine=engine,geometry=s.model.geometry,nodes=nodes,matched_anchor=source,join=match(nodes,wanted),rounded_input_error=error([dict(f=x) for x in rounded],wanted),diagnostics=s.metrics))
    save_json(ROOT/'provenance/preparation_join.json',dict(status='PASS',source_sha256=digest(__file__),rows=rows,exact_cross_engine_difference=error(roots['bm_exact'],roots['ref_lab']),linear_exact_difference=error(roots['bm_lab'],roots['bm_exact']),scope='Root identity at the common starting state only; no preparation-path replay'))
    print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
