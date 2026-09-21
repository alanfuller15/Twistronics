"""Repackage the preserved repository tree with the new v057 evidence."""
import argparse,hashlib,json,tempfile,zipfile
from pathlib import Path,PurePosixPath
from build_report import collect
from evidence import read,require,safe
from protocol import verify_preserved
ROOT=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def safe_relative(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('unsafe manifest member')
    return p

def write_archive(payload, output):
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('refusing to overwrite existing delivery')
    if 'TEAM_PACKAGE_MANIFEST.json' in payload:
        raise ValueError('reserved manifest path')
    for name in payload:
        safe_relative(name)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = {name: dict(bytes=len(data), sha256=sha(data)) for name, data in sorted(payload.items())}
    payload = dict(payload, **{'TEAM_PACKAGE_MANIFEST.json': (json.dumps(dict(files=manifest), indent=2) + '\n').encode()})
    with tempfile.NamedTemporaryFile(prefix='pending_', suffix='.zip', dir=output.parent, delete=False) as tmp:
        path = Path(tmp.name)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(payload.items()):
            entry = zipfile.ZipInfo('twistronics_v057_reconciled/' + name, (2026, 9, 21, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            z.writestr(entry, data)
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('archive CRC error')
        for name, row in manifest.items():
            if sha(z.read('twistronics_v057_reconciled/' + name)) != row['sha256']:
                raise ValueError('archive digest mismatch')
    path.replace(output)
    return dict(path=str(output), files=len(payload), bytes=output.stat().st_size, sha256=sha(output.read_bytes()))


def main(output):
    repo=ROOT.parents[1];baseline=read(ROOT/'BASELINE.json')
    checked=verify_preserved(repo,ROOT/'PRESERVED_TREE.json',baseline['preserved_manifest_sha256'])
    summary=read(ROOT/'SUMMARY.json')
    require(collect(ROOT/summary['test_evidence'])==summary,'publication summary is stale')
    output=Path(output).resolve();require(not output.is_relative_to(repo),'ZIP must be outside repository')
    payload={name:safe(repo,name).read_bytes() for name in read(ROOT/'PRESERVED_TREE.json')['files']}
    payload['README.md']=(repo/'README.md').read_bytes()
    for p in sorted(ROOT.rglob('*')):
        require(not p.is_symlink(),'symlink in batch')
        if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts and p.suffix!='.pyc':payload[p.relative_to(repo).as_posix()]=p.read_bytes()
    payload['START_HERE.md']=(ROOT/'TEAM_SHARE_v057.md').read_bytes()
    payload['TEAM_PACKAGE.json']=(json.dumps(dict(version='our_v057',contract='preserved tracked prior files plus v057 and current README; not byte-identical reconstruction of a prior ZIP',prior_commit=baseline['repository_commit'],preserved_files=checked,preserved_manifest_sha256=baseline['preserved_manifest_sha256'],summary_sha256=sha((ROOT/'SUMMARY.json').read_bytes())),indent=2)+'\n').encode()
    print(json.dumps(write_archive(payload,output),indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);main(p.parse_args().output)
