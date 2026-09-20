"""Preserve both v043 contributions and add the reconciled v044 evidence."""
import hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    result=json.loads((ROOT/'SUMMARY.json').read_text())
    if result['status']!='ACCEPT' or result['primary_states']!=148:raise ValueError('incomplete result')
    payload={};prior=BASE/'sequence-outputs/twistronics_v043_connections.zip'
    if sha(prior.read_bytes())!='9d9fcc20e55766770847997d6edf805308ca6afd37e31a4c2233e1666312e256':raise ValueError('prior package changed')
    with zipfile.ZipFile(prior) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name.split('/',1)[1]
            if '..' in Path(rel).parts or Path(rel).is_absolute():raise ValueError('unsafe prior member')
            payload['prior_our_v043/'+rel]=z.read(name)
    for prefix,root in [('team_v043',BASE/'team-v043'),('v044',ROOT)]:
        for f in sorted(root.rglob('*')):
            if not f.is_file() or '__pycache__' in f.parts or '.pytest_cache' in f.parts or f.suffix=='.pyc':continue
            payload[prefix+'/'+str(f.relative_to(root))]=f.read_bytes()
    payload['README.md']=(
      '# Twistronics v044 — reconciled record\n\n'
      'Read v044/REPORT.md for the measured result, v044/SOURCE_REVIEW.md for the incoming toolkit review, '
      'and v044/TEAM_SHARE_v044.md for the shareable note.\n\n'
      'All 148 primary early-route states pass in both engines at N=4/6, joining our v043 connections. '
      'The first-braid crossing is near B=-0.29017 under lab_nn_full. Exact-geometry root controls agree to roundoff. '
      'A separate cutoff-padding counterexample qualifies the assertion that only estimators differ; '
      'an optional tested patch makes padding explicit without changing historical defaults.\n\n'
      'team_v043/ is the unchanged newly uploaded partner package. prior_our_v043/ preserves the complete '
      'previous delivery, including v042 and older material. These are two different v043 contributions. '
      'v044/ contains source, frozen protocol, raw committed records/frames, comparisons, tests and fixes.\n\n'
      'The primary engines remain unchanged and retain their individual geometry and cutoff choices. '
      'No completed full campaign, infinite-cutoff bound or physical-bilayer validation is claimed.\n'
    ).encode()
    manifest=dict(version='v044',prior_our_v043_sha256=sha(prior.read_bytes()),
                  incoming_team_v043_sha256=sha((BASE/'upload/twistronics_v023-v043.zip').read_bytes()),
                  files={name:dict(bytes=len(data),sha256=sha(data)) for name,data in sorted(payload.items())})
    payload['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    output=BASE/'sequence-outputs/twistronics_v044_reconciled.zip'
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(payload.items()):z.writestr('twistronics_v044_reconciled/'+name,data)
    with zipfile.ZipFile(output) as z:
        if z.testzip():raise ValueError('archive checksum failure')
        for name,record in manifest['files'].items():
            if sha(z.read('twistronics_v044_reconciled/'+name))!=record['sha256']:raise ValueError('archive member changed')
    print(json.dumps(dict(path=str(output),files=len(payload),bytes=output.stat().st_size,sha256=sha(output.read_bytes())),indent=2))

if __name__=='__main__':main()
