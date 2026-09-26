"""Bounded, single-thread process workers with whole-batch failure cleanup.

Additive infrastructure; no historical runner imports this module. The caller
must verify its frozen commit, SPEC and dependency hashes before calling run_jobs.
Physical workers must independently verify those bindings and wheel provenance.
Every run requires a fresh directory; there is no resume, retry or adaptive work.
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

THREAD_KEYS = ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS',
               'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS')


@dataclass(frozen=True)
class Limits:
    workers: int = 4
    job_seconds: float = 90.
    batch_seconds: float = 600.
    address_space_bytes: int = 3 * 1024**3
    file_bytes: int = 64 * 1024**2
    cleanup_seconds: float = 2.
    poll_seconds: float = .02


@dataclass(frozen=True)
class Job:
    name: str
    argv: tuple[str, ...]
    points: tuple[int, ...]


class BatchFailed(RuntimeError):
    def __init__(self, report):
        super().__init__(report['failure'])
        self.report = report


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)


def group_exists(pid):
    try:
        os.killpg(pid, 0)
        return True
    except ProcessLookupError:
        return False


def send_group(pid, sig):
    try:
        os.killpg(pid, sig)
    except ProcessLookupError:
        pass


def inventory(directory):
    files = {}
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise RuntimeError('SYMLINK_IN_JOB_OUTPUT')
        if path.is_file() and path.name not in ('RECEIPT.json', 'RECEIPT.json.tmp'):
            b = path.read_bytes()
            files[str(path.relative_to(directory))] = {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
        elif not path.is_dir() and not path.is_file():
            raise RuntimeError('NONREGULAR_JOB_OUTPUT')
    return files


def run_jobs(jobs, output, *, cwd, source_commit, limits=Limits(), env=None):
    """Run fixed argv jobs, substituting only a literal {output} argument.

    Receipts record planned points, not inferred eigensolver starts. Exit zero
    does not constitute numerical acceptance; callers must replay and check the
    worker evidence. BatchFailed is raised only after cleanup and batch receipt.
    SIGTERM/SIGINT are handled; SIGKILL or host loss cannot guarantee receipts.
    """
    jobs = tuple(jobs); output = Path(output).resolve(); cwd = Path(cwd).resolve()
    if not re.fullmatch(r'[0-9a-f]{40}', source_commit):
        raise ValueError('EXACT_SOURCE_COMMIT_REQUIRED')
    if not (1 <= limits.workers <= 4 and jobs and len(jobs) % limits.workers == 0):
        raise ValueError('JOB_COUNT_MUST_BE_MULTIPLE_OF_1_TO_4_WORKERS')
    if not (0 < limits.job_seconds <= 90 and 0 < limits.batch_seconds <= 600 and
            0 < limits.cleanup_seconds <= 10 and 0 < limits.poll_seconds <= .1 and
            0 < limits.address_space_bytes <= 3*1024**3 and 0 < limits.file_bytes <= 64*1024**2):
        raise ValueError('INVALID_LIMITS')
    if len({j.name for j in jobs}) != len(jobs) or any(not re.fullmatch(r'job[0-9]{3,}', j.name) for j in jobs):
        raise ValueError('INVALID_JOB_NAMES')
    points = [p for j in jobs for p in j.points]
    if len(points) != len(set(points)) or any(not 1 <= len(j.points) <= 32 or not j.argv or any(not isinstance(a, str) for a in j.argv) for j in jobs):
        raise ValueError('INVALID_OR_OVERLAPPING_JOBS')
    output.mkdir(parents=True, exist_ok=False)
    child_env = dict(os.environ if env is None else env)
    child_env.update({key: '1' for key in THREAD_KEYS})
    active, completed, attempted = {}, [], []
    failure, primary, next_job, peak = None, None, 0, 0
    started = time.monotonic(); batch_deadline = started + limits.batch_seconds
    old_handlers = {}

    def interrupted(sig, _frame):
        raise RuntimeError('SUPERVISOR_SIGNAL:' + str(sig))

    def receipt(state, termination):
        proc = state['process']
        if state['log'] is not None:
            state['log'].close(); state['log'] = None
        empty = proc is None or not group_exists(proc.pid)
        row = {'name': state['job'].name, 'source_commit': source_commit,
               'planned_points': list(state['job'].points), 'pid': None if proc is None else proc.pid,
               'exit_code': None if proc is None else proc.returncode,
               'termination': termination, 'process_group_empty': empty,
               'monotonic_start': state['start'], 'monotonic_end': time.monotonic(),
               'job_deadline': state['start'] + limits.job_seconds,
               'batch_deadline': batch_deadline, 'signals': state['signals']}
        try:
            row['files'] = inventory(state['directory'])
        except Exception as ex:
            row['evidence_error'] = type(ex).__name__ + ': ' + str(ex)
        write_json(state['directory']/'RECEIPT.json', row)
        completed.append(row)
        return row

    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            old_handlers[sig] = signal.signal(sig, interrupted)
        while next_job < len(jobs) or active:
            now = time.monotonic()
            if now >= batch_deadline:
                raise RuntimeError('BATCH_WATCHDOG_TIMEOUT')
            # Observe all existing workers before admitting any replacement.
            for name, state in list(active.items()):
                proc = state['process']; code = proc.poll()
                if time.monotonic() >= state['start'] + limits.job_seconds:
                    primary = name; raise RuntimeError('JOB_WATCHDOG_TIMEOUT:' + name)
                if code is not None:
                    if code != 0 or group_exists(proc.pid):
                        primary = name; raise RuntimeError('WORKER_FAILED_OR_GROUP_NOT_EMPTY:' + name)
                    row = receipt(state, 'NORMAL_EXIT'); del active[name]
                    if 'evidence_error' in row:
                        primary = name; raise RuntimeError('INVALID_JOB_EVIDENCE:' + name)
            if time.monotonic() >= batch_deadline:
                raise RuntimeError('BATCH_WATCHDOG_TIMEOUT')
            while next_job < len(jobs) and len(active) < limits.workers:
                if time.monotonic() >= batch_deadline:
                    raise RuntimeError('BATCH_WATCHDOG_TIMEOUT')
                job = jobs[next_job]; directory = output/job.name; directory.mkdir()
                start = time.monotonic()
                state = {'job': job, 'directory': directory, 'start': start,
                         'process': None, 'log': None, 'signals': []}
                active[job.name] = state; attempted.append(job.name); next_job += 1
                argv = [str(directory) if a == '{output}' else a for a in job.argv]
                request = {'argv': argv, 'cwd': str(cwd), 'source_commit': source_commit,
                           'planned_points': list(job.points), 'limits': asdict(limits)}
                write_json(directory/'REQUEST.json', request)
                state['log'] = (directory/'WORKER.log').open('xb')
                try:
                    state['process'] = subprocess.Popen(
                        [sys.executable, '-B', str(Path(__file__).with_name('bounded_worker.py')), str(directory/'REQUEST.json')],
                        stdout=state['log'], stderr=subprocess.STDOUT, env=child_env, start_new_session=True)
                except BaseException:
                    primary = job.name
                    raise
                peak = max(peak, len(active))
            if active:
                time.sleep(min(limits.poll_seconds, max(0., batch_deadline - time.monotonic())))
    except BaseException as ex:
        failure = type(ex).__name__ + ': ' + str(ex)
    finally:
        # A second signal must not interrupt cleanup of already-started jobs.
        for sig in old_handlers:
            signal.signal(sig, signal.SIG_IGN)
        if active:
            for state in active.values():
                proc = state['process']
                if proc is not None and group_exists(proc.pid):
                    send_group(proc.pid, signal.SIGTERM); state['signals'].append('SIGTERM')
            grace = time.monotonic() + limits.cleanup_seconds
            while time.monotonic() < grace:
                for state in active.values():
                    if state['process'] is not None: state['process'].poll()
                if all(s['process'] is None or (s['process'].returncode is not None and not group_exists(s['process'].pid)) for s in active.values()):
                    break
                time.sleep(limits.poll_seconds)
            for state in active.values():
                proc = state['process']
                if proc is not None and group_exists(proc.pid):
                    send_group(proc.pid, signal.SIGKILL); state['signals'].append('SIGKILL')
            for name, state in active.items():
                proc = state['process']
                if proc is not None:
                    try: proc.wait(timeout=limits.cleanup_seconds)
                    except subprocess.TimeoutExpired: failure = (failure or '') + '; REAP_TIMEOUT:' + name
            # Reap every direct child before any receipt write can fail.
            for name, state in active.items():
                proc = state['process']
                termination = 'LAUNCH_ERROR' if proc is None else 'BATCH_ABORTED'
                if name == primary and proc is not None:
                    termination = 'WATCHDOG_TIMEOUT' if 'WATCHDOG' in (failure or '') else 'WORKER_ERROR'
                try:
                    row = receipt(state, termination)
                    if not row['process_group_empty']:
                        failure = (failure or '') + '; PROCESS_GROUP_NOT_EMPTY:' + name
                except Exception as ex:
                    failure = (failure or '') + '; RECEIPT_ERROR:' + name + ':' + str(ex)
            active.clear()
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)
    report = {'status': 'FAIL' if failure else 'PASS', 'failure': failure,
              'source_commit': source_commit, 'limits': asdict(limits),
              'monotonic_start': started, 'batch_deadline': batch_deadline,
              'elapsed_seconds_including_cleanup': time.monotonic()-started,
              'peak_workers': peak, 'attempted_jobs': attempted,
              'not_started_jobs': [j.name for j in jobs if j.name not in attempted],
              'receipts': sorted(completed, key=lambda r: r['name']),
              'retries': 0, 'numerical_acceptance': 'NOT_EVALUATED'}
    write_json(output/'BATCH.json', report)
    if failure:
        raise BatchFailed(report)
    return report
