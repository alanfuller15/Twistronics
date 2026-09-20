"""Record pre-replay node seeds. No charge labels are measured here."""
import json
from pathlib import Path
import numpy as np
from models import State
from measure import Sample,geometry,Rejected

out=[]
for engine in ['original','partner']:
    p=State();s=Sample(engine,4,p)
    pair=[s.node(q,4) for q in [[.53,.77],[.467,1.013]]];a,b=[np.array(q['f']) for q in pair]
    d=b-a;n=np.array([-d[1],d[0]])/np.linalg.norm(d)
    nodes=[];failures=[]
    for t,off in [(.2,.002),(.34,.048),(-.61,.011),(1.,.208)]:
        seed=a+t*d+off*n
        try:
            node=s.node(seed,5)
            if all(np.linalg.norm(np.array(node['f'])-z['f'])>.001 for z in nodes):nodes.append(node)
        except Rejected as error:failures.append(dict(seed=seed.tolist(),reason=str(error)))
    out.append(dict(engine=engine,N=4,state=p.__dict__,U=pair,next=nodes,geometry=[geometry(a,b,np.array(z['f'])) for z in nodes],failures=failures))
path=Path(__file__).resolve().parent/'results/discovery.json';path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
