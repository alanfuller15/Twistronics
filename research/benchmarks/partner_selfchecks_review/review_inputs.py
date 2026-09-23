"""Verify and safely extract the unchanged partner input; no network access."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT = Path(__file__).resolve().parent


def extract(target):
    target = Path(target); target.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT/'INPUT_MANIFEST.json').read_text())
    archive = ROOT/'partner_v076p.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest['archive_sha256']:
        raise RuntimeError('archive hash mismatch')
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != set(manifest['files']): raise RuntimeError('member list mismatch')
        for name, rec in manifest['files'].items():
            if Path(name).name != name or name in ('.', '..'): raise RuntimeError('unsafe member')
            data = z.read(name)
            if len(data) != rec['bytes'] or hashlib.sha256(data).hexdigest() != rec['sha256']: raise RuntimeError('member hash mismatch')
            out = target/name
            if out.exists() and out.read_bytes() != data: raise RuntimeError('refusing to replace changed input: '+name)
            out.write_bytes(data)
    return target


def activate():
    p = extract(ROOT/'original'); sys.path.insert(0, str(p)); return p


if __name__ == '__main__': print(activate())
