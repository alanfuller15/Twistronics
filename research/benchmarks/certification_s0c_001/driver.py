#!/usr/bin/env python3
"""Fixed correction regression run, retaining the raw numerical outcomes.

Usage: PYTHONPATH=<locked installation> python -B driver.py --wheel <wheel> --output <fresh-directory>
"""
import argparse
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import atomic_json,begin,finish,verify,sha
from run_calibration import environment

STATUSES=('CERTIFIED','INCONCLUSIVE','EXECUTION_ERROR')


def matches(result,job):
    return (result.get('status')==job['expected_status'] and
            result.get('reason')==job['expected_reason'] and
            ('expected_error_type' not in job or result.get('error_type')==job['expected_error_type']))


def execute_job(command,job,seconds):
    try:
        p=subprocess.run(command,capture_output=True,text=True,timeout=seconds)
        if p.returncode!=0:
            return {'status':'EXECUTION_ERROR','reason':'WORKER_EXIT','returncode':p.returncode,'job':job,'stderr':p.stderr[-4000:]}
        result=json.loads(p.stdout)
        if (not isinstance(result,dict) or result.get('job')!=job or result.get('status') not in STATUSES
                or not isinstance(result.get('reason'),str) or not result['reason']):
            raise ValueError('worker schema mismatch')
        return result
    except subprocess.TimeoutExpired:
        return {'status':'INCONCLUSIVE','reason':'WALL_BUDGET','job':job}
    except (ValueError,TypeError) as e:
        return {'status':'EXECUTION_ERROR','reason':'WORKER_SCHEMA','message':str(e),'job':job}


def worker(job,spec):
    start=time.monotonic()
    try:
        from flint import ctx
        import cases
        ctx.prec=job['precision']
        ctx.threads=1
        result=cases.run(job,spec)
    except Exception as e:
        result={'status':'EXECUTION_ERROR','reason':'WORKER_EXCEPTION','error_type':type(e).__name__,'message':str(e)}
    result.update({'job':job,'wall_seconds':time.monotonic()-start,'physical_evaluations':0,
                   'peak_resident_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wheel',type=Path)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--worker')
    args=ap.parse_args()
    spec=json.loads((HERE/'SPEC.json').read_text())
    if args.worker:
        job=next(j for j in spec['jobs'] if j['id']==args.worker)
        resource.setrlimit(resource.RLIMIT_AS,(spec['limits']['worker_address_bytes'],)*2)
        print(json.dumps(worker(job,spec),sort_keys=True))
        return 0
    if args.wheel is None or args.output is None:
        ap.error('--wheel and --output are required')
    env=environment(args.wheel.resolve(),spec)
    out=begin(args.output)
    groups={HERE.name:['SPEC.json','certified.py','cases.py','driver.py','test_driver.py'],
            'certification_s0b_001':['arithmetic.py','run_calibration.py','runner_io.py'],
            'certification_s0a_001':['primitives.py']}
    for folder,names in groups.items():
        for name in names:
            dest=out/'SOURCE'/folder/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HERE.parent/folder/name,dest)
    atomic_json(out/'ENVIRONMENT.json',env)
    frozen=out/'SOURCE'/HERE.name/'driver.py'
    start=time.monotonic()
    results=[]
    for job in spec['jobs']:
        remaining=spec['limits']['global_wall_seconds']-(time.monotonic()-start)
        if remaining<=0:
            result={'status':'INCONCLUSIVE','reason':'GLOBAL_BUDGET','job':job}
        else:
            result=execute_job([sys.executable,'-B',str(frozen),'--worker',job['id']],job,
                               min(remaining,spec['limits']['job_wall_seconds']))
        # Preserve the result. Test matching is a separate harness decision.
        atomic_json(out/(job['id']+'.json'),result)
        matched=matches(result,job)
        results.append({'id':job['id'],'raw_status':result['status'],'reason':result['reason'],
                        'behavior_pass':matched,'wall_seconds':result.get('wall_seconds')})
        print(job['id'],result['status'],result['reason'],matched,flush=True)
        if not matched:
            break
    passed=len(results)==len(spec['jobs']) and all(r['behavior_pass'] for r in results)
    summary={'spec_id':spec['id'],'status':'PASS_EXPECTED_BEHAVIORS' if passed else 'NOT_PASSED',
             'planned_jobs':len(spec['jobs']),'completed_jobs':len(results),
             'passed_behaviors':sum(r['behavior_pass'] for r in results),'jobs':results,
             'raw_status_counts':{s:sum(r['raw_status']==s for r in results) for s in STATUSES},
             'wall_seconds':time.monotonic()-start,'physical_evaluations':0,
             'interpretation':'Expected inconclusive and execution-error controls are not certificates; CERTIFIED here covers only the specified synthetic claim.'}
    finish(out,summary)
    print(json.dumps(verify(out),sort_keys=True),flush=True)
    return 0 if passed else 1


if __name__=='__main__':
    sys.exit(main())
