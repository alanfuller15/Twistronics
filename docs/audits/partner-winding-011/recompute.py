"""Independent numpy-eigh recomputation; reviewed coefficient assembly is reused explicitly."""
import argparse,hashlib,importlib.util,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TARGETS={'011':('partner_winding_011','71847eac2f9f3100dd6b928001a3b26a051848a4','be6f259d63445e7650db2bb688ba4e4c073a89d0','partner011')}
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
 import numpy as np
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','audit_assembly')
 np,base,assembly,case,prov=old.setup(a.wheel);prov['scope']='Independent Codex recomputation; shared reviewed assembly, numpy.linalg.eigh instead of producer scipy evr'
 case['cutoffs']['c']=read(ROOT/'research/benchmarks/cutoff_ladder_003/SPEC.json')['additional_cutoff']
 b=case['cutoffs']['b'];expected=sorted({(x+dx,y+dy) for x,y in b['ordered_indices'] for dx,dy in b['stencil']})
 assert case['cutoffs']['c']['ordered_indices']==[list(g) for g in expected]
 co={k:old.float_coefficients(assembly,case,k)[0] for k in 'abc'}
 def injection(left,right):
  A=case['cutoffs'][left]['ordered_indices'];B=case['cutoffs'][right]['ordered_indices'];pos={tuple(g):j for j,g in enumerate(B)}
  return np.array([2*layer*len(B)+2*pos[tuple(g)]+part for layer in (0,1) for g in A for part in (0,1)])
 inj={link:injection(*link) for link in ['ab','bc']};rows=[];saved={}
 for run,index in schedule()[6*a.job:6*(a.job+1)]:
  name,_,_,directory=TARGETS[run];spec=read(ROOT/f'research/benchmarks/{name}/SPEC.json');p=spec['points'][index]
  refrow=read(a.input/directory/'MAP.json')['samples'][index]
  j=next(j for j,owned in enumerate(spec['jobs']) if index in owned);loc=spec['jobs'][j].index(index)
  with np.load(a.input/directory/f'job{j:03}'/'STATES.npz') as d:
   refE={k:d[k+'_energies'][loc] for k in 'abc'};refV={k:d[k+'_vectors'][loc] for k in 'abc'}
  H={k:old.point_matrix(base,assembly,co[k],*p) for k in 'abc'};E={};V={};bands={};eerr=0.;rmax=0.;verr={};gaps={};gerr=0.
  for k in 'abc':
   assert np.max(abs(H[k]-H[k].T))<1e-12
   E[k],allv=np.linalg.eigh(H[k]);lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];bands[k]=(lo,hi);V[k]=allv[:,lo-1:hi+2]
   eerr=max(eerr,float(np.max(abs(E[k]-refE[k]))));rmax=max(rmax,float(np.max(abs(H[k]@V[k]-V[k]*E[k][lo-1:hi+2]))))
   gaps[k]={'pair':[float(E[k][lo]-E[k][lo-1]),float(E[k][hi+1]-E[k][hi])], 'four':[float(E[k][lo-1]-E[k][lo-2]),float(E[k][hi+2]-E[k][hi+1])]}
   verr[k]=float(np.linalg.norm(V[k]@V[k].T-refV[k]@refV[k].T,ord='fro'))
   if run=='011':saved[f'{index}_{k}_V']=V[k];saved[f'{index}_{k}_E']=E[k]
  out={'run':run,'index':index,'center':p,'upper_gap_microeV':{k:1000*gaps[k]['pair'][1] for k in 'abc'},'full_spectrum_max_error_meV':eerr,'max_eigenpair_residual_meV':rmax,'four_projector_difference_frobenius':verr,'comparisons':{}}
  for link,ii in inj.items():
   left,right=link;nest=float(np.max(abs(H[right][np.ix_(ii,ii)]-H[left])));assert nest<1e-12
   comp={}
   for group,cols in [('pair',[1,2]),('four',[0,1,2,3])]:
    A=np.zeros((len(V[right]),len(cols)));A[ii]=V[left][:,cols];B=V[right][:,cols];O=A.T@B
    sins=np.linalg.svd(B-A@O,compute_uv=False);angles=np.sort(np.rad2deg(np.arcsin(np.clip(sins,0,1))))
    singular=np.linalg.svd(O,compute_uv=False);ref=refrow['comparisons'][link]['metrics'][group]
    ge=max(abs(np.array(gaps[left][group])-ref['a_external_gaps_meV']).max(),abs(np.array(gaps[right][group])-ref['b_external_gaps_meV']).max());gerr=max(gerr,float(ge))
    comp[group]={'angles_degrees':angles.tolist(),'max_angle_difference_degrees':float(max(abs(angles-ref['principal_angles_degrees']))),'singular_values':singular.tolist(),'max_singular_value_difference':float(max(abs(singular-ref['singular_values']))),'external_gaps_meV':{left:gaps[left][group],right:gaps[right][group]}}
   ov=V[left][:,1:3].T@V[right][ii,:];contain=float(np.linalg.eigvalsh(ov@ov.T)[0]);comp['containment']=contain;comp['containment_error']=abs(contain-refrow['comparisons'][link]['minimum_pair_weight_in_four']);comp['nested_residual_meV']=nest;out['comparisons'][link]=comp
  out['max_external_gap_error_meV']=gerr
  assert eerr<5e-9 and gerr<5e-9 and rmax<1e-8
  rows.append(out)
 write(a.output/'POINTS.json',rows);prov.update(python=sys.version,numpy=np.__version__);write(a.output/'RUNTIME.json',prov)
 if saved:np.savez_compressed(a.output/'NODE_STATES.npz',**saved)

def run(a):
 a.output.mkdir(parents=True,exist_ok=False);write(a.output/'SOURCE_BINDING.json',binding());sched=schedule();assert len(sched)==35
 env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1');started=time.monotonic()
 for j in range((len(sched)+5)//6):
  d=a.output/f'job{j:03}';d.mkdir();t=time.monotonic()
  with (d/'WORKER.log').open('wb') as f:
   proc=subprocess.Popen([sys.executable,'-B',__file__,'worker','--job',str(j),'--input',str(a.input),'--output',str(d),'--wheel',str(a.wheel)],stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True)
   try:code=proc.wait(timeout=90);term='NORMAL_EXIT'
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);code=proc.wait();term='TIMEOUT'
  try:os.killpg(proc.pid,0);empty=False
  except ProcessLookupError:empty=True
  write(d/'RECEIPT.json',{'exit_code':code,'termination':term,'process_group_empty':empty,'elapsed_seconds':time.monotonic()-t,'points':sched[j*6:(j+1)*6],'eigensolves':3*len(sched[j*6:(j+1)*6]),'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.iterdir()}})
  assert code==0 and empty and term=='NORMAL_EXIT';assert time.monotonic()-started<600
  print(f'Independent review job {j+1}/6 complete',flush=True)
 write(a.output/'BATCH.json',{'points':35,'eigensolves':105,'jobs':6,'wall_seconds':time.monotonic()-started,'method':'numpy.linalg.eigh; shared reviewed coefficient assembly; independent comparison formulas'})
 collect(a)

def collect(a):
 import numpy as np
 from fractions import Fraction as F
 rows=sum([read(d/'POINTS.json') for d in sorted(a.output.glob('job*'))],[]);assert len(rows)==35
 spec=read(ROOT/'research/benchmarks/partner_winding_011/SPEC.json');fit=read(a.input/'locate010/SUMMARY.json');cent=[F(11785,32768),F(605,32768)]
 for i,k in enumerate('bc'):
  reported=fit['cutoffs'][k]['cone_fit']['node_fractional_k_float'];expected=[str(F(round(x*2**30),2**30)) for x in reported];assert expected==spec['points'][i]
  off=spec['nodes'][k]['offset_units_of_2^-30_from_x11785/32768_y605/32768'];assert [str(cent[j]+F(off[j],2**30)) for j in range(2)]==expected
 c=list(map(F,spec['points'][1]));r=F(1,65536);corners=[(-r,-r),(r,-r),(r,r),(-r,r)];loop=[]
 for j,(x,y) in enumerate(corners):
  X,Y=corners[(j+1)%4];loop += [[str(c[0]+x+(X-x)*i/8),str(c[1]+y+(Y-y)*i/8)] for i in range(8)]
 assert loop==[spec['points'][i] for i in spec['loop']['point_indices']]
 data={}
 for p in a.output.glob('job*/NODE_STATES.npz'):
  with np.load(p) as z:data.update({k:z[k] for k in z.files})
 def transport(vs):
  ds=[];mins=[]
  for i,v in enumerate(vs):
   ov=v.T@vs[(i+1)%len(vs)];ds.append(float(np.linalg.det(ov)));mins.append(float(min(np.linalg.svd(ov,compute_uv=False))))
  return {'sign':int(np.prod(np.sign(ds))),'determinant':float(np.prod(ds)),'minimum_step_singular_value':min(mins)}
 hol={};rng=np.random.default_rng(11011)
 for k in 'abc':
  hol[k]={}
  for g,cols in {'hi':[2],'hi_plus_1':[3],'selected_pair':[1,2],'four':[0,1,2,3]}.items():
   vs=[data[f'{i}_{k}_V'][:,cols] for i in spec['loop']['point_indices']];h=transport(vs);gauge=[v@(np.linalg.qr(rng.normal(size=(len(cols),len(cols))))[0]*rng.choice([-1,1],size=len(cols))) for v in vs]
   assert transport(gauge)['sign']==transport(vs[::-1])['sign']==h['sign'];ref=read(a.input/'partner011/HOLONOMY.json')['cutoffs'][k][g];assert h['sign']==ref['sign'];h['determinant_difference']=abs(h['determinant']-ref['determinant']);hol[k][g]=h
 report={'reviewed_commit':TARGETS['011'][2],'implementation_commit':TARGETS['011'][1],'points':35,'eigensolves':105,'maximum_full_spectrum_error_meV':max(x['full_spectrum_max_error_meV'] for x in rows),'maximum_external_gap_error_meV':max(x['max_external_gap_error_meV'] for x in rows),'maximum_eigenpair_residual_meV':max(x['max_eigenpair_residual_meV'] for x in rows),'maximum_angle_difference_degrees':max(x['comparisons'][l][g]['max_angle_difference_degrees'] for x in rows for l in ['ab','bc'] for g in ['pair','four']),'maximum_containment_error':max(x['comparisons'][l]['containment_error'] for x in rows for l in ['ab','bc']),'gaps_at_candidate_points_microeV':{str(x['index']):x['upper_gap_microeV'] for x in rows[:2]},'independent_holonomy':hol,'rounding_square_closure_gauge_reversal':'PASS','verdict':'Numerical PASS; interpretation changes requested: no certified node-count or partner correspondence; computed candidate gaps are numerical finite-cutoff gaps, whose nonzero size can be consistent with coordinate/fit error.'}
 write(a.output/'REVIEW.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','collect']);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--wheel',type=Path);p.add_argument('--job',type=int);a=p.parse_args();globals()[a.mode](a)
