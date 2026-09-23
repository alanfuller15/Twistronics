#!/usr/bin/env python3
"""Finite standard-library controls, no numerical workers or model code."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
from unittest.mock import patch
from runner_io import atomic_json, begin, finish, verify
from run_calibration import execute_job


def main():
    checks = []
    with tempfile.TemporaryDirectory(prefix='s0b-runner-controls-') as tmp:
        root = Path(tmp)
        # Fresh absolute output is deliberately outside the package directory.
        out = begin(root/'external')
        atomic_json(out/'sample.json',{'value':1})
        finish(out,{'status':'PASS','count':1})
        checks.append(('absolute_external_output',verify(out)['result_status']=='PASS'))
        moved = root/'moved'
        shutil.copytree(out,moved)
        checks.append(('portable_copied_output',verify(moved)['result_status']=='PASS'))
        try:
            begin(out)
            checks.append(('existing_output_refused',False))
        except FileExistsError:
            checks.append(('existing_output_refused',True))
        atomic_json(moved/'sample.json',{'value':2})
        try:
            verify(moved)
            checks.append(('tampering_refused',False))
        except ValueError:
            checks.append(('tampering_refused',True))
        broken = begin(root/'broken')
        with patch('runner_io.atomic_json',side_effect=OSError('injected write failure')):
            try:
                finish(broken,{'status':'PASS'})
            except OSError:
                pass
        checks.append(('write_failure_has_no_completion_marker',not (broken/'COMPLETE.json').exists()))
        incomplete = begin(root/'incomplete')
        atomic_json(incomplete/'RESULTS.json',{'status':'PASS'})
        try:
            verify(incomplete)
            checks.append(('missing_completion_refused',False))
        except FileNotFoundError:
            checks.append(('missing_completion_refused',True))
        import os
        previous = Path.cwd()
        try:
            os.chdir(root)
            rel = begin('relative')
            finish(rel,{'status':'PASS'})
            checks.append(('relative_external_output',verify(rel)['result_status']=='PASS'))
        finally:
            os.chdir(previous)
    job = {'id':'synthetic-runner-control'}
    mismatch = execute_job([sys.executable,'-c','print("{}")'],job,5)
    failed = execute_job([sys.executable,'-c','raise SystemExit(3)'],job,5)
    timeout = execute_job([sys.executable,'-c','import time; time.sleep(1)'],job,0.05)
    checks += [('worker_schema_rejected',mismatch.get('reason')=='WORKER_SCHEMA'),
               ('worker_exit_rejected',failed.get('reason')=='WORKER_EXIT'),
               ('worker_timeout_inconclusive',timeout.get('status')=='INCONCLUSIVE')]
    result = {'status':'PASS' if all(ok for _,ok in checks) else 'FAIL',
              'checks':[{'name':name,'pass':ok} for name,ok in checks],
              'passed':sum(ok for _,ok in checks),'physical_evaluations':0}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__':
    sys.exit(main())
