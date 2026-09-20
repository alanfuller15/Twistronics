"""Four cleanup legs, with common endpoints stored once."""
from dataclasses import replace
import numpy as np
from models import State
CASES={'cleanup':dict(index=4,expected_label='OPPOSITE')}

def schedule(case='cleanup'):
    if case!='cleanup':raise ValueError(case)
    p=State(ratio=1.);out=[dict(state=p,leg='start',leg_step=0,key='')]
    for number,(key,end) in enumerate([('T',-1.2),('A',-.2),('T',-1.8),('A',-.35)]):
        start=getattr(p,key)
        for j,value in enumerate(np.linspace(start,end,5)[1:],1):
            out.append(dict(state=replace(p,**{key:float(value)}),leg=str(number+1),leg_step=j,key=key))
        p=out[-1]['state']
    return out
