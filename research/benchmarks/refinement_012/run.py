"""Depth12 refinement of the reviewed111 unresolved parents, in actual20-cell jobs."""
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
def initial():
 cfg=spec();assert sha(HERE/'PREDECESSOR.json')==cfg['predecessor_sha256'];p=json.loads((HERE/'PREDECESSOR.json').read_text())
 accepted=sorted(tuple(c) for c in p['accepted']);parents=sorted(tuple(c) for c in p['unresolved'])
 assert len(accepted)==3040 and len(parents)==111 and not p['frontier'] and all(d==11 for d,x,y in parents)
 children=[(12,2*x+i,2*y+j) for d,x,y in parents for i in range(2) for j in range(2)]
 return accepted,parents,children
def jobs():
 children=initial()[2];return [children[i:i+20] for i in range(0,len(children),20)]
def partition_check(cells):
 import numpy as np
 raster=np.zeros((4096,4096),dtype=np.uint8)
 for d,x,y in cells:
  assert 1<=d<=12 and 0<=x<2**d and 0<=y<2**d
  scale=2**(12-d);view=raster[x*scale:(x+1)*scale,y*scale:(y+1)*scale];assert not view.any(),'overlap';view[:]=1
 assert raster.all(),'gap'
def strict():
 old=ROOT/'research/benchmarks/certification_s1b_quadrant_a_002';sys.path.insert(0,str(old))
 verifier=load(old/'verify.py','r12_verify');strictmod=load(ROOT/'research/benchmarks/parallel_domain_006/parallel.py','r12_strict');return verifier,strictmod

def worker(a):
 cfg=spec();bindings(a.commit);resource.setrlimit(resource.RLIMIT_AS,(cfg['memory_bytes'],)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(cfg['file_bytes'],)*2)
 o=load(ROOT/'research/benchmarks/three_front_001/run.py','r12_old');np,base,assembly,case,provenance=o.setup(a.wheel)
 method=load(ROOT/'research/benchmarks/certification_s1b_method_004/check.py','r12_method');cutoff=case['cutoffs']['a'];coef,_=assembly.assemble_coefficients(cutoff['ordered_indices'],case);verifier,s=strict();owned=jobs()[a.job];factors=0
 write(a.output/'RUNTIME.json',provenance)
 with (a.output/'CELLS.ndjson').open('x') as f:
  for cell in owned:
   e=method.probe_cell(base,assembly,coef,cutoff,{'precision_bits':128,'recomputation_decimal_digits':10},list(cell))
   p,r=s.strict_evidence(e,e['status'],{'algorithm':{'precision_bits':128,'recomputation_decimal_digits':10}},cell,verifier);assert p+r<=8;factors+=p+r
   f.write(json.dumps({'cell':cell,'evidence':e},sort_keys=True,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
 write(a.output/'RESULTS.json',{'implementation_commit':a.commit,'job':a.job,'cells':owned,'factorizations':factors,'completed_cells':len(owned),'independent_review':'PENDING'})
def stop(proc):
 if proc.poll() is None:
  os.killpg(proc.pid,signal.SIGTERM)
  try:proc.wait(timeout=10)
  except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
def run(a):
 cfg=spec();bindings(a.commit,True)
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
    if len(finished)%4==0:print(json.dumps({'completed_jobs':len(finished),'total_jobs':len(jobs()),'cells_completed':sum(len(jobs()[j]) for j in finished)}),flush=True)
   if failure:break
   time.sleep(.05)
 finally:
  for job,(proc,start,directory,log) in active.items():
   stop(proc);log.close()
   try:os.killpg(proc.pid,0);empty=False
   except ProcessLookupError:empty=True
   write(directory/'RECEIPT.json',{'implementation_commit':a.commit,'job':job,'indices':jobs()[job],'elapsed_seconds':time.monotonic()-start,'exit_code':proc.returncode,'termination':'BATCH_STOP','process_group_empty':empty,'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in directory.iterdir() if p.is_file()}})
 write(a.output/'BATCH_RECEIPT.json',{'implementation_commit':a.commit,'jobs_completed':len(finished),'elapsed_seconds':time.monotonic()-started,'failure':failure,'maximum_concurrent_workers':4,'cells_per_job_maximum':20})
 if failure:raise RuntimeError(failure)
 assert len(finished)==len(jobs())
 print(json.dumps({'status':'ALL_JOBS_COMPLETE','cells':444}),flush=True)

def replay(a):
 bindings(a.commit,True);cfg=spec();accepted,parents,children=initial();new=[];unresolved=[];factorizations=0;verifier,s=strict()
 batch=json.loads((a.output/'BATCH_RECEIPT.json').read_text());assert batch['failure'] is None and batch['jobs_completed']==len(jobs()) and batch['elapsed_seconds']<=cfg['batch_seconds']
 for j,owned in enumerate(jobs()):
  d=a.output/f'job{j:03}';r=json.loads((d/'RECEIPT.json').read_text());result=json.loads((d/'RESULTS.json').read_text())
  assert r['implementation_commit']==result['implementation_commit']==a.commit and r['job']==result['job']==j
  assert r['termination']=='NORMAL_EXIT' and r['exit_code']==0 and r['process_group_empty'] and r['elapsed_seconds']<=cfg['job_seconds']
  assert r['indices']==result['cells']==[list(c) for c in owned] and result['completed_cells']==len(owned)
  assert {p.name for p in d.iterdir()}==set(r['files'])|{'RECEIPT.json'}
  for name,entry in r['files'].items():assert sha(d/name)==entry['sha256'] and (d/name).stat().st_size==entry['bytes']
  runtime=json.loads((d/'RUNTIME.json').read_text());assert runtime['loaded_extension_bound_to_wheel'] and runtime['mapped_native_libraries_bound_to_wheel'] and runtime['wheel']['sha256']=='376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76'
  rows=[json.loads(line) for line in (d/'CELLS.ndjson').read_text().splitlines()];assert [tuple(row['cell']) for row in rows]==owned;factors=0
  for row in rows:
   e=row['evidence'];cell=tuple(row['cell']);p,r=s.strict_evidence(e,e['status'],{'algorithm':{'precision_bits':128,'recomputation_decimal_digits':10}},cell,verifier);assert p+r<=8;factors+=p+r
   (new if e['status']=='CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS' else unresolved).append(cell)
  assert factors==result['factorizations'];factorizations+=factors
 assert factorizations<=cfg['factorizations_batch_maximum'];partition_check(accepted+new+unresolved)
 area=sum((Fraction(1,4**d) for d,x,y in accepted+new),Fraction());oldarea=sum((Fraction(1,4**d) for d,x,y in accepted),Fraction());assert area-oldarea==len(new)*Fraction(1,4**12)
 final={'accepted':sorted(accepted+new),'frontier':[],'unresolved':sorted(unresolved)};newset=set(new);outcomes=[sum((12,2*x+i,2*y+j) in newset for i in range(2) for j in range(2)) for d,x,y in parents]
 summary={'implementation_commit':a.commit,'status':'INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE' if unresolved else 'FULL_FINITE_CUTOFF_LOCAL_ISOLATION_PENDING_REVIEW','accepted_area':str(area),'accepted_percent':float(area*100),'accepted_cells':len(accepted+new),'inherited_accepted_cells':len(accepted),'newly_accepted_children':len(new),'unresolved_depth12':len(unresolved),'parent_outcomes':{str(i):outcomes.count(i) for i in range(5)},'fully_resolved_parents':outcomes.count(4),'attempts':len(children),'factorizations':factorizations,'independent_review':'PENDING','claim_ceiling':cfg['claim_ceiling']}
 write(a.output/'PARTITION.json',final);write(a.output/'SUMMARY.json',summary);print(json.dumps(summary),flush=True)
def controls():
 accepted,parents,children=initial();js=jobs();assert len(js)==23 and max(map(len,js))==20 and len(js[-1])==4 and len(set(children))==444
 assert sum(js,[])==children
 owners={c:j for j,job in enumerate(js) for c in job}
 for d,x,y in parents:assert len({owners[(12,2*x+i,2*y+j)] for i in range(2) for j in range(2)})==1
 partition_check(accepted+children)
 rejected=[]
 for name,cells in [('duplicate',accepted+children+[children[0]]),('missing',accepted+children[:-1])]:
  try:partition_check(cells)
  except AssertionError:rejected.append(name)
 assert rejected==['duplicate','missing'];print(json.dumps({'status':'PASS','physical_calls':0,'jobs':23,'max_cells_per_job':20,'parents':111,'children':444,'inherited_accepted':3040,'checks':['exact tiling','complete distinct ownership','siblings stay in one job','duplicate and missing cell controls rejected']}))
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['run','worker','replay','controls']);p.add_argument('--job',type=int);p.add_argument('--commit');p.add_argument('--wheel',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();return {'run':run,'worker':worker,'replay':replay,'controls':lambda a:controls()}[a.mode](a)
if __name__=='__main__':main()
