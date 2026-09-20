"""Publication guard: local event evidence must not become a global-gap claim."""
from dataclasses import asdict
import numpy as np
from ledger_guard import accepted
from local_cases import CASES
from local_domain import inside_margin,outside_distance,require_positive_agreement
from measure import require

def validate(path,protocol):
 r=accepted(path);require(r.get('scope')=='LOCAL_DOMAIN_EVENT','local scope missing')
 require(r.get('protocol_sha256')==protocol,'protocol mismatch')
 require(r['case'] in CASES,'unexpected case');c=CASES[r['case']]
 require(r['definition']=={**c,'p':asdict(c['p'])},'definition differs from declared local case')
 require(len(r['states'])==9 and len(r['charges'])==2 and len(r['open_checks'])==3,'incomplete local event stations')
 require(r['nondegeneracy']['status']=='PASS','nondegeneracy absent')
 require([x['h'] for x in r['event']['fold_trials']]==[2e-5,1e-5],'fold derivative refinement absent')
 require(inside_margin(r['event']['f'],c['box'])>.005,'fold outside local domain')
 for row in r['states']:
  require(len(row['nodes'])==2 and all(0<=n['gap']<1e-6 and inside_margin(n['f'],c['box'])>.005 for n in row['nodes']),'local nodes invalid')
  require(np.linalg.norm(np.array(row['nodes'][0]['f'])-row['nodes'][1]['f'])>.001,'local nodes duplicate')
 for row in r['states']+r['open_checks']:
  trials=row['boundary']['trials'];require([x['grid'] for x in trials]==[24,48],'boundary refinement absent')
  require(all(x['box']==c['box'] for x in trials),'boundary domain mismatch')
  require_positive_agreement(trials,'boundary')
  nodes=row['original_pair']['nodes'];require(len(nodes)==2,'original pair missing')
  require(all(0<=n['gap']<1e-6 and outside_distance(n['f'],c['box'])>.02 for n in nodes),'original pair not outside domain')
  require(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f'])>.001,'original pair duplicate')
 require([x['station'] for x in r['open_checks']]==['fold','near_open','far_open'],'local station ordering')
 for row in r['open_checks'][1:]:
  require([x['grid'] for x in row['trials']]==[17,25],'local minimum refinement absent')
  require(all(x['box']==c['box'] for x in row['trials']),'local minimum domain mismatch')
  require_positive_agreement(row['trials'],'interior')
 for row in r['charges']:
  require(row['measurement']['label']=='OPPOSITE','charge gate absent')
  require(row['root_join']['max_distance']<1e-6,'charge root join missing')
 if r['case']=='extra_flat_ann':
  require(all(x['max_distance']<1e-6 for x in r['shared_station_join'].values()),'shared-station root join missing')
 return r
