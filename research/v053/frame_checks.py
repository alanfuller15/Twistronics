"""Inherited spatially based, mesh/radius-refined node-charge measurements."""
from measure import require,Rejected
def loops(sample,a,b,e1,e2,index,r):
    attempts=[]
    for n in [64,256,1024]:
        trials=[]
        try:
            for radius,points in [(r,n),(r,2*n),(r/2,2*n)]:
                qa=sample.winding(a,e1,index,radius,points)
                qb=sample.winding(b,e2,index,radius,points)
                trials.append(dict(radius=radius,points=points,a=qa,b=qb,
                    label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
            for side in ['a','b']:
                require(len({t[side]['charge'] for t in trials})==1,'charge fails mesh/radius refinement')
            return trials,attempts
        except Rejected as error:
            attempts.append(dict(base_points=n,reason=str(error),completed_trials=trials))
            if str(error)!='loop phase steps unresolved':raise
    raise Rejected('loop phase unresolved at maximum mesh')
