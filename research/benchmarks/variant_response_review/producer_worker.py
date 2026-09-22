"""Instrument an unchanged producer: log values, states, model bases and failures."""
from pathlib import Path
import collections,gzip,hashlib,inspect,json,os,runpy,sys,time,weakref
import numpy as np
import scipy.linalg
work=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();mode=sys.argv[3]
os.chdir(work);sys.path.insert(0,str(work));start=time.perf_counter();counts=collections.Counter();models=[];ids=weakref.WeakKeyDictionary();state={}
stream=gzip.open(out/f'{mode.upper()}_EVALUATIONS.jsonl.gz','wt',encoding='utf8')
def clean(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,Path):return str(x)
    raise TypeError(type(x).__name__)
def log(kind,**kw):
    counts[kind]+=1;stream.write(json.dumps({'kind':kind,'sequence':sum(counts.values()),**kw},default=clean,allow_nan=False)+'\n')
original_eigh=scipy.linalg.eigh

def recorded_eigh(*args,**kw):
    caller=inspect.currentframe().f_back;context={'file':Path(caller.f_code.co_filename).name,'function':caller.f_code.co_name}
    try:r=original_eigh(*args,**kw)
    except Exception as ex:log('eigh_failed',state=state.copy(),context=context,error_type=type(ex).__name__,error=str(ex));raise
    vals=r if kw.get('eigvals_only',False) else r[0]
    log('eigh',state=state.copy(),context=context,subset=kw.get('subset_by_index'),eigenvalues_meV=vals)
    return r
scipy.linalg.eigh=recorded_eigh
from bm_strain import BM
init0=BM.__init__;sig=inspect.signature(init0)
def init(self,*args,**kw):
    bound=sig.bind(self,*args,**kw);bound.apply_defaults();params={k:v for k,v in bound.arguments.items() if k!='self'}
    init0(self,*args,**kw);model_id=len(models);ids[self]=model_id
    idx=[list(t) for t in self.idx];record={'model_id':model_id,'parameters':params,'dimension':self.dim,'ordered_indices':idx,'indices_json_sha256':hashlib.sha256(json.dumps(idx,separators=(',',':')).encode()).hexdigest()};models.append(record);log('model_created',model_id=model_id,dimension=self.dim)
BM.__init__=init
H0=BM.H

def H(self,k):
    state.clear();state.update(model_id=ids[self],matrix='native_complex',k_cartesian=np.asarray(k).tolist())
    r=H0(self,k);log('native_H',**state);return r
BM.H=H
refine0=BM.refine
def refine(self,*args,**kw):
    try:r=refine0(self,*args,**kw)
    except Exception as ex:log('refine_failed',model_id=ids[self],error_type=type(ex).__name__,error=str(ex));raise
    log('refine_return',model_id=ids[self],seed=np.asarray(args[0]),coordinate=np.asarray(r[0]),returned_gap_meV=float(r[1]));return r
BM.refine=refine
from fast_engine import RealEngine
HR0=RealEngine.HR_k;bands0=RealEngine.bands

def HR(self,k):
    state.clear();state.update(model_id=ids[self.m],matrix='fast_real',k_cartesian=np.asarray(k).tolist())
    r=HR0(self,k);log('fast_HR',**state);return r
RealEngine.HR_k=HR

def bands(self,f,nb=3):
    r=bands0(self,f,nb);log('fast_bands',model_id=ids[self.m],f=np.asarray(f),nb=nb,eigenvalues_meV=r);return r
RealEngine.bands=bands
old_eigvalsh=np.linalg.eigvalsh
def eigvalsh(*args,**kw):
    r=old_eigvalsh(*args,**kw);log('numpy_eigvalsh',state=state.copy(),eigenvalues_meV=r);return r
np.linalg.eigvalsh=eigvalsh
sys.argv=['producers.py',mode]
status='FAILED'
try:runpy.run_path(str(work/'producers.py'),run_name='__main__');status='COMPLETED'
finally:
    stream.close()
    (out/f'{mode.upper()}_MODELS.json').write_text(json.dumps(models,indent=2,default=clean)+'\n')
    (out/f'{mode.upper()}_RUN.json').write_text(json.dumps({'status':status,'elapsed_s':time.perf_counter()-start,'counts':dict(counts),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in work.glob('*.py')},'scope':'Original source files unchanged. Wrappers log inputs and returned values without changing numerical return values. Timings include instrumentation.'},indent=2)+'\n')
