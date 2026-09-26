"""Additive verifier for completed CUTOFF-SHELL-012; no physical eigensolver calls.

Preserves the original failed replay and original raw metrics. Rechecks every
other metric at unchanged tolerances, reports stable projector distances, and
checks legacy distances separately in squared-distance roundoff units.
"""
import argparse,copy,json,subprocess,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run as r
import distance as stable

def controls(a):
 tests=[]
 for theta in [0.,1e-9,1e-6,.3]:
  A=np.array([[1.],[0.]]);B=np.array([[np.cos(theta)],[np.sin(theta)]])
  direct,gram=stable.projector_distance(A,B);assert abs(direct-np.sqrt(2)*abs(np.sin(theta)))<1e-14
  legacy=float(np.sqrt(max(0,2-2*float((A.T@B)[0,0])**2)));check=stable.legacy_compatibility(legacy,direct,gram,1);assert check['roundoff_compatible'];tests.append({'theta':theta,**check})
 assert tests[1]['legacy_value']==0 and tests[1]['stable_value']>0
 assert not stable.legacy_compatibility(.1,tests[1]['stable_value'],0,1)['roundoff_compatible']
 A=np.eye(5)[:,:2];Q=np.array([[0.,-1.],[1.,0.]]);direct,_=stable.projector_distance(A,A@Q);assert direct==0
 r.write(a.output,{'status':'PASS','physical_eigensolves':0,'known_angle_cases':tests,'large_legacy_error_rejected':True,'gauge_invariance':True})

def replay(a):
 cfg=r.bound(a.commit)
 for name in ['replay_stable.py','distance.py','REPLAY_SPEC.json']:
  path=f'research/benchmarks/cutoff_shell_012/{name}';assert subprocess.check_output(['git','show',a.verification_commit+':'+path],cwd=r.ROOT)==(r.ROOT/path).read_bytes()
 policy=json.loads((HERE/'REPLAY_SPEC.json').read_text());assert policy['implementation_commit']==a.commit
 sc=r.load(r.ROOT/'research/benchmarks/state_comparison_001/run.py','sc');case=r.ladder(json.loads((r.ROOT/'docs/certification-readiness/CASE.json').read_text()))
 batch=json.loads((a.output/'BATCH.json').read_text());assert batch['implementation_commit']==a.commit and batch['points']==18 and batch['eigensolver_starts']==72 and batch['jobs']==3
 assert batch['summed_job_seconds']<=cfg['limits']['batch_timeout_seconds']
 rows=[];spectra=[];checks=[]
 for job,owned in enumerate(cfg['jobs']):
  p=a.output/f'job{job:03}';receipt=json.loads((p/'RECEIPT.json').read_text());assert receipt['commit']==a.commit and receipt['points']==owned and receipt['exit_code']==0 and receipt['termination']=='NORMAL_EXIT' and receipt['process_group_empty'] and receipt['elapsed_seconds']<=90 and receipt['eigensolver_starts']==4*len(owned)
  assert {x.name for x in p.iterdir()}==set(receipt['files'])|{'RECEIPT.json'}
  for name,item in receipt['files'].items():assert r.sha(p/name)==item['sha256'] and (p/name).stat().st_size==item['bytes']
  runtime=json.loads((p/'RUNTIME.json').read_text());assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76' and runtime['limits']==cfg['limits'] and set(runtime['threads'].values())=={'1'}
  saved=json.loads((p/'SAMPLES.json').read_text());assert [x['index'] for x in saved]==owned
  with np.load(p/'STATES.npz') as z:
   for i,row in enumerate(saved):
    index=row['index'];assert row['center']==cfg['points'][index] and row['label']==cfg['labels'][index] and max(row['nested_residual_meV'].values())<1e-10 and max(row['eigenpair_residual_meV'].values())<1e-8
    E={k:z[k+'_energies'][i] for k in r.KEYS};V={k:z[k+'_vectors'][i] for k in r.KEYS}
    for k in r.KEYS:
     dim=case['cutoffs'][k]['dimension'];assert E[k].shape==(dim,) and V[k].shape==(dim,4) and np.isfinite(E[k]).all() and np.all(np.diff(E[k])>=0) and np.isfinite(V[k]).all() and np.max(abs(V[k].T@V[k]-np.eye(4)))<1e-10
    actual=r.metrics(sc,case,E,V)
    for link,comp in actual.items():
     left,right=link;ii=sc.embedding(r.pair_case(case,left,right));expected=copy.deepcopy(row['comparisons'][link]['metrics']);observed=copy.deepcopy(comp['metrics'])
     for group,cols in [('pair',[1,2]),('four',[0,1,2,3])]:
      rank=len(cols);A=np.zeros((len(V[right]),rank));A[ii]=V[left][:,cols];B=V[right][:,cols];direct,gram=stable.projector_distance(A,B)
      legacy=expected[group].pop('projector_frobenius_distance');observed[group].pop('projector_frobenius_distance')
      check=stable.legacy_compatibility(legacy,direct,gram,rank);assert check['roundoff_compatible'],(index,link,group,check)
      checks.append({'point':index,'link':link,'group':group,**check});row['comparisons'][link]['metrics'][group]['stable_projector_frobenius_distance']=direct
     sc.close_metrics(observed,expected)
     assert abs(comp['minimum_pair_weight_in_four']-row['comparisons'][link]['minimum_pair_weight_in_four'])<1e-10
    rows.append(row);spectra.append(E)
 assert [x['index'] for x in rows]==list(range(18));reg=cfg['regression'];worst=max(abs(r.upper_gap_microeV(rows[int(i)],k)-v)/1000 for k,refs in reg['upper_gap_microeV'].items() for i,v in refs.items());assert worst<=reg['threshold_meV']
 r.write(a.output/'REGRESSION.json',{'sources':reg['sources'],'compared_points':2,'cutoffs':['a','b','c'],'max_abs_upper_gap_difference_meV':worst,'threshold_meV':reg['threshold_meV'],'status':'PASS'})
 r.write(a.output/'LEGACY_DISTANCE_CHECKS.json',checks)
 r.write(a.output/'MAP.json',{'implementation_commit':a.commit,'verification_commit':a.verification_commit,'independent_review':'PENDING','samples':rows})
 summary=r.summarize(cfg,rows,spectra,case,a.commit);summary['verification_commit']=a.verification_commit
 for name,patch in summary['patches'].items():
  rr=[rows[i] for i in patch['geometry']['point_indices']]
  for link,m in patch['comparisons'].items():m['maximum_stable_four_projector_frobenius_distance']=max(x['comparisons'][link]['metrics']['four']['stable_projector_frobenius_distance'] for x in rr)
 r.write(a.output/'SUMMARY.json',summary)
 r.write(a.output/'REPLAY.json',{'status':'PASS_WITH_ADDITIVE_STABLE_DISTANCE_VERIFIER','implementation_commit':a.commit,'verification_commit':a.verification_commit,'points':18,'physical_eigensolves':0,'original_replay_status':'FAILED_projector_frobenius_distance','legacy_distance_checks':len(checks),'all_other_metric_tolerances':'UNCHANGED','legacy_roundoff_guard_is_certified':False})
 print('REPLAY_PASS: 18 points; stable projector distances; zero physical eigensolves')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['controls','replay']);p.add_argument('--commit');p.add_argument('--verification-commit');p.add_argument('--output',type=Path,required=True);a=p.parse_args();globals()[a.mode](a)
