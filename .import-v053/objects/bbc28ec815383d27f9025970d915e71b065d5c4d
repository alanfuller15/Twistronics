"""Two local preparation folds; never apply global-flat-gap positivity here."""
import argparse,json,time
from pathlib import Path
from dataclasses import replace,asdict
import numpy as np
from local_cases import CASES
from local_fold import locate
from fold_character import check
from local_domain import bounded_node,inside_margin,outside_distance,gap_objective,bounded_minimum,boundary_minimum,require_positive_agreement
from measure import Sample,require
from pair_measure import refined_pair
from checkpoints import save_json
from protocol import frozen_protocol,match
ROOT=Path(__file__).resolve().parent

def originals(sample,seeds,box):
 nodes=[sample.node(x,3) for x in seeds]
 require(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f'])>.001,'original pair collapsed')
 distances=[outside_distance(n['f'],box) for n in nodes]
 require(min(distances)>.02,'original node approaches local domain')
 require(max(np.linalg.norm(np.array(n['f'])-s) for n,s in zip(nodes,seeds))<.06,'original-root continuation jump')
 return dict(nodes=nodes,outside_distances=distances)

def boundary(sample,box):
 fn=gap_objective(sample,3);trials=[boundary_minimum(fn,box,n) for n in [24,48]]
 minimum=require_positive_agreement(trials,'boundary')
 return dict(trials=trials,minimum=minimum)

def run(engine,N,case,path):
 c=CASES[case];protocol=frozen_protocol()
 r=dict(status='RUNNING',scope='LOCAL_DOMAIN_EVENT',engine=engine,N=N,case=case,protocol_sha256=protocol,definition={**c,'p':asdict(c['p'])},states=[],charges=[],open_checks=[])
 save_json(path,r)
 event=locate(engine,N,c);r['event']=event;require(inside_margin(event['f'],c['box'])>.005,'fold near domain boundary')
 r['nondegeneracy']=check(engine,N,case,r);save_json(path,r)
 print(engine,N,case,'FOLD',event['parameter'],event['f'],flush=True)
 side=np.sign(c['pair_at']-event['parameter']);near=event['parameter']+side*c['delta'];after=event['parameter']-side*c['delta']
 require(min(c['pair_at'],c['gapped_at'])<near<max(c['pair_at'],c['gapped_at']),'near-event point out of bracket')
 seeds=[n['f'] for n in event['initial_nodes']];original_seeds=c['original_seeds']
 for value in np.linspace(c['pair_at'],near,9):
  s=Sample(engine,N,replace(c['p'],**{c['key']:float(value)}))
  nodes=[bounded_node(s,x,3,c['box']) for x in seeds];sep=float(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f']))
  require(sep>.001,'duplicate or unresolved local roots')
  require(max(np.linalg.norm(np.array(n['f'])-z) for n,z in zip(nodes,seeds))<.06,'extra-root continuation jump')
  control=originals(s,original_seeds,c['box']);original_seeds=[n['f'] for n in control['nodes']]
  row=dict(parameter=float(value),nodes=nodes,separation=sep,original_pair=control,boundary=boundary(s,c['box']),diagnostics=s.metrics)
  r['states'].append(row);save_json(path,r);seeds=[n['f'] for n in nodes]
  print(engine,N,case,'ROOT_STATE',len(r['states']),flush=True)
 require(r['states'][-1]['separation']<r['states'][0]['separation'],'pair fails to approach fold')
 for row in [r['states'][0],r['states'][-1]]:
  s=Sample(engine,N,replace(c['p'],**{c['key']:row['parameter']}))
  radius=min(.002,row['separation']/8)
  require(min(inside_margin(n['f'],c['box']) for n in row['nodes'])>2*radius,'charge loops leave local domain')
  measurement=refined_pair(s,[n['f'] for n in row['nodes']],3,radius)
  require(measurement['label']=='OPPOSITE','extra pair charge not opposite')
  root_join=match(measurement['nodes'],row['nodes'])
  r['charges'].append(dict(parameter=row['parameter'],measurement=measurement,root_join=root_join));save_json(path,r)
  print(engine,N,case,'CHARGE',row['parameter'],measurement['label'],flush=True)
 # Fold and both open-side stations retain the original roots separately.
 for label,value in [('fold',event['parameter']),('near_open',after),('far_open',c['gapped_at'])]:
  s=Sample(engine,N,replace(c['p'],**{c['key']:float(value)}));control=originals(s,original_seeds,c['box']);original_seeds=[n['f'] for n in control['nodes']]
  row=dict(station=label,parameter=float(value),original_pair=control,boundary=boundary(s,c['box']))
  if label!='fold':
   fn=gap_objective(s,3);trials=[bounded_minimum(fn,c['box'],n,extra=[event['f']]) for n in [17,25]]
   row['local_minimum']=require_positive_agreement(trials,'interior');row['trials']=trials
  row['diagnostics']=s.metrics;r['open_checks'].append(row);save_json(path,r)
  print(engine,N,case,label.upper(),row.get('local_minimum'),flush=True)
 if case=='extra_flat_ann':
  birth_path=ROOT/'results'/f'extra_flat_birth_{engine}_N{N}.json';birth=json.loads(birth_path.read_text())
  require(birth['status']=='ACCEPT' and birth['protocol_sha256']==protocol,'birth window not accepted')
  r['shared_station_join']=dict(extra_pair=match(event['initial_nodes'],birth['event']['initial_nodes']),original_pair=match(r['states'][0]['original_pair']['nodes'],birth['states'][0]['original_pair']['nodes']))
 r['status']='ACCEPT';save_json(path,r);return r

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);p.add_argument('--N',type=int,choices=[4,6],required=True);a=p.parse_args()
 for case in CASES:
  path=ROOT/'results'/f'{case}_{a.engine}_N{a.N}.json'
  if path.exists():
   previous=json.loads(path.read_text())
   if previous.get('status')=='ACCEPT' and previous.get('protocol_sha256')==frozen_protocol():
    print('SKIP accepted',case,a.engine,a.N,flush=True);continue
  start=time.time()
  try:r=run(a.engine,a.N,case,path)
  except Exception as error:
   r=json.loads(path.read_text()) if path.exists() else dict(case=case,engine=a.engine,N=a.N)
   r.update(status='REJECTED',error=type(error).__name__+': '+str(error))
  r['seconds']=time.time()-start;save_json(path,r);print('FINAL',a.engine,a.N,case,r['status'],r.get('error'),flush=True)
  if r['status']!='ACCEPT':raise SystemExit(1)
