"""Protocol amendment: increase loop resolution; keep every acceptance floor.

The original N4 first-annihilation attempt rejected phase increments at 64
points. A diagnostic resolves one node only at 256. Use 256/512 and 1024/2048
fallback only for phase-resolution rejection; retain all rejected stages.
"""
import numpy as np
from measure import require,Rejected

def refined_pair(sample,seeds,index,r):
    nodes=[sample.node(seed,index) for seed in seeds];a,b=[np.array(z['f']) for z in nodes]
    distance=float(np.linalg.norm(b-a));require(distance>3*r,'node loops overlap or duplicate roots')
    _,base=sample.frame(a,index);attempts=[]
    fast,d1=sample.transport(a,b,base,index,steps=128);fine,d2=sample.transport(a,b,base,index,steps=256)
    require(np.linalg.det(fast.T@fine)>.99,'transport orientation refinement')
    for n in [256,1024]:
        trials=[]
        try:
            for radius,points,end,td in [(r,n,fast,d1),(r,2*n,fine,d2),(r/2,2*n,fine,d2)]:
                qa=sample.winding(a,base,index,radius,points);qb=sample.winding(b,end,index,radius,points)
                trials.append(dict(radius=radius,points=points,a=qa,b=qb,transport=td,label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
            require(len({t['label'] for t in trials})==1,'refined pair label fails mesh/radius agreement')
            return dict(nodes=nodes,separation=distance,label=trials[0]['label'],trials=trials,rejected_stages=attempts)
        except Rejected as error:
            attempts.append(dict(base_points=n,reason=str(error)))
            if str(error)!='loop phase steps unresolved':raise
    raise Rejected('loop phase unresolved at amended maximum mesh')
