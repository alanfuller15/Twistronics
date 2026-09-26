"""Independent numpy-eigh recomputation; reviewed coefficient assembly is reused explicitly."""
import argparse,hashlib,importlib.util,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TARGETS={'013':('loop_cutoff_d_013','7635c8586e13865487b396ea21ec7d274c13976e','76dadaf9478bbb8e99ee26ada6b5ff046fc1628a','loop_cutoff_d_013_execution'),'014':('loop_lower_014','0453e09a4b2721f3dd51166a9bda064d4693d125','e1fa393b33984862cce885d320c77324fedffa98','loop_lower_014_execution'),'015':('cutoff_e_015','8cba7ef0f07d099c57d03b3efdba8aae49bb0512','4445bddae841373db5b049fe423b7d3f09c5e883','cutoff_e_015_execution')}
def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def schedule():return [(r,i) for r,(name,_,_,_) in TARGETS.items() for i in range(len(read(ROOT/f'research/benchmarks/{name}/SPEC.json')['points']))]
def binding():
 checked={}
 for run,(name,impl,exe,_) in TARGETS.items():
  spec=read(ROOT/f'research/benchmarks/{name}/SPEC.json')
  paths=[f'research/benchmarks/{name}/run.py',f'research/benchmarks/{name}/SPEC.json',*spec['dependencies']]
  for path in paths:
   data=(ROOT/path).read_bytes()
   assert data==subprocess.check_output(['git','show',impl+':'+path],cwd=ROOT)
   assert data==subprocess.check_output(['git','show',exe+':'+path],cwd=ROOT)
   if path in spec['dependencies']:assert hashlib.sha256(data).hexdigest()==spec['dependencies'][path]
  manifest=f'research/benchmarks/{name}_execution/MANIFEST.json'
  assert (ROOT/manifest).read_bytes()==subprocess.check_output(['git','show',exe+':'+manifest],cwd=ROOT)
  checked[run]={'implementation_commit':impl,'execution_commit':exe,'checked_source_files':len(paths),'execution_manifest_sha256':hashlib.sha256((ROOT/manifest).read_bytes()).hexdigest()}
 return checked

def worker(a):
 resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,)*2)
 assert all(os.environ[k]=='1' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'])
 import numpy as np
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','assembly')
 np,base,assembly,case,prov=old.setup(a.wheel)
 for k,name in [('c','cutoff_ladder_003'),('d','cutoff_shell_012')]:case['cutoffs'][k]=read(ROOT/f'research/benchmarks/{name}/SPEC.json')['additional_cutoff']
 case['cutoffs']['e']=read(ROOT/'research/benchmarks/cutoff_e_015/SPEC.json')['additional_cutoff_e']
 for left,right,n in [('b','c',111),('c','d',151),('d','e',197)]:
  indices=sorted({(x+dx,y+dy) for x,y in case['cutoffs'][left]['ordered_indices'] for dx,dy in case['cutoffs']['b']['stencil']})
  assert case['cutoffs'][right]['ordered_indices']==[list(v) for v in indices] and len(indices)==n
  assert case['cutoffs'][right]['selected_bands_zero_based']==[2*n-1,2*n]
 co={k:old.float_coefficients(assembly,case,k)[0] for k in ['d','e']};rows=[];saved={}
 for run,index in schedule()[6*a.job:6*(a.job+1)]:
  name,_,_,directory=TARGETS[run];spec=read(ROOT/f'research/benchmarks/{name}/SPEC.json');point=spec['points'][index];k='e' if run=='015' else 'd'
  j=next(j for j,idx in enumerate(spec['jobs']) if index in idx);loc=spec['jobs'][j].index(index)
  with np.load(a.input/directory/f'job{j:03}'/'STATES.npz') as z:refE=z[k+'_energies'][loc];refV=z[k+'_vectors'][loc]
  H=old.point_matrix(base,assembly,co[k],*point);E,V=np.linalg.eigh(H);lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];V=V[:,lo-1:hi+2]
  err=float(max(abs(E-refE)));res=float(np.max(abs(H@V-V*E[lo-1:hi+2])));assert err<1e-9 and res<1e-8
  ext=[float(E[lo]-E[lo-1]),float(E[hi+1]-E[hi])];refext=[refE[lo]-refE[lo-1],refE[hi+1]-refE[hi]]
  rows.append({'run':run,'index':index,'center':point,'cutoff':k,'full_spectrum_max_error_meV':err,'external_gap_max_error_meV':float(max(abs(np.array(ext)-refext))),'max_eigenpair_residual_meV':res,'lower_gap_meV':ext[0],'upper_gap_meV':ext[1],'four_projector_error':float(np.linalg.norm(V@V.T-refV@refV.T))})
  saved[f'{run}_{index}_{k}_E']=E;saved[f'{run}_{index}_{k}_V']=V
 write(a.output/'POINTS.json',rows);prov.update(python=sys.version,numpy=np.__version__,scope='Independent NumPy eigh at every largest-cutoff point; shared reviewed coefficient assembly; own loop and fit formulas');write(a.output/'RUNTIME.json',prov);np.savez_compressed(a.output/'STATES.npz',**saved)

def run(a):
 assert subprocess.check_output(['git','show',a.commit+':docs/audits/loops-013-015/recompute.py'],cwd=ROOT)==Path(__file__).read_bytes()
 a.output.mkdir(parents=True,exist_ok=False);write(a.output/'SOURCE_BINDING.json',binding());sched=schedule();assert len(sched)==601
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1');started=time.monotonic()
 for j in range((len(sched)+5)//6):
  d=a.output/f'job{j:03}';d.mkdir();t=time.monotonic()
  with (d/'WORKER.log').open('wb') as f:
   proc=subprocess.Popen([sys.executable,'-B',__file__,'worker','--commit',a.commit,'--job',str(j),'--input',str(a.input),'--output',str(d),'--wheel',str(a.wheel)],stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True)
   try:code=proc.wait(timeout=90);term='NORMAL_EXIT'
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);code=proc.wait();term='TIMEOUT'
  try:os.killpg(proc.pid,0);empty=False
  except ProcessLookupError:empty=True
  write(d/'RECEIPT.json',{'exit_code':code,'termination':term,'process_group_empty':empty,'elapsed_seconds':time.monotonic()-t,'points':sched[j*6:(j+1)*6],'eigensolves':len(sched[j*6:(j+1)*6]),'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir()}})
  assert code==0 and empty and term=='NORMAL_EXIT';assert time.monotonic()-started<1800
  print(f'Independent review job {j+1}/101 complete',flush=True)
 write(a.output/'BATCH.json',{'points':601,'eigensolves':601,'jobs':101,'wall_seconds':time.monotonic()-started,'method':'numpy.linalg.eigh; shared reviewed coefficient assembly; independent comparison formulas'})
 collect(a)

def collect(a):
 import numpy as np
 from fractions import Fraction as F
 rows=sum([read(p) for p in sorted(a.output.glob('job*/POINTS.json'))],[]);assert len(rows)==601
 arrays={}
 for p in a.output.glob('job*/STATES.npz'):
  with np.load(p) as z:arrays.update({k:z[k] for k in z.files})
 def product(vs):
  dets=[];mins=[]
  for i,v in enumerate(vs):
   ov=v.T@vs[(i+1)%len(vs)];dets.append(float(np.linalg.det(ov)));mins.append(float(min(np.linalg.svd(ov,compute_uv=False))))
  return {'sign':int(np.prod(np.sign(dets))),'determinant':float(np.prod(dets)),'minimum_link_singular_value':min(mins)}
 reports={};rng=np.random.default_rng(131415)
 for run,(name,impl,exe,directory) in TARGETS.items():
  cfg=read(ROOT/f'research/benchmarks/{name}/SPEC.json');ref=read(a.input/directory/'HOLONOMY.json');k='e' if run=='015' else 'd';rr=[r for r in rows if r['run']==run];loops={}
  groups={'hi':[2],'hi_plus_1':[3],'selected_pair':[1,2],'four':[0,1,2,3]}
  if run=='014':groups.update(lo_minus_1=[0],lo=[1])
  for loop in cfg['loops']:
   idx=loop['point_indices'];pts=[list(map(F,cfg['points'][i])) for i in idx]
   assert sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))>0
   loops[loop['id']]={}
   for group,cols in groups.items():
    vs=[arrays[f'{run}_{i}_{k}_V'][:,cols] for i in idx];h=product(vs);gauged=[v@np.linalg.qr(rng.normal(size=(len(cols),len(cols))))[0] for v in vs]
    assert product(gauged)['sign']==product(vs[::-1])['sign']==h['sign']
    refh=ref['loops'][loop['id']]['cutoffs'][k][group];assert h['sign']==refh['sign']
    h['determinant_error']=abs(h['determinant']-refh['raw_determinant']);h['conditioning_error']=abs(h['minimum_link_singular_value']-refh['min_step_singular_value']);assert h['determinant_error']<1e-6 and h['conditioning_error']<1e-6
    loops[loop['id']][group]=h
  report={'reviewed_execution':exe,'frozen_implementation':impl,'independent_cutoff':k,'points':len(rr),'max_spectrum_error_meV':max(r['full_spectrum_max_error_meV'] for r in rr),'max_gap_error_meV':max(r['external_gap_max_error_meV'] for r in rr),'max_residual_meV':max(r['max_eigenpair_residual_meV'] for r in rr),'loops':loops,'gauge_reversal':'PASS','scope':'Complete source/packet replay plus independent largest-cutoff spectra and loop products at all points; no continuous-path or count certification'}
  if run=='015':
   z=np.array([r['upper_gap_meV']*1000 for r in rr[:9]]);xy=np.array([(x,y) for y in [-1,0,1] for x in [-1,0,1]],float);x,y=xy.T;D=np.column_stack([x*x,y*y,x*y,x,y,np.ones(9)]);co=np.linalg.lstsq(D,z*z,rcond=None)[0];Q=np.array([[co[0],co[2]/2],[co[2]/2,co[1]]]);o=np.linalg.solve(Q,-co[3:5]/2);report['independent_e_patch_fit']={'center_gap_microeV':float(z[4]),'offset_steps':o.tolist(),'raw_fitted_minimum_gap_squared_microeV2':float(co[5]+co[3:5]@o+o@Q@o),'positive_definite':bool(min(np.linalg.eigvalsh(Q))>0),'inside_patch':bool(max(abs(o))<=1),'scope':'descriptive float least-squares; a rounded zero is not proof of touching'}
  reports[run]=report
 write(a.output/'REVIEW.json',reports);print(json.dumps({r:{k:v for k,v in report.items() if k not in ['loops']} for r,report in reports.items()},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','collect']);p.add_argument('--commit');p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);a=p.parse_args();globals()[a.mode](a)
