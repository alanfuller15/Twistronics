"""Verify the preserved partner ZIP and expose its unchanged source files."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

ROOT=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'PLAN.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def originals():
    meta=json.loads((ROOT/'INPUT_MANIFEST.json').read_text());archive=ROOT/'partner_joint_mapping.zip'
    assert sha(archive)==meta['archive_sha256']==PLAN['input_archive_sha256']
    folder=ROOT/'original';folder.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())==set(meta['files'])
        for n,h in meta['files'].items():
            target=folder/n
            if Path(n).name!=n:raise ValueError('unexpected archive path')
            b=z.read(n);assert hashlib.sha256(b).hexdigest()==h
            if target.exists():assert sha(target)==h,n
            else:target.write_bytes(b)
    sys.path.insert(0,str(folder));return folder

def binding(extra):
    return {n:sha(ROOT/n) for n in ['PLAN.json','INPUT_MANIFEST.json','partner_joint_mapping.zip','inputs.py',*extra]}
