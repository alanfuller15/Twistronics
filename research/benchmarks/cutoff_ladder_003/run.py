"""Bounded three-cutoff ladder; computation authorization is separate from review."""
import argparse,hashlib,importlib.util,json,os,resource,subprocess,sys,time
from fractions import Fraction
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def bound(commit):
 spec=json.loads((HERE/'SPEC.json').read_text())
 for path,h in spec['dependencies'].items():assert sha(ROOT/path)==h,path
 for path in ['research/benchmarks/cutoff_ladder_003/run.py','research/benchmarks/cutoff_ladder_003/SPEC.json',*spec['dependencies']]:assert subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)==(ROOT/path).read_bytes(),path
 return spec

def ladder(case,cfg):
 import copy
 case=copy.deepcopy(case);case['cutoffs']['c']=cfg['additional_cutoff']
 b=case['cutoffs']['b'];c=case['cutoffs']['c'];expected=sorted({(x+dx,y+dy) for x,y in b['ordered_indices'] for dx,dy in b['stencil']})
 assert c['ordered_indices']==[list(v) for v in expected] and c['dimension']==4*len(expected)==444
 assert c['selected_bands_zero_based']==[221,222] and sum(cfg['jobs'],[])==list(range(17)) and max(map(len,cfg['jobs']))<=6
 return case

def pair_case(case,left,right):
 return {'cutoffs':{'a':case['cutoffs'][left],'b':case['cutoffs'][right]}}

def metrics(sc,case,E,V):
 result={}
 for left,right in [('a','b'),('b','c')]:
  pair=pair_case(case,left,right);ii=sc.embedding(pair);ov=V[left].T@V[right][ii,:]
  import numpy as np
  result[left+right]={'metrics':sc.measure(pair,ii,E[left],E[right],V[left],V[right]),'minimum_pair_weight_in_four':float(min(np.linalg.svd(ov[1:3,:],compute_uv=False)**2))}
 return result

def worker(a):
 cfg=bound(a.commit);resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
 import numpy as np
 from scipy.linalg import eigh
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','old');sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc')
 np,base,assembly,case,provenance=old.setup(a.wheel);case=ladder(case,cfg);co={k:old.float_coefficients(assembly,case,k)[0] for k in ['a','b','c']};rows=[];arrays={k:[] for k in ['a_energies','b_energies','c_energies','a_vectors','b_vectors','c_vectors']}
 for index in cfg['jobs'][a.job]:
  x,y=cfg['points'][index];H={k:old.point_matrix(base,assembly,co[k],x,y) for k in ['a','b','c']};nested={}
  for left,right in [('a','b'),('b','c')]:
   ii=sc.embedding(pair_case(case,left,right));nested[left+right]=float(np.max(abs(H[right][np.ix_(ii,ii)]-H[left])));assert nested[left+right]<1e-10
  E={};V={};res={}
  for k in ['a','b','c']:
   assert np.max(abs(H[k]-H[k].T))<1e-10
   E[k],v=eigh(H[k],driver='evr');lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];V[k]=v[:,lo-1:hi+2];res[k]=float(np.max(abs(H[k]@V[k]-V[k]*E[k][lo-1:hi+2])));assert res[k]<1e-8
   arrays[k+'_energies'].append(E[k]);arrays[k+'_vectors'].append(V[k])
  rows.append({'index':index,'center':[x,y],'nested_residual_meV':nested,'eigenpair_residual_meV':res,'comparisons':metrics(sc,case,E,V)})
 write(a.output/'SAMPLES.json',rows);write(a.output/'RUNTIME.json',provenance);np.savez_compressed(a.output/'STATES.npz',**{k:np.array(v) for k,v in arrays.items()})

def replay(a):
 import numpy as np
 cfg=bound(a.commit);sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc');case=json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text());case=ladder(case,cfg);rows=[]
 for job,owned in enumerate(cfg['jobs']):
  d=a.output/f'job{job:03}';receipt=json.loads((d/'RECEIPT.json').read_text());assert receipt['commit']==a.commit and receipt['exit_code']==0 and receipt['elapsed_seconds']<=90 and receipt['eigensolver_starts']==3*len(owned)
  assert {p.name for p in d.iterdir()}==set(receipt['files'])|{'RECEIPT.json'}
  for name,item in receipt['files'].items():assert sha(d/name)==item['sha256'] and (d/name).stat().st_size==item['bytes']
  data=np.load(d/'STATES.npz');saved=json.loads((d/'SAMPLES.json').read_text());assert [r['index'] for r in saved]==owned
  for local,r in enumerate(saved):
   assert r['center']==cfg['points'][r['index']] and max(r['nested_residual_meV'].values())<1e-10 and max(r['eigenpair_residual_meV'].values())<1e-8
   E={k:data[k+'_energies'][local] for k in ['a','b','c']};V={k:data[k+'_vectors'][local] for k in ['a','b','c']}
   for k in ['a','b','c']:
    dim=case['cutoffs'][k]['dimension'];assert E[k].shape==(dim,) and V[k].shape==(dim,4) and np.isfinite(E[k]).all() and np.all(np.diff(E[k])>=0)
   for key,d in metrics(sc,case,E,V).items():
    sc.close_metrics(d['metrics'],r['comparisons'][key]['metrics']);assert abs(d['minimum_pair_weight_in_four']-r['comparisons'][key]['minimum_pair_weight_in_four'])<1e-10
   rows.append(r)
 assert [r['index'] for r in rows]==list(range(17));write(a.output/'MAP.json',{'implementation_commit':a.commit,'independent_review':'PENDING','kind':'three-cutoff momentum scan, not time evolution','samples':rows});print('REPLAY_PASS: 17 points, zero physical eigensolves')

def run(a):
 cfg=bound(a.commit);a.output.mkdir(parents=True,exist_ok=False);started=time.monotonic();env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
 for j,owned in enumerate(cfg['jobs']):
  d=a.output/f'job{j:03}';d.mkdir();t=time.monotonic()
  with (d/'WORKER.log').open('wb') as log:
   try:r=subprocess.run([sys.executable,str(HERE/'run.py'),'worker','--job',str(j),'--commit',a.commit,'--output',str(d),'--wheel',str(a.wheel)],stdout=log,stderr=subprocess.STDOUT,env=env,timeout=90);code=r.returncode
   except subprocess.TimeoutExpired:code=-9
  write(d/'RECEIPT.json',{'commit':a.commit,'exit_code':code,'elapsed_seconds':time.monotonic()-t,'eigensolver_starts':3*len(owned) if code==0 else None,'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in d.iterdir()}})
  assert code==0,f'worker {j} failed';print(f'Completed job {j+1}/3',flush=True)
 write(a.output/'BATCH.json',{'implementation_commit':a.commit,'points':17,'eigensolver_starts':51,'elapsed_seconds':time.monotonic()-started,'authorization':cfg['authorization'],'independent_review':'PENDING'});replay(a)
p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay']);p.add_argument('--commit',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);a=p.parse_args();globals()[a.mode](a)
