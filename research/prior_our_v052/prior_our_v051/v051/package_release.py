"""Preserve the full prior delivery and new local event batch in one v051 ZIP."""
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    s=json.loads((ROOT/'SUMMARY.json').read_text())
    if s['status']!='ACCEPT' or s['fold_windows']!=8 or s['root_state_records']!=72 or s['charge_measurements']!=16:raise ValueError('incomplete measured batch')
    prior=BASE/'sequence-outputs/twistronics_v050_reconciled.zip'
    if sha(prior.read_bytes())!='e6a72efe41150db0354f87fc024954fd0cfec084794ac54b0cab9b26b7ead7c4':raise ValueError('prior delivery changed')
    payload={}
    with zipfile.ZipFile(prior) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name.split('/',1)[1]
            if Path(rel).is_absolute() or '..' in Path(rel).parts:raise ValueError('unsafe prior member')
            payload['prior_our_v050/'+rel]=z.read(name)
    for prefix,folder in [('v051',ROOT)]:
        for f in sorted(folder.rglob('*')):
            if not f.is_file() or '__pycache__' in f.parts or '.pytest_cache' in f.parts or f.suffix=='.pyc':continue
            payload[prefix+'/'+str(f.relative_to(folder))]=f.read_bytes()
    payload['README.md']=b'# Twistronics: our v051\n\nStart with v051/REPORT.md, v051/LEDGER.md and v051/TEAM_SHARE_v051.md. METHOD.md describes the separately frozen local-domain gate; SOURCE_REVIEW.md contains findings and ranked actions.\n\nNew: eight local extra-flat-pair preparation windows, 72 root-state records and 16 charge measurements, with original roots retained outside the local domain. Shared-state repeats are counted explicitly. Remaining lower-pair birth, original-pair full preparation/frame join and separate lower unlink collision stay open.\n\nprior_our_v050/ preserves the complete previous delivery including all incoming partner versions. No new upload was supplied for this continuation. v051/ contains code, protocols, records and reports. Self-tested; no physical validation. Recipient consumption unconfirmed.\n' 
    manifest=dict(version='v051',prior_sha256=sha(prior.read_bytes()),files={n:dict(bytes=len(d),sha256=sha(d)) for n,d in sorted(payload.items())})
    payload['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    dest=BASE/'sequence-outputs/twistronics_v051_reconciled.zip';tmp=dest.with_suffix('.tmp.zip')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,d in sorted(payload.items()):z.writestr('twistronics_v051_reconciled/'+n,d)
    with zipfile.ZipFile(tmp) as z:
        if z.testzip():raise ValueError('archive CRC error')
        for n,r in manifest['files'].items():
            if sha(z.read('twistronics_v051_reconciled/'+n))!=r['sha256']:raise ValueError('archive digest error')
    tmp.replace(dest);r=dict(path=str(dest),files=len(payload),bytes=dest.stat().st_size,sha256=sha(dest.read_bytes()))
    (BASE/'sequence-outputs/v051_archive.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
