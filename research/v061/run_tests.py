"""Run all tests and retain immutable, source/environment-bound evidence."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from test_evidence import identity, runtime_identity, read_evidence, sha

ROOT = Path(__file__).resolve().parent


def main():
    started = datetime.now(timezone.utc).isoformat()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:8]
    folder = ROOT / 'provenance/test_runs' / run_id
    folder.mkdir(parents=True)
    before = identity(ROOT)
    runtime = runtime_identity()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    env.pop('PYTEST_ADDOPTS', None)
    command = [sys.executable, '-B', str(ROOT / '_test_worker.py'), str(folder)]
    proc = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    (folder / 'stdout.txt').write_text(proc.stdout + proc.stderr)
    execution = json.loads((folder / 'execution.json').read_text()) if (folder / 'execution.json').exists() else {'calls': []}
    record = dict(schema=1, scope='complete tests directory', run_id=run_id, started_utc=started,
        finished_utc=datetime.now(timezone.utc).isoformat(), command=command, exit_code=proc.returncode,
        identity_before=before, identity_after=identity(ROOT), runtime=runtime,
        passed=sum(x['outcome'] == 'passed' and not x['xfail'] for x in execution['calls']),
        artifacts={name: sha(folder / name) for name in ['junit.xml', 'execution.json', 'stdout.txt'] if (folder / name).exists()})
    path = folder / 'result.json'
    path.write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
    print(proc.stdout + proc.stderr, end='')
    if proc.returncode:
        print('FAILED EVIDENCE:', path)
        raise SystemExit(proc.returncode)
    checked = read_evidence(ROOT, path)
    print(json.dumps(dict(evidence=str(path), **checked), indent=2))


if __name__ == '__main__':
    main()
