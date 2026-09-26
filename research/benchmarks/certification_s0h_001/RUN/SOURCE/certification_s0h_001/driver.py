"""Environment-locked, frozen-source S0h runner, using the reviewed S0e protocol."""
import argparse
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0f_001'))
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import atomic_json,begin,finish,verify
from run_calibration import environment


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--wheel',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--worker')
    args=parser.parse_args()
    spec=json.loads((HERE/'SPEC.json').read_text())
    if args.worker:
        job=next(j for j in spec['jobs'] if j['id']==args.worker)
        resource.setrlimit(resource.RLIMIT_AS,(spec['limits']['worker_address_bytes'],)*2)
        try:
            from flint import ctx
            from cases import run
            ctx.prec=job['precision']; ctx.threads=1
            result=run(job,spec)
        except Exception as exc:
            result={'status':'EXECUTION_ERROR','reason':'WORKER_EXCEPTION','error_type':type(exc).__name__,'message':str(exc)}
        result.update(job=job,physical_evaluations=0)
        print(json.dumps(result,sort_keys=True)); return 0
    if args.wheel is None or args.output is None: parser.error('--wheel and --output required')
    env=environment(args.wheel.resolve(),spec)
    if not env['native_artifacts']: raise ValueError('no native artifacts checked')
    out=begin(args.output)
    groups={HERE.name:['driver.py','cases.py','SPEC.json'],
            'certification_s0b_001':['runner_io.py','run_calibration.py'],
            'certification_s0f_001':['certified_s0f.py','primitives_s0f.py','pair_s0f.py','frame_bridge.py']}
    for folder,names in groups.items():
        for name in names:
            dest=out/'SOURCE'/folder/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HERE.parent/folder/name,dest)
    atomic_json(out/'ENVIRONMENT.json',env)
    shutil.copyfile(HERE.parents[2]/'docs/certification-readiness/S0H_COMPOSITION.md',out/'S0H_COMPOSITION.md')
    results=[]; start=time.monotonic()
    for job in spec['jobs']:
        remaining=spec['limits']['global_wall_seconds']-(time.monotonic()-start)
        try:
            if remaining<=0: raise subprocess.TimeoutExpired('global',0)
            p=subprocess.run([sys.executable,'-B',str(out/'SOURCE'/HERE.name/'driver.py'),'--worker',job['id']],
                capture_output=True,text=True,timeout=min(remaining,spec['limits']['job_wall_seconds']))
            if p.returncode: raise RuntimeError(p.stderr[-2000:])
            result=json.loads(p.stdout)
            if result.get('job')!=job or result.get('status') not in ('CERTIFIED','INCONCLUSIVE','EXECUTION_ERROR'):
                raise ValueError('worker schema mismatch')
        except subprocess.TimeoutExpired:
            result={'status':'INCONCLUSIVE','reason':'WALL_BUDGET','job':job}
        except Exception as exc:
            result={'status':'EXECUTION_ERROR','reason':'WORKER_PROTOCOL','message':str(exc),'job':job}
        atomic_json(out/(job['id']+'.json'),result)
        ok=(result.get('status'),result.get('reason'))==(job['expected_status'],job['expected_reason'])
        results.append({'id':job['id'],'passed':ok,'status':result['status'],'reason':result['reason']})
        print(job['id'],result['status'],result['reason'],ok,flush=True)
        if not ok: break
    passed=len(results)==len(spec['jobs']) and all(r['passed'] for r in results)
    summary={'status':'PASS_EXPECTED_BEHAVIORS' if passed else 'NOT_PASSED','jobs':results,
        'planned_jobs':len(spec['jobs']),'physical_evaluations':0,
        'scope':'Fixed analytic rectangle composition only; no physical certificate'}
    finish(out,summary)
    print(json.dumps(verify(out)))
    return 0 if passed else 1


if __name__=='__main__': raise SystemExit(main())
