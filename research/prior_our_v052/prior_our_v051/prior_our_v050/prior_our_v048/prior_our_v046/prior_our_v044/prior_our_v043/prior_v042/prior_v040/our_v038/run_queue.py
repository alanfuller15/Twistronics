"""Run a finite reviewed job list sequentially; record every exit code.

Subprocesses invoke only local allowlisted scripts via Python, no shell.
Each job has its own log and JSON checkpoint. No network or deletion.
"""
import json,sys,os,subprocess,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ALLOWED={'replay_second.py','replay_events.py','replay_events_refined.py','check_gapped.py','boundary_audit.py'}
if __name__=='__main__':
    queue=Path(sys.argv[1]);jobs=json.loads(queue.read_text());records=[]
    for job in jobs:
        script=job['script']
        if script not in ALLOWED:raise ValueError('Unreviewed script '+script)
        log=ROOT/'results'/(job['name']+'.log');t=time.time()
        with log.open('w') as stream:
            r=subprocess.run([sys.executable,'-B',str(ROOT/script),*job['args']],env={**os.environ,'OPENBLAS_NUM_THREADS':'1'},stdout=stream,stderr=subprocess.STDOUT)
        records.append(dict(**job,exit_code=r.returncode,seconds=time.time()-t,script_sha256=hashlib.sha256((ROOT/script).read_bytes()).hexdigest()))
        (ROOT/'results'/(queue.stem+'_status.json')).write_text(json.dumps(records,indent=2)+'\n')
        print(job['name'],r.returncode,round(time.time()-t,1),flush=True)
