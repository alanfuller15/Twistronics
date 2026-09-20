"""Original flat-pair preparation, ending at the accepted v044 start state."""
from dataclasses import replace
import numpy as np
from models import State
INITIAL=[[.7594291615,.6066145846],[.5815527478,.7265971522]]
def schedule(pilot=False):
    p=State(A=0,B=0,T=0,phi=0,ratio=.8);out=[dict(state=p,leg=0,leg_step=0,key='start')]
    counts=[4,6] if pilot else [8,10]
    for leg,(key,end,n) in enumerate([('A',.2,counts[0]),('B',-.25,counts[1])],1):
        for j,x in enumerate(np.linspace(getattr(p,key),end,n+1)[1:],1):out.append(dict(state=replace(p,**{key:float(x)}),leg=leg,leg_step=j,key=key))
        p=out[-1]['state']
    return out
