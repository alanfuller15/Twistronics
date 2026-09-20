"""Publication guard for this lower-gap event, separate from flat-gap/local claims."""
from dataclasses import asdict
import numpy as np
from ledger_guard import accepted
from lower_case import CASES
from measure import require
from local_domain import inside_margin

def validate(path,protocol):
 r=accepted(path);c=CASES['prep_lower_birth']
 require(r.get('scope')=='FULL_CHART_LOWER_GAP_SEARCH','wrong lower-gap scope')
 require(r.get('case')=='prep_lower_birth' and r.get('protocol_sha256')==protocol,'case/protocol mismatch')
 require(r['definition']=={**c,'p':asdict(c['p'])},'changed lower-gap definition')
 require(len(r['states'])==9 and len(r['charges'])==2 and len(r['open_checks'])==2,'incomplete lower event stations')
 require(r['nondegeneracy']['status']=='PASS','nondegeneracy missing')
 require([x['h'] for x in r['event']['fold_trials']]==[2e-5,1e-5],'derivative refinement missing')
 require(inside_margin(r['event']['f'],c['box'])>.005,'fold outside chart')
 require(r['v044_lower_root_join']['max_distance']<1e-6,'early-route lower-root join failed')
 for row in r['states']:
  require(len(row['nodes'])==2,'missing lower root')
  require(all(n['index']==2 and 0<=n['gap']<1e-6 and inside_margin(n['f'],c['box'])>.005 for n in row['nodes']),'wrong gap index or unresolved lower root')
  require(np.linalg.norm(np.array(row['nodes'][0]['f'])-row['nodes'][1]['f'])>.001,'duplicate lower pair')
 require(all(row['B']<r['event']['parameter'] for row in r['states']),'root states on wrong side')
 for row in r['charges']:
  require(row['measurement']['label']=='OPPOSITE','opposite charge missing')
  require(row['root_join']['max_distance']<1e-6,'charge node join failed')
  require(all(n['index']==2 for n in row['measurement']['nodes']),'charge measured wrong gap')
 for row in r['open_checks']:
  require(row['B']>r['event']['parameter'],'open sample on wrong side')
  require([t['grid'] for t in row['trials']]==[18,24],'open-side mesh refinement missing')
  vals=[]
  for t in row['trials']:
   require(inside_margin(t['minimum']['f'],c['box'])>=-1e-12,'minimum outside chart')
   vals.append(t['minimum']['gap'])
  require(min(vals)>1e-5 and abs(vals[0]-vals[1])<.01,'opening unresolved or grid disagreement')
 return r
