"""Package verified supplied trees; no byte-identical prior ZIP is claimed."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import zipfile
from build_report import collect

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_relative(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError('unsafe manifest member')
    return p


def verify_prior_tree(folder, expected_manifest_sha256):
    folder = Path(folder).resolve()
    manifest = folder / 'MANIFEST.json'
    if sha(manifest.read_bytes()) != expected_manifest_sha256:
        raise ValueError('prior manifest digest mismatch')
    rows = json.loads(manifest.read_text())['files']
    for name, row in rows.items():
        p = folder.joinpath(*safe_relative(name).parts)
        if any(q.is_symlink() for q in (p, *p.parents) if q.is_relative_to(folder)) or not p.resolve().is_relative_to(folder):
            raise ValueError('prior member escapes tree or is a symlink')
        data = p.read_bytes()
        if len(data) != row['bytes'] or sha(data) != row['sha256']:
            raise ValueError('prior file digest/size mismatch: ' + name)
    return len(rows)


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
            entry = zipfile.ZipInfo('twistronics_v055_reconciled/' + name, (2026, 9, 21, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            z.writestr(entry, data)
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('archive CRC error')
        for name, row in manifest.items():
            if sha(z.read('twistronics_v055_reconciled/' + name)) != row['sha256']:
                raise ValueError('archive digest mismatch')
    path.replace(output)
    return dict(path=str(output), files=len(payload), bytes=output.stat().st_size, sha256=sha(output.read_bytes()))


def main(output, prior_tree=None):
    repo = ROOT.parents[1]
    prior = Path(prior_tree).resolve() if prior_tree else ROOT.parent
    baseline = json.loads((ROOT / 'BASELINE.json').read_text())
    checked = verify_prior_tree(prior, baseline['research_manifest_sha256'])
    for name, expected in baseline['v054_files'].items():
        path = ROOT.parent / 'v054' / safe_relative(name)
        if path.is_symlink() or sha(path.read_bytes()) != expected:
            raise ValueError('frozen v054 file changed: ' + name)
    partner_zip = ROOT / 'provenance/incoming_partner_v054.zip'
    if sha(partner_zip.read_bytes()) != baseline['partner_archive_sha256']:
        raise ValueError('incoming partner archive changed')
    with zipfile.ZipFile(partner_zip) as source:
        for item in source.infolist():
            if item.is_dir():
                continue
            member = ROOT.parent / 'incoming_partner_v054' / safe_relative(item.filename)
            if member.is_symlink() or member.read_bytes() != source.read(item):
                raise ValueError('incoming partner member changed: ' + item.filename)
    summary = json.loads((ROOT / 'SUMMARY.json').read_text())
    if collect(ROOT / summary['test_evidence']) != summary:
        raise ValueError('publication summary is stale')
    output = Path(output).resolve()
    if output.is_relative_to(repo):
        raise ValueError('delivery output must be outside the supplied repository tree')
    payload = {}
    for name in ('README.md', 'RELEASE.json'):
        payload[name] = (repo / name).read_bytes()
    for name in ('research', 'audits'):
        for p in sorted((repo / name).rglob('*')):
            if p.is_symlink():
                raise ValueError('symlink in delivery inputs')
            if not p.is_file() or '__pycache__' in p.parts or '.pytest_cache' in p.parts or p.suffix == '.pyc':
                continue
            payload[p.relative_to(repo).as_posix()] = p.read_bytes()
    verify_prior_tree(ROOT.parent, baseline['research_manifest_sha256'])
    payload['START_HERE.md'] = (ROOT / 'TEAM_SHARE_v055.md').read_bytes().replace(b'Start with REPORT.md,', b'Start in research/v055/ with REPORT.md,')
    payload['TEAM_PACKAGE.json'] = (json.dumps(dict(version='our_v055', contract=baseline['packaging_contract'],
        prior_tree_manifest_sha256=baseline['research_manifest_sha256'], prior_files_verified=checked,
        original_prior_zip_reproduced=False, publication_summary_sha256=sha((ROOT / 'SUMMARY.json').read_bytes())), indent=2) + '\n').encode()
    print(json.dumps(write_archive(payload, output), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prior-tree', type=Path, help='Explicit preserved v053 extraction; verified against BASELINE.json')
    args = parser.parse_args()
    main(args.output, args.prior_tree)
