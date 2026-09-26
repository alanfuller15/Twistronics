"""Review-gated state comparison across two nested finite cutoffs."""
import argparse,hashlib,importlib.util,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
from fractions import Fraction
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def spec():return json.loads((HERE/'SPEC.json').read_text())
def bindings(commit,git=False):
 m=json.loads((HERE/'SOURCE_BINDINGS.json').read_text())
 for p,h in m.items():assert sha(ROOT/p)==h,p
 if git:
  for p in [*m,str((HERE/'SOURCE_BINDINGS.json').relative_to(ROOT))]:
   assert subprocess.check_output(['git','show',commit+':'+p],cwd=ROOT)==(ROOT/p).read_bytes(),p
 return sha(HERE/'SOURCE_BINDINGS.json')
def jobs():return [list(range(i,i+8)) for i in range(0,64,8)]
def validate_review(r,commit):
 import re
 if not (r.get('reviewer')=='CLAUDE' and r.get('verdict')=='PASS' and r.get('reviewed_commit')==commit and re.fullmatch('[0-9a-f]{40}',commit or '') and re.fullmatch(r'https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-[0-9]+',r.get('url',''))):raise RuntimeError('BLOCKED_PRE_EXECUTION_REVIEW')
 return r
def review_gate(path,commit):
 if path is None or not Path(path).is_file():raise RuntimeError('BLOCKED_PRE_EXECUTION_REVIEW')
 return validate_review(json.loads(Path(path).read_text()),commit)
def embedding(case):
 a=case['cutoffs']['a']['ordered_indices'];b=case['cutoffs']['b']['ordered_indices'];assert len({tuple(x) for x in a})==len(a) and len({tuple(x) for x in b})==len(b)
 pos={tuple(x):i for i,x in enumerate(b)};assert all(tuple(x) in pos for x in a)
 return [2*layer*len(b)+2*pos[tuple(g)]+component for layer in range(2) for g in a for component in range(2)]
def compare(A,B,indices):
 import numpy as np
 assert A.ndim==B.ndim==2 and A.shape[1]==B.shape[1] and len(indices)==len(A) and len(set(indices))==len(indices)
 assert np.isfinite(A).all() and np.isfinite(B).all()
 rank=A.shape[1];assert np.max(abs(A.T@A-np.eye(rank)))<1e-10 and np.max(abs(B.T@B-np.eye(rank)))<1e-10
 embedded=np.zeros_like(B);embedded[indices]=A;s=np.linalg.svd(embedded.T@B,compute_uv=False);assert s.min()>=-1e-10 and s.max()<=1+1e-10
 from scipy.linalg import subspace_angles
 angles=np.rad2deg(subspace_angles(embedded,B))[::-1];clipped=np.clip(s,0,1);extra=np.ones(len(B),bool);extra[indices]=False;leak=B[extra].T@B[extra]
 return {'singular_values':s.tolist(),'min_singular_value':float(s.min()),'principal_angles_degrees':angles.tolist(),'projector_frobenius_distance':float(np.sqrt(max(0,2*rank-2*np.sum(clipped**2)))),'mean_added_component_weight':float(np.trace(leak)/rank),'max_added_component_weight':float(np.linalg.eigvalsh(leak)[-1])}
def measure(case,indices,Ea,Eb,Va,Vb):
 groups={'pair':compare(Va[:,1:3],Vb[:,1:3],indices),'four':compare(Va,Vb,indices)}
 for key,E in [('a',Ea),('b',Eb)]:
  lo,hi=case['cutoffs'][key]['selected_bands_zero_based']
  groups['pair'][key+'_external_gaps_meV']=[float(E[lo]-E[lo-1]),float(E[hi+1]-E[hi])]
  groups['four'][key+'_external_gaps_meV']=[float(E[lo-1]-E[lo-2]),float(E[hi+2]-E[hi+1])]
 groups['upper_gap_change_b_minus_a_microeV']=1000*(groups['pair']['b_external_gaps_meV'][1]-groups['pair']['a_external_gaps_meV'][1]);return groups

def worker(a):
 cfg=spec();review_gate(a.review,a.commit);bindings(a.commit);resource.setrlimit(resource.RLIMIT_AS,(cfg['memory_bytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(cfg['file_bytes'],)*2)
 import numpy as np
 from scipy.linalg import eigh
 o=load(ROOT/'research/benchmarks/three_front_001/run.py','sc_old');np,base,assembly,case,provenance=o.setup(a.wheel);indices=embedding(case);coef={k:o.float_coefficients(assembly,case,k)[0] for k in ['a','b']};reference=json.loads((HERE/'REFERENCE.json').read_text())['data']
 arrays={k:[] for k in ['a_energies','b_energies','a_vectors','b_vectors']};rows=[];starts=0
 for index in jobs()[a.job]:
  point=cfg['points'][index];H={k:o.point_matrix(base,assembly,coef[k],*point['center']) for k in ['a','b']};nested=float(np.max(abs(H['b'][np.ix_(indices,indices)]-H['a'])));assert nested<=cfg['nested_matrix_tolerance_meV'];E={};V={};res={}
  for k in ['a','b']:
   assert np.max(abs(H[k]-H[k].T))<1e-10;starts+=1;assert starts<=16
   E[k],allv=eigh(H[k],driver='evr');lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];V[k]=allv[:,lo-1:hi+2]
   res[k]=float(np.max(abs(H[k]@V[k]-V[k]*E[k][lo-1:hi+2])));assert res[k]<=cfg['eigenpair_residual_meV']
   assert reference[k][index]['point']==point and np.max(abs(E[k][lo-1:hi+2]-reference[k][index]['four_energies_meV']))<=cfg['reference_energy_tolerance_meV']
   arrays[k+'_energies'].append(E[k]);arrays[k+'_vectors'].append(V[k])
  rows.append({'index':index,'point':point,'nested_matrix_residual_meV':nested,'eigenpair_residuals_meV':res,'metrics':measure(case,indices,E['a'],E['b'],V['a'],V['b'])})
 np.savez_compressed(a.output/'STATES.npz',**{k:np.array(v) for k,v in arrays.items()});write(a.output/'SAMPLES.json',rows);write(a.output/'RUNTIME.json',provenance)
 write(a.output/'RESULTS.json',{'implementation_commit':a.commit,'job':a.job,'indices':jobs()[a.job],'eigensolver_starts':starts,'review_receipt_sha256':sha(a.review),'independent_review':'PENDING'})
def stop(proc):
 if proc.poll() is None:
  os.killpg(proc.pid,signal.SIGTERM)
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
def run(a):
 cfg=spec();review=review_gate(a.review,a.commit);bindings(a.commit,True)
 a.output.mkdir(parents=True,exist_ok=False);write(a.output/'REVIEW_RECEIPT.json',review);env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
 pending=list(range(len(jobs())));active={};finished=[];started=time.monotonic();failure=None
 try:
  while pending or active:
   while pending and len(active)<2 and failure is None:
    job=pending.pop(0);directory=a.output/f'job{job:03}';directory.mkdir();log=(directory/'WORKER.log').open('wb')
    cmd=[sys.executable,'-B',str(HERE/'run.py'),'worker','--job',str(job),'--output',str(directory),'--wheel',str(a.wheel),'--commit',a.commit,'--review',str((a.output/'REVIEW_RECEIPT.json').resolve())]
    proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True);active[job]=(proc,time.monotonic(),directory,log)
   now=time.monotonic()
   if now-started>cfg['batch_seconds']:failure='BATCH_TIMEOUT'
   for job,(proc,start,directory,log) in list(active.items()):
    timed=now-start>cfg['job_seconds']
    if timed or failure:stop(proc)
    code=proc.poll()
    if code is None:continue
    log.close()
    try:os.killpg(proc.pid,0);empty=False
    except ProcessLookupError:empty=True
    files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in directory.iterdir() if p.is_file()}
    receipt={'implementation_commit':a.commit,'job':job,'indices':jobs()[job],'elapsed_seconds':time.monotonic()-start,'exit_code':code,'termination':'WATCHDOG_TIMEOUT' if timed else 'BATCH_STOP' if failure else 'NORMAL_EXIT','process_group_empty':empty,'files':files}
    write(directory/'RECEIPT.json',receipt);del active[job];finished.append(job)
    if code or not empty or timed:failure='WORKER_FAILURE'
    if len(finished)%1==0:print(json.dumps({'completed_jobs':len(finished),'total_jobs':len(jobs()),'points_completed':sum(len(jobs()[j]) for j in finished)}),flush=True)
   if failure:break
   time.sleep(.05)
 finally:
  for job,(proc,start,directory,log) in active.items():
   stop(proc);log.close()
   try:os.killpg(proc.pid,0);empty=False
   except ProcessLookupError:empty=True
   write(directory/'RECEIPT.json',{'implementation_commit':a.commit,'job':job,'indices':jobs()[job],'elapsed_seconds':time.monotonic()-start,'exit_code':proc.returncode,'termination':'BATCH_STOP','process_group_empty':empty,'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in directory.iterdir() if p.is_file()}})
 write(a.output/'BATCH_RECEIPT.json',{'implementation_commit':a.commit,'jobs_completed':len(finished),'elapsed_seconds':time.monotonic()-started,'failure':failure,'maximum_concurrent_workers':2,'points_per_job_maximum':8})
 if failure:raise RuntimeError(failure)
 assert len(finished)==len(jobs())
 print(json.dumps({'status':'ALL_JOBS_COMPLETE','points':64}),flush=True)


def close_metrics(actual,expected,key=''):
 import numpy as np
 if isinstance(actual,dict):
  assert actual.keys()==expected.keys()
  for k in actual:close_metrics(actual[k],expected[k],k)
 else:
  tolerance=spec()['angle_replay_tolerance_degrees'] if key=='principal_angles_degrees' else spec()['metric_replay_absolute_tolerance']
  assert np.allclose(actual,expected,atol=tolerance,rtol=0),key

def replay(a):
 import numpy as np
 cfg=spec();bindings(a.commit,True);review_gate(a.output/'REVIEW_RECEIPT.json',a.commit);case=json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text());indices=embedding(case);reference=json.loads((HERE/'REFERENCE.json').read_text())['data'];allrows=[];starts=0
 batch=json.loads((a.output/'BATCH_RECEIPT.json').read_text());assert batch['implementation_commit']==a.commit and batch['jobs_completed']==8 and batch['failure'] is None and batch['elapsed_seconds']<=600
 for j,owned in enumerate(jobs()):
  d=a.output/f'job{j:03}';r=json.loads((d/'RECEIPT.json').read_text());result=json.loads((d/'RESULTS.json').read_text())
  assert r['implementation_commit']==result['implementation_commit']==a.commit and r['job']==result['job']==j and r['indices']==result['indices']==owned
  assert r['termination']=='NORMAL_EXIT' and r['exit_code']==0 and r['process_group_empty'] and r['elapsed_seconds']<=90
  assert set(p.name for p in d.iterdir())==set(r['files'])|{'RECEIPT.json'}
  for name,entry in r['files'].items():assert sha(d/name)==entry['sha256'] and (d/name).stat().st_size==entry['bytes']
  assert result['review_receipt_sha256']==sha(a.output/'REVIEW_RECEIPT.json') and result['eigensolver_starts']==16;starts+=result['eigensolver_starts']
  runtime=json.loads((d/'RUNTIME.json').read_text());assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76'
  rows=json.loads((d/'SAMPLES.json').read_text());m=np.load(d/'STATES.npz');assert [r['index'] for r in rows]==owned
  for loc,index in enumerate(owned):
   row=rows[loc];assert row['point']==cfg['points'][index] and row['nested_matrix_residual_meV']<=cfg['nested_matrix_tolerance_meV'] and max(row['eigenpair_residuals_meV'].values())<=cfg['eigenpair_residual_meV']
   for k,dim in cfg['dimensions'].items():
    E=m[k+'_energies'][loc];V=m[k+'_vectors'][loc];lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];assert E.shape==(dim,) and V.shape==(dim,4) and np.isfinite(E).all() and np.all(np.diff(E)>=0)
    assert np.max(abs(E[lo-1:hi+2]-reference[k][index]['four_energies_meV']))<=1e-9
   metrics=measure(case,indices,m['a_energies'][loc],m['b_energies'][loc],m['a_vectors'][loc],m['b_vectors'][loc]);close_metrics(metrics,row['metrics']);allrows.append(row)
 assert starts==128 and [r['index'] for r in allrows]==list(range(64));write(a.output/'MAP.json',{'implementation_commit':a.commit,'scope':cfg['claim_ceiling'],'independent_review':'PENDING','samples':allrows});print(json.dumps({'status':'ALL_RECEIPTS_AND_METRICS_MATCH','points':64,'physical_replay_calls':0,'independent_review':'PENDING'}))
def controls():
 import numpy as np
 case=json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text());indices=embedding(case);assert len(indices)==196 and len(set(indices))==196 and max(indices)<308
 A=np.eye(4)[:,:2];B=np.zeros((6,2));B[:4]=A;ii=list(range(4));same=compare(A,B,ii);assert np.isclose(same['min_singular_value'],1) and same['mean_added_component_weight']==0
 Q=np.array([[0.,-1.],[1.,0.]]);assert np.allclose(compare(A@Q,B@Q.T,ii)['singular_values'],same['singular_values'])
 theta=.3;tilted=B.copy();tilted[0,0]=np.cos(theta);tilted[4,0]=np.sin(theta);m=compare(A,tilted,ii);assert np.isclose(m['min_singular_value'],np.cos(theta)) and np.isclose(m['mean_added_component_weight'],np.sin(theta)**2/2)
 orth=np.zeros((6,2));orth[4:]=np.eye(2);m=compare(A,orth,ii);assert m['min_singular_value']==0 and m['mean_added_component_weight']==1
 rejected=0
 for bad in [{},{'reviewer':'CLAUDE','verdict':'PASS','reviewed_commit':'b'*40,'url':'https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-1'},{'reviewer':'CODEX','verdict':'PASS','reviewed_commit':'a'*40}]:
  try:validate_review(bad,'a'*40)
  except RuntimeError:rejected+=1
 assert rejected==3
 try:compare(A,B,[0,0,2,3]);raise RuntimeError('duplicate embedding accepted')
 except AssertionError:pass
 js=jobs();assert len(js)==8 and all(len(j)==8 for j in js) and sum(js,[])==list(range(64));assert len(spec()['points'])==64
 print(json.dumps({'status':'PASS','physical_calls':0,'jobs':8,'paired_points':64,'checks':['basis injection has196 distinct rows','identical/orthogonal subspaces','sign and in-group rotation invariance','known-angle and added-weight fixture','duplicate embedding rejected','missing/wrong-commit/self-review gates rejected','complete point ownership']}))
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay','controls']);p.add_argument('--job',type=int);p.add_argument('--commit');p.add_argument('--wheel',type=Path);p.add_argument('--output',type=Path);p.add_argument('--review',type=Path);a=p.parse_args();return {'run':run,'worker':worker,'replay':replay,'controls':lambda a:controls()}[a.mode](a)
if __name__=='__main__':main()
