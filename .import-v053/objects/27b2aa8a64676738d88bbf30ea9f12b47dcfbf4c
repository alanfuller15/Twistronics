"""Single package: unchanged incoming v045, preserved v044 and new v046 evidence."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sha=lambda data:hashlib.sha256(data).hexdigest()

def main():
    s=json.loads((ROOT/'SUMMARY.json').read_text())
    if s['status']!='ACCEPT' or s['cleanup_states']!=68 or s['upper_fold_windows']!=4:raise ValueError('incomplete batch')
    incoming=BASE/'upload/twistronics_v023-v045.zip';prior=BASE/'sequence-outputs/twistronics_v044_reconciled.zip'
    if sha(incoming.read_bytes())!='cc22853d630eec758be15bd4e09145ddb2945661b332f959d2bba9590483b411':raise ValueError('incoming archive changed')
    if sha(prior.read_bytes())!='a5bf60427f6e6cfbadc7323ecc325604e458d2a006c7244460e48e38a9bf0442':raise ValueError('prior delivery changed')
    payload={}
    with zipfile.ZipFile(prior) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name.split('/',1)[1]
            if '..' in Path(rel).parts or Path(rel).is_absolute():raise ValueError('unsafe prior path')
            payload['prior_our_v044/'+rel]=z.read(name)
    for prefix,root in [('incoming_v045',BASE/'team-v045'),('v046',ROOT)]:
        for f in sorted(root.rglob('*')):
            if not f.is_file() or '__pycache__' in f.parts or '.pytest_cache' in f.parts or f.suffix=='.pyc' or any(x.startswith('pending_') for x in f.parts):continue
            payload[prefix+'/'+str(f.relative_to(root))]=f.read_bytes()
    # Every uploaded file must survive byte for byte in the incoming subtree.
    with zipfile.ZipFile(incoming) as z:
        for info in z.infolist():
            if not info.is_dir():
                if payload['incoming_v045/'+info.filename]!=z.read(info):raise ValueError('incoming member changed: '+info.filename)
    payload['README.md']=(
      '# Twistronics v046\n\n'
      'Start with v046/REPORT.md and v046/TEAM_SHARE_v046.md. The layered review, ranked actions and findings table are in v046/SOURCE_REVIEW.md.\n\n'
      'This batch measures 68 cleanup states and four upper-annihilation windows in both engines at N4/N6, '
      'then checks the v045 local endpoint and sampled tunneling claims. All passing numerical evidence is self-tested; '
      'the broader physical and global-convergence claims remain explicitly limited.\n\n'
      'incoming_v045/ is the unchanged uploaded package. prior_our_v044/ preserves the complete previous delivery. '
      'v046/ contains the new code, protocols, raw frame checkpoints, numerical results, source review and optional finite-input patch. '
      'No entire-campaign completion or physical-bilayer validation is claimed. See the v046 README for reproduction and recipient-side acceptance.\n'
    ).encode()
    manifest=dict(version='v046',incoming_v045_sha256=sha(incoming.read_bytes()),prior_v044_sha256=sha(prior.read_bytes()),files={name:dict(bytes=len(data),sha256=sha(data)) for name,data in sorted(payload.items())})
    payload['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    output=BASE/'sequence-outputs/twistronics_v046_reconciled.zip';temp=output.with_suffix('.tmp.zip')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(payload.items()):z.writestr('twistronics_v046_reconciled/'+name,data)
    with zipfile.ZipFile(temp) as z:
        if z.testzip():raise ValueError('archive CRC error')
        for name,record in manifest['files'].items():
            if sha(z.read('twistronics_v046_reconciled/'+name))!=record['sha256']:raise ValueError('archive digest error: '+name)
    temp.replace(output)
    result=dict(path=str(output),files=len(payload),bytes=output.stat().st_size,sha256=sha(output.read_bytes()))
    (BASE/'sequence-outputs/v046_archive.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
