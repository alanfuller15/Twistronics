"""Sampled preparation replay with fine/coarse parameter frames and v044 join."""
import argparse,json,time,traceback
from dataclasses import asdict
from pathlib import Path
import numpy as np
from measure import Sample,require
from basis import labels,carry
from spatial import transport
from routes import INITIAL,schedule
from frame_checks import loops
from frame_join import join
from checkpoints import digest,load_steps,save_step,save_json
from protocol import frozen_protocol
ROOT=Path(__file__).resolve().parent

def run(engine,N,pilot=False,max_new=None):
 protocol=digest(ROOT/'PILOT_PLAN.json') if pilot else frozen_protocol();grid=schedule(pilot)
 folder=ROOT/('pilot' if pilot else 'results')/f'prep_{engine}_N{N}';folder.mkdir(parents=True,exist_ok=True)
 rows,arrays=load_steps(folder,protocol);require(len(rows)<=len(grid),'too many committed states')
 for i,row in enumerate(rows):
  require(row['state']==asdict(grid[i]['state']) and row['engine']==engine and row['N']==N and row['pilot']==pilot,'saved identity/state mismatch')
 seeds=[n['f'] for n in rows[-1]['nodes']] if rows else INITIAL;start=len(rows)
 for step in range(start,len(grid)):
  if max_new is not None and step-start>=max_new:break
  tick=time.time();g=grid[step];s=Sample(engine,N,g['state']);lab=labels(s.model)
  nodes=[s.node(f,3) for f in seeds];jumps=[float(np.linalg.norm(np.array(n['f'])-f)) for n,f in zip(nodes,seeds)]
  require(max(jumps)<.06,'root continuation jump')
  a,b=[np.array(n['f']) for n in nodes];sep=float(np.linalg.norm(a-b));require(sep>.001,'duplicate original flat roots')
  require(all(np.all(f>=0) and np.all(f<=1) for f in [a,b]),'original root outside chart')
  radius=min(.004,sep/8);_,q1=s.frame(a,3);_,q2=s.frame(b,3);temporal=[];mesh=None
  if arrays is None:
   e1=q1;e2,_=transport(s,a,b,e1,3,256);c1,c2=e1.copy(),e2.copy();coarse_labels=lab.copy()
  else:
   # A/B knobs do not alter strain-defined basis; enforce this rather than silently changing it.
   require(np.array_equal(lab,arrays['labels']),'preparation basis unexpectedly changed')
   e1,t1=carry(arrays['e1'],arrays['labels'],q1,lab);e2,t2=carry(arrays['e2'],arrays['labels'],q2,lab);temporal=[t1,t2]
   c1,c2=arrays['c1'],arrays['c2'];coarse_labels=arrays['coarse_labels']
   if g['leg_step']%2==0:
    c1,d1=carry(c1,coarse_labels,q1,lab);c2,d2=carry(c2,coarse_labels,q2,lab)
    orientation=[float(np.linalg.det(c1.T@e1)),float(np.linalg.det(c2.T@e2))];require(min(orientation)>.99,'parameter mesh orientation disagreement')
    mesh=dict(orientation=orientation,transport=[d1,d2]);coarse_labels=lab.copy()
  fast,d1=transport(s,a,b,e1,3,128);fine,d2=transport(s,a,b,e1,3,256)
  spatial_det=float(np.linalg.det(fast.T@fine));require(spatial_det>.99,'spatial mesh orientation disagreement')
  trials,attempts=loops(s,a,b,e1,e2,3,radius);direct=s.winding(b,fine,3,radius,trials[1]['points'])
  rectangle=int(np.sign(np.linalg.det(e2.T@fine)));require(direct['charge']==rectangle*trials[1]['b']['charge'],'carried/spatial charge mismatch')
  label='SAME' if trials[1]['a']['charge']*direct['charge']>0 else 'OPPOSITE'
  row=dict(status='PILOT' if pilot else 'ACCEPT',pilot=pilot,step=step,protocol_sha256=protocol,engine=engine,N=N,geometry=s.model.geometry,kinetic='lab_nn_full',cutoff_tol=s.model.cutoff_tol,state=asdict(g['state']),leg=g['leg'],leg_step=g['leg_step'],varying=g['key'],nodes=nodes,node_jumps=jumps,separation=sep,basis_dimension=s.model.dim,temporal_transport=temporal,parameter_mesh_check=mesh,spatial_transport=[d1,d2],spatial_mesh_determinant=spatial_det,temporal_trials=trials,rejected_loop_stages=attempts,rectangle_orientation=rectangle,spatial_direct_charge=direct,label=label,diagnostics=s.metrics,sampled_points=len(s.cache),seconds=time.time()-tick)
  if step==len(grid)-1:row['endpoint_join']=join(engine,N,g['state'],nodes,[e1,e2],lab,trials,label)
  arrays=dict(e1=e1,e2=e2,labels=lab,c1=c1,c2=c2,coarse_labels=coarse_labels)
  row=save_step(folder,step,row,arrays);rows.append(row);seeds=[n['f'] for n in nodes]
  print(engine,N,'PILOT' if pilot else 'PRIMARY',step,'of',len(grid)-1,g['key'],getattr(g['state'],g['key'],''),label,'gap',d2['min_external_gap'],'seconds',round(row['seconds'],2),flush=True)
 complete=len(rows)==len(grid)
 charges={side:sorted({t[side]['charge'] for row in rows for t in row['temporal_trials']}) for side in ['a','b']}
 if complete:require(all(len(x)==1 for x in charges.values()),'individual carried charge changed')
 result=dict(status=('PILOT_COMPLETE' if pilot else 'ACCEPT') if complete else 'PARTIAL',pilot=pilot,engine=engine,N=N,scope='ORIGINAL_FLAT_PAIR_SAMPLED_FRAME_REPLAY',protocol_sha256=protocol,completed=len(rows),scheduled=len(grid),labels=sorted({r['label'] for r in rows}),temporal_charges=charges,label_changes=[dict(step=r['step'],label=r['label']) for i,r in enumerate(rows) if i and r['label']!=rows[i-1]['label']],states=rows,seconds=sum(r['seconds'] for r in rows))
 save_json(folder/'summary.json',result);return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);p.add_argument('--N',type=int,choices=[4,6],required=True);p.add_argument('--pilot',action='store_true');p.add_argument('--max-new',type=int);a=p.parse_args()
 try:r=run(a.engine,a.N,a.pilot,a.max_new);print('FINAL',a.engine,a.N,r['status'],flush=True)
 except Exception as error:
  folder=ROOT/('pilot' if a.pilot else 'results')/f'prep_{a.engine}_N{a.N}';folder.mkdir(parents=True,exist_ok=True)
  r=dict(status='REJECTED',engine=a.engine,N=a.N,pilot=a.pilot,error=type(error).__name__+': '+str(error),traceback=traceback.format_exc());save_json(folder/f'failure_{time.time_ns()}.json',r);print(json.dumps(r),flush=True);raise SystemExit(1)
