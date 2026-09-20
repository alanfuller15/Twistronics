"""Small sequential event batch, one BLAS thread, checkpoint after every job.

The only subprocess runs this package's reviewed replay_events.py using the
current Python interpreter, without a shell. No network or deletion calls.
"""
import argparse,os,subprocess,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['original','partner'],required=True);ap.add_argument('--N',type=int,choices=[4,6],required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    rows=[]
    for case in ['first_ann','upper_ann','flat_birth','final_ann']:
        result=ROOT/'results'/f'{case}_{a.engine}_N{a.N}.json'
        if a.resume and result.exists() and json.loads(result.read_text()).get('status')=='ACCEPT':
            rows.append(dict(case=case,status='SKIPPED_ACCEPTED'));continue
        log=ROOT/'results'/f'{case}_{a.engine}_N{a.N}.log'
        command=[sys.executable,'-B',str(ROOT/'replay_events.py'),'--engine',a.engine,'--N',str(a.N),'--case',case]
        with log.open('w') as stream:proc=subprocess.run(command,env={**os.environ,'OPENBLAS_NUM_THREADS':'1'},stdout=stream,stderr=subprocess.STDOUT)
        r=json.loads(result.read_text()) if result.exists() else {}
        rows.append(dict(case=case,exit_code=proc.returncode,status=r.get('status'),error=r.get('error')))
        (ROOT/'results'/f'batch_{a.engine}_N{a.N}.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows[-1],flush=True)
