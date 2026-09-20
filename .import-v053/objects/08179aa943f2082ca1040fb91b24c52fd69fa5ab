"""Known-node discovery for later upper-pair annihilation; no topology labels."""
import json
from pathlib import Path
import numpy as np
from models import State
from measure import Sample,Rejected
rows=[]
for engine in ['original','partner']:
    s=Sample(engine,4,State(A=-.35,T=-1.8,ratio=1.0));fs=np.linspace(0,1,18,endpoint=False);v=np.empty((18,18))
    for i,x in enumerate(fs):
        for j,y in enumerate(fs):
            w,_=s.at([x,y]);v[i,j]=w[5]-w[4]
    seeds=[]
    for i,x in enumerate(fs):
        for j,y in enumerate(fs):
            if v[i,j]<=min(v[(i+a)%18,(j+b)%18] for a in [-1,0,1] for b in [-1,0,1]):seeds.append([x,y])
    nodes=[];failures=[]
    for seed in seeds:
        try:
            node=s.node(seed,4)
            if all(np.linalg.norm(np.array(node['f'])-z['f'])>.001 for z in nodes):nodes.append(node)
        except Rejected as error:failures.append(dict(seed=seed,error=str(error)))
    rows.append(dict(engine=engine,nodes=nodes,failures=failures))
p=Path(__file__).resolve().parent/'results/fold_discovery.json';p.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
