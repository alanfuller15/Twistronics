"""Preserve the full prior delivery and new lower event batch in one v052 ZIP."""
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    s=json.loads((ROOT/'SUMMARY.json').read_text())
    if s['status']!='ACCEPT' or s['fold_windows']!=4 or s['root_state_records']!=36 or s['charge_measurements']!=8:raise ValueError('incomplete measured batch')
    prior=BASE/'sequence-outputs/twistronics_v051_reconciled.zip'
    if sha(prior.read_bytes())!='301c84e6cc762485add457d5c8f714e76654f93e39235b64333c1fdf67d3c6cc':raise ValueError('prior delivery changed')
    payload={}
    with zipfile.ZipFile(prior) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name.split('/',1)[1]
            if Path(rel).is_absolute() or '..' in Path(rel).parts:raise ValueError('unsafe prior member')
            payload['prior_our_v051/'+rel]=z.read(name)
    for prefix,folder in [('v052',ROOT)]:
        for f in sorted(folder.rglob('*')):
            if not f.is_file() or '__pycache__' in f.parts or '.pytest_cache' in f.parts or f.suffix=='.pyc':continue
            payload[prefix+'/'+str(f.relative_to(folder))]=f.read_bytes()
    payload['README.md']=b'# Twistronics: our v052\n\nStart with v052/REPORT.md, v052/LEDGER.md and v052/TEAM_SHARE_v052.md. METHOD.md describes the frozen lower-gap gate; SOURCE_REVIEW.md contains findings and ranked actions.\n\nNew: four preparation lower-pair birth windows, 36 root-state records and eight charge measurements, plus positive full-chart lower-gap searches and momentum joins into v044. Full original-flat-pair preparation/frame replay and the separate lower unlink collision remain open.\n\nprior_our_v051/ preserves the complete previous delivery. No new upload was supplied. v052/ contains code, protocols, records and reports. Self-tested; no physical validation. Recipient consumption unconfirmed.\n' 
    manifest=dict(version='v052',prior_sha256=sha(prior.read_bytes()),files={n:dict(bytes=len(d),sha256=sha(d)) for n,d in sorted(payload.items())})
    payload['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    dest=BASE/'sequence-outputs/twistronics_v052_reconciled.zip';tmp=dest.with_suffix('.tmp.zip')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,d in sorted(payload.items()):z.writestr('twistronics_v052_reconciled/'+n,d)
    with zipfile.ZipFile(tmp) as z:
        if z.testzip():raise ValueError('archive CRC error')
        for n,r in manifest['files'].items():
            if sha(z.read('twistronics_v052_reconciled/'+n))!=r['sha256']:raise ValueError('archive digest error')
    tmp.replace(dest);r=dict(path=str(dest),files=len(payload),bytes=dest.stat().st_size,sha256=sha(dest.read_bytes()))
    (BASE/'sequence-outputs/v052_archive.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
