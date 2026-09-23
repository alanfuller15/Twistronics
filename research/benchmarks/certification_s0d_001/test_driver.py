#!/usr/bin/env python3
"""Fixed S0d protocol regressions; no physical or numerical fixture run."""
import json
from pathlib import Path
import sys
import tempfile

from driver import execute_job, matches

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'certification_s0b_001'))
from runner_io import atomic_json, begin, finish, verify


def command(record):
    return [sys.executable, '-c', 'print('+repr(json.dumps(record))+')']


def main():
    checks = []
    job = {'id': 'control', 'expected_status': 'INCONCLUSIVE',
           'expected_reason': 'NONFINITE_ENCLOSURE'}
    raw = {'status': 'INCONCLUSIVE', 'reason': job['expected_reason'], 'job': job}
    got = execute_job(command(raw), job, 5)
    checks.append(('recognized_nonfinite_preserved', got == raw and matches(got, job)))
    fault = {'status': 'EXECUTION_ERROR', 'reason': 'WORKER_EXCEPTION',
             'error_type': 'ValueError', 'job': job}
    got = execute_job(command(fault), job, 5)
    checks.append(('shape_fault_remains_error', got == fault and not matches(got, job)))
    wrong = {**raw, 'status': 'CERTIFIED'}
    checks.append(('unexpected_certificate_is_failure',
                   not matches(execute_job(command(wrong), job, 5), job)))
    missing = {k: v for k, v in raw.items() if k != 'reason'}
    checks.append(('missing_reason_rejected',
                   execute_job(command(missing), job, 5)['reason'] == 'WORKER_SCHEMA'))
    other = {**raw, 'job': {'id': 'different'}}
    checks.append(('wrong_job_rejected',
                   execute_job(command(other), job, 5)['reason'] == 'WORKER_SCHEMA'))
    checks.append(('nonzero_exit_is_error',
                   execute_job([sys.executable, '-c', 'raise SystemExit(3)'], job, 5)['reason'] == 'WORKER_EXIT'))
    slow = execute_job([sys.executable, '-c', 'import time; time.sleep(1)'], job, 0.05)
    checks.append(('timeout_is_distinct_inconclusive',
                   slow['status'] == 'INCONCLUSIVE' and slow['reason'] == 'WALL_BUDGET'
                   and not matches(slow, job)))
    with tempfile.TemporaryDirectory(prefix='s0d-protocol-') as temporary:
        out = begin(Path(temporary)/'external')
        atomic_json(out/'control.json', raw)
        finish(out, {'status': 'NOT_PASSED'})
        checks.append(('complete_records_do_not_imply_pass',
                       verify(out)['result_status'] == 'NOT_PASSED'))
    checks.append(('raw_status_vocabulary_closed',
                   execute_job(command({**raw, 'status': 'PASS'}), job, 5)['reason'] == 'WORKER_SCHEMA'))
    checks.append(('error_type_match_is_explicit',
                   not matches({**fault, 'error_type': 'TypeError'},
                               {**job, 'expected_status': 'EXECUTION_ERROR',
                                'expected_reason': 'WORKER_EXCEPTION',
                                'expected_error_type': 'ValueError'})))
    result = {'status': 'PASS' if all(ok for _, ok in checks) else 'FAIL',
              'passed': sum(ok for _, ok in checks),
              'checks': [{'name': name, 'pass': ok} for name, ok in checks],
              'physical_evaluations': 0}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
