"""Preserve the incoming archive and full prior delivery in one v048 ZIP."""
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    s=json.loads((ROOT/'SUMMARY.json').read_text())
    if s['status']!='ACCEPT' or s['fold_windows']!=8 or s['gapped_states']!=32:raise ValueError('incomplete measured batch')
    prior=BASE/'sequence-outputs/twistronics_v046_reconciled.zip';incoming=BASE/'upload/twistronics_v023-v047.zip'
    if sha(prior.read_bytes())!='d32ec40df72d1eb67fb9a80caa478aa98fa6ee7f05931dd92cf29c90b29e8cbe':raise ValueError('prior delivery changed')
    if sha(incoming.read_bytes())!='18217505087fe95e88c7bfaec8188c1e1364bc3876b1b70642851c1bd4077fa5':raise ValueError('incoming archive changed')
    payload={}
    with zipfile.ZipFile(prior) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name.split('/',1)[1]
            if Path(rel).is_absolute() or '..' in Path(rel).parts:raise ValueError('unsafe prior member')
            payload['prior_our_v046/'+rel]=z.read(name)
    for prefix,folder in [('incoming_v047',BASE/'team-v047'),('v048',ROOT)]:
        for f in sorted(folder.rglob('*')):
            if not f.is_file() or '__pycache__' in f.parts or '.pytest_cache' in f.parts or f.suffix=='.pyc':continue
            payload[prefix+'/'+str(f.relative_to(folder))]=f.read_bytes()
    with zipfile.ZipFile(incoming) as z:
        for i in z.infolist():
            if not i.is_dir() and payload['incoming_v047/'+i.filename]!=z.read(i):raise ValueError('incoming member altered')
    payload['README.md']=b'# Twistronics v048\n\nStart with v048/REPORT.md, v048/LEDGER.md and v048/TEAM_SHARE_v048.md. The layered review is v048/SOURCE_REVIEW.md.\n\nThis batch measures eight late fold windows and 32 sampled gapped states, with joins to the bridge and endpoint. Preparation and the separate lower unlink collision remain open. Numerical results are self-tested, not physical-bilayer validation. Recipient consumption is unconfirmed.\n\nincoming_v047/ preserves the upload unchanged. prior_our_v046/ preserves the complete previous delivery; its v046 is different from the partner v046 in incoming_v047/. v048/ contains the new code, protocols, records, ledger, findings and optional input patch.\n'
    manifest=dict(version='v048',incoming_sha256=sha(incoming.read_bytes()),prior_sha256=sha(prior.read_bytes()),files={n:dict(bytes=len(d),sha256=sha(d)) for n,d in sorted(payload.items())})
    payload['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    dest=BASE/'sequence-outputs/twistronics_v048_reconciled.zip';tmp=dest.with_suffix('.tmp.zip')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,d in sorted(payload.items()):z.writestr('twistronics_v048_reconciled/'+n,d)
    with zipfile.ZipFile(tmp) as z:
        if z.testzip():raise ValueError('archive CRC error')
        for n,r in manifest['files'].items():
            if sha(z.read('twistronics_v048_reconciled/'+n))!=r['sha256']:raise ValueError('archive digest error')
    tmp.replace(dest);r=dict(path=str(dest),files=len(payload),bytes=dest.stat().st_size,sha256=sha(dest.read_bytes()))
    (BASE/'sequence-outputs/v048_archive.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
