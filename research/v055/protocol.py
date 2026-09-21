import json,itertools
from pathlib import Path
import numpy as np
from checkpoints import digest
from measure import require
ROOT=Path(__file__).resolve().parent

def frozen_protocol():
    p=json.loads((ROOT/'PLAN.json').read_text())
    for group in ['source_sha256','anchor_sha256']:
        for name,h in p[group].items():require(digest(ROOT/name)==h,'frozen input changed: '+name)
    return digest(ROOT/'PLAN.json')

def match(nodes,target):
    rows=[]
    for order in itertools.permutations(range(2)):
        d=[float(np.linalg.norm(np.asarray(nodes[i]['f'])-target[j]['f'])) for i,j in enumerate(order)]
        rows.append(dict(permutation=list(order),distances=d,max_distance=max(d)))
    r=min(rows,key=lambda x:x['max_distance']);require(r['max_distance']<1e-6,'root join misses tolerance');return r
