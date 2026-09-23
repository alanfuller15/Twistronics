"""Instrument an unchanged partner producer, retaining every native eigensolve."""
from pathlib import Path
import collections
import gzip
import hashlib
import inspect
import json
import os
import platform
import runpy
import sys
import time
import weakref
import numpy as np
import scipy
import scipy.linalg
from threadpoolctl import threadpool_info

work, out, script = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), sys.argv[3]
name = Path(script).stem.upper(); os.chdir(work); sys.path.insert(0, str(work))
start = time.perf_counter(); counts = collections.Counter(); models = []; ids = weakref.WeakKeyDictionary(); state = {}; active = []
stream = gzip.open(out/f'{name}_EVALUATIONS.jsonl.gz', 'wt', encoding='utf8')
def clean(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, Path): return str(x)
    raise TypeError(type(x).__name__)
def log(kind, **kw):
    counts[kind] += 1
    stream.write(json.dumps(dict(kind=kind, sequence=sum(counts.values()), measurement=active[-1] if active else None, **kw), default=clean, allow_nan=False)+'\n')
eigh0 = scipy.linalg.eigh
def eigh(*args, **kw):
    caller = inspect.currentframe().f_back
    context = dict(file=Path(caller.f_code.co_filename).name, function=caller.f_code.co_name)
    try: r = eigh0(*args, **kw)
    except Exception as ex:
        log('eigh_failed', state=state.copy(), context=context, error_type=type(ex).__name__, error=str(ex)); raise
    vals = r if kw.get('eigvals_only', False) else r[0]
    log('eigh', state=state.copy(), context=context, subset=kw.get('subset_by_index'), eigenvalues_meV=vals)
    return r
scipy.linalg.eigh = eigh
import bm_strain as bs
from bm_strain import BM
init0 = BM.__init__; sig = inspect.signature(init0)
def init(self, *args, **kw):
    bound = sig.bind(self, *args, **kw); bound.apply_defaults()
    params = {k: v for k, v in bound.arguments.items() if k != 'self'}
    init0(self, *args, **kw); mid = len(models); ids[self] = mid; idx = [list(t) for t in self.idx]
    models.append(dict(model_id=mid, parameters=params, hbar_v_meV_A=bs.HBARV, dimension=self.dim, ordered_indices=idx,
                       indices_json_sha256=hashlib.sha256(json.dumps(idx, separators=(',', ':')).encode()).hexdigest()))
    log('model_created', model_id=mid, dimension=self.dim)
BM.__init__ = init
H0 = BM.H
def H(self, k):
    state.clear(); state.update(model_id=ids[self], matrix='native_complex', k_cartesian=np.asarray(k).tolist(), hbar_v_meV_A=bs.HBARV)
    r = H0(self, k); log('native_H', **state); return r
BM.H = H
refine0 = BM.refine
def refine(self, *args, **kw):
    try: r = refine0(self, *args, **kw)
    except Exception as ex:
        log('refine_failed', model_id=ids[self], seed=np.asarray(args[0]), error_type=type(ex).__name__, error=str(ex)); raise
    log('refine_return', model_id=ids[self], seed=np.asarray(args[0]), coordinate=np.asarray(r[0]), returned_gap_meV=float(r[1]), optimizer=self.last_refine)
    return r
BM.refine = refine
measurement_count = 0
def record_measurement(method_name):
    original = getattr(BM, method_name)
    def wrapped(self, *args, **kw):
        global measurement_count
        measurement_count += 1; mid = measurement_count; active.append(mid)
        log('measurement_start', model_id=ids[self], method=method_name, args=args, kwargs=kw)
        try:
            r = original(self, *args, **kw)
            log('measurement_return', model_id=ids[self], method=method_name, value=r)
            return r
        except Exception as ex:
            log('measurement_failed', model_id=ids[self], method=method_name, error_type=type(ex).__name__, error=str(ex)); raise
        finally: active.pop()
    setattr(BM, method_name, wrapped)
record_measurement('flat_bandwidth'); record_measurement('min_remote')
from fast_engine import RealEngine
hr0 = RealEngine.HR_k
def HR(self, k):
    state.clear(); state.update(model_id=ids[self.m], matrix='fast_real', k_cartesian=np.asarray(k).tolist(), hbar_v_meV_A=bs.HBARV)
    r = hr0(self, k); log('fast_HR', **state); return r
RealEngine.HR_k = HR
status = 'FAILED'; error = None
try:
    sys.argv = [script]; runpy.run_path(str(work/script), run_name='__main__'); status = 'COMPLETED'
except BaseException as ex:
    error = dict(type=type(ex).__name__, message=str(ex)); raise
finally:
    stream.close()
    (out/f'{name}_MODELS.json').write_text(json.dumps(models, indent=2, default=clean)+'\n')
    (out/f'{name}_RUN.json').write_text(json.dumps(dict(status=status, error=error, elapsed_s=time.perf_counter()-start, counts=dict(counts),
         sources={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in work.glob('*.py')},
         instrumentation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, threadpools=threadpool_info()),
         scope='Unchanged producer files; wrappers retain values without modifying numerical returns. Times include instrumentation.'), indent=2)+'\n')
