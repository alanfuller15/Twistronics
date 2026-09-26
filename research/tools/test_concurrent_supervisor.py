"""Real-process infrastructure controls. All workers are synthetic; no physics.

Run: python -B research/tools/test_concurrent_supervisor.py OUTPUT.json
Fault cases are independent fixtures, never retries of a physical launch.
"""
import hashlib
import json
import os
import resource
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import concurrent_supervisor as supervisor
from concurrent_supervisor import BatchFailed, Job, Limits, run_jobs

COMMIT = '0' * 40  # Explicitly synthetic; not a physical source binding.


def fixture(mode, output):
    output = Path(output)
    if mode == 'fail':
        time.sleep(.08)
        raise SystemExit(7)
    if mode == 'ignore_term':
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        (output/'READY').write_text('synthetic')
        time.sleep(30)
        return
    if mode == 'memory':
        bytearray(256*1024**2)
        raise RuntimeError('MEMORY_LIMIT_NOT_ENFORCED')
    if mode == 'file':
        with (output/'TOO_LARGE').open('wb') as f:
            f.write(b'x' * 1024**2)
        raise RuntimeError('FILE_LIMIT_NOT_ENFORCED')
    if mode == 'descendant':
        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
        def term(_sig, _frame):
            child.wait(timeout=2)
            raise SystemExit(1)
        signal.signal(signal.SIGTERM, term)
        (output/'DESCENDANT_PID').write_text(str(child.pid))
        time.sleep(30)
        return
    time.sleep(.08)
    data = {'synthetic': True, 'arithmetic': [sum((i*j)**2 for j in range(40)) for i in range(12)],
            'threads': {k: os.environ[k] for k in supervisor.THREAD_KEYS},
            'address_space': list(resource.getrlimit(resource.RLIMIT_AS)),
            'file_bytes': list(resource.getrlimit(resource.RLIMIT_FSIZE))}
    (output/'RESULT.json').write_text(json.dumps(data, sort_keys=True)+'\n')


def job(i, mode='normal'):
    return Job(f'job{i:03}', (sys.executable, '-B', str(Path(__file__).resolve()), 'fixture', mode, '{output}'), (i,))


def verify_cleanup(report, directory):
    assert len(report['attempted_jobs']) == len(set(report['attempted_jobs']))
    assert len(report['receipts']) == len(report['attempted_jobs'])
    assert report['retries'] == 0
    for receipt in report['receipts']:
        assert receipt['process_group_empty'], receipt
        if receipt['pid'] is not None:
            assert not supervisor.group_exists(receipt['pid'])
            try:
                os.waitpid(receipt['pid'], os.WNOHANG)
            except ChildProcessError:
                pass
            else:
                raise AssertionError('DIRECT_CHILD_NOT_REAPED')
        for name, expected in receipt['files'].items():
            b = (directory/receipt['name']/name).read_bytes()
            assert len(b) == expected['bytes'] and hashlib.sha256(b).hexdigest() == expected['sha256']


def main(out):
    results, reference = [], None
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for workers in (1, 2, 4):
            directory = root/f'normal{workers}'
            report = run_jobs([job(i) for i in range(4)], directory, cwd=root,
                              source_commit=COMMIT, limits=Limits(workers=workers))
            verify_cleanup(report, directory)
            payloads = [(directory/f'job{i:03}'/'RESULT.json').read_bytes() for i in range(4)]
            if reference is None: reference = payloads[0]
            assert all(b == reference for b in payloads)
            assert report['peak_workers'] == workers and all(r['termination']=='NORMAL_EXIT' for r in report['receipts'])
            data = json.loads(reference)
            assert set(data['threads'].values()) == {'1'}
            assert data['address_space'] == [3*1024**3]*2 and data['file_bytes'] == [64*1024**2]*2
            results.append({'case': f'normal_{workers}_workers', 'status': 'PASS', 'jobs': 4,
                            'bit_identical_synthetic_output_sha256': hashlib.sha256(reference).hexdigest()})
        scenarios = [('worker_failure', 'fail', Limits(workers=4)),
                     ('job_timeout', 'ignore_term', Limits(workers=4, job_seconds=.5, cleanup_seconds=.15)),
                     ('batch_timeout', 'ignore_term', Limits(workers=4, batch_seconds=.5, cleanup_seconds=.15)),
                     ('file_limit', 'file', Limits(workers=4, file_bytes=32768)),
                     ('memory_limit', 'memory', Limits(workers=4, address_space_bytes=64*1024**2)),
                     ('descendant_cleanup', 'descendant', Limits(workers=4, job_seconds=.7, cleanup_seconds=.5))]
        for name, mode, limits in scenarios:
            directory = root/name
            tasks = [job(0, mode)] + [job(i, 'ignore_term') for i in range(1,4)] + [job(i) for i in range(4,8)]
            try:
                run_jobs(tasks, directory, cwd=root, source_commit=COMMIT, limits=limits)
            except BatchFailed as ex:
                report = ex.report
            else: raise AssertionError('FAULT_NOT_REJECTED:' + name)
            verify_cleanup(report, directory)
            assert report['attempted_jobs'] == ['job000','job001','job002','job003']
            assert report['not_started_jobs'] == ['job004','job005','job006','job007']
            if name == 'file_limit':
                assert 'File too large' in (directory/'job000/WORKER.log').read_text() or report['receipts'][0]['exit_code'] == -signal.SIGXFSZ
            if name == 'memory_limit':
                assert 'MemoryError' in (directory/'job000/WORKER.log').read_text()
            if mode == 'ignore_term':
                assert any('SIGKILL' in r['signals'] for r in report['receipts'])
            results.append({'case': name, 'status': 'PASS', 'observed_failure': report['failure'],
                            'attempted_jobs': report['attempted_jobs'], 'receipts': len(report['receipts']),
                            'all_groups_empty': True, 'all_direct_children_reaped': True})
        real_popen = subprocess.Popen
        calls = 0
        def launch_error(*a, **kw):
            nonlocal calls
            calls += 1
            if calls == 2: raise OSError('SYNTHETIC_SECOND_LAUNCH_FAILURE')
            return real_popen(*a, **kw)
        directory = root/'launch_error'
        with patch.object(supervisor.subprocess, 'Popen', launch_error):
            try:
                run_jobs([job(i,'ignore_term') for i in range(4)], directory, cwd=root, source_commit=COMMIT,
                         limits=Limits(workers=4,cleanup_seconds=.15))
            except BatchFailed as ex: report = ex.report
            else: raise AssertionError('LAUNCH_ERROR_ACCEPTED')
        verify_cleanup(report,directory)
        assert report['attempted_jobs'] == ['job000','job001'] and report['receipts'][1]['termination']=='LAUNCH_ERROR'
        results.append({'case': 'second_launch_exception', 'status': 'PASS', 'receipts': 2, 'all_groups_empty': True})
        directory = root/'signal'
        # Delivery in the current supervisor process exercises the installed handler.
        timer = threading.Timer(.35, lambda: os.kill(os.getpid(), signal.SIGTERM))
        timer.start()
        try:
            try:
                run_jobs([job(i,'ignore_term') for i in range(4)],directory,cwd=root,source_commit=COMMIT,
                         limits=Limits(workers=4,cleanup_seconds=.15))
            except BatchFailed as ex: report = ex.report
            else: raise AssertionError('SIGNAL_NOT_REJECTED')
        finally: timer.cancel(); timer.join()
        verify_cleanup(report,directory)
        assert 'SUPERVISOR_SIGNAL' in report['failure']
        results.append({'case': 'supervisor_sigterm', 'status': 'PASS', 'receipts':len(report['receipts']), 'all_groups_empty':True})
        for name, tasks, limits, directory in [
            ('existing_output', [job(i) for i in range(4)], Limits(), root/'normal4'),
            ('unbalanced_jobs', [job(i) for i in range(3)], Limits(), root/'unused1'),
            ('overlap', [job(0), Job('job001', job(1).argv,(0,))], Limits(workers=2), root/'unused2')]:
            with patch.object(supervisor.subprocess,'Popen',side_effect=AssertionError('SHOULD_NOT_LAUNCH')):
                try: run_jobs(tasks,directory,cwd=root,source_commit=COMMIT,limits=limits)
                except (ValueError,FileExistsError): pass
                else: raise AssertionError('BAD_INPUT_ACCEPTED')
            results.append({'case':name,'status':'PASS','launches':0})
    report = {'status':'PASS','physical_eigensolves':0,'synthetic_only':True,
              'tests':results,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
              (Path(__file__),Path(supervisor.__file__),Path(supervisor.__file__).with_name('bounded_worker.py'))}}
    Path(out).write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','cases':len(results),'physical_eigensolves':0}))


if __name__ == '__main__':
    if sys.argv[1] == 'fixture': fixture(sys.argv[2],sys.argv[3])
    else: main(sys.argv[1])
