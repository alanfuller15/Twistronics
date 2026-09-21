"""Mesh/radius agreement with both exterior gaps located on the comparison path."""
import numpy as np
from measure import require,Rejected
from spatial import transport
def refined_pair(sample,seeds,index,r=.004):
    nodes=[sample.node(seed,index) for seed in seeds];a,b=[np.asarray(x['f']) for x in nodes]
    distance=float(np.linalg.norm(a-b));require(distance>3*r,'overlapping loops or duplicate roots')
    _,base=sample.frame(a,index)
    fast,d1=transport(sample,a,b,base,index,128);fine,d2=transport(sample,a,b,base,index,256)
    require(np.linalg.det(fast.T@fine)>.99,'spatial mesh disagreement')
    attempts=[]
    for n in [256,1024]:
        trials=[]
        try:
            for radius,points in [(r,n),(r,2*n),(r/2,2*n)]:
                qa=sample.winding(a,base,index,radius,points);qb=sample.winding(b,fine,index,radius,points)
                trials.append(dict(radius=radius,points=points,a=qa,b=qb,label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
            for side in ['a','b']:
                require(len({t[side]['charge'] for t in trials})==1,'charge mesh/radius disagreement')
            return dict(nodes=nodes,separation=distance,label=trials[0]['label'],trials=trials,spatial_transport=[d1,d2],rejected_stages=attempts,diagnostics=sample.metrics)
        except Rejected as error:
            attempts.append(dict(base_points=n,reason=str(error),completed_trials=trials))
            if str(error)!='loop phase steps unresolved':raise
    raise Rejected('loop phase unresolved at maximum mesh')
