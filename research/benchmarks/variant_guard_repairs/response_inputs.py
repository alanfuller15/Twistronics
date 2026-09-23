"""Verify and extract the preserved partner archive without network access."""
import hashlib, json, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def extract(target):
    target=Path(target); target.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'INPUT_MANIFEST.json').read_text())
    archive=ROOT/'partner_v074p.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=manifest['archive_sha256']:
        raise RuntimeError('partner archive hash mismatch')
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist())!=set(manifest['files']): raise RuntimeError('archive member mismatch')
        for n,rec in manifest['files'].items():
            if Path(n).name!=n or n in ('.','..'): raise RuntimeError('unsafe archive member')
            b=z.read(n)
            if len(b)!=rec['bytes'] or hashlib.sha256(b).hexdigest()!=rec['sha256']: raise RuntimeError('member hash mismatch')
            p=target/n
            if p.exists() and p.read_bytes()!=b: raise RuntimeError('refusing to replace changed input: '+n)
            p.write_bytes(b)
    return target

def activate():
    p=extract(ROOT/'original')
    sys.path.insert(0,str(p))
    return p

if __name__=='__main__': print(activate())
