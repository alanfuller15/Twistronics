"""VALLEY-027: 1/1024 gap map of the R2-R4 valley at cutoff d (batches A, B; eigenvalues only) and discrete
loop signs around the SWEEP-D-026 shallow lower-gap dip (batch C; full evr with four-state vectors), against a
frozen all-+1 prediction. Reviewed concurrent_supervisor; one launch per batch, no retries. Not gated on review.
Modes: controls, run --batch, worker, replay --batch (zero solves), combine (zero solves).
"""
import argparse,copy,hashlib,importlib.util,json,os,resource,subprocess,sys,time,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];KEYS=['d'];NPOINTS=17977
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
 n=len(spec['points']);assert n==len(spec['labels'])==NPOINTS and sorted(sum(sum(spec['batches'].values(),[]),[]))==list(range(n)) and all(len(j)<=spec['limits']['points_per_job'] for b in spec['batches'].values() for j in b)
 validate_geometry(spec)
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

def validate_geometry(cfg):
 from fractions import Fraction as F
 g=cfg['grid'];x0,x1=g['x_range'];y0,y1=g['y_range'];D=g['denominator']
 assert cfg['points'][:g['points']]==[[str(F(x,D)),str(F(y,D))] for y in range(y0,y1+1) for x in range(x0,x1+1)]
 for loop in cfg['loops']:
  x0,x1=loop['x_range'];y0,y1=loop['y_range'];D=loop['lattice_denominator']
  pts=[(x,y0) for x in range(x0,x1)]+[(x1,y) for y in range(y0,y1)]+[(x,y1) for x in range(x1,x0,-1)]+[(x0,y) for y in range(y1,y0,-1)]
  assert [cfg['points'][i] for i in loop['point_indices']]==[[str(F(x,D)),str(F(y,D))] for x,y in pts]
 assert len({tuple(p) for p in cfg['points']})==len(cfg['points'])

def gaps(E,case,k):
 lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];return {'lower_meV':float(E[lo]-E[lo-1]),'upper_meV':float(E[hi+1]-E[hi]),'pair_meV':float(E[hi]-E[lo])}

def worker(a):
 cfg=bound(a.commit);assert all(os.environ.get(k)=='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'])
 import numpy as np
 from scipy.linalg import eigh
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','old')
 np,base,assembly,case,provenance=old.setup(a.wheel);case=ladder(case);provenance.update(python=sys.version,numpy=np.__version__,scipy=__import__('scipy').__version__,limits=cfg['limits'],rlimit_as=resource.getrlimit(resource.RLIMIT_AS),rlimit_fsize=resource.getrlimit(resource.RLIMIT_FSIZE),threads={k:os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']})
 vectors=a.batch=='C';fp=fastpipe();co={k:fp.FastPointMatrix(base,assembly,old.float_coefficients(assembly,case,k)[0]) for k in KEYS};rows=[];arrays={f'{k}_energies':[] for k in KEYS};solves=0
 if vectors:arrays.update({f'{k}_vectors':[] for k in KEYS})
 for index in cfg['batches'][a.batch][a.job]:
  x,y=cfg['points'][index];row={'index':index,'label':cfg['labels'][index],'center':[x,y],'gaps':{}}
  for k in KEYS:
   H=co[k](x,y);assert np.max(abs(H-H.T))<1e-10;lo,hi=case['cutoffs'][k]['selected_bands_zero_based']
   if vectors:
    E,v=eigh(H,driver='evr');V=v[:,lo-1:hi+2];res=float(np.max(abs(H@V-V*E[lo-1:hi+2])));assert res<1e-8;row['eigenpair_residual_meV']={k:res};arrays[k+'_vectors'].append(V)
   else:E=eigh(H,driver='evr',eigvals_only=True)
   solves+=1;assert np.all(np.diff(E)>=0);arrays[k+'_energies'].append(E);row['gaps'][k]=gaps(E,case,k)
  rows.append(row)
 write(a.output/'SAMPLES.json',rows);write(a.output/'RUNTIME.json',provenance);write(a.output/'WORK.json',{'eigensolves':solves,'points':len(rows),'eigvals_only':not vectors})
 (a.output/'STATES.pack').write_bytes(fp.pack_states({k:np.array(v) for k,v in arrays.items()}))

GROUPS={'lo_minus_1':[0],'lo':[1],'hi':[2],'hi_plus_1':[3],'selected_pair':[1,2],'four':[0,1,2,3]}
def loop_holonomy(Vs,cols,threshold=0.5):
 """Closed discrete transport (identical to LOOP-ROBUSTNESS-007): log determinants avoid underflow; polar product keeps orientation."""
 import numpy as np
 P=np.eye(len(cols));sign=1.;logabs=0.;smin=1.;links=[]
 for i in range(len(Vs)):
  O=Vs[i][:,cols].T@Vs[(i+1)%len(Vs)][:,cols];u,s,vt=np.linalg.svd(O);sg,lg=np.linalg.slogdet(O)
  links.append({'from':i,'to':(i+1)%len(Vs),'sign':int(sg),'min_singular_value':float(min(s))})
  sign*=sg;logabs+=lg;smin=min(smin,float(min(s)));P=P@(u@vt)
 valid=bool(smin>=threshold and sign!=0 and np.isfinite(logabs))
 return {'valid':valid,'sign':int(sign) if valid else None,'raw_determinant':float(sign*np.exp(logabs)) if np.isfinite(logabs) else 0.,'log_abs_determinant':float(logabs) if np.isfinite(logabs) else None,'polar_determinant':float(np.linalg.det(P)),'min_step_singular_value':smin,'links':links}

def replay(a):
 import numpy as np
 cfg=bound(a.commit);case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));fp=fastpipe();jobs=cfg['batches'][a.batch];rows=[];vectors={};vec=a.batch=='C'
 batch=json.loads((a.output/'BATCH.json').read_text());assert batch['status']=='PASS' and batch['source_commit']==a.commit and batch['retries']==0 and batch['not_started_jobs']==[] and len(batch['receipts'])==len(jobs)
 solves=0
 for job,owned in enumerate(jobs):
  d=a.output/f'job{job:03}';receipt=json.loads((d/'RECEIPT.json').read_text());assert receipt in batch['receipts']
  assert receipt['exit_code']==0 and receipt['termination']=='NORMAL_EXIT' and receipt['process_group_empty'] and receipt['planned_points']==owned and receipt['source_commit']==a.commit and 'evidence_error' not in receipt
  assert {str(p.relative_to(d)) for p in d.rglob('*') if p.is_file()}==set(receipt['files'])|{'RECEIPT.json'}
  for name,item in receipt['files'].items():assert sha(d/name)==item['sha256'] and (d/name).stat().st_size==item['bytes'],name
  runtime=json.loads((d/'RUNTIME.json').read_text());assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76' and set(runtime['threads'].values())=={'1'}
  assert runtime['rlimit_as']==[cfg['limits']['address_space_bytes']]*2 and runtime['rlimit_fsize']==[cfg['limits']['file_bytes']]*2
  work=json.loads((d/'WORK.json').read_text());assert work=={'eigensolves':len(owned),'points':len(owned),'eigvals_only':not vec};solves+=work['eigensolves']
  data=fp.unpack_states((d/'STATES.pack').read_bytes());saved=json.loads((d/'SAMPLES.json').read_text());assert [r['index'] for r in saved]==owned
  for local,r in enumerate(saved):
   assert r['center']==cfg['points'][r['index']] and r['label']==cfg['labels'][r['index']]
   E=data['d_energies'][local];assert E.shape==(604,) and np.isfinite(E).all() and np.all(np.diff(E)>=0) and gaps(E,case,'d')==r['gaps']['d']
   if vec:
    V=data['d_vectors'][local];assert V.shape==(604,4) and np.max(abs(V.T@V-np.eye(4)))<1e-10 and r['eigenpair_residual_meV']['d']<1e-8;vectors[r['index']]=V
   rows.append(r)
 out={'implementation_commit':a.commit,'batch':a.batch,'independent_review':'PENDING','kind':'momentum gap samples and loops at cutoff d, not time evolution','eigensolves':solves,'samples':rows}
 if vec:
  hol={};case_d=case['cutoffs']['d'];lo,hi=case_d['selected_bands_zero_based']
  spec_E={r['index']:r for r in rows}
  for loop in cfg['loops']:
   idx=loop['point_indices'];entry={}
   for g,cols in GROUPS.items():
    vs=[vectors[i] for i in idx];r=loop_holonomy(vs,cols,cfg['holonomy']['min_step_overlap']);r.pop('links');r['reverse_sign']=loop_holonomy(vs[::-1],cols,cfg['holonomy']['min_step_overlap'])['sign']
    r['predicted']=loop['predicted_signs'][g];r['match']=bool(r['valid'] and r['sign']==r['predicted'] and r['reverse_sign']==r['sign']);entry[g]=r
   entry['min_sampled_lower_gap_meV']=min(spec_E[i]['gaps']['d']['lower_meV'] for i in idx);entry['min_sampled_upper_gap_meV']=min(spec_E[i]['gaps']['d']['upper_meV'] for i in idx)
   hol[loop['id']]=entry
  out['holonomy']=hol
 write(a.output/'MAP.json',out);print(f'REPLAY_PASS batch {a.batch}: {len(rows)} points, {solves} solves verified, zero physical eigensolves')

def combine(a):
 """Grid map summary (A+B) and loop verdicts (C). Zero solves."""
 import numpy as np
 from fractions import Fraction as F
 cfg=bound(a.commit);maps={b:json.loads((a.output/b/'MAP.json').read_text()) for b in 'ABC'}
 for b,m in maps.items():assert m['implementation_commit']==a.commit and m['batch']==b
 g=cfg['grid'];nx=g['x_range'][1]-g['x_range'][0]+1;ny=g['y_range'][1]-g['y_range'][0]+1
 rows={r['index']:r for b in 'AB' for r in maps[b]['samples']};assert sorted(rows)==list(range(g['points']))
 cand={k:tuple(map(float,v)) for k,v in cfg['candidates'].items()};S={'implementation_commit':a.commit,'independent_review':'PENDING','scope':cfg['scope'],'grid':{},'loops':{},'all_loop_predictions_matched':True}
 for gname in ('lower_meV','upper_meV','pair_meV'):
  M=np.array([rows[i]['gaps']['d'][gname] for i in range(g['points'])]).reshape(ny,nx);j,i=np.unravel_index(np.argmin(M),M.shape)
  mins=[]
  for jj in range(1,ny-1):
   for ii in range(1,nx-1):
    v=M[jj,ii]
    if all(v<M[jj+dj,ii+di] for dj in (-1,0,1) for di in (-1,0,1) if (dj,di)!=(0,0)):
     r=rows[jj*nx+ii];p=tuple(float(F(c)) for c in r['center']);near=min(cand,key=lambda c:((p[0]-cand[c][0])**2+(p[1]-cand[c][1])**2)**.5)
     mins.append({'label':r['label'],'center':r['center'],'gap_meV':float(v),'nearest_candidate':near,'distance':((p[0]-cand[near][0])**2+(p[1]-cand[near][1])**2)**.5})
  mins.sort(key=lambda m:m['gap_meV'])
  S['grid'][gname]={'min':float(M.min()),'argmin_center':rows[int(j)*nx+int(i)]['center'],'median':float(np.median(M)),'interior_local_minima':mins}
 for lid,e in maps['C']['holonomy'].items():
  S['loops'][lid]={k:({kk:e[k][kk] for kk in ('sign','reverse_sign','predicted','match','valid','raw_determinant','min_step_singular_value')} if isinstance(e[k],dict) else e[k]) for k in e}
  S['all_loop_predictions_matched']&=all(e[k]['match'] for k in GROUPS)
 S['eigensolves']=sum(m['eigensolves'] for m in maps.values())
 write(a.output/'SUMMARY.json',S);print('COMBINE_PASS matched:',S['all_loop_predictions_matched'])

def controls(a):
 import numpy as np
 cfg=json.loads((HERE/'SPEC.json').read_text());validate_geometry(cfg);ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()))
 line=[np.array([[np.cos(t/2)],[np.sin(t/2)]]) for t in np.arange(32)*2*np.pi/32]
 assert loop_holonomy(line,[0])['sign']==-1 and loop_holonomy([np.array([[1.],[0.]])]*32,[0])['sign']==1
 import concurrent_supervisor as cs
 assert all(len(v)%cfg['limits']['concurrent_workers']==0 and all(1<=len(j)<=32 for j in v) for v in cfg['batches'].values())
 write(a.output,{'status':'PASS','physical_eigensolves':0,'checks':['d shell re-derived','exact 1/1024 valley grid','three exact 1/4096 loops, R2 outside all','synthetic holonomy -1/+1','batch partitions valid for the reviewed supervisor'],'points':NPOINTS})

def run(a):
 cfg=bound(a.commit);lim=cfg['limits'];import concurrent_supervisor as cs
 jobs=[cs.Job(f'job{j:03}',(sys.executable,'-B',str(HERE/'run.py'),'worker','--batch',a.batch,'--job',str(j),'--commit',a.commit,'--output','{output}','--wheel',str(Path(a.wheel).resolve())),tuple(owned)) for j,owned in enumerate(cfg['batches'][a.batch])]
 limits=cs.Limits(workers=lim['concurrent_workers'],job_seconds=lim['job_timeout_seconds'],batch_seconds=lim['batch_timeout_seconds'],address_space_bytes=lim['address_space_bytes'],file_bytes=lim['file_bytes'])
 cs.run_jobs(jobs,a.output,cwd=ROOT,source_commit=a.commit,limits=limits);replay(a)

if __name__=='__main__':
 sys.path.insert(0,str(ROOT/'research/tools/concurrent'))
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay','controls','combine']);p.add_argument('--commit');p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);p.add_argument('--batch',choices=['A','B','C'])
 a=p.parse_args();globals()[a.mode](a)
