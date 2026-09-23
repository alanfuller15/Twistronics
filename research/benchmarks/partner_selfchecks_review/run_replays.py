"""Fresh bounded producer runs. Preserve inputs and retain nonzero exits/timeouts."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from review_inputs import ROOT, extract

plan = json.loads((ROOT/'PLAN.json').read_text())
replay = ROOT/'replay'
if replay.exists(): raise RuntimeError('refusing to overwrite an earlier replay')
replay.mkdir()
env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
executions = []
for job in plan['full_replays']:
    work = extract(replay/Path(job['script']).stem)
    for name in ('METAMORPHIC.json', 'BASIS_DEPENDENCE.json'): (work/name).unlink()
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in work.glob('*.py')}
    log = ROOT/(Path(job['script']).stem.upper()+'_REPLAY.log')
    t = time.perf_counter(); timed_out = False
    command = [sys.executable, str(ROOT/'producer_worker.py'), str(work), str(ROOT), job['script']]
    with log.open('w') as f:
        try: code = subprocess.run(command, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=job['budget_seconds']).returncode
        except subprocess.TimeoutExpired: code = None; timed_out = True
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in work.glob('*.py')}
    rec = dict(script=job['script'], argv=command, returncode=code, timed_out=timed_out, elapsed_s=time.perf_counter()-t,
               source_files_unchanged=before == after, result_present=(work/job['output']).exists())
    if rec['result_present']: shutil.copy2(work/job['output'], ROOT/('REPLAY_'+job['output']))
    executions.append(rec); (ROOT/'EXECUTIONS.json').write_text(json.dumps(executions, indent=2)+'\n')
    print(json.dumps(rec), flush=True)
