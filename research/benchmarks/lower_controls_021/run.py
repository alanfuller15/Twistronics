"""LOWER-CONTROLS-021: stage 2 predeclared fitted-point loops. No retries or adaptive points.
Shared reviewed assembly and bounded supervisor; c/d/e spectra and four-state vectors retained.
Replay re-derives maps without physical eigensolves."""
import argparse,copy,hashlib,importlib.util,json,os,resource,subprocess,sys,time,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];KEYS=['c','d','e'];LINKS=[('c','d'),('d','e')];NPOINTS=192
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def bound(commit):
 """Exact-commit provenance: every executed or consumed file must equal its bytes at the frozen commit."""
 spec=json.loads((HERE/'SPEC.json').read_text())
 for path,h in spec['dependencies'].items():assert sha(ROOT/path)==h,path
 for path in [f'research/benchmarks/{HERE.name}/run.py',f'research/benchmarks/{HERE.name}/SPEC.json',f'research/benchmarks/{HERE.name}/CONTROLS.json',*spec['dependencies']]:
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
 return case

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
 link,alias={'c':('cd','a'),'d':('cd','b'),'e':('de','b')}[k];return 1000*row['comparisons'][link]['metrics']['pair'][alias+'_external_gaps_meV'][1]

def validate_geometry(cfg):
 from fractions import Fraction as F
 assert len({tuple(p) for p in cfg['points']})==len(cfg['points'])
 for grid in cfg.get('grids',[]):
  cx,cy=map(F,grid['center']);step=F(grid['step']);h=grid['half_steps']
  assert h==8 and step==F(1,32768)
  assert [cfg['points'][i] for i in grid['point_indices']]==[[str(cx+x*step),str(cy+y*step)] for y in range(-h,h+1) for x in range(-h,h+1)]
 for loop in cfg['loops']:
  base=list(map(F,loop['reference_center']));h=F(1,65536);family=loop['family']
  assert family in ['baseline','half_radius','translated_x4']
  expected_center=[base[0]+(4*h if family=='translated_x4' else 0),base[1]]
  assert list(map(F,loop['center']))==expected_center and F(loop['half_width'])==h/(2 if family=='half_radius' else 1) and loop['points_per_side']==8
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
 links={}
 for left,right in LINKS:
  key=left+right;metrics=[r['comparisons'][key]['metrics'] for r in rows]
  links[key]={'maximum_lower_gap_change_meV':max(abs(m['pair']['b_external_gaps_meV'][0]-m['pair']['a_external_gaps_meV'][0]) for m in metrics),'maximum_upper_gap_change_meV':max(abs(m['pair']['b_external_gaps_meV'][1]-m['pair']['a_external_gaps_meV'][1]) for m in metrics),'maximum_pair_angle_degrees':max(max(m['pair']['principal_angles_degrees']) for m in metrics),'maximum_four_angle_degrees':max(max(m['four']['principal_angles_degrees']) for m in metrics),'minimum_pair_weight_in_four':min(r['comparisons'][key]['minimum_pair_weight_in_four'] for r in rows)}
 return {'implementation_commit':commit,'independent_review':'PENDING','scope':cfg['scope'],'links':links,'loops':{lid:{k:{g:{field:r[field] for field in ['sign','valid','raw_determinant','min_step_singular_value','minimum_sampled_external_gap_meV']} for g,r in groups.items()} for k,groups in entry['cutoffs'].items()} for lid,entry in hol['loops'].items()}}

def replay(a):
 import numpy as np
 cfg=bound(a.commit);sc=load(ROOT/'research/benchmarks/state_comparison_001/run.py','sc');case=ladder(json.loads((ROOT/'docs/certification-readiness/CASE.json').read_text()));rows=[];vectors=[];spectra=[]
 batch=json.loads((a.output/'BATCH.json').read_text());assert batch['implementation_commit']==a.commit and batch['points']==NPOINTS and batch['jobs']==len(cfg['jobs']) and batch['eigensolver_starts']==len(KEYS)*NPOINTS and batch['summed_job_seconds']<=cfg['limits']['batch_timeout_seconds']
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
 assert [r['index'] for r in rows]==list(range(NPOINTS))
 reg=cfg['regression'];worst=0.0;count=0
 for k,ref in reg['upper_gap_microeV'].items():
  for i,v in ref.items():worst=max(worst,abs(upper_gap_microeV(rows[int(i)],k)-v)/1000);count+=1
 lower_worst=0.0
 for k,ref in reg['lower_gap_meV'].items():
  alias={'c':'a','d':'b'}[k]
  for i,v in ref.items():lower_worst=max(lower_worst,abs(rows[int(i)]['comparisons']['cd']['metrics']['pair'][alias+'_external_gaps_meV'][0]-v))
 assert lower_worst<=reg['threshold_meV'],lower_worst
 assert worst<=reg['threshold_meV'],worst
 write(a.output/'REGRESSION.json',{'sources':reg['sources'],'compared_point_cutoff_pairs':count,'max_abs_upper_gap_difference_meV':worst,'threshold_meV':reg['threshold_meV'],'maximum_lower_gap_error_meV':lower_worst,'status':'PASS'})
 hol=holonomy(cfg,vectors,spectra,case);write(a.output/'HOLONOMY.json',hol)
 write(a.output/'SUMMARY.json',summarize(cfg,rows,hol,a.commit))
 write(a.output/'MAP.json',{'implementation_commit':a.commit,'independent_review':'PENDING','kind':'three-cutoff closed lower-gap loops; not time evolution','samples':rows});print(f'REPLAY_PASS: {len(rows)} points, zero physical eigensolves')

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
 write(a.output,{'status':'PASS','physical_eigensolves':0,'checks':['exact closed CCW square loops','c/d/e shell constructions and inclusion','baseline/half-radius/translated exact geometry','nontrivial line -1,constant +1,singular invalid','O2 gauge/reflection/reversal invariant'],'points':NPOINTS,'loop_count':len(cfg['loops']),'regression_coordinates':len(cfg['regression']['upper_gap_microeV']['c'])})


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
 write(a.output/'BATCH.json',{'implementation_commit':a.commit,'points':NPOINTS,'jobs':len(done),'eigensolver_starts':sum(r['eigensolver_starts'] for r in receipts),'summed_job_seconds':sum(r['elapsed_seconds'] for r in receipts),'authorization':cfg['authorization'],'independent_review':'PENDING'});replay(a)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay','controls']);p.add_argument('--commit');p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);p.add_argument('--only',type=int,nargs=2,metavar=('START','STOP'))
 a=p.parse_args();globals()[a.mode](a)
