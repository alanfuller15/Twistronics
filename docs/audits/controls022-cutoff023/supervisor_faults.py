"""Deterministic fault injection into the unchanged producer run() functions.

No physical worker, subprocess, Hamiltonian, or eigensolver is launched. Only
run() is compiled from the producer's AST. Its process, clock and OS interfaces
are fakes; output directories/receipts are real temporary files. Each scenario
is independent, not a retry. This tests supervisor control flow, not OS behavior.
"""
import ast
import hashlib
import json
import signal
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]


def check(path, scenario):
    tree = ast.parse(path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    clock = SimpleNamespace(now=0.)
    children, killed = [], []

    class Process:
        def __init__(self, job):
            self.job, self.pid, self.returncode = job, 10000 + job, None
        def poll(self):
            if scenario == 'normal' or (scenario == 'worker_failure' and self.job == 0):
                self.returncode = 7 if scenario == 'worker_failure' else 0
            return self.returncode
        def wait(self):
            assert self.returncode is not None, 'unexpected blocking wait'
            return self.returncode

    def popen(argv, **kwargs):
        job = int(argv[argv.index('--job') + 1])
        assert kwargs['start_new_session'] is True
        assert all(kwargs['env'][k] == '1' for k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'))
        if scenario == 'second_launch_failure' and job == 1:
            raise OSError('synthetic launch failure')
        proc = Process(job)
        children.append(proc)
        return proc

    def killpg(pid, sig):
        proc = next(p for p in children if p.pid == pid)
        if proc.returncode is not None:
            raise ProcessLookupError(pid)
        if sig:
            assert sig == signal.SIGKILL
            killed.append(proc.job)
            proc.returncode = -9

    def sleep(seconds):
        clock.now += seconds

    cfg = {'jobs': [[i] for i in range(4)], 'authorization': 'SYNTHETIC ONLY',
           'reuse': {'regression_points': []},
           'limits': {'batch_timeout_seconds': .01 if scenario == 'batch_timeout' else 1.,
                      'job_timeout_seconds': .01 if scenario == 'job_timeout' else 1.,
                      'concurrent_workers': 4}}
    ns = dict(bound=lambda _: cfg, os=SimpleNamespace(environ={}, killpg=killpg),
              time=SimpleNamespace(monotonic=lambda: clock.now, sleep=sleep),
              subprocess=SimpleNamespace(Popen=popen, STDOUT=-2), sys=sys,
              signal=signal, HERE=path.parent, KEYS=['c', 'd', 'e'], SOLVE=['f'],
              NPOINTS=4, json=json, replay=lambda _: None,
              sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest(),
              write=lambda p, v: p.write_text(json.dumps(v, sort_keys=True)),
              print=lambda *a, **k: None)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), ns)
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / 'output'
        a = SimpleNamespace(commit='SYNTHETIC', output=output, wheel='UNUSED', reuse_021='UNUSED')
        error = None
        try:
            ns['run'](a)
        except (AssertionError, OSError) as ex:
            error = type(ex).__name__ + ': ' + str(ex)
        receipts = sorted(p.parent.name for p in output.glob('job*/RECEIPT.json'))
        result = {'scenario': scenario, 'exception': error,
                  'launched_jobs': [p.job for p in children],
                  'running_after_supervisor_returns': [p.job for p in children if p.returncode is None],
                  'killed_jobs': killed, 'receipt_jobs': receipts,
                  'batch_receipt': (output / 'BATCH.json').exists()}
    if scenario == 'normal':
        assert error is None and len(receipts) == 4 and result['batch_receipt']
    else:
        assert error is not None and result['running_after_supervisor_returns']
    return result


def main():
    results = {}
    for name in ('controls_e_022', 'cutoff_f_023'):
        path = ROOT / 'research/benchmarks' / name / 'run.py'
        results[name] = {'run_py_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'scenarios': [check(path, s) for s in
                                       ('normal', 'worker_failure', 'job_timeout', 'batch_timeout', 'second_launch_failure')]}
    out = {'physical_eigensolves': 0, 'real_subprocesses': 0,
           'finding': 'Failure paths return with other worker process groups still active and without their receipts.',
           'results': results}
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'MATERIAL_FINDING_REPRODUCED', 'producers': 2, 'scenarios_per_producer': 5,
                      'physical_eigensolves': 0, 'real_subprocesses': 0}))


if __name__ == '__main__':
    main()
