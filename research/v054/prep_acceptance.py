"""Require complete frame checkpoints, not root-only summaries, for publication."""
from pathlib import Path
from dataclasses import asdict
import numpy as np
from ledger_guard import accepted
from checkpoints import load_steps
from routes import schedule
from models import State
from measure import require
from frame_join import join

def validate(folder,protocol):
 folder=Path(folder);r=accepted(folder/'summary.json');grid=schedule(False)
 require(not r['pilot'] and r['scope']=='ORIGINAL_FLAT_PAIR_SAMPLED_FRAME_REPLAY','pilot or wrong scope')
 require(r['protocol_sha256']==protocol and r['completed']==len(grid)==r['scheduled'],'incomplete or wrong-protocol replay')
 rows,arrays=load_steps(folder,protocol);require(len(rows)==len(grid) and rows==r['states'],'checkpoint/summary mismatch')
 for i,(row,g) in enumerate(zip(rows,grid)):
  require(row['status']=='ACCEPT' and not row['pilot'],'nonaccepted checkpoint')
  require(row['engine']==r['engine'] and row['N']==r['N'] and row['step']==i,'checkpoint identity mismatch')
  require(row['state']==asdict(g['state']),'wrong preparation state')
  require(row['kinetic']=='lab_nn_full' and row['geometry']==('linear' if r['engine']=='bm_lab' else 'exact'),'wrong model metadata')
  require(row['cutoff_tol']==(1e-6 if r['engine']=='bm_lab' else 1e-9),'wrong cutoff tolerance')
  require(len(row['nodes'])==2 and all(n['index']==3 and 0<=n['gap']<1e-6 for n in row['nodes']),'wrong or unresolved flat nodes')
  require(row['separation']>.001 and max(row['node_jumps'])<.06,'root tracking gate absent')
  require(row['spatial_mesh_determinant']>.99 and len(row['spatial_transport'])==2,'spatial refinement missing')
  require(min(x['min_external_gap'] for x in row['spatial_transport'])>1e-5,'spatial isolation missing')
  require(len(row['temporal_trials'])==3,'loop/radius refinement missing')
  for side in ['a','b']:require(len({t[side]['charge'] for t in row['temporal_trials']})==1,'charge refinement mismatch')
  if i:
   require(len(row['temporal_transport'])==2,'parameter frame transport absent')
   require(min(x['min_overlap'] for x in row['temporal_transport'])>.1,'parameter overlap unresolved')
  needed=i>0 and g['leg_step']%2==0
  require((row['parameter_mesh_check'] is not None)==needed,'parameter mesh checkpoint missing/unexpected')
  if needed:require(min(row['parameter_mesh_check']['orientation'])>.99,'parameter orientation refinement failed')
 charges={s:sorted({t[s]['charge'] for row in rows for t in row['temporal_trials']}) for s in ['a','b']}
 require(charges==r['temporal_charges'] and all(len(v)==1 for v in charges.values()),'carried charges not constant')
 require(r['labels']==sorted({x['label'] for x in rows}),'label summary inconsistent')
 last=rows[-1];current=join(r['engine'],r['N'],State(**last['state']),last['nodes'],[arrays['e1'],arrays['e2']],arrays['labels'],last['temporal_trials'],last['label'])
 saved=last['endpoint_join'];require(saved['relative_orientation']==current['relative_orientation']==1 and saved['common_orientation']==current['common_orientation'],'endpoint orientation claim mismatch')
 require(abs(saved['root_join']['max_distance']-current['root_join']['max_distance'])<1e-12,'endpoint root claim mismatch')
 require(all(x['min_overlap']>.999999 for x in saved['frame_joins']),'endpoint plane claim mismatch')
 return r
