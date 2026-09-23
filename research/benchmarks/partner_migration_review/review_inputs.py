"""Extract the unchanged, hash-bound v077p attachment into a fresh directory."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent

def extract(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / 'INPUT_MANIFEST.json').read_text())
    archive = ROOT / 'partner_v077p.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist()) == set(manifest['files'])
        for name, record in manifest['files'].items():
            assert Path(name).name == name and name not in ('.', '..')
            b = z.read(name)
            assert len(b) == record['bytes'] and hashlib.sha256(b).hexdigest() == record['sha256']
            p = destination / name
            if p.exists() and p.read_bytes() != b:
                raise RuntimeError('Refusing changed input: ' + name)
            p.write_bytes(b)
    return destination
