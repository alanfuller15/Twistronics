"""Explore backward two-seed continuation; unresolved roots are not an event."""
from pathlib import Path
import numpy as np
from models import State
from measure import Sample,require
from boundary_audit import seeds as boundary_seeds
from checkpoints import save_json
ROOT=Path(__file__).resolve().parent
seeds=[[.6570477101,.6394959048],[.6989918503,.5857819107]]
out=dict(status='PILOT',engine='bm_lab',N=4,states=[])
for B in np.linspace(-.25,-.10,16):
 s=Sample('bm_lab',4,State(A=.2,B=float(B),T=0,phi=0,ratio=.8))
 try:
  nodes=[s.node(f,2) for f in seeds];sep=float(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f']))
  require(sep>.001,'duplicate roots')
  require(max(np.linalg.norm(np.array(n['f'])-f) for n,f in zip(nodes,seeds))<.06,'root jump')
 except Exception as error:
  out['first_unresolved']=dict(B=float(B),reason=str(error));print('UNRESOLVED',B,str(error),flush=True);break
 row=dict(B=float(B),nodes=nodes,separation=sep);out['states'].append(row);seeds=[n['f'] for n in nodes]
 save_json(ROOT/'pilot/backward.json',out);print('PAIR',B,sep,[n['f'] for n in nodes],flush=True)
s=Sample('bm_lab',4,State(A=.2,B=-.1,T=0,phi=0,ratio=.8))
try:
 trials=[s.minimum(2,n,extra=boundary_seeds(s,2,seeds)) for n in [18,24]]
 out['far_open_probe']=dict(B=-.1,trials=trials)
 print('FULL_CHART_MINIMA',[x['minimum']['gap'] for x in trials],flush=True)
except Exception as error:out['far_open_probe']=dict(B=-.1,error=str(error));print('FULL_CHART_UNRESOLVED',str(error),flush=True)
save_json(ROOT/'pilot/backward.json',out)
