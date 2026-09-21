"""Bind a pytest run to complete source/test/input and runtime identities.

This is a consistency gate, not an attestation against a malicious producer.
"""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import xml.etree.ElementTree as ET


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def identity(root):
    root = Path(root)
    paths = set(root.rglob('*.py'))
    paths.update(root / name for name in ('requirements.txt', 'ENVIRONMENT.txt', 'BASELINE.json', 'PLAN.json', 'IMPACT.json', 'IMPACT_PLAN.json', 'NUMERICAL_PLAN.json', 'SOURCE_INDEX.json', 'HISTORICAL_TARGETS.json', 'PRESERVED_TREE.json') if (root / name).is_file())
    for name in ('anchors', 'results'):
        paths.update(p for p in (root / name).rglob('*') if p.is_file())
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(paths)
            if '__pycache__' not in p.parts and '.pytest_cache' not in p.parts and p.suffix != '.pyc'}


def runtime_identity():
    import numpy
    import scipy.linalg
    from threadpoolctl import threadpool_info
    libraries = []
    for item in threadpool_info():
        row = dict(item)
        row['binary_sha256'] = sha(row['filepath'])
        libraries.append(row)
    return dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
        packages=sorted((d.metadata['Name'], d.version) for d in importlib.metadata.distributions()),
        native_libraries=libraries,
        thread_environment={k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')})


def read_evidence(root, record_path, current_runtime=None):
    root, record_path = Path(root), Path(record_path)
    r = json.loads(record_path.read_text())
    if r.get('schema') != 1 or r.get('scope') != 'complete tests directory' or r.get('exit_code') != 0:
        raise ValueError('missing/failed complete-suite test evidence')
    if r['identity_before'] != r['identity_after'] or r['identity_after'] != identity(root):
        raise ValueError('test evidence source/test/input identity mismatch')
    actual = runtime_identity() if current_runtime is None else current_runtime
    if r['runtime'] != json.loads(json.dumps(actual)):
        raise ValueError('test evidence environment mismatch')
    for name, digest in r['artifacts'].items():
        if name not in {'junit.xml', 'execution.json', 'stdout.txt'} or sha(record_path.parent / name) != digest:
            raise ValueError('test artifact digest mismatch')
    if set(r['artifacts']) != {'junit.xml', 'execution.json', 'stdout.txt'}:
        raise ValueError('missing test artifacts')
    execution = json.loads((record_path.parent / 'execution.json').read_text())
    ids = execution['collected']
    reports = execution['calls']
    if execution['exit_code'] != 0 or not ids or len(ids) != len(set(ids)):
        raise ValueError('invalid test collection')
    if len(reports) != len(ids) or {x['nodeid'] for x in reports} != set(ids):
        raise ValueError('incomplete test execution')
    if any(x['outcome'] != 'passed' or x['xfail'] for x in reports):
        raise ValueError('test run contains failed/skipped/xfail cases')
    xml = ET.parse(record_path.parent / 'junit.xml').getroot()
    cases = list(xml.iter('testcase'))
    if len(cases) != len(ids) or any(list(c) for c in cases):
        raise ValueError('JUnit does not confirm all collected tests passed')
    if r['passed'] != len(ids):
        raise ValueError('test pass count mismatch')
    return dict(passed=len(ids), run_id=r['run_id'], started_utc=r['started_utc'],
                record_sha256=sha(record_path), source_and_input_files=len(r['identity_after']))
