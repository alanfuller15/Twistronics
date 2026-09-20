from dataclasses import replace
import numpy as np
from models import State

INITIAL=dict(F1=[.7434,.6126],F3=[.5156,.8278],U1=[.68085143478,.71955859478],U2=[.36082927404,.01932742508],L1=[.65557276154,.63961936569],L2=[.69990297061,.58403829417])
INDICES=dict(F1=3,F3=3,U1=4,U2=4,L1=2,L2=2)

def schedule():
    p=State(A=.2,B=-.25,T=0,phi=0,ratio=.8)
    out=[dict(state=p,leg=0,leg_step=0,key='start')]
    for leg,(key,end,n) in enumerate([('B',-.30,20),('B',-.40,8),('T',-.40,8)],1):
        for j,x in enumerate(np.linspace(getattr(p,key),end,n+1)[1:],1):
            out.append(dict(state=replace(p,**{key:float(x)}),leg=leg,leg_step=j,key=key))
        p=out[-1]['state']
    return out
