"""Fixed independent recalculations. No retry, resume, adaptation or production driver change."""
import argparse, hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
WORK=ROOT.parent
sys.path.insert(0,str(ROOT/'research/tools'))
from concurrent_supervisor import Job,Limits,run_jobs

def read(p):return json.loads(p.read_bytes())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m

def bound(commit):
 cfg=read(HERE/'SPEC.json')
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==commit
 for name,h in cfg['input_sha256'].items():assert digest(WORK/name)==h,name
 for name in ['SPEC.json','recompute.py','controls.json','README.md']:
  p=HERE/name;assert p.read_bytes()==subprocess.check_output(['git','show',commit+':'+str(p.relative_to(ROOT))],cwd=ROOT)
 return cfg

def assess(np,H,E,V,ref,rv,lo,hi,cfg,exact):
 residual=float(np.max(abs(H@V-V*E[lo-1:hi+2])))
 err=float(np.max(abs(E-ref)))
 gaps=lambda e:np.array([e[lo]-e[lo-1],e[hi+1]-e[hi],e[hi]-e[lo]])
 ge=float(np.max(abs(gaps(E)-gaps(ref))))
 assert residual<cfg['residual_tolerance_meV'] and err<cfg['energy_tolerance_meV'] and ge<cfg['gap_tolerance_meV']
 frame=0.
 if rv is not None:
  # Each band and central pair are checked without cancellation-prone projector subtraction.
  for cols in [[0],[1],[2],[3],[1,2],[0,1,2,3]]:
   a=V[:,cols];b=rv[:,cols];frame=max(frame,float(np.linalg.norm(a-b@(b.T@a))))
  assert frame<cfg['frame_tolerance']
 same=E.tobytes()==ref.tobytes() and (rv is None or V.tobytes()==rv.tobytes())
 if exact:assert same,'EXACT_REGRESSION_MISMATCH'
 return dict(energy_error_meV=err,gap_error_meV=ge,residual_meV=residual,frame_error=frame,byte_identical=same)

def worker(a,cfg):
 import numpy as np
 from scipy.linalg import eigh
 review=load(ROOT/'docs/audits/controls022-cutoff023/retained_review.py','retained_review')
 old=load(ROOT/'research/benchmarks/three_front_001/run.py','reference')
 np,base,assembly,case,provenance=old.setup(a.wheel)
 case['cutoffs']=review.shells()
 provenance.update(scope='independent reviewer physical recalculation',numpy=np.__version__,scipy=__import__('scipy').__version__,python=sys.version,threads={k:os.environ[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']})
 write(a.output/'RUNTIME.json',provenance)
 co={};cache={};rows=[];arrays={}
 with (a.output/'PROGRESS.ndjson').open('x') as log:
  for rid in cfg['jobs'][a.job]:
   rec=cfg['records'][rid];k=rec['cutoff'];p=WORK/rec['file']
   if k not in co:co[k]=old.float_coefficients(assembly,case,k)[0]
   if str(p) not in cache:
    cache[str(p)]=review.unpack(p) if p.suffix=='.pack' else dict(np.load(p,allow_pickle=False))
   d=cache[str(p)];ref=d[k+'_energies'][rec['row']];rv=d[k+'_vectors'][rec['row']] if rec['vectors'] else None
   H=old.point_matrix(base,assembly,co[k],*rec['center']);assert np.isfinite(H).all() and np.max(abs(H-H.T))<1e-10
   log.write(json.dumps(dict(record=rid,state='EIGENSOLVE_START'))+'\n');log.flush();os.fsync(log.fileno())
   E,V=eigh(H,driver='evr') if rec['mode']=='exact_evr' else np.linalg.eigh(H)
   lo,hi=case['cutoffs'][k]['selected_bands_zero_based'];V=np.ascontiguousarray(V[:,lo-1:hi+2])
   m=assess(np,H,E,V,ref,rv,lo,hi,cfg,rec['mode']=='exact_evr')
   rows.append(dict(record=rid,**rec,**m,matrix_sha256=hashlib.sha256(H.tobytes()).hexdigest()))
   arrays[f'r{rid}_energies']=E;arrays[f'r{rid}_vectors']=V
   log.write(json.dumps(dict(record=rid,state='PASS',**m))+'\n');log.flush();os.fsync(log.fileno())
 np.savez_compressed(a.output/'STATES.npz',**arrays);write(a.output/'RESULTS.json',rows)

def controls():
 import numpy as np
 cfg=read(HERE/'SPEC.json');assert len(cfg['records'])==200 and len(cfg['jobs'])==26
 assert sum(cfg['jobs'],[])==list(range(200))
 for p,h in cfg['input_sha256'].items():assert digest(WORK/p)==h
 H=np.diag(np.arange(6.));E=np.arange(6.);V=np.eye(6)[:,1:5]
 assess(np,H,E,V,E,V,2,3,cfg,True)
 bad=E.copy();bad[2]+=.01
 try:assess(np,H,E,V,bad,V,2,3,cfg,False)
 except AssertionError:pass
 else:raise AssertionError('BAD_ENERGIES_ACCEPTED')
 write(HERE/'controls.json',dict(status='PASS',physical_eigensolves=0,records=200,jobs=26,input_bindings=len(cfg['input_sha256']),checks=['ownership','input hashes','synthetic exact and residual','bad energies rejected']))

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['controls','run','worker']);p.add_argument('--commit');p.add_argument('--wheel',type=Path);p.add_argument('--output',type=Path);p.add_argument('--job',type=int);a=p.parse_args()
 if a.mode=='controls':controls();return
 assert a.commit and a.wheel and a.output
 cfg=bound(a.commit)
 if a.mode=='worker':worker(a,cfg);return
 jobs=[Job(f'job{j:03}',(sys.executable,'-B',str(HERE/'recompute.py'),'worker','--commit',a.commit,'--wheel',str(a.wheel),'--output','{output}','--job',str(j)),tuple(ids)) for j,ids in enumerate(cfg['jobs'])]
 run_jobs(jobs,a.output,cwd=ROOT,source_commit=a.commit,limits=Limits(workers=cfg['workers'],job_seconds=cfg['job_seconds'],batch_seconds=cfg['batch_seconds']))
 rows=sum([read(a.output/f'job{j:03}'/'RESULTS.json') for j in range(len(jobs))],[])
 assert [r['record'] for r in rows]==list(range(200))
 summary=dict(status='PASS',source_commit=a.commit,physical_eigensolves=len(rows),groups={})
 for tag in ['022','023','023-regression','024']:
  rr=[r for r in rows if r['tag']==tag];summary['groups'][tag]=dict(solves=len(rr),byte_identical=sum(r['byte_identical'] for r in rr),**{k:max(r[k] for r in rr) for k in ['energy_error_meV','gap_error_meV','residual_meV','frame_error']})
 write(a.output/'SUMMARY.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
