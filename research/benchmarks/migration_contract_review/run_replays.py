"""Bounded clean-source replay and supplied control suite in isolated processes."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import numpy
import scipy
from review_inputs import ROOT,extract,pack

ENV=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
ENV.pop('FORCE_MR1_FAILURE',None)

def execute(name,command,work,limit):
    t=time.perf_counter()
    try:
        p=subprocess.run(command,cwd=work,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=limit)
        code,log,timed_out=p.returncode,p.stdout,False
    except subprocess.TimeoutExpired as e:code,log,timed_out=None,e.stdout or b'',True
    (ROOT/(name+'.log')).write_bytes(log)
    record=dict(name=name,command=command,returncode=code,timed_out=timed_out,limit_seconds=limit,wall_seconds=time.perf_counter()-t)
    (ROOT/(name+'_EXECUTION.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(name,code,round(record['wall_seconds'],3),flush=True)
    return record

def positive():
    with tempfile.TemporaryDirectory(prefix='v078-positive-') as tmp:
        work=extract(tmp,True)
        r=execute('POSITIVE',[sys.executable,'migrated_valley_control.py','REPLAY'],work,180)
        v=execute('POSITIVE_VERIFY',[sys.executable,'verify_migration.py','REPLAY'],work,30)
        files=[(p,p.relative_to(work).as_posix()) for p in (work/'REPLAY').glob('*') if p.is_file()]
        if (work/'VERIFY_REPLAY.json').exists(): files.append((work/'VERIFY_REPLAY.json','VERIFY_REPLAY.json'))
        pack(ROOT/'POSITIVE_EVIDENCE.zip',files)
        return r['returncode']==0 and v['returncode']==0 and not r['timed_out']

def controls():
    with tempfile.TemporaryDirectory(prefix='v078-controls-') as tmp:
        work=extract(tmp,True)
        for n in ['FAILURE_CONTROLS.json','METAMORPHIC.json']:(work/n).unlink()
        r=execute('SUPPLIED_CONTROLS',[sys.executable,'failure_controls.py'],work,300)
        files=[(p,p.relative_to(work).as_posix()) for d in work.glob('CONTROL_*') if d.is_dir() for p in d.rglob('*') if p.is_file()]
        for n in ['FAILURE_CONTROLS.json','METAMORPHIC.json']:
            if (work/n).exists(): files.append((work/n,n))
        pack(ROOT/'SUPPLIED_CONTROLS_EVIDENCE.zip',files)
        records=json.loads((work/'FAILURE_CONTROLS.json').read_text())['controls'] if (work/'FAILURE_CONTROLS.json').exists() else []
        expected=[('all_measurements_rejected',1),('no_pair_found',1),('discovery_fails_after_first_B',1),('forced_MR1_violation',1),('metamorphic_clean',0)]
        return r['returncode']==0 and [(x['control'],x['exit_code']) for x in records]==expected and records[3]['mr1_holds'] is False

def tests():
    with tempfile.TemporaryDirectory(prefix='v078-tests-') as tmp:
        work=extract(tmp,True)
        r=execute('TESTS',[sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_guards.py','test_claim_lint.py'],work,60)
        l=execute('LINT',[sys.executable,'claim_lint.py','.'],work,30)
        return r['returncode']==0 and l['returncode']==1

if __name__=='__main__':
    meta=dict(python=sys.version,platform=platform.platform(),numpy=numpy.__version__,scipy=scipy.__version__,threads={k:ENV[k] for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']},plan_sha256=hashlib.sha256((ROOT/'PLAN.json').read_bytes()).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (ROOT/'RUNTIME.json').write_text(json.dumps(meta,indent=2)+'\n')
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(fn) for fn in [positive,controls,tests]]
        results=[f.result() for f in futures]
    (ROOT/'REPLAY_STATUS.json').write_text(json.dumps(dict(positive=results[0],supplied_controls=results[1],tests_and_lint_expected=results[2]),indent=2)+'\n')
    if not all(results): raise SystemExit(1)
