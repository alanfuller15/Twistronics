"""Reconcile dense candidate records, native final spectra and review evidence."""
import json,sys,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from sparse_inputs import ROOT,PLAN,binding,sha
sys.path.insert(0,str(ROOT.parent/'joint_mapping_guarded'))
import jm_model as model

def main():
 d=json.loads((ROOT/'CANDIDATES.json').read_text());r=json.loads((ROOT/'REGRESSIONS.json').read_text())
 for record in [d,r]:
  for n,h in record['source_hashes'].items():assert sha(ROOT/n)==h,n
 tests=ET.parse(ROOT/'SUPPLIED_TESTS.xml').getroot();suite=tests.find('testsuite')
 assert int(suite.attrib['tests'])==9 and int(suite.attrib['failures'])==0 and int(suite.attrib['errors'])==0
 spec=PLAN['candidate_check'];rows=[];gaps=[];errors=[];freshchecks=[]
 with zipfile.ZipFile(ROOT/'partner_v071p.zip') as z:supplied={v['N']:v for v in json.loads(z.read('locate_event_results.json'))}
 for row in d['rows']:
  assert row['pass'];e=row['event'];assert row['bracket'][0]<=e['D']<=row['bracket'][1]
  assert row['logged_eigensolves']==sum(m['result']['cost'] for m in row['measurements'])
  for m in row['measurements']:
   assert row['bracket'][0]<=m['D']<=row['bracket'][1]
   v=m['result'];assert v['ok'] and spec['t_margin']<v['t']<1-spec['t_margin']
   assert v['cost']==sum(p['eigensolves'] for p in v['roots'])+sum(p['eigensolves'] for p in v['native'])
   assert all(p['accepted'] for p in v['roots']) and all(p['ok'] for p in v['native'])
   f=np.array([p['f'] for p in v['roots']]);seed=supplied[row['seed_record_N']];sf=np.array([*seed['flat'],seed['node']])
   assert np.max(abs(f-sf))<=spec['root_radius'] and np.min(f)>=0 and np.max(f)<=1
   assert model.image_shifts(f)==model.image_shifts(sf)==v['image_shifts']
   t,off,sep=model.segment_geometry(*f);assert max(abs(t-v['t']),abs(off-v['offset']),abs(sep-v['sep']))<1e-12
   assert sep>1e-3
  m=row['measurements'][e['measurement_index']];assert m['D']==e['D'];v=m['result'];assert abs(v['offset'])<=spec['offset_tolerance']
  x=dict(spec['state'],D=e['D']);family=model.Family(x,row['config'])
  checks=[]
  for k,p in enumerate(v['roots']):
   check=family.native_check(e['D'],np.array(p['f']),family.dim//2-1+int(k==2));assert check['ok'];checks.append(check)
   gaps.append(check['gap_meV']);errors.append(check['matrix_error_meV'])
  freshchecks.append({'N':row['N'],'engine':row['engine'],'native':checks})
  rows.append({'N':row['N'],'engine':row['engine'],'basis_vectors':row['basis_vectors'],'dimension':row['dimension'],'D':e['D'],'offset':e['offset'],'t':e['t'],'supplied_D_offset':row['supplied_D_offset'],'measurements':len(row['measurements']),'logged_eigensolves':row['logged_eigensolves']})
  print('RECONCILED',row['N'],row['engine'],flush=True)
 assert len(rows)==10 and len({(v['N'],v['engine']) for v in rows})==10
 diffs=[]
 for N in spec['N']:
  a=next(v for v in rows if v['N']==N and v['engine']=='bm');b=next(v for v in rows if v['N']==N and v['engine']=='ref')
  diffs.append({'N':N,'D_difference_meV':abs(a['D']-b['D'])})
 out={'status':'RECONCILED_SAMPLED_DENSE_CANDIDATES_PASS_SPARSE_GUARDS_NOT_ACCEPTED','source_hashes':binding(['report.py','CANDIDATES.json','REGRESSIONS.json','SUPPLIED_TESTS.xml','SUPPLIED_TESTS.log','SOLVER_PROBE.log']),
      'candidate_source_hashes':d['source_hashes'],'rows':rows,'native_final_checks':freshchecks,'max_native_gap_meV':max(gaps),'max_native_matrix_error_meV':max(errors),'engine_differences':diffs,'controls_pass':9,'regressions':r['cases'],
      'basis_vectors':{str(v['N']):v['basis_vectors'] for v in rows},'max_engine_D_difference_meV':max(v['D_difference_meV'] for v in diffs),'logged_production_eigensolves':sum(v['logged_eigensolves'] for v in rows),'report_native_spectral_evaluations':60,'seconds_production':d['seconds'],'scope':PLAN['scope']}
 (ROOT/'SUMMARY.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 print(out['status']);print('max native gap',out['max_native_gap_meV']);print('max matrix error',out['max_native_matrix_error_meV']);print('max engine D difference',out['max_engine_D_difference_meV']);print('logged production eigensolves',out['logged_production_eigensolves'])
if __name__=='__main__':main()
