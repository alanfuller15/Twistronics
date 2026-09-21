"""test_evidence_bound.py v2 (Codex v065 hardening of partner v065p) — source/runtime-bound recorder, publication gate, historical check.

Selection contract: SELECTION lists exactly the test files executed; the certificate names that scope, never the archive.
Bound inputs: every file under the root matching INPUT_SUFFIXES (recursive; evidence/cache dirs excluded), so matching source/configuration files within the root are bound. JSON/NPZ data and outside-root imports are not bound. Independent execution log: evidence_plugin.py records collection,
deselection, per-phase outcomes and wasxfail; the gate cross-checks it against JUnit rather than copying either.
Publication: gate(bundle, root) requires the root and captures the CURRENT runtime; it rejects differences in Python version/implementation, packages, native binaries and thread settings, any input change, any non-passing outcome (fail, error,
skip, xfail, xpass), any deselection or undeclared filter, missing or unsafe artifacts, and tampering.
historical_consistency(bundle) reports internal consistency of an old bundle and never returns a publication certificate.
Importing this module runs nothing and writes nothing."""
import hashlib, json, os, subprocess, sys, time, platform, datetime, xml.etree.ElementTree as ET
from collections import Counter
SELECTION = ['test_regression.py', 'test_tbg_ref.py']
INPUT_SUFFIXES = ('.py', '.txt', '.ini', '.toml', '.cfg')
EXCLUDE_DIRS = {'test_evidence', '__pycache__', '.pytest_cache', '.git'}
TIMEOUT_S = 900
SCHEMA = 'partner_test_evidence_v2'
REQUIRED = ('stdout.txt', 'stderr.txt', 'junit.xml', 'execution.json')
class EvidenceError(RuntimeError): pass
def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()
def identity(root):
    """recursive digest of all bound inputs relative to root"""
    out = {}
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in EXCLUDE_DIRS)
        for f in sorted(files):
            if f.endswith(INPUT_SUFFIXES):
                p = os.path.join(d, f); out[os.path.relpath(p, root).replace(os.sep, '/')] = sha(p)
    return out
def runtime():
    import importlib.metadata as md
    import numpy, scipy.linalg                       # load the numerical libraries so native identity is visible
    info = dict(python=platform.python_version(), implementation=platform.python_implementation(), executable=sys.executable, platform=platform.platform(),
                packages={d.metadata['Name'].lower(): d.version for d in md.distributions()},
                threads={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')},
                env_filters={k: os.environ.get(k) for k in ('PYTEST_ADDOPTS', 'PYTEST_PLUGINS', 'PYTHONPATH', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD')}, native=[])
    try:
        import threadpoolctl
        for lib in threadpoolctl.threadpool_info():
            fp = lib.get('filepath'); info['native'].append(dict(user_api=lib.get('user_api'), internal_api=lib.get('internal_api'), version=lib.get('version'), filepath=fp, sha256=sha(fp) if fp and os.path.exists(fp) else None))
    except Exception as e:
        info['native_error'] = repr(e)
    return info
def _require_native_identity(info):
    """A capture error or absent/incomplete native identity is not evidence of equality."""
    if info.get('native_error') or not info.get('native'):
        raise EvidenceError('native identity capture missing or failed')
    for lib in info['native']:
        digest = lib.get('sha256')
        if not all(lib.get(k) for k in ('user_api', 'internal_api', 'version', 'filepath')) or not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise EvidenceError('native identity capture incomplete')
def _require_complete_phases(ex):
    expected = Counter((node, phase) for node in ex['collected'] for phase in ('setup', 'call', 'teardown'))
    observed = Counter((row['nodeid'], row['when']) for row in ex['reports'])
    if observed != expected:
        raise EvidenceError('missing, duplicate or unexpected setup/call/teardown phase')
    if ex.get('testscollected') != len(ex['collected']):
        raise EvidenceError('session testscollected differs from collected node ids')
def _junit_cases(path):
    cases = []
    for tc in ET.parse(path).getroot().iter('testcase'):
        outcome = 'passed'
        for tag in ('failure', 'error', 'skipped'):
            if tc.find(tag) is not None: outcome = tag
        cases.append(dict(classname=tc.get('classname'), name=tc.get('name'), file=tc.get('file'), outcome=outcome))
    return cases
def record(root, out_root=None, selection=None, timeout=TIMEOUT_S):
    root = os.path.abspath(root); selection = list(selection or SELECTION)
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = os.path.join(out_root or root, 'test_evidence', run_id); os.makedirs(out, exist_ok=False)
    before = identity(root); rt_before = runtime()
    env = {k: v for k, v in os.environ.items() if k not in ('PYTEST_ADDOPTS', 'PYTEST_PLUGINS')}   # undeclared filters removed from the run
    env['PYTHONDONTWRITEBYTECODE'] = '1'; env['EVIDENCE_EXEC_LOG'] = os.path.join(out, 'execution.json'); env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + env.get('PYTHONPATH', '')
    junit = os.path.join(out, 'junit.xml'); start = datetime.datetime.now(datetime.timezone.utc).isoformat(); t0 = time.time()
    cmd = [sys.executable, '-B', '-m', 'pytest', *selection, '-q', '-p', 'no:cacheprovider', '-p', 'evidence_plugin', '--junitxml', junit]
    timed_out = False; rc = None; so = se = ''
    try:
        r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, timeout=timeout, env=env); rc, so, se = r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True; so = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or ''); se = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or '')
    finish = datetime.datetime.now(datetime.timezone.utc).isoformat(); wall = time.time() - t0
    open(os.path.join(out, 'stdout.txt'), 'w').write(so); open(os.path.join(out, 'stderr.txt'), 'w').write(se)
    after = identity(root); rt_after = runtime()
    ev = dict(schema=SCHEMA, run_id=run_id, root_basename=os.path.basename(root), selection=selection, command=cmd, removed_env=['PYTEST_ADDOPTS', 'PYTEST_PLUGINS'],
              timeout_s=timeout, timed_out=timed_out, started_utc=start, finished_utc=finish, wall_seconds=wall, returncode=rc,
              identity_before=before, identity_after=after, runtime_before=rt_before, runtime_after=rt_after,
              artifacts={a: sha(os.path.join(out, a)) for a in REQUIRED if os.path.exists(os.path.join(out, a))})
    with open(os.path.join(out, 'evidence.json'), 'w') as f: json.dump(ev, f, indent=1)
    return out
def _check_bundle(bundle):
    """structural and internal checks shared by publication and historical modes; returns (evidence, cases, execlog)"""
    bundle = os.path.abspath(bundle); ev = json.load(open(os.path.join(bundle, 'evidence.json')))
    if ev.get('schema') != SCHEMA: raise EvidenceError('unknown or old evidence schema (historical bundles are not publication evidence)')
    if ev['timed_out']: raise EvidenceError('run timed out')
    for a in REQUIRED:
        if a not in ev['artifacts']: raise EvidenceError(f'required artifact {a} not recorded')
    for a, h in ev['artifacts'].items():
        if a not in REQUIRED or os.sep in a or a.startswith('.'): raise EvidenceError(f'unsafe or unexpected artifact name {a!r}')
        p = os.path.join(bundle, a)
        if not os.path.exists(p) or sha(p) != h: raise EvidenceError(f'artifact {a} missing or tampered')
    if ev['returncode'] != 0: raise EvidenceError(f'pytest returncode {ev["returncode"]}')
    if ev['identity_before'] != ev['identity_after']: raise EvidenceError('bound inputs changed during the run')
    if ev['runtime_before'] != ev['runtime_after']: raise EvidenceError('runtime identity changed during the run')
    _require_native_identity(ev['runtime_before'])
    if ev['runtime_before']['env_filters'].get('PYTEST_ADDOPTS'): raise EvidenceError('PYTEST_ADDOPTS was set in the recording environment')
    ex = json.load(open(os.path.join(bundle, 'execution.json'))); cases = _junit_cases(os.path.join(bundle, 'junit.xml'))
    if ex['config'].get('PYTEST_ADDOPTS') or ex['config'].get('keyword') or ex['config'].get('markexpr') or ex['config'].get('deselect_opt'): raise EvidenceError('undeclared test filtering in the effective pytest configuration')
    if ex['deselected']: raise EvidenceError(f'{len(ex["deselected"])} test(s) deselected')
    declared = set(ev['selection']); inv = [a for a in ex['config']['invocation_args'] if a.endswith('.py')]
    if set(inv) != declared: raise EvidenceError(f'effective invocation files {inv} differ from the declared selection')
    if not ex['collected']: raise EvidenceError('nothing collected')
    if len(ex['collected']) != len(set(ex['collected'])): raise EvidenceError('duplicate collected node ids')
    calls = [r for r in ex['reports'] if r['when'] == 'call']; call_ids = [r['nodeid'] for r in calls]
    if sorted(call_ids) != sorted(ex['collected']): raise EvidenceError('collected node ids and executed call phases do not match (missing or duplicate calls)')
    for r in ex['reports']:
        if r['outcome'] != 'passed' or r['wasxfail']: raise EvidenceError(f'non-passing or xfail/xpass phase: {r["nodeid"]} {r["when"]} {r["outcome"]} wasxfail={r["wasxfail"]}')
    _require_complete_phases(ex)
    if len(cases) != len(call_ids): raise EvidenceError(f'JUnit case count {len(cases)} != executed calls {len(call_ids)}')
    jn = sorted(c['name'] for c in cases); xn = sorted(n.split('::')[-1] for n in call_ids)
    if jn != xn: raise EvidenceError('JUnit test names and execution-log node ids disagree')
    if any(c['outcome'] != 'passed' for c in cases): raise EvidenceError('JUnit records a non-passing outcome')
    if ex.get('exitstatus') != 0 or ex.get('testsfailed'): raise EvidenceError('session exit status or failure count nonzero')
    return ev, cases, ex
def historical_consistency(bundle):
    """internal consistency of an old bundle: NOT a publication certificate"""
    ev, cases, ex = _check_bundle(bundle)
    return dict(certified=False, historical_consistent=True, run_id=ev['run_id'], passed=len(cases), note='internally consistent recorded evidence; current sources and runtime were not compared')
def gate(bundle, root):
    """publication certificate: requires the current source root and compares the CURRENT runtime"""
    if root is None: raise EvidenceError('publication requires an explicit source root')
    ev, cases, ex = _check_bundle(bundle)
    cur = identity(os.path.abspath(root))
    if cur != ev['identity_before']:
        added = sorted(set(cur) - set(ev['identity_before'])); removed = sorted(set(ev['identity_before']) - set(cur)); changed = sorted(k for k in cur if k in ev['identity_before'] and cur[k] != ev['identity_before'][k])
        raise EvidenceError(f'stale: bound inputs differ from the record (added {added}, removed {removed}, changed {changed})')
    now = runtime()
    _require_native_identity(now)
    for k in ('python', 'implementation', 'packages', 'threads', 'native'):
        if now[k] != ev['runtime_before'][k]: raise EvidenceError(f'current runtime differs from the record in {k!r}')
    if now['env_filters'].get('PYTEST_ADDOPTS'): raise EvidenceError('PYTEST_ADDOPTS is set in the current environment')
    return dict(certified=True, run_id=ev['run_id'], selection=ev['selection'], passed=len(cases), scope=f'exactly the files {ev["selection"]} under root {ev["root_basename"]!r}; not the archive',
                bound_inputs=len(ev['identity_before']), python=now['python'], packages={k: now['packages'][k] for k in ('numpy', 'scipy', 'pytest', 'threadpoolctl') if k in now['packages']}, native=[(n['internal_api'], n['version'], (n['sha256'] or '')[:16]) for n in now['native']])
def main(argv):
    root = os.path.abspath(argv[1]) if len(argv) > 1 else os.getcwd()
    out = record(root); print('evidence dir:', out)
    try: print(json.dumps(gate(out, root), indent=1)); return 0
    except EvidenceError as e: print('GATE REJECTED:', e); return 1
if __name__ == '__main__':
    sys.exit(main(sys.argv))
