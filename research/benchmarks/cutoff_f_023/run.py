"""CUTOFF-F-023: the sixth nested cutoff f (dimension 996) on all twelve local loops at R3, R1, R2 and R4.
Computation is not gated on review.

Reuse (authorized upgrade): cutoff-e energies and four-state vectors are read from retained, SHA-256-bound
state files of CONTROLS-E-022 (this branch) and LOWER-CONTROLS-021 (Codex; materialized, passed as
--reuse-021). Only f is eigensolved. At every point the e matrix is rebuilt (FastPointMatrix, no
eigensolve) for the e-in-f nested residual and for the residual of the retained e eigenpairs against it;
on the 64 regression points e is re-solved and must be byte-identical to the retained arrays.
Comparisons and six-group holonomy as CONTROLS-E-022 (link e->f). Jobs of 24, 4 concurrent workers.

Modes: controls, run (supervise bounded jobs, resumable), worker (one job), replay (no physical eigensolves).
"""
import argparse,copy,hashlib,importlib.util,json,os,resource,subprocess,sys,time,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];KEYS=['e','f'];SOLVE=['f'];LINKS=[('e','f')];NPOINTS=384
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
 """Attach c (CUTOFF-LADDER-003) and d (CUTOFF-SHELL-012) exactly as frozen, re-verifying both shell constructions."""
 case=copy.deepcopy(case);b=case['cutoffs']['b']
 case['cutoffs']['c']=json.loads((ROOT/'research/benchmarks/cutoff_ladder_003/SPEC.json').read_text())['additional_cutoff'];c=case['cutoffs']['c']
 expected=sorted({(x+dx,y+dy) for x,y in b['ordered_indices'] for dx,dy in b['stencil']})
 assert c['ordered_indices']==[list(v) for v in expected] and c['dimension']==4*len(expected)==444 and c['selected_bands_zero_based']==[221,222]
 case['cutoffs']['d']=json.loads((ROOT/'research/benchmarks/cutoff_shell_012/SPEC.json').read_text())['additional_cutoff'];d=case['cutoffs']['d']
 expected=sorted({(x+dx,y+dy) for x,y in c['ordered_indices'] for dx,dy in b['stencil']})
 assert d['ordered_indices']==[list(v) for v in expected] and d['dimension']==4*len(expected)==604 and d['selected_bands_zero_based']==[301,302]
 case['cutoffs']['e']=json.loads((HERE/'SPEC.json').read_text())['additional_cutoff_e'];e=case['cutoffs']['e']
 expected=sorted({(x+dx,y+dy) for x,y in d['ordered_indices'] for dx,dy in b['stencil']})
 assert e['ordered_indices']==[list(v) for v in expected] and e['dimension']==4*len(expected)==788 and e['selected_bands_zero_based']==[393,394]
 case['cutoffs']['f']=json.loads((HERE/'SPEC.json').read_text())['additional_cutoff_f'];f=case['cutoffs']['f']
 expected=sorted({(x+dx,y+dy) for x,y in e['ordered_indices'] for dx,dy in b['stencil']})
 assert f['ordered_indices']==[list(v) for v in expected] and f['dimension']==4*len(expected)==996 and f['selected_bands_zero_based']==[497,498]
 return case

def reused_e(cfg,a,fp):
 """Retained cutoff-e states, every file checked against its SHA-256 in SPEC.reuse before use."""
 import numpy as np
 src=cfg['reuse']['sources'];roots={'022':ROOT/src['022']['root'],'021':Path(a.reuse_021)}
 cache={};out={}
 for name,s in src.items():
  for rel,h in s['files'].items():assert sha(roots[name]/rel)==h,(name,rel)
 for i,(name,d,r) in cfg['reuse']['point_source'].items():
  key=(name,d)
  if key not in cache:
   p=roots[name]/d;data=fp.unpack_states((p/'STATES.pack').read_bytes()) if name=='022' else dict(np.load(p/'STATES.npz'))
   cache[key]=(data,json.loads((p/'SAMPLES.json').read_text()))
  data,rows=cache[key];assert rows[r]['center']==cfg['points'][int(i)]
  out[int(i)]=(np.array(data['e_energies'][r]),np.array(data['e_vectors'][r]))
 return out

def pair_case(case,left,right):return {'cutoffs':{'a':case['cutoffs'][left],'b':case['cutoffs'][right]}}

def metrics(sc,case,E,V):
 import numpy as np
 out={}
 for left,right in LINKS:
  pair=pair_case(case,left,right);ii=sc.embedding(pair);ov=V[left].T@V[right][ii,:]
  m=sc.measure(pair,ii,E[left],E[right],V[left],V[right])
  for g in ('pair','four'):m[g].pop('projector_frobenius_distance')   # cancellation-prone legacy formula (see CUTOFF-SHELL-012); not used here
  out[left+right]={'metrics':m,'minimum_pair_weight_in_four':float(min(np.linalg.svd(ov[1:3,:],compute_uv=False)**2))}
 return out

def worker(a):
 cfg=bound(a.commit);lim=cfg['limits'];assert all(os.environ.get(k)=='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']);resource.setrlimit(resource.RLIMIT_AS,(lim['address_space_bytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(lim['file_bytes'],)*2)
 import numpy as np
 from scipy.linalg import eigh
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','old');sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc')
 np,base,assembly,case,provenance=old.setup(a.wheel);case=ladder(case);provenance.update(python=sys.version,numpy=np.__version__,scipy=__import__('scipy').__version__,limits=lim,threads={k:os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']});fp=fastpipe();co={k:fp.FastPointMatrix(base,assembly,old.float_coefficients(assembly,case,k)[0]) for k in KEYS};rows=[];arrays={f'{k}_{t}':[] for k in SOLVE for t in ['energies','vectors']};R_e=reused_e(cfg,a,fp);regset=set(cfg['reuse']['regression_points'])
 for index in cfg['jobs'][a.job]:
  x,y=cfg['points'][index];H={k:co[k](x,y) for k in KEYS};nested={}
  for left,right in LINKS:
   ii=sc.embedding(pair_case(case,left,right));nested[left+right]=float(np.max(abs(H[right][np.ix_(ii,ii)]-H[left])));assert nested[left+right]<1e-10
  E={};V={};res={};reuse={}
  for k in KEYS:
   assert np.max(abs(H[k]-H[k].T))<1e-10;lo,hi=case['cutoffs'][k]['selected_bands_zero_based']
   if k in SOLVE:
    E[k],v=eigh(H[k],driver='evr');V[k]=v[:,lo-1:hi+2];arrays[k+'_energies'].append(E[k]);arrays[k+'_vectors'].append(V[k])
   else:
    E[k],V[k]=R_e[index]
    if index in regset:
     e2,v2=eigh(H[k],driver='evr');reuse['e_resolved_bit_identical']=bool(e2.tobytes()==E[k].tobytes() and np.ascontiguousarray(v2[:,lo-1:hi+2]).tobytes()==np.ascontiguousarray(V[k]).tobytes());assert reuse['e_resolved_bit_identical']
   res[k]=float(np.max(abs(H[k]@V[k]-V[k]*E[k][lo-1:hi+2])));assert res[k]<1e-8
  rows.append({'index':index,'label':cfg['labels'][index],'center':[x,y],'nested_residual_meV':nested,'eigenpair_residual_meV':res,'reuse':reuse,'comparisons':metrics(sc,case,E,V)})
 write(a.output/'SAMPLES.json',rows);write(a.output/'RUNTIME.json',provenance);(a.output/'STATES.pack').write_bytes(fp.pack_states({k:np.array(v) for k,v in arrays.items()}))

def gaps_meV(row,k):
 link,alias={'e':('ef','a'),'f':('ef','b')}[k];return row['comparisons'][link]['metrics']['pair'][alias+'_external_gaps_meV']

def validate_geometry(cfg):
 from fractions import Fraction as F
 assert len({tuple(p) for p in cfg['points']})==len(cfg['points'])
 for loop in cfg['loops']:
  c=list(map(F,loop['center']));r=F(loop['half_width']);n=loop['points_per_side'];corners=[(-r,-r),(r,-r),(r,r),(-r,r)];expected=[]
  for i,(x,y) in enumerate(corners):
   X,Y=corners[(i+1)%4]
   expected += [[str(c[0]+x+(X-x)*j/n),str(c[1]+y+(Y-y)*j/n)] for j in range(n)]
  assert [cfg['points'][i] for i in loop['point_indices']]==expected
 for patch in cfg['patches']:
  c=list(map(F,patch['center']));s=F(patch['step'])
  assert [cfg['points'][i] for i in patch['point_indices']]==[[str(c[0]+x*s),str(c[1]+y*s)] for y in [-1,0,1] for x in [-1,0,1]]

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

def holonomy(cfg,vectors,spectra,case):
 out={'scope':cfg['scope'],'min_step_overlap_required':cfg['holonomy']['min_step_overlap'],'loops':{}}
 for loop in cfg['loops']:
  idx=loop['point_indices'];entry={'geometry':loop,'cutoffs':{}}
  for k in KEYS:
   lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];entry['cutoffs'][k]={}
   for g,cols in GROUPS.items():
    vs=[vectors[i][k] for i in idx];r=loop_holonomy(vs,cols,cfg['holonomy']['min_step_overlap'])
    bands=[lo-1+c for c in cols];r['bands_zero_based']=bands
    r['minimum_sampled_external_gap_meV']=min(float(min(spectra[i][k][bands[0]]-spectra[i][k][bands[0]-1],spectra[i][k][bands[-1]+1]-spectra[i][k][bands[-1]])) for i in idx)
    r['reverse_sign']=loop_holonomy(vs[::-1],cols,cfg['holonomy']['min_step_overlap'])['sign'];assert r['sign']==r['reverse_sign']
    entry['cutoffs'][k][g]=r
  out['loops'][loop['id']]=entry
 return out

def summarize(cfg,rows,hol,commit):
 import numpy as np
 out={'implementation_commit':commit,'independent_review':'PENDING','scope':cfg['scope'],'loops':{},
      'max_eigenpair_residual_meV':max(max(r['eigenpair_residual_meV'].values()) for r in rows),'max_nested_residual_meV':max(max(r['nested_residual_meV'].values()) for r in rows)}
 for lid,entry in hol['loops'].items():
  out['loops'][lid]={k:{g:{'sign':r['sign'],'raw_determinant':r['raw_determinant'],'min_step_singular_value':r['min_step_singular_value'],'minimum_sampled_external_gap_microeV':1000*r['minimum_sampled_external_gap_meV']} for g,r in groups.items()} for k,groups in entry['cutoffs'].items()}
 out['links']={l+r_:{'maximum_abs_lower_gap_change_meV':max(abs(gaps_meV(r,r_)[0]-gaps_meV(r,l)[0]) for r in rows),'maximum_abs_upper_gap_change_meV':max(abs(gaps_meV(r,r_)[1]-gaps_meV(r,l)[1]) for r in rows),'maximum_four_angle_degrees':max(max(r['comparisons'][l+r_]['metrics']['four']['principal_angles_degrees']) for r in rows),'maximum_pair_angle_degrees':max(max(r['comparisons'][l+r_]['metrics']['pair']['principal_angles_degrees']) for r in rows),'minimum_pair_in_four_containment':min(r['comparisons'][l+r_]['minimum_pair_weight_in_four'] for r in rows)} for l,r_ in LINKS}
 return out

def replay(a):
 import numpy as np
 cfg=bound(a.commit);sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc');case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));rows=[];vectors=[];spectra=[];fp=fastpipe();R_e=reused_e(cfg,a,fp)
 batch=json.loads((a.output/'BATCH.json').read_text());assert batch['implementation_commit']==a.commit and batch['points']==NPOINTS and batch['jobs']==len(cfg['jobs']) and batch['eigensolver_starts']==len(SOLVE)*NPOINTS+len(cfg['reuse']['regression_points']) and batch['wall_seconds']<=cfg['limits']['batch_timeout_seconds'];fp=fastpipe()
 for job,owned in enumerate(cfg['jobs']):
  d=a.output/f'job{job:03}';receipt=json.loads((d/'RECEIPT.json').read_text())
  assert receipt['commit']==a.commit and receipt['exit_code']==0 and receipt['elapsed_seconds']<=cfg['limits']['job_timeout_seconds'] and receipt['eigensolver_starts']==len(SOLVE)*len(owned)+len(set(owned)&set(cfg['reuse']['regression_points']))
  assert receipt['points']==owned and receipt['process_group_empty'] and receipt['termination']=='NORMAL_EXIT'
  runtime=json.loads((d/'RUNTIME.json').read_text());assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76' and runtime['limits']==cfg['limits'] and set(runtime['threads'].values())=={'1'}
  assert {p.name for p in d.iterdir()}==set(receipt['files'])|{'RECEIPT.json'}
  for name,item in receipt['files'].items():assert sha(d/name)==item['sha256'] and (d/name).stat().st_size==item['bytes'],name
  data=fp.unpack_states((d/'STATES.pack').read_bytes());saved=json.loads((d/'SAMPLES.json').read_text());assert [r['index'] for r in saved]==owned
  for local,r in enumerate(saved):
   assert r['center']==cfg['points'][r['index']] and r['label']==cfg['labels'][r['index']] and max(r['nested_residual_meV'].values())<1e-10 and max(r['eigenpair_residual_meV'].values())<1e-8
   E={'f':data['f_energies'][local],'e':R_e[r['index']][0]};V={'f':data['f_vectors'][local],'e':R_e[r['index']][1]};assert r['reuse']=={'e_resolved_bit_identical':True} if r['index'] in cfg['reuse']['regression_points'] else r['reuse']=={}
   for k in KEYS:
    dim=case['cutoffs'][k]['dimension'];assert E[k].shape==(dim,) and V[k].shape==(dim,4) and np.isfinite(E[k]).all() and np.all(np.diff(E[k])>=0) and np.isfinite(V[k]).all() and np.max(abs(V[k].T@V[k]-np.eye(4)))<1e-10
   for key,m in metrics(sc,case,E,V).items():
    sc.close_metrics(m['metrics'],r['comparisons'][key]['metrics']);assert abs(m['minimum_pair_weight_in_four']-r['comparisons'][key]['minimum_pair_weight_in_four'])<1e-10
   rows.append(r);vectors.append(V);spectra.append(E)
 assert [r['index'] for r in rows]==list(range(NPOINTS))
 regp=cfg['reuse']['regression_points']
 write(a.output/'REGRESSION.json',{'reuse':'cutoff e states read from SHA-256-bound retained files (022 pack, 021 npz)','reused_points':NPOINTS,'e_resolved_bit_identical_points':sum(1 for r in rows if r['reuse'].get('e_resolved_bit_identical')),'regression_points':len(regp),'max_retained_e_eigenpair_residual_meV':max(r['eigenpair_residual_meV']['e'] for r in rows),'status':'PASS'})
 hol=holonomy(cfg,vectors,spectra,case);write(a.output/'HOLONOMY.json',hol)
 write(a.output/'SUMMARY.json',summarize(cfg,rows,hol,a.commit))
 write(a.output/'MAP.json',{'implementation_commit':a.commit,'independent_review':'PENDING','kind':'e/f closed momentum loops and controls, not time evolution','samples':rows});print(f'REPLAY_PASS: {len(rows)} points, zero physical eigensolves')

def controls(a):
 import numpy as np
 cfg=json.loads((HERE/'SPEC.json').read_text());validate_geometry(cfg);case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc')
 for left,right in LINKS:
  ii=sc.embedding(pair_case(case,left,right));assert len(ii)==case['cutoffs'][left]['dimension'] and len(set(ii))==len(ii)
 line=[np.array([[np.cos(t/2)],[np.sin(t/2)]]) for t in np.arange(32)*2*np.pi/32]
 assert loop_holonomy(line,[0])['sign']==-1 and loop_holonomy([np.array([[1.],[0.]])]*32,[0])['sign']==1
 assert loop_holonomy([np.array([[1.],[0.]]),np.array([[0.],[1.]])],[0])['sign'] is None
 frames=[np.column_stack((np.r_[v[:,0],0.],[0.,0.,1.])) for v in line];gauged=[]
 for i,v in enumerate(frames):
  t=i*.31;Q=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]]);Q[:,0]*=(-1)**i;gauged.append(v@Q)
 for vs in [frames,gauged,gauged[::-1]]:assert loop_holonomy(vs,[0,1])['sign']==-1
 write(a.output,{'status':'PASS','physical_eigensolves':0,'checks':['c, d, e and f shell constructions re-derived','distinct basis injection e/f','exact CCW square loop coordinates (twelve loops from 022 and 021)','nontrivial line -1, constant line +1, singular link invalid','O(2) gauge and reversal invariance'],'points':NPOINTS,'reuse_regression_points':len(cfg['reuse']['regression_points'])})

def run(a):
 """Bounded supervisor: up to limits.concurrent_workers isolated single-thread worker processes at once."""
 cfg=bound(a.commit);lim=cfg['limits'];a.output.mkdir(parents=True,exist_ok=True);env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1');started=time.monotonic()
 pending=[];running={}
 for j,owned in enumerate(cfg['jobs']):
  d=a.output/f'job{j:03}'
  if (d/'RECEIPT.json').exists():
   rec=json.loads((d/'RECEIPT.json').read_text());assert rec['commit']==a.commit and rec['exit_code']==0 and rec['points']==owned
   for name,item in rec['files'].items():assert sha(d/name)==item['sha256']
  else:pending.append(j)
 def finish(j,proc,t,termination,log):
  log.close();code=proc.returncode;d=a.output/f'job{j:03}';owned=cfg['jobs'][j]
  try:os.killpg(proc.pid,0);empty=False
  except ProcessLookupError:empty=True
  if not empty:os.killpg(proc.pid,signal.SIGKILL)
  write(d/'RECEIPT.json',{'commit':a.commit,'exit_code':code,'termination':termination,'process_group_empty':empty,'elapsed_seconds':time.monotonic()-t,'eigensolver_starts':len(SOLVE)*len(owned)+len(set(owned)&set(cfg['reuse']['regression_points'])) if code==0 else None,'points':owned,'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in d.iterdir()}})
  assert code==0 and empty and termination=='NORMAL_EXIT',f'worker {j} failed';print(f'Completed job {j+1}/{len(cfg["jobs"])} ({len(owned)} points)',flush=True)
 while pending or running:
  assert time.monotonic()-started<lim['batch_timeout_seconds']
  while pending and len(running)<lim['concurrent_workers']:
   j=pending.pop(0);d=a.output/f'job{j:03}';d.mkdir(exist_ok=False);log=(d/'WORKER.log').open('wb')
   proc=subprocess.Popen([sys.executable,'-B',str(HERE/'run.py'),'worker','--job',str(j),'--commit',a.commit,'--output',str(d),'--wheel',str(a.wheel),'--reuse-021',str(a.reuse_021)],stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
   running[j]=(proc,time.monotonic(),log)
  time.sleep(0.05)
  for j,(proc,t,log) in list(running.items()):
   if proc.poll() is not None:del running[j];finish(j,proc,t,'NORMAL_EXIT',log)
   elif time.monotonic()-t>lim['job_timeout_seconds'] or time.monotonic()-started>lim['batch_timeout_seconds']:
    os.killpg(proc.pid,signal.SIGKILL);proc.wait();del running[j];finish(j,proc,t,'WATCHDOG_TIMEOUT',log)
 wall=time.monotonic()-started
 receipts=[json.loads((a.output/f'job{j:03}'/'RECEIPT.json').read_text()) for j in range(len(cfg['jobs']))]
 write(a.output/'BATCH.json',{'implementation_commit':a.commit,'points':NPOINTS,'jobs':len(receipts),'eigensolver_starts':sum(r['eigensolver_starts'] for r in receipts),'summed_job_seconds':sum(r['elapsed_seconds'] for r in receipts),'wall_seconds':wall,'concurrent_workers':lim['concurrent_workers'],'authorization':cfg['authorization'],'independent_review':'PENDING'});replay(a)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay','controls']);p.add_argument('--commit');p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);p.add_argument('--reuse-021',dest='reuse_021')
 a=p.parse_args();globals()[a.mode](a)
