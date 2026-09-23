"""Run the frozen, bounded review in separate fresh source directories."""
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import numpy
import scipy
from review_inputs import ROOT, extract

env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
           PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1')
executions = []

def run(name, args, limit, generated=(), mode=None):
    with tempfile.TemporaryDirectory(prefix='v077-review-') as tmp:
        work = extract(Path(tmp)/'partner')
        for file in generated:
            (work/file).unlink(missing_ok=True)
        command = [str(x).replace('{work}', str(work)) for x in args]
        start = time.perf_counter()
        timeout = False
        try:
            p = subprocess.run(command, cwd=work, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=limit)
            code, output = p.returncode, p.stdout
        except subprocess.TimeoutExpired as ex:
            code, output, timeout = None, ex.stdout or b'', True
        elapsed = time.perf_counter()-start
        (ROOT/(name+'.log')).write_bytes(output)
        produced = {}
        for file in generated:
            source = work/file
            if source.exists():
                target = ROOT/(name+'_'+file)
                shutil.copyfile(source, target)
                produced[file] = dict(file=target.name, bytes=target.stat().st_size,
                                     sha256=hashlib.sha256(target.read_bytes()).hexdigest())
        row = dict(name=name, command=[str(x) for x in args], timeout_seconds=limit,
                   timed_out=timeout, returncode=code, wall_seconds=elapsed,
                   generated=produced, mode=mode)
        executions.append(row)
        (ROOT/'EXECUTIONS.json').write_text(json.dumps(executions,indent=2)+'\n')
        print(name, 'returncode', code, 'seconds',round(elapsed,3), 'files',list(produced),flush=True)

if __name__ == '__main__':
    metadata = dict(python=sys.version, platform=platform.platform(), numpy=numpy.__version__, scipy=scipy.__version__,
                    threads={k:env[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')},
                    plan_sha256=hashlib.sha256((ROOT/'PLAN.json').read_bytes()).hexdigest(),
                    review_sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')})
    (ROOT/'METADATA.json').write_text(json.dumps(metadata,indent=2)+'\n')
    run('REPLAY',[sys.executable, ROOT/'migration_worker.py','{work}',ROOT],180,['MIGRATION_RESULTS.json'],'passive instrumentation')
    run('CLEAN',[sys.executable,'migrated_valley_control.py'],180,['MIGRATION_RESULTS.json'],'unchanged source, no instrumentation')
    run('TESTS',[sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_guards.py'],60)
    run('NEGATIVE',[sys.executable,'record_controls.py'],60,['NEGATIVE_CONTROLS.json'])
    run('METAMORPHIC',[sys.executable,'metamorphic.py'],120,['METAMORPHIC.json'],'unchanged source')
    run('LINT',[sys.executable,'claim_lint.py','.'],60)
    for mode in ('rejected','no_pair','late_discovery_error','metamorphic'):
        file = 'METAMORPHIC.json' if mode=='metamorphic' else 'MIGRATION_RESULTS.json'
        run('CONTROL_'+mode.upper(),[sys.executable,ROOT/'failure_worker.py','{work}',mode],60,[file],'synthetic injected failure')
