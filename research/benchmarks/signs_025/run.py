"""SIGNS-025: discrete sign-accounting test at cutoff d on seven exact rectangles (1/2048 lattice) that enclose
different subsets of the four candidates, against predictions frozen in SPEC. Computation is not gated on review.

Scheduling uses the Codex-reviewed concurrent_supervisor (byte-identical copy): whole-batch cleanup on any
failure, receipts per job, no resume or retries. Workers: FastPointMatrix, full-spectrum scipy evr, pack_states.
Modes: controls, run, worker, replay (no physical eigensolves).
"""
import argparse,copy,hashlib,importlib.util,json,os,resource,subprocess,sys,time,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];KEYS=['d'];NPOINTS=2453
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
 n=len(spec['points']);assert n==len(spec['labels'])==NPOINTS and sum(spec['jobs'],[])==list(range(n)) and max(map(len,spec['jobs']))<=spec['limits']['points_per_job']
 validate_geometry(spec)
 return spec

def ladder(case):
 case=copy.deepcopy(case);b=case['cutoffs']['b']
 c=json.loads((ROOT/'research/benchmarks/cutoff_ladder_003/SPEC.json').read_text())['additional_cutoff']
 expected=sorted({(x+dx,y+dy) for x,y in b['ordered_indices'] for dx,dy in b['stencil']});assert c['ordered_indices']==[list(v) for v in expected]
 case['cutoffs']['d']=json.loads((ROOT/'research/benchmarks/cutoff_shell_012/SPEC.json').read_text())['additional_cutoff'];d=case['cutoffs']['d']
 expected=sorted({(x+dx,y+dy) for x,y in c['ordered_indices'] for dx,dy in b['stencil']})
 assert d['ordered_indices']==[list(v) for v in expected] and d['dimension']==4*len(expected)==604 and d['selected_bands_zero_based']==[301,302]
 return case

def validate_geometry(cfg):
 from fractions import Fraction as F
 for loop in cfg['loops']:
  x0,x1=loop['x_range'];y0,y1=loop['y_range'];D=loop['lattice_denominator']
  pts=[(x,y0) for x in range(x0,x1)]+[(x1,y) for y in range(y0,y1)]+[(x,y1) for x in range(x1,x0,-1)]+[(x0,y) for y in range(y1,y0,-1)]
  assert [cfg['points'][i] for i in loop['point_indices']]==[[str(F(x,D)),str(F(y,D))] for x,y in pts]
 assert len({tuple(p) for p in cfg['points']})==len(cfg['points'])

def gaps(E,case,k):
 lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];return {'lower_meV':float(E[lo]-E[lo-1]),'upper_meV':float(E[hi+1]-E[hi])}

def worker(a):
 cfg=bound(a.commit);assert all(os.environ.get(k)=='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'])
 import numpy as np
 from scipy.linalg import eigh
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','old')
 np,base,assembly,case,provenance=old.setup(a.wheel);case=ladder(case);provenance.update(python=sys.version,numpy=np.__version__,scipy=__import__('scipy').__version__,limits=cfg['limits'],threads={k:os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},rlimit_as=resource.getrlimit(resource.RLIMIT_AS),rlimit_fsize=resource.getrlimit(resource.RLIMIT_FSIZE))
 fp=fastpipe();co={k:fp.FastPointMatrix(base,assembly,old.float_coefficients(assembly,case,k)[0]) for k in KEYS};rows=[];arrays={f'{k}_{t}':[] for k in KEYS for t in ['energies','vectors']};solves=0
 for index in cfg['jobs'][a.job]:
  x,y=cfg['points'][index];row={'index':index,'label':cfg['labels'][index],'center':[x,y],'gaps':{},'eigenpair_residual_meV':{}}
  for k in KEYS:
   H=co[k](x,y);assert np.max(abs(H-H.T))<1e-10;E,v=eigh(H,driver='evr');solves+=1;lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];V=v[:,lo-1:hi+2]
   row['eigenpair_residual_meV'][k]=float(np.max(abs(H@V-V*E[lo-1:hi+2])));assert row['eigenpair_residual_meV'][k]<1e-8
   row['gaps'][k]=gaps(E,case,k);arrays[k+'_energies'].append(E);arrays[k+'_vectors'].append(V)
  rows.append(row)
 write(a.output/'SAMPLES.json',rows);write(a.output/'RUNTIME.json',provenance);write(a.output/'WORK.json',{'eigensolves':solves,'points':len(rows)})
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
 cfg=bound(a.commit);case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));fp=fastpipe();rows=[];vectors=[];spectra=[]
 batch=json.loads((a.output/'BATCH.json').read_text());assert batch['status']=='PASS' and batch['source_commit']==a.commit and batch['retries']==0 and batch['not_started_jobs']==[] and len(batch['receipts'])==len(cfg['jobs'])
 solves=0
 for job,owned in enumerate(cfg['jobs']):
  d=a.output/f'job{job:03}';receipt=json.loads((d/'RECEIPT.json').read_text());assert receipt in batch['receipts']
  assert receipt['exit_code']==0 and receipt['termination']=='NORMAL_EXIT' and receipt['process_group_empty'] and receipt['planned_points']==owned and receipt['source_commit']==a.commit
  assert receipt['monotonic_end']-receipt['monotonic_start']<=cfg['limits']['job_timeout_seconds'] and 'evidence_error' not in receipt
  assert {str(p.relative_to(d)) for p in d.rglob('*') if p.is_file()}==set(receipt['files'])|{'RECEIPT.json'}
  for name,item in receipt['files'].items():assert sha(d/name)==item['sha256'] and (d/name).stat().st_size==item['bytes'],name
  runtime=json.loads((d/'RUNTIME.json').read_text());assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76' and set(runtime['threads'].values())=={'1'}
  assert runtime['rlimit_as']==[cfg['limits']['address_space_bytes']]*2 and runtime['rlimit_fsize']==[cfg['limits']['file_bytes']]*2
  work=json.loads((d/'WORK.json').read_text());assert work=={'eigensolves':len(KEYS)*len(owned),'points':len(owned)};solves+=work['eigensolves']
  data=fp.unpack_states((d/'STATES.pack').read_bytes());saved=json.loads((d/'SAMPLES.json').read_text());assert [r['index'] for r in saved]==owned
  for local,r in enumerate(saved):
   assert r['center']==cfg['points'][r['index']] and r['label']==cfg['labels'][r['index']] and max(r['eigenpair_residual_meV'].values())<1e-8
   E={k:data[k+'_energies'][local] for k in KEYS};V={k:data[k+'_vectors'][local] for k in KEYS}
   for k in KEYS:
    dim=case['cutoffs'][k]['dimension'];assert E[k].shape==(dim,) and V[k].shape==(dim,4) and np.isfinite(E[k]).all() and np.all(np.diff(E[k])>=0) and np.max(abs(V[k].T@V[k]-np.eye(4)))<1e-10 and gaps(E[k],case,k)==r['gaps'][k]
   rows.append(r);vectors.append(V);spectra.append(E)
 assert [r['index'] for r in rows]==list(range(NPOINTS))
 reg=cfg['regression'];worst={'lower':0.0,'upper':0.0};count=0
 for key,g in (('lower','lower_meV'),('upper','upper_meV')):
  for i,v in reg[key+'_gap_meV'].items():worst[key]=max(worst[key],abs(rows[int(i)]['gaps']['d'][g]-v));count+=1
 assert max(worst.values())<=reg['threshold_meV'],worst
 write(a.output/'REGRESSION.json',{'sources':reg['sources'],'compared_gap_values':count,'max_abs_lower_gap_difference_meV':worst['lower'],'max_abs_upper_gap_difference_meV':worst['upper'],'threshold_meV':reg['threshold_meV'],'status':'PASS'})
 hol={'scope':cfg['scope'],'loops':{}};summary={'implementation_commit':a.commit,'independent_review':'PENDING','scope':cfg['scope'],'eigensolves':solves,'loops':{},'all_predictions_matched':True,'invalid_groups':0}
 for loop in cfg['loops']:
  idx=loop['point_indices'];entry={};srow={'encloses':loop['encloses'],'groups':{}}
  for g,cols in GROUPS.items():
   vs=[vectors[i]['d'] for i in idx];r=loop_holonomy(vs,cols,cfg['holonomy']['min_step_overlap']);lo,hi=case['cutoffs']['d']['selected_bands_zero_based']
   bands=[lo-1+c for c in cols];r['bands_zero_based']=bands
   r['minimum_sampled_external_gap_meV']=min(float(min(spectra[i]['d'][bands[0]]-spectra[i]['d'][bands[0]-1],spectra[i]['d'][bands[-1]+1]-spectra[i]['d'][bands[-1]])) for i in idx)
   r['reverse_sign']=loop_holonomy(vs[::-1],cols,cfg['holonomy']['min_step_overlap'])['sign'];entry[g]=r
   pred=loop['predicted_signs'][g];match=r['valid'] and r['sign']==pred and r['reverse_sign']==r['sign']
   summary['all_predictions_matched']&=bool(match);summary['invalid_groups']+=0 if r['valid'] else 1
   srow['groups'][g]={'predicted':pred,'sign':r['sign'],'reverse_sign':r['reverse_sign'],'valid':r['valid'],'match':bool(match),'raw_determinant':r['raw_determinant'],'min_step_singular_value':r['min_step_singular_value'],'minimum_sampled_external_gap_meV':r['minimum_sampled_external_gap_meV']}
  hol['loops'][loop['id']]={'geometry':{k:loop[k] for k in ('x_range','y_range','lattice_denominator','encloses','predicted_signs')},'cutoffs':{'d':entry}};summary['loops'][loop['id']]=srow
 write(a.output/'HOLONOMY.json',hol);write(a.output/'SUMMARY.json',summary)
 write(a.output/'MAP.json',{'implementation_commit':a.commit,'independent_review':'PENDING','kind':'closed momentum rectangles at cutoff d, not time evolution','samples':rows});print(f'REPLAY_PASS: {len(rows)} points, zero physical eigensolves; predictions matched: {summary["all_predictions_matched"]}')

def controls(a):
 import numpy as np
 cfg=json.loads((HERE/'SPEC.json').read_text());validate_geometry(cfg);ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()))
 line=[np.array([[np.cos(t/2)],[np.sin(t/2)]]) for t in np.arange(32)*2*np.pi/32]
 assert loop_holonomy(line,[0])['sign']==-1 and loop_holonomy([np.array([[1.],[0.]])]*32,[0])['sign']==1 and loop_holonomy([np.array([[1.],[0.]]),np.array([[0.],[1.]])],[0])['sign'] is None
 for loop in cfg['loops']:
  assert all(v in (1,-1) for v in loop['predicted_signs'].values()) and loop['predicted_signs']['four']==1
 import concurrent_supervisor as cs
 assert len(cfg['jobs'])%cfg['limits']['concurrent_workers']==0 and all(1<=len(j)<=32 for j in cfg['jobs'])
 write(a.output,{'status':'PASS','physical_eigensolves':0,'checks':['d shell re-derived','seven exact CCW lattice rectangles','synthetic holonomy -1/+1/invalid','predictions frozen for all 42 loop-groups','job partition valid for the reviewed supervisor'],'points':NPOINTS})

def run(a):
 """One-shot batch through the reviewed supervisor. Bindings are verified here and again in every worker."""
 cfg=bound(a.commit);lim=cfg['limits'];import concurrent_supervisor as cs
 jobs=[cs.Job(f'job{j:03}',(sys.executable,'-B',str(HERE/'run.py'),'worker','--job',str(j),'--commit',a.commit,'--output','{output}','--wheel',str(Path(a.wheel).resolve())),tuple(owned)) for j,owned in enumerate(cfg['jobs'])]
 limits=cs.Limits(workers=lim['concurrent_workers'],job_seconds=lim['job_timeout_seconds'],batch_seconds=lim['batch_timeout_seconds'],address_space_bytes=lim['address_space_bytes'],file_bytes=lim['file_bytes'])
 cs.run_jobs(jobs,a.output,cwd=ROOT,source_commit=a.commit,limits=limits);replay(a)

if __name__=='__main__':
 sys.path.insert(0,str(ROOT/'research/tools/concurrent'))
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay','controls']);p.add_argument('--commit');p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int)
 a=p.parse_args();globals()[a.mode](a)
