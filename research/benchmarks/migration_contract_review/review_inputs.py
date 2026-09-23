"""Extract the immutable v078p attachment, checking every member."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

ROOT=Path(__file__).resolve().parent
def extract(destination, source_only=False):
    destination=Path(destination); destination.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'INPUT_MANIFEST.json').read_text())
    archive=ROOT/'partner_v078p.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        assert {i.filename for i in z.infolist() if not i.is_dir()}==set(manifest['files'])
        for name,rec in manifest['files'].items():
            n=PurePosixPath(name)
            assert not n.is_absolute() and '..' not in n.parts and '\\' not in name
            b=z.read(name)
            assert len(b)==rec['bytes'] and hashlib.sha256(b).hexdigest()==rec['sha256']
            if source_only and (n.parts[0]=='RUN' or n.parts[0].startswith('CONTROL_')): continue
            p=destination/name;p.parent.mkdir(parents=True,exist_ok=True)
            if p.exists() and p.read_bytes()!=b: raise RuntimeError('Changed input '+name)
            p.write_bytes(b)
    return destination

def pack(path, files):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for source,name in files: z.write(source,name)
    with zipfile.ZipFile(path) as z: assert z.testzip() is None
