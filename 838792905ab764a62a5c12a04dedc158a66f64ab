"""Bounded roots, two spatial meshes, and three charge-loop refinements."""
import numpy as np
from evidence import require
from fold import root
from transport import transport


def refined_pair(sample,seeds,index,r,box):
    from measure import align
    nodes=[root(sample,seed,index,box) for seed in seeds];a,b=[np.array(n['f']) for n in nodes]
    distance=float(np.linalg.norm(a-b));require(np.isfinite(r) and 0<r<distance/3,'invalid radius or overlapping loops')
    _,base=sample.frame(a,index)
    fast,d1=transport(sample,a,b,base,index,128,[],align);fine,d2=transport(sample,a,b,base,index,256,[],align)
    determinant=float(np.linalg.det(fast.T@fine));require(determinant>.99,'spatial mesh disagreement');attempts=[]
    for n in [256,1024]:
        trials=[]
        try:
            for radius,points in [(r,n),(r,2*n),(r/2,2*n)]:
                qa=sample.winding(a,base,index,radius,points);qb=sample.winding(b,fine,index,radius,points)
                trials.append(dict(radius=radius,points=points,a=qa,b=qb,label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
            require(all(len({t[side]['charge'] for t in trials})==1 for side in ['a','b']),'charge mesh/radius disagreement')
            return dict(nodes=nodes,separation=distance,label=trials[0]['label'],trials=trials,spatial_transport=[d1,d2],spatial_mesh_determinant=determinant,rejected_stages=attempts,diagnostics=sample.metrics,sampled_points=len(sample.cache))
        except ValueError as error:
            attempts.append(dict(base_points=n,reason=str(error),completed_trials=trials))
            if str(error)!='loop phase steps unresolved':error.attempts=attempts;raise
    error=ValueError('loop phase unresolved at maximum mesh');error.attempts=attempts;raise error
