"""Bound resumable candidate sweeps; one writer, explicit retries and recovery."""
from pathlib import Path
from contextlib import contextmanager
import fcntl
import itertools
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import jm_model as model

def plan_checked(raw):
    allowed = {'config', 'axes', 'grid', 'keep', 'local_grid', 'tracked', 'max_attempts'}
    if set(raw)-allowed or set(raw.get('axes', {})) != set(model.KNOBS):
        raise ValueError('invalid sweep plan')
    plan = dict(config=model.config(raw.get('config')), axes=raw['axes'], grid=raw.get('grid',24),
                keep=raw.get('keep',10), local_grid=raw.get('local_grid',0),
                tracked=raw.get('tracked',{}), max_attempts=raw.get('max_attempts',3))
    for key in ('grid','keep','local_grid','max_attempts'):
        value = plan[key]
        if isinstance(value, bool) or int(value) != value or value < (0 if key=='local_grid' else 1):
            raise ValueError('invalid '+key)
    if plan['grid'] < 2:
        raise ValueError('grid must be at least two')
    axes = {}
    for k in model.KNOBS:
        a = [float(v) for v in plan['axes'][k]]
        if not a or len(a) != len(set(a)):
            raise ValueError('empty or duplicate axis '+k)
        axes[k] = a
    plan['axes'] = axes
    # Validate all input states before touching the output ledger.
    for x in states(plan): model.state(x)
    model.canonical(plan)
    return plan

def states(plan):
    for values in itertools.product(*(plan['axes'][k] for k in model.KNOBS)):
        yield model.state(dict(zip(model.KNOBS,values)))

def binding(plan):
    payload = dict(schema=1, plan=plan, model=model.MODEL, source_hashes=model.sources())
    return dict(payload, run_id=model.digest(payload))

@contextmanager
def writer_lock(path):
    with open(str(path)+'.lock', 'a+b') as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as e: raise RuntimeError('another sweep writer holds this ledger') from e
        try: yield
        finally: fcntl.flock(lock, fcntl.LOCK_UN)

def durable_write(path, content, mode='xb'):
    with open(path, mode) as f:
        f.write(content); f.flush(); os.fsync(f.fileno())

def recover(path, meta):
    """Only a syntactically incomplete final line can be quarantined/truncated.

    Any complete but invalid record or malformed interior line stops the run.
    The exact damaged suffix is fsynced to a content-addressed sibling first.
    """
    path = Path(path)
    data = path.read_bytes() if path.exists() else b''
    lines = data.splitlines(keepends=True); rows = []; position = 0; previous = None
    known = {model.digest(dict(run_id=meta['run_id'], x=x)):x for x in states(meta['plan'])}
    recovery = None
    for i, line in enumerate(lines):
        try: row = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            if i != len(lines)-1 or line.endswith(b'\n'):
                raise ValueError('malformed interior/terminated JSONL record')
            suffix = data[position:]
            import hashlib
            quarantine = Path(str(path)+'.tail.'+hashlib.sha256(suffix).hexdigest()+'.bin')
            if quarantine.exists():
                if quarantine.read_bytes() != suffix: raise ValueError('quarantine collision')
            else: durable_write(quarantine, suffix)
            with open(path,'r+b') as f:
                f.truncate(position); f.flush(); os.fsync(f.fileno())
            recovery = dict(quarantined=str(quarantine), bytes=len(suffix))
            break
        if not isinstance(row,dict): raise ValueError('invalid ledger record')
        h = row.get('record_hash'); payload = {k:v for k,v in row.items() if k!='record_hash'}
        if (h != model.digest(payload) or row.get('seq') != len(rows) or row.get('previous') != previous
            or row.get('run_id') != meta['run_id'] or row.get('key') not in known
            or row.get('x') != known[row['key']] or row.get('status') not in ('ok','error')):
            raise ValueError('ledger schema, binding or hash-chain mismatch')
        expected_attempt = 1+sum(r['key']==row['key'] for r in rows)
        if row.get('attempt') != expected_attempt: raise ValueError('invalid attempt sequence')
        rows.append(row); previous=h; position += len(line)
    # A complete last JSON record without newline is valid, but needs a delimiter.
    if recovery is None and data and not data.endswith(b'\n'):
        durable_write(path,b'\n','ab')
        recovery = dict(added_final_newline=True)
    return rows, recovery

def work(item):
    x, plan = item; start = time.perf_counter()
    try:
        result = model.survey(x, plan['config'], plan['grid'], plan['keep'], plan['tracked'], plan['local_grid'])
        status = 'ok'
    except Exception as e:
        result = dict(error=repr(e), cost_complete=False); status='error'
    return dict(status=status, result=result, seconds=time.perf_counter()-start)

def limit_threads():
    from threadpoolctl import threadpool_limits
    threadpool_limits(1)

def run(raw_plan, out_path, workers=1, worker=None):
    plan = plan_checked(raw_plan); meta = binding(plan); path=Path(out_path)
    if isinstance(workers,bool) or int(workers)!=workers or workers<1:
        raise ValueError('workers must be a positive integer')
    if workers>1 and worker is not None: raise ValueError('injected workers are serial controls only')
    start=time.perf_counter(); manifest=Path(str(path)+'.manifest.json')
    with writer_lock(path):
        if manifest.exists():
            if json.loads(manifest.read_text()) != meta:
                raise ValueError('resume rejected: plan, model or source binding differs')
        else:
            if path.exists() and path.stat().st_size: raise ValueError('nonempty ledger has no binding manifest')
            durable_write(manifest,(json.dumps(meta,indent=2)+'\n').encode())
        rows,recovery=recover(path,meta)
        done={r['key'] for r in rows if r['status']=='ok'}
        attempts={}
        for r in rows: attempts[r['key']]=attempts.get(r['key'],0)+1
        todo=[]
        for x in states(plan):
            key=model.digest(dict(run_id=meta['run_id'],x=x))
            if key not in done and attempts.get(key,0)<plan['max_attempts']: todo.append((key,x))
        worker=worker or work
        def append(key,x,result):
            if result.get('status') not in ('ok','error'): raise ValueError('invalid worker status')
            row=dict(result,seq=len(rows),previous=rows[-1]['record_hash'] if rows else None,
                     run_id=meta['run_id'],key=key,x=x,attempt=attempts.get(key,0)+1)
            row['record_hash']=model.digest(row)
            durable_write(path,(model.canonical(row)+'\n').encode(),'ab'); rows.append(row)
        if workers==1:
            limit_threads()
            for key,x in todo: append(key,x,worker((x,plan)))
        else:
            with ProcessPoolExecutor(max_workers=workers,initializer=limit_threads) as pool:
                for (key,x),result in zip(todo,pool.map(work,[(x,plan) for _,x in todo])): append(key,x,result)
    return dict(run_id=meta['run_id'],attempted=len(todo),retained_rows=len(rows),recovery=recovery,
                successes=sum(r['status']=='ok' for r in rows),seconds=time.perf_counter()-start)

if __name__=='__main__':
    print(json.dumps(run(json.loads(Path(sys.argv[1]).read_text()),sys.argv[2],int(sys.argv[3]) if len(sys.argv)>3 else 1),indent=2))
