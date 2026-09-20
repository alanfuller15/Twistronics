"""Preserve the incoming archive and full prior delivery in one v050 ZIP."""
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    s=json.loads((ROOT/'SUMMARY.json').read_text())
    if s['status']!='ACCEPT' or s['fold_windows']!=4 or s['root_states']!=36 or s['charge_stations']!=8:raise ValueError('incomplete measured batch')
    prior=BASE/'sequence-outputs/twistronics_v048_reconciled.zip';incoming=BASE/'upload/twistronics_v023-v049.zip'
    if sha(prior.read_bytes())!='e1f2159c21b6677a00b2e71998f80776771b8874d4de96b6268ef6309e17b3d6':raise ValueError('prior delivery changed')
    if sha(incoming.read_bytes())!='341d4d9f6d179ee3ed1679b509d3f6bce2d75bd2e21a9b6dcf91b2998298bfc3':raise ValueError('incoming archive changed')
    payload={}
    with zipfile.ZipFile(prior) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name.split('/',1)[1]
            if Path(rel).is_absolute() or '..' in Path(rel).parts:raise ValueError('unsafe prior member')
            payload['prior_our_v048/'+rel]=z.read(name)
    for prefix,folder in [('incoming_v049',BASE/'team-v049'),('v050',ROOT)]:
        for f in sorted(folder.rglob('*')):
            if not f.is_file() or '__pycache__' in f.parts or '.pytest_cache' in f.parts or f.suffix=='.pyc':continue
            payload[prefix+'/'+str(f.relative_to(folder))]=f.read_bytes()
    with zipfile.ZipFile(incoming) as z:
        for i in z.infolist():
            if not i.is_dir() and payload['incoming_v049/'+i.filename]!=z.read(i):raise ValueError('incoming member altered')
    payload['README.md']=b'# Twistronics v050\n\nStart with v050/REPORT.md, v050/LEDGER.md and v050/TEAM_SHARE_v050.md. SOURCE_REVIEW.md contains the layered findings and ranked actions.\n\nNew: four preparation upper-pair birth windows, 36 root states and eight charge stations; correction of a missing late root and misdescribed residual. Remaining preparation and the separate lower unlink collision are open.\n\nincoming_v049/ preserves the upload unchanged. prior_our_v048/ preserves our complete earlier delivery, distinct from the partner v048 in incoming_v049/. v050/ contains the new code, frozen protocol, records, reports and optional logging patch. Self-tested; no physical-bilayer validation. Recipient consumption unconfirmed.\n' 
    manifest=dict(version='v050',incoming_sha256=sha(incoming.read_bytes()),prior_sha256=sha(prior.read_bytes()),files={n:dict(bytes=len(d),sha256=sha(d)) for n,d in sorted(payload.items())})
    payload['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    dest=BASE/'sequence-outputs/twistronics_v050_reconciled.zip';tmp=dest.with_suffix('.tmp.zip')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,d in sorted(payload.items()):z.writestr('twistronics_v050_reconciled/'+n,d)
    with zipfile.ZipFile(tmp) as z:
        if z.testzip():raise ValueError('archive CRC error')
        for n,r in manifest['files'].items():
            if sha(z.read('twistronics_v050_reconciled/'+n))!=r['sha256']:raise ValueError('archive digest error')
    tmp.replace(dest);r=dict(path=str(dest),files=len(payload),bytes=dest.stat().st_size,sha256=sha(dest.read_bytes()))
    (BASE/'sequence-outputs/v050_archive.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
