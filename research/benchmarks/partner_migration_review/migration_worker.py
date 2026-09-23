"""Passive in-memory recording around the unchanged partner entry point.

All wrapped methods call their original implementation exactly once. No
numerical substitutions, extra solves or altered thresholds in this replay.
Full matrices/eigenvectors and every internal optimizer evaluation are not saved.
"""
import dataclasses
import gzip
import hashlib
import inspect
import json
import runpy
import sys
from pathlib import Path
import numpy as np

WORK = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(WORK))
import guarded_topology as gt
import bm_strain as bs
import knobs

def plain(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, dict): return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)): return [plain(v) for v in x]
    if x is None or isinstance(x, (str, bool, int, float)): return x
    if callable(x): return '<callable>'
    raise TypeError(type(x))

models, refinements, searches, calls = [], [], [], []
model_ids = {}
def write(name, data):
    (OUT/name).write_text(json.dumps(plain(data), indent=2, allow_nan=False)+'\n')

init0 = bs.BM.__init__
def init(self, *args, **kwargs):
    bound = inspect.signature(init0).bind(self, *args, **kwargs)
    bound.apply_defaults()
    constructor = {k: plain(v) for k,v in bound.arguments.items() if k != 'self'}
    init0(self, *args, **kwargs)
    mid = len(models)
    model_ids[id(self)] = mid
    indices = [list(t) for t in self.idx]
    models.append(dict(id=mid, constructor=constructor, ordered_index_set=indices,
                       index_sha256=hashlib.sha256(json.dumps(indices).encode()).hexdigest(),
                       dimension=self.dim, nG=self.nG, HBARV=bs.HBARV,
                       G1=self.G1.tolist(), G2=self.G2.tolist(), harmonics=[]))
bs.BM.__init__ = init

harmonic0 = knobs.add_harmonic
def harmonic(m, *args, **kwargs):
    bound = inspect.signature(harmonic0).bind(m, *args, **kwargs)
    bound.apply_defaults()
    record = {}
    for k,v in bound.arguments.items():
        if k == 'm': continue
        if k == 'mat':
            record[k] = dict(real=np.asarray(v).real.tolist(), imag=np.asarray(v).imag.tolist())
        else: record[k] = plain(v)
    result = harmonic0(m, *args, **kwargs)
    models[model_ids[id(m)]]['harmonics'].append(record)
    return result
knobs.add_harmonic = harmonic

refine0 = bs.BM.refine
def refine(self, *args, **kwargs):
    row = dict(model_id=model_ids[id(self)], seed=plain(args[0]), kwargs=plain(kwargs))
    try:
        result = refine0(self, *args, **kwargs)
        row.update(status='RETURNED', result=plain(result))
        return result
    except Exception as e:
        row.update(status='EXCEPTION', exception=repr(e))
        raise
    finally:
        row['last_refine'] = plain(getattr(self, 'last_refine', None))
        refinements.append(row)
bs.BM.refine = refine

find0 = bs.BM.find_nodes
def find(self, *args, **kwargs):
    row = dict(model_id=model_ids[id(self)], args=plain(args), kwargs=plain(kwargs))
    try:
        result = find0(self, *args, **kwargs)
        row.update(status='RETURNED', result=plain(result))
        return result
    except Exception as e:
        row.update(status='EXCEPTION', exception=repr(e))
        raise
    finally: searches.append(row)
bs.BM.find_nodes = find

pair0 = gt.pair_charges
with gzip.open(OUT/'MIGRATION_LEDGER.jsonl.gz', 'wt') as ledger:
    def pair(S, g, *args, **kwargs):
        call_id = len(calls)
        row = dict(call_id=call_id, model_id=model_ids[id(S.m)], geometry=plain(g),
                   policy=dataclasses.asdict(S.p), args=plain(args), kwargs=plain(kwargs))
        start = len(S.records)
        try:
            result = pair0(S, g, *args, **kwargs)
            row.update(status='RETURNED', result=plain(result))
            return result
        except Exception as e:
            row.update(status='EXCEPTION', exception=repr(e), rejection=getattr(e,'record',None))
            raise
        finally:
            rows = S.records[start:]
            row['ledger_rows'] = len(rows)
            for record in rows:
                ledger.write(json.dumps(dict(call_id=call_id, **plain(record)), allow_nan=False)+'\n')
            ledger.flush()
            calls.append(row)
    gt.pair_charges = pair
    try:
        sys.argv = ['migrated_valley_control.py']
        runpy.run_path(str(WORK/'migrated_valley_control.py'), run_name='__main__')
    finally:
        write('MIGRATION_MODELS.json', models)
        write('MIGRATION_GEOMETRY.json', calls)
        write('MIGRATION_DISCOVERY.json', dict(searches=searches, refinements=refinements))
        write('LOADED_SOURCES.json', {name:dict(path=str(Path(mod.__file__).relative_to(WORK)),
              sha256=hashlib.sha256(Path(mod.__file__).read_bytes()).hexdigest())
              for name,mod in sorted(sys.modules.items()) if getattr(mod,'__file__',None)
              and Path(mod.__file__).resolve().is_relative_to(WORK)})
