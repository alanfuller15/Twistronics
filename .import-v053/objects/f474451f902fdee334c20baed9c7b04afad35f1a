"""Lower-pair birth: bounded root window and finite full-chart opening checks."""
import argparse,json,time
from pathlib import Path
from dataclasses import replace,asdict
import numpy as np
from lower_case import CASES
from lower_fold import locate
from fold_character import check
from local_domain import bounded_node,inside_margin
from measure import Sample,require
from pair_measure import refined_pair
from boundary_audit import seeds as boundary_seeds
from checkpoints import save_json
from protocol import frozen_protocol,match
ROOT=Path(__file__).resolve().parent

def anchor_join(engine,N,nodes):
 a=json.loads((ROOT/'anchors'/f'early_{engine}_N{N}.json').read_text())
 require(a['status']=='ACCEPT' and a['kinetic']=='lab_nn_full' and a['engine']==engine and a['N']==N,'invalid early-route anchor')
 p=CASES['prep_lower_birth']['p'];require(all(a['state'][k]==getattr(p,k) for k in ['A','B','T','phi','ratio','theta','eps']),'anchor state mismatch')
 require(a['geometry']==('linear' if engine=='bm_lab' else 'exact'),'anchor geometry mismatch')
 return match(nodes,[a['nodes']['L1'],a['nodes']['L2']])

def run(engine,N,path):
 c=CASES['prep_lower_birth'];protocol=frozen_protocol()
 r=dict(status='RUNNING',scope='FULL_CHART_LOWER_GAP_SEARCH',engine=engine,N=N,case='prep_lower_birth',protocol_sha256=protocol,definition={**c,'p':asdict(c['p'])},states=[],charges=[],open_checks=[])
 save_json(path,r);event=locate(engine,N,c);r['event']=event
 require(inside_margin(event['f'],c['box'])>.005,'fold outside momentum chart')
 r['nondegeneracy']=check(engine,N,r['case'],r);r['v044_lower_root_join']=anchor_join(engine,N,event['initial_nodes']);save_json(path,r)
 print(engine,N,'FOLD',event['parameter'],event['f'],flush=True)
 side=np.sign(c['pair_at']-event['parameter']);near=event['parameter']+side*c['delta'];after=event['parameter']-side*c['delta']
 require(c['pair_at']<near<event['parameter']<after<c['gapped_at'],'lower-birth ordering')
 seeds=[n['f'] for n in event['initial_nodes']]
 for B in np.linspace(c['pair_at'],near,9):
  s=Sample(engine,N,replace(c['p'],B=float(B)));nodes=[bounded_node(s,f,2,c['box']) for f in seeds]
  sep=float(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f']));jump=max(float(np.linalg.norm(np.array(n['f'])-f)) for n,f in zip(nodes,seeds))
  require(sep>.001 and jump<.06,'unresolved lower pair or root jump')
  r['states'].append(dict(B=float(B),nodes=nodes,separation=sep,max_jump=jump,diagnostics=s.metrics));save_json(path,r);seeds=[n['f'] for n in nodes]
  print(engine,N,'ROOT_STATE',len(r['states']),flush=True)
 require(r['states'][-1]['separation']<r['states'][0]['separation'],'pair does not approach fold')
 for row in [r['states'][0],r['states'][-1]]:
  s=Sample(engine,N,replace(c['p'],B=row['B']));radius=min(.002,row['separation']/8)
  measurement=refined_pair(s,[n['f'] for n in row['nodes']],2,radius)
  require(measurement['label']=='OPPOSITE','lower pair is not opposite at charge station')
  r['charges'].append(dict(B=row['B'],measurement=measurement,root_join=match(measurement['nodes'],row['nodes'])));save_json(path,r)
  print(engine,N,'CHARGE',row['B'],measurement['label'],flush=True)
 for B in [after,c['gapped_at']]:
  s=Sample(engine,N,replace(c['p'],B=float(B)));trials=[]
  for grid in [18,24]:
   row=s.minimum(2,grid,extra=boundary_seeds(s,2,[event['f']]))
   require(row['minimum']['gap']>1e-5,'lower full-chart opening unresolved');trials.append(row)
  require(abs(trials[0]['minimum']['gap']-trials[1]['minimum']['gap'])<.01,'lower opening fails grid refinement')
  r['open_checks'].append(dict(B=float(B),trials=trials,diagnostics=s.metrics));save_json(path,r)
  print(engine,N,'OPEN',B,trials[-1]['minimum']['gap'],flush=True)
 r['status']='ACCEPT';save_json(path,r);return r

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);p.add_argument('--N',type=int,choices=[4,6],required=True);a=p.parse_args()
 path=ROOT/'results'/f'prep_lower_birth_{a.engine}_N{a.N}.json'
 if path.exists():
  old=json.loads(path.read_text())
  if old.get('status')=='ACCEPT' and old.get('protocol_sha256')==frozen_protocol():print('SKIP accepted',flush=True);raise SystemExit(0)
 start=time.time()
 try:r=run(a.engine,a.N,path)
 except Exception as error:
  r=json.loads(path.read_text()) if path.exists() else dict(engine=a.engine,N=a.N,case='prep_lower_birth')
  r.update(status='REJECTED',error=type(error).__name__+': '+str(error))
 r['seconds']=time.time()-start;save_json(path,r);print('FINAL',a.engine,a.N,r['status'],r.get('error'),flush=True)
 raise SystemExit(int(r['status']!='ACCEPT'))
