"""Bounded refined 2-D momentum neighborhood (NEIGHBORHOOD-REFINE-005) on the three-cutoff ladder; computation is not gated on review.

Modes: run (supervise bounded jobs, resumable; --only restricts jobs), worker (one job), replay (no physical eigensolves).
"""
import argparse,copy,hashlib,importlib.util,json,os,resource,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];KEYS=['a','b','c'];LINKS=[('a','b'),('b','c')]
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
 assert len(spec['points'])==81 and sum(spec['jobs'],[])==list(range(81)) and max(map(len,spec['jobs']))<=spec['limits']['points_per_job']
 return spec

def ladder(case):
 """Attach cutoff c exactly as CUTOFF-LADDER-003 froze it, and re-verify its shell construction."""
 cfg=json.loads((ROOT/'research/benchmarks/cutoff_ladder_003/SPEC.json').read_text())
 case=copy.deepcopy(case);case['cutoffs']['c']=cfg['additional_cutoff']
 b=case['cutoffs']['b'];c=case['cutoffs']['c'];expected=sorted({(x+dx,y+dy) for x,y in b['ordered_indices'] for dx,dy in b['stencil']})
 assert c['ordered_indices']==[list(v) for v in expected] and c['dimension']==4*len(expected)==444 and c['selected_bands_zero_based']==[221,222]
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
 cfg=bound(a.commit);lim=cfg['limits'];resource.setrlimit(resource.RLIMIT_AS,(lim['address_space_bytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(lim['file_bytes'],)*2)
 import numpy as np
 from scipy.linalg import eigh
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','old');sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc')
 np,base,assembly,case,provenance=old.setup(a.wheel);case=ladder(case);co={k:old.float_coefficients(assembly,case,k)[0] for k in KEYS};rows=[];arrays={f'{k}_{t}':[] for k in KEYS for t in ['energies','vectors']}
 for index in cfg['jobs'][a.job]:
  x,y=cfg['points'][index];H={k:old.point_matrix(base,assembly,co[k],x,y) for k in KEYS};nested={}
  for left,right in LINKS:
   ii=sc.embedding(pair_case(case,left,right));nested[left+right]=float(np.max(abs(H[right][np.ix_(ii,ii)]-H[left])));assert nested[left+right]<1e-10
  E={};V={};res={}
  for k in KEYS:
   assert np.max(abs(H[k]-H[k].T))<1e-10
   E[k],v=eigh(H[k],driver='evr');lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];V[k]=v[:,lo-1:hi+2];res[k]=float(np.max(abs(H[k]@V[k]-V[k]*E[k][lo-1:hi+2])));assert res[k]<1e-8
   arrays[k+'_energies'].append(E[k]);arrays[k+'_vectors'].append(V[k])
  rows.append({'index':index,'offset':cfg['offsets'][index],'center':[x,y],'nested_residual_meV':nested,'eigenpair_residual_meV':res,'comparisons':metrics(sc,case,E,V)})
 write(a.output/'SAMPLES.json',rows);write(a.output/'RUNTIME.json',provenance);np.savez_compressed(a.output/'STATES.npz',**{k:np.array(v) for k,v in arrays.items()})

def upper_gap_microeV(row,k):
 link,alias={'a':('ab','a'),'b':('ab','b'),'c':('bc','b')}[k];return 1000*row['comparisons'][link]['metrics']['pair'][alias+'_external_gaps_meV'][1]

def replay(a):
 import numpy as np
 cfg=bound(a.commit);sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc');case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));rows=[]
 for job,owned in enumerate(cfg['jobs']):
  d=a.output/f'job{job:03}';receipt=json.loads((d/'RECEIPT.json').read_text())
  assert receipt['commit']==a.commit and receipt['exit_code']==0 and receipt['elapsed_seconds']<=cfg['limits']['job_timeout_seconds'] and receipt['eigensolver_starts']==3*len(owned)
  assert {p.name for p in d.iterdir()}==set(receipt['files'])|{'RECEIPT.json'}
  for name,item in receipt['files'].items():assert sha(d/name)==item['sha256'] and (d/name).stat().st_size==item['bytes'],name
  data=np.load(d/'STATES.npz');saved=json.loads((d/'SAMPLES.json').read_text());assert [r['index'] for r in saved]==owned
  for local,r in enumerate(saved):
   assert r['center']==cfg['points'][r['index']] and r['offset']==cfg['offsets'][r['index']] and max(r['nested_residual_meV'].values())<1e-10 and max(r['eigenpair_residual_meV'].values())<1e-8
   E={k:data[k+'_energies'][local] for k in KEYS};V={k:data[k+'_vectors'][local] for k in KEYS}
   for k in KEYS:
    dim=case['cutoffs'][k]['dimension'];assert E[k].shape==(dim,) and V[k].shape==(dim,4) and np.isfinite(E[k]).all() and np.all(np.diff(E[k])>=0)
   for key,m in metrics(sc,case,E,V).items():
    sc.close_metrics(m['metrics'],r['comparisons'][key]['metrics']);assert abs(m['minimum_pair_weight_in_four']-r['comparisons'][key]['minimum_pair_weight_in_four'])<1e-10
   rows.append(r)
 assert [r['index'] for r in rows]==list(range(81))
 reg=cfg['regression'];worst=0.0
 for k,ref in reg['upper_gap_microeV'].items():
  for i,v in ref.items():worst=max(worst,abs(upper_gap_microeV(rows[int(i)],k)-v)/1000)
 assert worst<=reg['threshold_meV'],worst
 write(a.output/'REGRESSION.json',{'source_commit':reg['source_commit'],'compared_points':len(next(iter(reg['upper_gap_microeV'].values()))),'cutoffs':sorted(reg['upper_gap_microeV']),'max_abs_upper_gap_difference_meV':worst,'threshold_meV':reg['threshold_meV'],'status':'PASS'})
 write(a.output/'MAP.json',{'implementation_commit':a.commit,'independent_review':'PENDING','kind':'three-cutoff 9x9 refined momentum neighborhood, not time evolution','samples':rows});print('REPLAY_PASS: 81 points, zero physical eigensolves')

def run(a):
 cfg=bound(a.commit);lim=cfg['limits'];a.output.mkdir(parents=True,exist_ok=True);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
 only=range(len(cfg['jobs'])) if a.only is None else range(*a.only)
 for j in only:
  owned=cfg['jobs'][j];d=a.output/f'job{j:03}'
  if (d/'RECEIPT.json').exists():
   assert json.loads((d/'RECEIPT.json').read_text())['exit_code']==0,f'job {j} previously failed; remove it explicitly to retry';continue
  d.mkdir(exist_ok=False);t=time.monotonic()
  with (d/'WORKER.log').open('wb') as log:
   try:r=subprocess.run([sys.executable,str(HERE/'run.py'),'worker','--job',str(j),'--commit',a.commit,'--output',str(d),'--wheel',str(a.wheel)],stdout=log,stderr=subprocess.STDOUT,env=env,timeout=lim['job_timeout_seconds']);code=r.returncode
   except subprocess.TimeoutExpired:code=-9
  write(d/'RECEIPT.json',{'commit':a.commit,'exit_code':code,'elapsed_seconds':time.monotonic()-t,'eigensolver_starts':3*len(owned) if code==0 else None,'points':owned,'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in d.iterdir()}})
  assert code==0,f'worker {j} failed';print(f'Completed job {j+1}/{len(cfg["jobs"])} ({len(owned)} points)',flush=True)
 done=[j for j in range(len(cfg['jobs'])) if (a.output/f'job{j:03}'/'RECEIPT.json').exists()]
 if len(done)<len(cfg['jobs']):print(f'PARTIAL: {len(done)}/{len(cfg["jobs"])} jobs complete');return
 receipts=[json.loads((a.output/f'job{j:03}'/'RECEIPT.json').read_text()) for j in done]
 write(a.output/'BATCH.json',{'implementation_commit':a.commit,'points':81,'jobs':len(done),'eigensolver_starts':sum(r['eigensolver_starts'] for r in receipts),'summed_job_seconds':sum(r['elapsed_seconds'] for r in receipts),'authorization':cfg['authorization'],'independent_review':'PENDING'});replay(a)

p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay']);p.add_argument('--commit',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);p.add_argument('--only',type=int,nargs=2,metavar=('START','STOP'))
a=p.parse_args();globals()[a.mode](a)
