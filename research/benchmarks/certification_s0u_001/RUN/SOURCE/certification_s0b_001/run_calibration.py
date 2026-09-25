#!/usr/bin/env python3
"""Frozen synthetic run with portable output and a final completion marker.

Usage: PYTHONPATH=<locked installation> python run_calibration.py --wheel <wheel> --output <fresh-directory>
Both relative and absolute outputs outside this source directory are supported.
"""
import argparse
import importlib.metadata
import json
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time
from runner_io import atomic_json, begin, finish, sha, verify

HERE = Path(__file__).resolve().parent


def environment(wheel, spec):
    import flint
    if sha(wheel) != spec['backend']['wheel_sha256']:
        raise ValueError('wheel hash differs from frozen specification')
    if (flint.__version__,flint.__FLINT_VERSION__) != (spec['backend']['python_flint'],spec['backend']['flint']):
        raise ValueError('backend version mismatch')
    dist = importlib.metadata.distribution('python-flint')
    artifacts = []
    # Compare installed native modules against the exact supplied wheel.
    import zipfile
    with zipfile.ZipFile(wheel) as z:
        import hashlib
        for member in sorted(dist.files or [],key=str):
            if str(member).endswith('.so') or '.so.' in str(member):
                p = Path(dist.locate_file(member))
                installed = sha(p)
                if installed != hashlib.sha256(z.read(str(member))).hexdigest():
                    raise ValueError('installed native artifact differs from wheel: '+str(member))
                artifacts.append({'path':str(member),'sha256':installed,'bytes':p.stat().st_size})
    return {'python':platform.python_version(),'python_flint':flint.__version__,
            'FLINT':flint.__FLINT_VERSION__,'machine':platform.machine(),'system':platform.system(),
            'wheel':{'name':wheel.name,'sha256':sha(wheel)},'threads':1,'native_artifacts':artifacts}


def worker(job, spec):
    from flint import ctx
    import arithmetic
    ctx.prec = job['precision']
    ctx.threads = 1
    start = time.monotonic()
    if job['kind']=='controls':
        result = arithmetic.controls(spec)
    elif job['kind']=='cell':
        result = arithmetic.cell(job,spec)
    elif job['kind']=='transport':
        result = arithmetic.variable_transport(job,spec)
    else:
        raise ValueError('unknown job kind')
    result.update({'job':job,'wall_seconds':time.monotonic()-start,'physical_evaluations':0,
                   'peak_resident_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    return result


def execute_job(command, job, seconds):
    try:
        p = subprocess.run(command,capture_output=True,text=True,timeout=seconds)
        if p.returncode != 0:
            return {'status':'EXECUTION_ERROR','reason':'WORKER_EXIT','returncode':p.returncode,'job':job,'stderr':p.stderr[-4000:]}
        result = json.loads(p.stdout)
        if not isinstance(result,dict) or result.get('job') != job or result.get('status') not in ('PASS','EXECUTION_ERROR'):
            raise ValueError('worker schema mismatch')
        return result
    except subprocess.TimeoutExpired:
        return {'status':'INCONCLUSIVE','reason':'WALL_BUDGET','job':job}
    except (ValueError,TypeError) as e:
        return {'status':'EXECUTION_ERROR','reason':'WORKER_SCHEMA','message':str(e),'job':job}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--wheel',type=Path)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--worker')
    args = ap.parse_args()
    spec = json.loads((HERE/'SPEC.json').read_text())
    if args.worker:
        job = next(j for j in spec['jobs'] if j['id']==args.worker)
        resource.setrlimit(resource.RLIMIT_AS,(spec['limits']['worker_address_bytes'],)*2)
        try:
            result = worker(job,spec)
        except Exception as e:
            result = {'status':'EXECUTION_ERROR','job':job,'error_type':type(e).__name__,'message':str(e)}
        print(json.dumps(result,sort_keys=True))
        return 0
    if args.wheel is None or args.output is None:
        ap.error('--wheel and --output are required')
    # Validate the backend before any job. Never reuse an existing destination.
    env = environment(args.wheel.resolve(),spec)
    out = begin(args.output)
    source_names = ['SPEC.json','arithmetic.py','runner_io.py','run_calibration.py','test_runner.py']
    source = out/'SOURCE'
    for name in source_names:
        dest = source/HERE.name/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(HERE/name,dest)
    prior = source/'certification_s0a_001'/'primitives.py'
    prior.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(HERE.parent/'certification_s0a_001'/'primitives.py',prior)
    atomic_json(out/'ENVIRONMENT.json',env)
    frozen_worker = source/HERE.name/'run_calibration.py'
    start = time.monotonic()
    results = []
    for job in spec['jobs']:
        remaining = spec['limits']['global_wall_seconds']-(time.monotonic()-start)
        if remaining <= 0:
            result = {'status':'INCONCLUSIVE','reason':'GLOBAL_BUDGET','job':job}
        else:
            result = execute_job([sys.executable,'-B',str(frozen_worker),'--worker',job['id']],job,
                                 min(remaining,spec['limits']['job_wall_seconds']))
        atomic_json(out/(job['id']+'.json'),result)
        results.append({'id':job['id'],'status':result['status'],'observed':result.get('observed'),
                        'wall_seconds':result.get('wall_seconds')})
        print(job['id'],result['status'],result.get('observed'),result.get('wall_seconds'),flush=True)
        if result['status'] != 'PASS':
            break
    passed = len(results)==len(spec['jobs']) and all(r['status']=='PASS' for r in results)
    summary = {'spec_id':spec['id'],'status':'PASS_EXPECTED_BEHAVIORS' if passed else 'NOT_PASSED',
               'planned_jobs':len(spec['jobs']),'completed_jobs':len(results),
               'passed_jobs':sum(r['status']=='PASS' for r in results),'jobs':results,
               'wall_seconds':time.monotonic()-start,'physical_evaluations':0,
               'interpretation':'Expected INCONCLUSIVE controls passing are not numerical certificates.'}
    finish(out,summary)
    print(json.dumps(verify(out),sort_keys=True),flush=True)
    return 0 if passed else 1


if __name__=='__main__':
    sys.exit(main())
