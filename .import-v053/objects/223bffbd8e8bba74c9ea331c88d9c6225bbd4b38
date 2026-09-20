"""Preserve the full prior delivery and new preparation frame batch in one v053 ZIP."""
import json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def main():
    s=json.loads((ROOT/'SUMMARY.json').read_text())
    if s['status']!='ACCEPT' or s['accepted_states']!=76 or s['charged_states']!=76 or s['parameter_mesh_checks']!=36:raise ValueError('incomplete measured batch')
    prior=BASE/'sequence-outputs/twistronics_v052_reconciled.zip'
    if sha(prior.read_bytes())!='eb16e54c5731341b3de4c166b12331964cd5550ed25a664bc401b89b285c15be':raise ValueError('prior delivery changed')
    payload={}
    with zipfile.ZipFile(prior) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name.split('/',1)[1]
            if Path(rel).is_absolute() or '..' in Path(rel).parts:raise ValueError('unsafe prior member')
            payload['prior_our_v052/'+rel]=z.read(name)
    for prefix,folder in [('v053',ROOT)]:
        for f in sorted(folder.rglob('*')):
            if not f.is_file() or '__pycache__' in f.parts or '.pytest_cache' in f.parts or f.suffix=='.pyc':continue
            payload[prefix+'/'+str(f.relative_to(folder))]=f.read_bytes()
    payload['README.md']=b'# Twistronics: our v053\n\nStart with v053/REPORT.md, v053/LEDGER.md and v053/TEAM_SHARE_v053.md. METHOD.md gives the frozen frame-replay gate; SOURCE_REVIEW.md contains findings and ranked actions.\n\nNew: 76 charge-checked preparation states with fine/coarse parameter frames, four endpoint root/relative-orientation joins into v044, and a production stop/resume check. The separate lower unlink collision remains open.\n\nprior_our_v052/ preserves the complete previous delivery. No new upload was supplied. v053/ contains code, protocols, frame checkpoints and reports. Self-tested; finite sampled evidence, no physical validation. Recipient consumption unconfirmed.\n' 
    manifest=dict(version='v053',prior_sha256=sha(prior.read_bytes()),files={n:dict(bytes=len(d),sha256=sha(d)) for n,d in sorted(payload.items())})
    payload['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    dest=BASE/'sequence-outputs/twistronics_v053_reconciled.zip';tmp=dest.with_suffix('.tmp.zip')
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,d in sorted(payload.items()):z.writestr('twistronics_v053_reconciled/'+n,d)
    with zipfile.ZipFile(tmp) as z:
        if z.testzip():raise ValueError('archive CRC error')
        for n,r in manifest['files'].items():
            if sha(z.read('twistronics_v053_reconciled/'+n))!=r['sha256']:raise ValueError('archive digest error')
    tmp.replace(dest);r=dict(path=str(dest),files=len(payload),bytes=dest.stat().st_size,sha256=sha(dest.read_bytes()))
    (BASE/'sequence-outputs/v053_archive.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
