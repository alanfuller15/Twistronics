from dataclasses import replace
import numpy as np
from models import State

CASES={
 'pre_ann':dict(start=State(A=.2,B=-.4,T=-.4,phi=0,ratio=.8),index=3,
   seeds=[[.7686,.6476],[.5277,.9319]],expected_label='OPPOSITE',
   legs=[('phi',60.,6),('A',0.,4),('phi',65.,2),('T',-.70,6)]),
 'post_ann':dict(start=State(A=0,B=-.4,T=-.74,phi=65,ratio=.8),index=4,
   expected_label='SAME',legs=[('phi',80.,6),('T',-.8,2),('ratio',.9,4),('ratio',.98,4),('ratio',.99,4)])
}

def schedule(case):
    c=CASES[case];p=c['start'];out=[dict(state=p,leg=0,leg_step=0,key='start')]
    for leg,(key,end,n) in enumerate(c['legs'],1):
        start=getattr(p,key)
        for j,x in enumerate(np.linspace(start,end,n+1)[1:],1):out.append(dict(state=replace(p,**{key:float(x)}),leg=leg,leg_step=j,key=key))
        p=out[-1]['state']
    return out
