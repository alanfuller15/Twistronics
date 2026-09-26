"""Grid64 follow-up: 20-point jobs; source-bound, finite-box comparison."""
import argparse,hashlib,importlib.util,json,os,resource,signal,subprocess,sys,time
from pathlib import Path
from fractions import Fraction
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def spec():return json.loads((HERE/'SPEC.json').read_text())
def bindings(commit,git=False):
 m=json.loads((HERE/'SOURCE_BINDINGS.json').read_text())
 for p,h in m.items():assert sha(ROOT/p)==h,p
 if git:
  for p in [*m,str((HERE/'SOURCE_BINDINGS.json').relative_to(ROOT))]:
   assert subprocess.check_output(['git','show',commit+':'+p],cwd=ROOT)==(ROOT/p).read_bytes(),p
 return sha(HERE/'SOURCE_BINDINGS.json')
def old():return load(ROOT/'research/benchmarks/three_front_001/run.py','dyn2_old')
def jobs():return [list(range(i,min(4096,i+20))) for i in range(0,4096,20)]
def worker(a):
 cfg=spec();bindings(a.commit);resource.setrlimit(resource.RLIMIT_AS,(cfg['memory_bytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(cfg['file_bytes'],)*2)
 import numpy as np
 from scipy.linalg import eigh
 o=old();np,base,assembly,case,provenance=o.setup(a.wheel);coef,_=o.float_coefficients(assembly,case,'a');indices=jobs()[a.job];ev=[];vec=[];worst=0.
 for index in indices:
  i,j=divmod(index,64);h=o.point_matrix(base,assembly,coef,Fraction(2*i+1,128),Fraction(2*j+1,128))
  e,v=eigh(h,subset_by_index=(97,98),driver='evr');r=float(np.max(abs(h@v-v*e)));assert r<1e-8;worst=max(worst,r);ev.append(e);vec.append(v)
 np.savez_compressed(a.output/'MODES.npz',indices=indices,energies_meV=np.array(ev),vectors=np.array(vec))
 write(a.output/'RESULTS.json',{'implementation_commit':a.commit,'job':a.job,'indices':indices,'eigensolver_starts':len(indices),'max_eigenpair_residual_meV':worst,'modes_sha256':sha(a.output/'MODES.npz'),'runtime':provenance,'independent_review':'PENDING'})
def stop(proc):
 if proc.poll() is None:
  os.killpg(proc.pid,signal.SIGTERM)
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
def run(a):
 cfg=spec();bindings(a.commit,True);assert sha(a.coarse/'MODES.npz')==cfg['coarse_modes_sha256'];assert sha(a.coarse/'RESULTS.json')==cfg['coarse_results_sha256']
 a.output.mkdir(parents=True,exist_ok=False);env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1')
 pending=list(range(len(jobs())));active={};finished=[];started=time.monotonic();failure=None
 try:
  while pending or active:
   while pending and len(active)<4 and failure is None:
    job=pending.pop(0);directory=a.output/f'job{job:03}';directory.mkdir();log=(directory/'WORKER.log').open('wb')
    cmd=[sys.executable,'-B',str(HERE/'run.py'),'worker','--job',str(job),'--output',str(directory),'--wheel',str(a.wheel),'--commit',a.commit]
    proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True);active[job]=(proc,time.monotonic(),directory,log)
   now=time.monotonic()
   if now-started>cfg['batch_seconds']:failure='BATCH_TIMEOUT'
   for job,(proc,start,directory,log) in list(active.items()):
    timed=now-start>cfg['job_seconds']
    if timed or failure:stop(proc)
    code=proc.poll()
    if code is None:continue
    log.close()
    try:os.killpg(proc.pid,0);empty=False
    except ProcessLookupError:empty=True
    files={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in directory.iterdir() if p.is_file()}
    receipt={'implementation_commit':a.commit,'job':job,'indices':jobs()[job],'elapsed_seconds':time.monotonic()-start,'exit_code':code,'termination':'WATCHDOG_TIMEOUT' if timed else 'BATCH_STOP' if failure else 'NORMAL_EXIT','process_group_empty':empty,'files':files}
    write(directory/'RECEIPT.json',receipt);del active[job];finished.append(job)
    if code or not empty or timed:failure='WORKER_FAILURE'
    if len(finished)%20==0:print(json.dumps({'completed_jobs':len(finished),'total_jobs':len(jobs()),'points_completed':sum(len(jobs()[j]) for j in finished)}),flush=True)
   if failure:break
   time.sleep(.05)
 finally:
  for job,(proc,start,directory,log) in active.items():
   stop(proc);log.close()
   try:os.killpg(proc.pid,0);empty=False
   except ProcessLookupError:empty=True
   write(directory/'RECEIPT.json',{'implementation_commit':a.commit,'job':job,'indices':jobs()[job],'elapsed_seconds':time.monotonic()-start,'exit_code':proc.returncode,'termination':'BATCH_STOP','process_group_empty':empty,'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in directory.iterdir() if p.is_file()}})
 write(a.output/'BATCH_RECEIPT.json',{'implementation_commit':a.commit,'jobs_completed':len(finished),'elapsed_seconds':time.monotonic()-started,'failure':failure,'maximum_concurrent_workers':4,'points_per_job_maximum':20})
 if failure:raise RuntimeError(failure)
 assert len(finished)==205
 print(json.dumps({'status':'ALL_205_JOBS_COMPLETE','points':4096}),flush=True)
def restore_modes(output,commit):
 import numpy as np
 ev=np.zeros((64,64,2));vec=np.zeros((64,64,196,2));seen=set();worst=0.
 for j,indices in enumerate(jobs()):
  d=output/f'job{j:03}';r=json.loads((d/'RECEIPT.json').read_text());v=json.loads((d/'RESULTS.json').read_text())
  assert r['implementation_commit']==v['implementation_commit']==commit and r['termination']=='NORMAL_EXIT' and r['exit_code']==0 and r['process_group_empty']
  assert r['job']==v['job']==j and r['indices']==v['indices']==indices and v['eigensolver_starts']==len(indices)
  assert r['elapsed_seconds']<=spec()['job_seconds'] and sha(d/'MODES.npz')==v['modes_sha256']
  for name,entry in r['files'].items():assert sha(d/name)==entry['sha256'] and (d/name).stat().st_size==entry['bytes']
  m=np.load(d/'MODES.npz');assert list(m['indices'])==indices
  worst=max(worst,v['max_eigenpair_residual_meV'])
  for k,index in enumerate(indices):
   assert index not in seen;seen.add(index);i,l=divmod(index,64);ev[i,l]=m['energies_meV'][k];vec[i,l]=m['vectors'][k]
 assert seen==set(range(4096));return ev,vec,worst

def render(a):
 import numpy as np
 cfg=spec();bindings(a.commit,True);resource.setrlimit(resource.RLIMIT_AS,(cfg['memory_bytes'],)*2);signal.alarm(cfg['render_seconds'])
 assert sha(a.coarse/'MODES.npz')==cfg['coarse_modes_sha256'];assert sha(a.coarse/'RESULTS.json')==cfg['coarse_results_sha256']
 coarse=np.load(a.coarse/'MODES.npz');meta=json.loads((a.coarse/'RESULTS.json').read_text());e,v,worst=restore_modes(a.output,a.commit)
 dest=a.output/'render';dest.mkdir(exist_ok=False);times=cfg['times_fs'];summary={};seed=meta['seed_real_basis_index'];area=meta['pixel_area_nm_squared']
 for width in cfg['widths']:
  tag='sigma'+str(width).replace('.','p');density={};edge={};mass={};norm={}
  for n,E,V in [(32,coarse['energies_meV'],coarse['vectors']),(64,e,v)]:
   if n==32:weights=coarse[tag+'_weights']
   else:
    x=(np.arange(n)+.5)/n;xx,yy=np.meshgrid(x,x,indexing='ij');cx,cy=map(lambda s:float(Fraction(s)),cfg['center'])
    envelope=np.exp(-((xx-cx)**2+(yy-cy)**2)/(4*width*width));weights=V[:,:,seed,:]*envelope[:,:,None];weights/=np.linalg.norm(weights)
   m=4*n;start=(m-n)//2;frames=[];edges=[];norms=[];masses=[]
   for t in times:
    amp=np.einsum('ijdb,ijb->ijd',V,weights*np.exp(-1j*E*t/cfg['hbar_meV_fs']));pad=np.zeros((m,m,196),complex);pad[start:start+n,start:start+n]=amp
    psi=np.fft.fftshift(np.fft.ifft2(np.fft.ifftshift(pad,axes=(0,1)),axes=(0,1)),axes=(0,1))*m
    prob=np.sum(abs(psi)**2,axis=2);total=float(prob.sum());assert abs(total-1)<1e-10
    edges.append(float(total-prob[8:-8,8:-8].sum()));norms.append(abs(total-1));mid=m//2;crop=prob[mid-32:mid+32,mid-32:mid+32]/area
    frames.append(crop.astype('<f4'));masses.append(float(crop.sum()*area));del amp,pad,psi,prob
   density[n]=np.stack(frames);edge[n]=edges;mass[n]=masses;norm[n]=norms
   density[n].tofile(dest/f'{tag}-grid{n}.bin')
  l1=np.sum(abs(density[32].astype(float)-density[64].astype(float)),axis=(1,2))*area
  passes=max(l1)<=cfg['density_L1_tolerance'] and max(edge[32])<=cfg['edge_mass_tolerance'] and max(edge[64])<=cfg['edge_mass_tolerance']
  summary[tag]={'max_density_L1':float(max(l1)),'density_L1_per_frame':l1.tolist(),'edge_mass_by_grid':edge,'window_probability_by_grid':mass,'max_norm_error':max(max(x) for x in norm.values()),'numerical_gate_passes':bool(passes),'site_promotion':'PENDING_INDEPENDENT_REVIEW' if passes else 'BLOCKED_NUMERICAL_GATE'}
 write(dest/'RESULTS.json',{'implementation_commit':a.commit,'max_eigenpair_residual_meV':worst,'grids':[32,64],'times_fs':times,'density_L1_tolerance':cfg['density_L1_tolerance'],'edge_mass_tolerance':cfg['edge_mass_tolerance'],'packets':summary,'independent_review':'PENDING','scope':cfg['claim_ceiling'],'display_grid':64,'pixel_area_nm_squared':area,'direct_basis_columns_nm':meta['direct_basis_columns_nm'],'step_moire':.25})
 write(dest/'MANIFEST.json',{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in dest.iterdir() if p.is_file()})
 print(json.dumps({tag:{'L1':s['max_density_L1'],'coarse_edge':max(s['edge_mass_by_grid'][32]),'fine_edge':max(s['edge_mass_by_grid'][64]),'passes':s['numerical_gate_passes']} for tag,s in summary.items()}))
def controls():
 js=jobs();assert len(js)==205 and max(map(len,js))==20 and len(js[-1])==16 and sum(js,[])==list(range(4096))
 assert set(sum(js,[]))==set(range(4096));cfg=spec();assert max(cfg['times_fs'])==125 and all(x<=125 for x in cfg['times_fs'])
 print(json.dumps({'status':'PASS','physical_calls':0,'jobs':205,'job_size_maximum':20,'last_job_size':16,'points':4096,'checks':['complete distinct row-major jobs','fixed prefix and grid','no repeated jobs']}))
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','render','controls']);p.add_argument('--job',type=int);p.add_argument('--commit');p.add_argument('--wheel',type=Path);p.add_argument('--output',type=Path);p.add_argument('--coarse',type=Path);a=p.parse_args()
 return {'run':run,'worker':worker,'render':render,'controls':lambda a:controls()}[a.mode](a)
if __name__=='__main__':main()
