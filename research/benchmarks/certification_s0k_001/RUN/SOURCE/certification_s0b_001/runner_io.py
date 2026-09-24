"""Portable run records; a completion marker is installed only after hashes."""
import hashlib
import json
import os
from pathlib import Path
import tempfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, data):
    path = Path(path)
    fd, temp = tempfile.mkstemp(prefix='write-',suffix='.tmp',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(data,f,indent=2,sort_keys=True)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def begin(path):
    path = Path(path).resolve()
    path.mkdir(parents=True,exist_ok=False)
    return path


def finish(out, summary):
    out = Path(out).resolve()
    if (out/'COMPLETE.json').exists():
        raise FileExistsError('run already completed')
    atomic_json(out/'RESULTS.json',summary)
    paths = sorted(p for p in out.rglob('*') if p.is_file() and p.name not in ('MANIFEST.json','COMPLETE.json')
                   and p.suffix != '.tmp' and '__pycache__' not in p.parts)
    manifest = {'schema':'portable_run_manifest_v1','path_base':'output_directory',
                'files':[{'path':p.relative_to(out).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]}
    atomic_json(out/'MANIFEST.json',manifest)
    atomic_json(out/'COMPLETE.json',{'schema':'run_completion_v1','records_complete':True,
                'result_status':summary['status'],'manifest_sha256':sha(out/'MANIFEST.json')})


def verify(out):
    out = Path(out).resolve()
    marker = json.loads((out/'COMPLETE.json').read_text())
    if marker.get('records_complete') is not True or marker['manifest_sha256'] != sha(out/'MANIFEST.json'):
        raise ValueError('incomplete or changed manifest')
    manifest = json.loads((out/'MANIFEST.json').read_text())
    for row in manifest['files']:
        p = (out/row['path']).resolve()
        p.relative_to(out)
        if p.stat().st_size != row['bytes'] or sha(p) != row['sha256']:
            raise ValueError('changed artifact: '+row['path'])
    results = json.loads((out/'RESULTS.json').read_text())
    if marker['result_status'] != results['status']:
        raise ValueError('completion/result status mismatch')
    return {'status':'PASS_RECORD_INTEGRITY','files':len(manifest['files']),'result_status':results['status']}
