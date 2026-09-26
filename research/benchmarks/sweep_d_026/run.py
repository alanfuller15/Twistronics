"""SWEEP-D-026: full-cell gap maps at cutoffs a and d on a 128x128 exact cell-centred grid (+8 regression points
from SWEEP-D-024), in two predeclared batches under the reviewed concurrent_supervisor. Eigenvalues only
(scipy evr, eigvals_only=True); full spectra retained with pack_states. Not gated on review.
Modes: controls, run --batch A|B, worker, replay --batch A|B (zero solves), combine (zero solves).
"""
import argparse,copy,hashlib,importlib.util,json,os,resource,subprocess,sys,time,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];KEYS=['a','d'];NPOINTS=16392
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fastpipe():
 import sys as _s;_s.path.insert(0,str(ROOT/'research/tools/fast_pipeline'));import fast_pipeline;return fast_pipeline
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bound(commit):
 """Exact-commit provenance: every executed or consumed file must equal its bytes at the frozen commit."""
 spec=json.loads((HERE/'SPEC.json').read_text())
 for path,h in spec['dependencies'].items():assert sha(ROOT/path)==h,path
 for path in [f'research/benchmarks/{HERE.name}/run.py',f'research/benchmarks/{HERE.name}/SPEC.json',*spec['dependencies']]:
  assert subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)==(ROOT/path).read_bytes(),path
 n=len(spec['points']);assert n==len(spec['labels'])==NPOINTS and sorted(sum(spec['batches']['A'],[])+sum(spec['batches']['B'],[]))==list(range(n)) and all(len(j)<=spec['limits']['points_per_job'] for b in spec['batches'].values() for j in b)
 validate_grid(spec)
 return spec

def ladder(case):
 """Attach d (CUTOFF-SHELL-012) exactly as frozen, re-verifying the c and d shell constructions."""
 case=copy.deepcopy(case);b=case['cutoffs']['b']
 c=json.loads((ROOT/'research/benchmarks/cutoff_ladder_003/SPEC.json').read_text())['additional_cutoff']
 expected=sorted({(x+dx,y+dy) for x,y in b['ordered_indices'] for dx,dy in b['stencil']});assert c['ordered_indices']==[list(v) for v in expected]
 case['cutoffs']['d']=json.loads((ROOT/'research/benchmarks/cutoff_shell_012/SPEC.json').read_text())['additional_cutoff'];d=case['cutoffs']['d']
 expected=sorted({(x+dx,y+dy) for x,y in c['ordered_indices'] for dx,dy in b['stencil']})
 assert d['ordered_indices']==[list(v) for v in expected] and d['dimension']==4*len(expected)==604 and d['selected_bands_zero_based']==[301,302]
 assert case['cutoffs']['a']['selected_bands_zero_based']==[97,98]
 return case

def validate_grid(cfg):
 from fractions import Fraction as F
 n=cfg['grid']['n'];assert [cfg['points'][j*n+i] for j in range(n) for i in range(n)]==[[str(F(2*i+1,2*n)),str(F(2*j+1,2*n))] for j in range(n) for i in range(n)]
 assert len({tuple(p) for p in cfg['points']})==len(cfg['points'])

def gaps(E,case,k):
 lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];return {'lower_meV':float(E[lo]-E[lo-1]),'upper_meV':float(E[hi+1]-E[hi]),'pair_meV':float(E[hi]-E[lo])}

def worker(a):
 cfg=bound(a.commit);lim=cfg['limits'];assert all(os.environ.get(k)=='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'])
 import numpy as np
 from scipy.linalg import eigh
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','old')
 np,base,assembly,case,provenance=old.setup(a.wheel);case=ladder(case);provenance.update(python=sys.version,numpy=np.__version__,scipy=__import__('scipy').__version__,limits=lim,rlimit_as=resource.getrlimit(resource.RLIMIT_AS),rlimit_fsize=resource.getrlimit(resource.RLIMIT_FSIZE),threads={k:os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']});fp=fastpipe();co={k:fp.FastPointMatrix(base,assembly,old.float_coefficients(assembly,case,k)[0]) for k in KEYS};rows=[];arrays={f'{k}_energies':[] for k in KEYS}
 solves=0
 for index in cfg['batches'][a.batch][a.job]:
  x,y=cfg['points'][index];row={'index':index,'label':cfg['labels'][index],'center':[x,y],'gaps':{}}
  for k in KEYS:
   H=co[k](x,y);assert np.max(abs(H-H.T))<1e-10;E=eigh(H,driver='evr',eigvals_only=True);solves+=1;assert np.all(np.diff(E)>=0)
   arrays[k+'_energies'].append(E);row['gaps'][k]=gaps(E,case,k)
  rows.append(row)
 write(a.output/'SAMPLES.json',rows);write(a.output/'RUNTIME.json',provenance);write(a.output/'WORK.json',{'eigensolves':solves,'points':len(rows),'eigvals_only':True});(a.output/'STATES.pack').write_bytes(fp.pack_states({k:np.array(v) for k,v in arrays.items()}))

from fractions import Fraction
def periodic_dist(p,q):
 dx=abs(p[0]-q[0])%1;dy=abs(p[1]-q[1])%1;return (min(dx,1-dx)**2+min(dy,1-dy)**2)**.5

def summarize(cfg,rows,commit):
 import numpy as np
 n=cfg['grid']['n'];cand={k:tuple(map(float,v)) for k,v in cfg['candidates'].items()};out={'implementation_commit':commit,'independent_review':'PENDING','scope':cfg['scope'],'grid_points':n*n,'maps':{},'changes_a_to_d':{},'local_minima_d':{},'new_region_flags':[]}
 G=rows[:n*n]
 for k in KEYS:
  for g in ('lower_meV','upper_meV','pair_meV'):
   M=np.array([r['gaps'][k][g] for r in G]).reshape(n,n);j,i=np.unravel_index(np.argmin(M),M.shape)
   out['maps'][k+'_'+g]={'min':float(M.min()),'argmin_label':G[j*n+i]['label'],'argmin_center':G[j*n+i]['center'],'median':float(np.median(M)),'max':float(M.max())}
 for g in ('lower_meV','upper_meV','pair_meV'):
  D=np.array([r['gaps']['d'][g]-r['gaps']['a'][g] for r in G]);out['changes_a_to_d'][g]={'max_abs':float(abs(D).max()),'at_label':G[int(np.argmax(abs(D)))]['label'],'median_abs':float(np.median(abs(D)))}
 for g in ('lower_meV','upper_meV'):
  M=np.array([r['gaps']['d'][g] for r in G]).reshape(n,n);mins=[]
  for j in range(n):
   for i in range(n):
    v=M[j,i]
    if all(v<M[(j+dj)%n,(i+di)%n] for dj in (-1,0,1) for di in (-1,0,1) if (dj,di)!=(0,0)):
     r=G[j*n+i];p=tuple(float(Fraction(c)) for c in r['center']);near=min(cand,key=lambda c:periodic_dist(p,cand[c]))
     mins.append({'label':r['label'],'center':r['center'],'gap_d_meV':float(v),'gap_a_meV':r['gaps']['a'][g],'nearest_candidate':near,'distance':periodic_dist(p,cand[near])})
  mins.sort(key=lambda m:m['gap_d_meV']);out['local_minima_d'][g]={'count':len(mins),'minima':mins}
  out['new_region_flags']+=[dict(m,gap=g) for m in mins if m['gap_d_meV']<1.0 and m['distance']>2/64]
 return out

def replay(a):
 import numpy as np
 cfg=bound(a.commit);case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));fp=fastpipe();jobs=cfg['batches'][a.batch];rows=[]
 batch=json.loads((a.output/'BATCH.json').read_text());assert batch['status']=='PASS' and batch['source_commit']==a.commit and batch['retries']==0 and batch['not_started_jobs']==[] and len(batch['receipts'])==len(jobs)
 solves=0
 for job,owned in enumerate(jobs):
  d=a.output/f'job{job:03}';receipt=json.loads((d/'RECEIPT.json').read_text());assert receipt in batch['receipts']
  assert receipt['exit_code']==0 and receipt['termination']=='NORMAL_EXIT' and receipt['process_group_empty'] and receipt['planned_points']==owned and receipt['source_commit']==a.commit and 'evidence_error' not in receipt
  assert {str(p.relative_to(d)) for p in d.rglob('*') if p.is_file()}==set(receipt['files'])|{'RECEIPT.json'}
  for name,item in receipt['files'].items():assert sha(d/name)==item['sha256'] and (d/name).stat().st_size==item['bytes'],name
  runtime=json.loads((d/'RUNTIME.json').read_text());assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76' and set(runtime['threads'].values())=={'1'}
  assert runtime['rlimit_as']==[cfg['limits']['address_space_bytes']]*2 and runtime['rlimit_fsize']==[cfg['limits']['file_bytes']]*2
  work=json.loads((d/'WORK.json').read_text());assert work=={'eigensolves':len(KEYS)*len(owned),'points':len(owned),'eigvals_only':True};solves+=work['eigensolves']
  data=fp.unpack_states((d/'STATES.pack').read_bytes());saved=json.loads((d/'SAMPLES.json').read_text());assert [r['index'] for r in saved]==owned
  for local,r in enumerate(saved):
   assert r['center']==cfg['points'][r['index']] and r['label']==cfg['labels'][r['index']]
   for k in KEYS:
    E=data[k+'_energies'][local];assert E.shape==(case['cutoffs'][k]['dimension'],) and np.isfinite(E).all() and np.all(np.diff(E)>=0) and gaps(E,case,k)==r['gaps'][k]
   rows.append(r)
 write(a.output/'MAP.json',{'implementation_commit':a.commit,'batch':a.batch,'independent_review':'PENDING','kind':'full-cell momentum gap maps, not time evolution','eigensolves':solves,'samples':rows});print(f'REPLAY_PASS batch {a.batch}: {len(rows)} points, {solves} solves verified, zero physical eigensolves')

def combine(a):
 """Merge the two replayed batch MAPs; regression and summary over the full grid. Zero solves."""
 cfg=bound(a.commit);rows={}
 for b in ('A','B'):
  m=json.loads((a.output/b/'MAP.json').read_text());assert m['implementation_commit']==a.commit and m['batch']==b
  for r in m['samples']:assert r['index'] not in rows;rows[r['index']]=r
 rows=[rows[i] for i in range(NPOINTS)]
 reg=cfg['regression'];worst={'lower':0.0,'upper':0.0};count=0
 for key,g in (('lower','lower_meV'),('upper','upper_meV')):
  for k,ref in reg[key+'_gap_meV'].items():
   for i,v in ref.items():worst[key]=max(worst[key],abs(rows[int(i)]['gaps'][k][g]-v));count+=1
 assert max(worst.values())<=reg['threshold_meV'],worst
 write(a.output/'REGRESSION.json',{'sources':reg['sources'],'compared_point_cutoff_gap_values':count,'max_abs_lower_gap_difference_meV':worst['lower'],'max_abs_upper_gap_difference_meV':worst['upper'],'threshold_meV':reg['threshold_meV'],'note':'eigenvalue-only solves; tolerance comparison','status':'PASS'})
 write(a.output/'SUMMARY.json',summarize(cfg,rows,a.commit));print('COMBINE_PASS')

def controls(a):
 import numpy as np
 cfg=json.loads((HERE/'SPEC.json').read_text());validate_grid(cfg);case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()))
 E=np.arange(10.);c={'cutoffs':{'z':{'selected_bands_zero_based':[4,5]}}};assert gaps(E,c,'z')=={'lower_meV':1.0,'upper_meV':1.0,'pair_meV':1.0}
 assert abs(periodic_dist((0.01,0.5),(0.99,0.5))-0.02)<1e-12
 import concurrent_supervisor as cs
 assert all(len(v)%cfg['limits']['concurrent_workers']==0 and all(1<=len(j)<=32 for j in v) for v in cfg['batches'].values())
 write(a.output,{'status':'PASS','physical_eigensolves':0,'checks':['c and d shells re-derived','exact 128x128 cell-centred grid','gap definitions','periodic distance','both batch partitions valid for the reviewed supervisor'],'points':NPOINTS})

def run(a):
 cfg=bound(a.commit);lim=cfg['limits'];import concurrent_supervisor as cs
 jobs=[cs.Job(f'job{j:03}',(sys.executable,'-B',str(HERE/'run.py'),'worker','--batch',a.batch,'--job',str(j),'--commit',a.commit,'--output','{output}','--wheel',str(Path(a.wheel).resolve())),tuple(owned)) for j,owned in enumerate(cfg['batches'][a.batch])]
 limits=cs.Limits(workers=lim['concurrent_workers'],job_seconds=lim['job_timeout_seconds'],batch_seconds=lim['batch_timeout_seconds'],address_space_bytes=lim['address_space_bytes'],file_bytes=lim['file_bytes'])
 cs.run_jobs(jobs,a.output,cwd=ROOT,source_commit=a.commit,limits=limits);replay(a)

if __name__=='__main__':
 sys.path.insert(0,str(ROOT/'research/tools/concurrent'))
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay','controls','combine']);p.add_argument('--commit');p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);p.add_argument('--batch',choices=['A','B'])
 a=p.parse_args();globals()[a.mode](a)
