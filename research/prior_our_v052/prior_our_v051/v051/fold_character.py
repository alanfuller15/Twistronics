"""Independent local nondegeneracy checks for every accepted collision.

Rank-one Jacobian alone is insufficient: verify nonzero curvature along its
null direction and a transverse parameter derivative, at two difference steps.
"""
import json
from pathlib import Path
from dataclasses import replace
import numpy as np
from local_cases import CASES
from local_fold import spatial_jac
from measure import Sample,require
ROOT=Path(__file__).resolve().parent

def check(engine,N,case,record):
    c=CASES[case];value=record['event']['parameter'];f=np.array(record['event']['f']);index=c['index']
    p=replace(c['p'],**{c['key']:value});s=Sample(engine,N,p);_,anchor=s.frame(f,index)
    J=spatial_jac(s,f,anchor,index,1e-5);u,sv,vh=np.linalg.svd(J);n=vh[-1];left=u[:,-1];rows=[]
    for h in [2e-4,1e-4]:
        d0=s.vector(f,anchor,index)[0];dp=s.vector(f+h*n,anchor,index)[0];dm=s.vector(f-h*n,anchor,index)[0]
        curvature=float(left@(dp-2*d0+dm)/h**2)
        plus=Sample(engine,N,replace(p,**{c['key']:value+h}));minus=Sample(engine,N,replace(p,**{c['key']:value-h}))
        slope=float(left@(plus.vector(f,anchor,index)[0]-minus.vector(f,anchor,index)[0])/(2*h))
        require(abs(curvature)>1 and abs(slope)>.01,'collision not a resolved nondegenerate fold')
        side=float(np.sign(c['pair_at']-value));require(-2*slope*side/curvature>0,'fold predicts nodes on wrong side')
        rows.append(dict(step=h,curvature=curvature,parameter_slope=slope,squared_separation_coefficient=-8*slope/curvature))
    require(abs(rows[1]['curvature']-rows[0]['curvature'])<.01*abs(rows[1]['curvature']),'curvature refinement')
    require(abs(rows[1]['parameter_slope']-rows[0]['parameter_slope'])<.01*abs(rows[1]['parameter_slope']),'parameter derivative refinement')
    return dict(engine=engine,N=N,case=case,status='PASS',trials=rows)

