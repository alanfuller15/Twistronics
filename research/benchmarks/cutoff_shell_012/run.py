"""CUTOFF-SHELL-012: four-cutoff local comparisons at two candidate sites; computation is not gated on review.

Modes: run (supervise bounded jobs, resumable; --only restricts jobs), worker (one job), replay (no physical eigensolves).
"""
import argparse,copy,hashlib,importlib.util,json,os,resource,subprocess,sys,time,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];KEYS=['a','b','c','d'];LINKS=[('a','b'),('b','c'),('c','d')]
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bound(commit):
 """Exact-commit provenance: every executed or consumed file must equal its bytes at the frozen commit."""
 spec=json.loads((HERE/'SPEC.json').read_text())
 for path,h in spec['dependencies'].items():assert sha(ROOT/path)==h,path
 for path in [f'research/benchmarks/{HERE.name}/run.py',f'research/benchmarks/{HERE.name}/SPEC.json',*spec['dependencies']]:
  assert subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)==(ROOT/path).read_bytes(),path
 n=len(spec['points']);assert n==len(spec['labels'])==18 and sum(spec['jobs'],[])==list(range(n)) and max(map(len,spec['jobs']))<=spec['limits']['points_per_job']
 validate_geometry(spec)
 return spec

def ladder(case):
 """Attach cutoff c exactly as CUTOFF-LADDER-003 froze it, and re-verify its shell construction."""
 cfg=json.loads((ROOT/'research/benchmarks/cutoff_ladder_003/SPEC.json').read_text())
 case=copy.deepcopy(case);case['cutoffs']['c']=cfg['additional_cutoff']
 b=case['cutoffs']['b'];c=case['cutoffs']['c'];expected=sorted({(x+dx,y+dy) for x,y in b['ordered_indices'] for dx,dy in b['stencil']})
 assert c['ordered_indices']==[list(v) for v in expected] and c['dimension']==4*len(expected)==444 and c['selected_bands_zero_based']==[221,222]
 cfg=json.loads((HERE/'SPEC.json').read_text());case['cutoffs']['d']=cfg['additional_cutoff'];d=case['cutoffs']['d'];expected=sorted({(x+dx,y+dy) for x,y in c['ordered_indices'] for dx,dy in b['stencil']});assert d['ordered_indices']==[list(v) for v in expected] and d['dimension']==4*len(expected)==604 and d['selected_bands_zero_based']==[301,302]
 return case

def pair_case(case,left,right):return {'cutoffs':{'a':case['cutoffs'][left],'b':case['cutoffs'][right]}}

def metrics(sc,case,E,V):
 import numpy as np
 out={}
 for left,right in LINKS:
  pair=pair_case(case,left,right);ii=sc.embedding(pair);ov=V[left].T@V[right][ii,:]
  out[left+right]={'metrics':sc.measure(pair,ii,E[left],E[right],V[left],V[right]),'minimum_pair_weight_in_four':float(min(np.linalg.svd(ov[1:3,:],compute_uv=False)**2))}
 return out

def worker(a):
 cfg=bound(a.commit);lim=cfg['limits'];assert all(os.environ.get(k)=='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']);resource.setrlimit(resource.RLIMIT_AS,(lim['address_space_bytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(lim['file_bytes'],)*2)
 import numpy as np
 from scipy.linalg import eigh
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','old');sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc')
 np,base,assembly,case,provenance=old.setup(a.wheel);case=ladder(case);provenance.update(python=sys.version,numpy=np.__version__,scipy=__import__('scipy').__version__,limits=lim,threads={k:os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']});co={k:old.float_coefficients(assembly,case,k)[0] for k in KEYS};rows=[];arrays={f'{k}_{t}':[] for k in KEYS for t in ['energies','vectors']}
 for index in cfg['jobs'][a.job]:
  x,y=cfg['points'][index];H={k:old.point_matrix(base,assembly,co[k],x,y) for k in KEYS};nested={}
  for left,right in LINKS:
   ii=sc.embedding(pair_case(case,left,right));nested[left+right]=float(np.max(abs(H[right][np.ix_(ii,ii)]-H[left])));assert nested[left+right]<1e-10
  E={};V={};res={}
  for k in KEYS:
   assert np.max(abs(H[k]-H[k].T))<1e-10
   E[k],v=eigh(H[k],driver='evr');lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];V[k]=v[:,lo-1:hi+2];res[k]=float(np.max(abs(H[k]@V[k]-V[k]*E[k][lo-1:hi+2])));assert res[k]<1e-8
   arrays[k+'_energies'].append(E[k]);arrays[k+'_vectors'].append(V[k])
  rows.append({'index':index,'label':cfg['labels'][index],'center':[x,y],'nested_residual_meV':nested,'eigenpair_residual_meV':res,'comparisons':metrics(sc,case,E,V)})
 write(a.output/'SAMPLES.json',rows);write(a.output/'RUNTIME.json',provenance);np.savez_compressed(a.output/'STATES.npz',**{k:np.array(v) for k,v in arrays.items()})

def upper_gap_microeV(row,k):
 link,alias={'a':('ab','a'),'b':('ab','b'),'c':('bc','b'),'d':('cd','b')}[k];return 1000*row['comparisons'][link]['metrics']['pair'][alias+'_external_gaps_meV'][1]

def replay(a):
 import numpy as np
 cfg=bound(a.commit);sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc');case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));rows=[];vectors=[];spectra=[]
 batch=json.loads((a.output/'BATCH.json').read_text());assert batch['implementation_commit']==a.commit and batch['points']==18 and batch['jobs']==len(cfg['jobs']) and batch['eigensolver_starts']==72 and batch['summed_job_seconds']<=cfg['limits']['batch_timeout_seconds']
 for job,owned in enumerate(cfg['jobs']):
  d=a.output/f'job{job:03}';receipt=json.loads((d/'RECEIPT.json').read_text())
  assert receipt['commit']==a.commit and receipt['exit_code']==0 and receipt['elapsed_seconds']<=cfg['limits']['job_timeout_seconds'] and receipt['eigensolver_starts']==len(KEYS)*len(owned)
  assert receipt['points']==owned and receipt['process_group_empty'] and receipt['termination']=='NORMAL_EXIT'
  runtime=json.loads((d/'RUNTIME.json').read_text());assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76' and runtime['limits']==cfg['limits'] and set(runtime['threads'].values())=={'1'}
  assert {p.name for p in d.iterdir()}==set(receipt['files'])|{'RECEIPT.json'}
  for name,item in receipt['files'].items():assert sha(d/name)==item['sha256'] and (d/name).stat().st_size==item['bytes'],name
  data=np.load(d/'STATES.npz');saved=json.loads((d/'SAMPLES.json').read_text());assert [r['index'] for r in saved]==owned
  for local,r in enumerate(saved):
   assert r['center']==cfg['points'][r['index']] and r['label']==cfg['labels'][r['index']] and max(r['nested_residual_meV'].values())<1e-10 and max(r['eigenpair_residual_meV'].values())<1e-8
   E={k:data[k+'_energies'][local] for k in KEYS};V={k:data[k+'_vectors'][local] for k in KEYS}
   for k in KEYS:
    dim=case['cutoffs'][k]['dimension'];assert E[k].shape==(dim,) and V[k].shape==(dim,4) and np.isfinite(E[k]).all() and np.all(np.diff(E[k])>=0) and np.isfinite(V[k]).all() and np.max(abs(V[k].T@V[k]-np.eye(4)))<1e-10
   for key,m in metrics(sc,case,E,V).items():
    sc.close_metrics(m['metrics'],r['comparisons'][key]['metrics']);assert abs(m['minimum_pair_weight_in_four']-r['comparisons'][key]['minimum_pair_weight_in_four'])<1e-10
   rows.append(r);vectors.append(V);spectra.append(E)
 assert [r['index'] for r in rows]==list(range(len(cfg['points'])))
 reg=cfg['regression'];worst=0.0
 for k,ref in reg['upper_gap_microeV'].items():
  for i,v in ref.items():worst=max(worst,abs(upper_gap_microeV(rows[int(i)],k)-v)/1000)
 assert worst<=reg['threshold_meV'],worst
 write(a.output/'REGRESSION.json',{'sources':reg['sources'],'compared_points':len(next(iter(reg['upper_gap_microeV'].values()))),'cutoffs':sorted(reg['upper_gap_microeV']),'max_abs_upper_gap_difference_meV':worst,'threshold_meV':reg['threshold_meV'],'status':'PASS'})
 write(a.output/'SUMMARY.json',summarize(cfg,rows,spectra,case,a.commit))
 write(a.output/'MAP.json',{'implementation_commit':a.commit,'independent_review':'PENDING','kind':'four-cutoff rational momentum patches, not time evolution','samples':rows});print(f'REPLAY_PASS: {len(rows)} points, zero physical eigensolves')

def validate_geometry(cfg):
 from fractions import Fraction as F
 assert len({tuple(p) for p in cfg['points']})==18
 for patch in cfg['patches']:
  center=list(map(F,patch['center']));step=F(patch['step']);expected=[[str(center[0]+x*step),str(center[1]+y*step)] for y in [-1,0,1] for x in [-1,0,1]]
  assert [cfg['points'][i] for i in patch['point_indices']]==expected

def summarize(cfg,rows,spectra,case,commit):
 import numpy as np
 from fractions import Fraction as F
 result={'implementation_commit':commit,'independent_review':'PENDING','scope':cfg['scope'],'dimensions':{k:case['cutoffs'][k]['dimension'] for k in KEYS},'patches':{},'max_eigenpair_residual_meV':max(max(r['eigenpair_residual_meV'].values()) for r in rows),'max_nested_residual_meV':max(max(r['nested_residual_meV'].values()) for r in rows)}
 for patch in cfg['patches']:
  ids=patch['point_indices'];rr=[rows[i] for i in ids];out={'geometry':patch,'cutoffs':{},'comparisons':{}}
  offsets=np.array([(x,y) for y in [-1,0,1] for x in [-1,0,1]],float);x,y=offsets.T;D=np.column_stack([x*x,y*y,x*y,x,y,np.ones(9)])
  for k in KEYS:
   z=np.array([upper_gap_microeV(r,k) for r in rr]);co=np.linalg.lstsq(D,z*z,rcond=None)[0];Q=np.array([[co[0],co[2]/2],[co[2]/2,co[1]]]);positive=bool(min(np.linalg.eigvalsh(Q))>0)
   fit={'coefficients_xx_yy_xy_x_y_1':co.tolist(),'positive_definite_quadratic':positive,'max_gap_squared_residual_microeV2':float(max(abs(D@co-z*z)))}
   if positive:
    offset=-np.linalg.solve(Q,co[3:5])/2;fit.update(candidate_offset_in_steps=offset.tolist(),candidate_fractional_k=[float(F(v))+float(F(patch['step']))*offset[j] for j,v in enumerate(patch['center'])],candidate_inside_sampled_square=bool(max(abs(offset))<=1),fitted_minimum_gap_squared_microeV2=float(co[5]+co[3:5]@offset+offset@Q@offset))
   out['cutoffs'][k]={'center_upper_gap_microeV':float(z[4]),'minimum_sampled_upper_gap_microeV':float(min(z)),'gap_rows_microeV':z.reshape(3,3).tolist(),'descriptive_fit':fit}
  for left,right in LINKS:
   link=left+right;out['comparisons'][link]={'maximum_pair_angle_degrees':max(max(r['comparisons'][link]['metrics']['pair']['principal_angles_degrees']) for r in rr),'maximum_four_angle_degrees':max(max(r['comparisons'][link]['metrics']['four']['principal_angles_degrees']) for r in rr),'minimum_pair_in_four_containment':min(r['comparisons'][link]['minimum_pair_weight_in_four'] for r in rr),'maximum_abs_upper_gap_shift_microeV':max(abs(r['comparisons'][link]['metrics']['upper_gap_change_b_minus_a_microeV']) for r in rr)}
  result['patches'][patch['id']]=out
 return result

def controls(a):
 import numpy as np
 cfg=json.loads((HERE/'SPEC.json').read_text());validate_geometry(cfg);case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc')
 for left,right in LINKS:
  ii=sc.embedding(pair_case(case,left,right));assert len(ii)==case['cutoffs'][left]['dimension'] and len(set(ii))==len(ii)
  A=np.eye(len(ii))[:,:4];B=np.zeros((case['cutoffs'][right]['dimension'],4));B[ii]=A;v=sc.compare(A,B,ii);assert v['min_singular_value']==1 and v['mean_added_component_weight']==0
  Q=np.linalg.qr(np.arange(16).reshape(4,4)+np.eye(4))[0];assert np.max(abs(np.array(sc.compare(A@Q,B,ii)['principal_angles_degrees'])))<1e-5
 write(a.output,{'status':'PASS','physical_eigensolves':0,'checks':['independent c-to-d shell construction','exact 3x3 rational grids','distinct basis injections for a/b/b/c/c/d','identical embedded four-state span','in-group rotation invariant'],'dimensions':{k:case['cutoffs'][k]['dimension'] for k in KEYS},'points':18,'new_coordinates':16,'regression_coordinates':2})

def run(a):
 cfg=bound(a.commit);lim=cfg['limits'];a.output.mkdir(parents=True,exist_ok=True);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1');started=time.monotonic()
 only=range(len(cfg['jobs'])) if a.only is None else range(*a.only)
 for j in only:
  owned=cfg['jobs'][j];d=a.output/f'job{j:03}'
  if (d/'RECEIPT.json').exists():
   rec=json.loads((d/'RECEIPT.json').read_text());assert rec['commit']==a.commit and rec['exit_code']==0 and rec['points']==owned
   for name,item in rec['files'].items():assert sha(d/name)==item['sha256']
   continue
  assert time.monotonic()-started<lim['batch_timeout_seconds']
  d.mkdir(exist_ok=False);t=time.monotonic();termination='NORMAL_EXIT'
  with (d/'WORKER.log').open('wb') as log:
   proc=subprocess.Popen([sys.executable,'-B',str(HERE/'run.py'),'worker','--job',str(j),'--commit',a.commit,'--output',str(d),'--wheel',str(a.wheel)],stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
   try:code=proc.wait(timeout=min(lim['job_timeout_seconds'],lim['batch_timeout_seconds']-(t-started)))
   except subprocess.TimeoutExpired:
    termination='WATCHDOG_TIMEOUT';os.killpg(proc.pid,signal.SIGKILL);code=proc.wait()
  try:os.killpg(proc.pid,0);empty=False
  except ProcessLookupError:empty=True
  if not empty:os.killpg(proc.pid,signal.SIGKILL)
  write(d/'RECEIPT.json',{'commit':a.commit,'exit_code':code,'termination':termination,'process_group_empty':empty,'elapsed_seconds':time.monotonic()-t,'eigensolver_starts':len(KEYS)*len(owned) if code==0 else None,'points':owned,'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in d.iterdir()}})
  assert code==0 and empty and termination=='NORMAL_EXIT',f'worker {j} failed';print(f'Completed job {j+1}/{len(cfg["jobs"])} ({len(owned)} points)',flush=True)
 done=[j for j in range(len(cfg['jobs'])) if (a.output/f'job{j:03}'/'RECEIPT.json').exists()]
 if len(done)<len(cfg['jobs']):print(f'PARTIAL: {len(done)}/{len(cfg["jobs"])} jobs complete');return
 receipts=[json.loads((a.output/f'job{j:03}'/'RECEIPT.json').read_text()) for j in done]
 assert sum(r['elapsed_seconds'] for r in receipts)<=lim['batch_timeout_seconds']
 write(a.output/'BATCH.json',{'implementation_commit':a.commit,'points':len(cfg['points']),'new_coordinates':16,'regression_coordinates':2,'jobs':len(done),'eigensolver_starts':sum(r['eigensolver_starts'] for r in receipts),'summed_job_seconds':sum(r['elapsed_seconds'] for r in receipts),'authorization':cfg['authorization'],'independent_review':'PENDING'});replay(a)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay','controls']);p.add_argument('--commit');p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);p.add_argument('--only',type=int,nargs=2,metavar=('START','STOP'))
 a=p.parse_args();globals()[a.mode](a)
