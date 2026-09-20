"""Bundle the complete prior delivery and v043 evidence into one archive."""
import hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
    summary=json.loads((ROOT/'SUMMARY.json').read_text())
    resume=json.loads((ROOT/'provenance/resume_verification.json').read_text())
    if summary['status']!='ACCEPT' or summary['states']!=160 or resume['status']!='PASS':
        raise ValueError('incomplete acceptance/resume evidence')
    if any(t['labels']!=['OPPOSITE' if t['case']=='pre_ann' else 'SAME'] for t in summary['cases']):
        raise ValueError('valid unexpected label requires a revised package overview')
    output=BASE/'sequence-outputs/twistronics_v043_connections.zip'
    payload={}
    prior=BASE/'sequence-outputs/twistronics_v042_lab_replay.zip'
    if sha(prior.read_bytes())!='97b400892307d23fc6e7f3e9cae575fd5f63256beb9353facf1e7545ea33625a':
        raise ValueError('prior delivery hash changed')
    with zipfile.ZipFile(prior) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            rel=name.split('/',1)[1]
            if '..' in Path(rel).parts or Path(rel).is_absolute():raise ValueError('unsafe prior member')
            payload['prior_v042/'+rel]=z.read(name)
    for f in sorted(ROOT.rglob('*')):
        if not f.is_file() or '__pycache__' in f.parts or '.pytest_cache' in f.parts or f.suffix=='.pyc':continue
        # Probe code/anchors exactly duplicate frozen source; retain its raw
        # numerical output, while the protocol defines the code used for it.
        rel=f.relative_to(ROOT)
        if rel.parts[:2]==('provenance','resume_probe') and len(rel.parts)>2 and rel.parts[2]!='results':continue
        payload['v043/'+str(rel)]=f.read_bytes()
    readme=(
      '# Twistronics v043 — measured connections\n\n'
      'Start with v043/REPORT.md for the new result and v043/TEAM_SHARE_v043.md for the shareable note. '
      'Both connecting routes pass at N=4 and N=6 in both engines with lab_nn_full: 160 accepted states. '
      'The pre-annihilation flat pair stays OPPOSITE; the post-transfer upper pair stays SAME into braid 2. '
      'Endpoint roots match the accepted v042 windows. See the report for finite-sampling and model limits.\n\n'
      'v043/ includes source, frozen protocol, tests, raw records, saved frames, resume verification and a remaining-sequence plan. '
      'prior_v042/ retains the complete previous delivery, including the unchanged v041 partner package and prior work. '
      'Older kinetic conventions retain their original labels; they are not silently treated as new lab_nn_full results.\n\n'
      'The three-person workflow remains implementation, independent review and gated replay, coordinated through a shared record. '
      'No physical-bilayer validation or completed full campaign is claimed.\n'
    )
    payload['README.md']=readme.encode()
    manifest=dict(version='v043',prior_archive_sha256=sha(prior.read_bytes()),
                  files={name:dict(bytes=len(data),sha256=sha(data)) for name,data in sorted(payload.items())})
    payload['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(payload.items()):z.writestr('twistronics_v043_connections/'+name,data)
    with zipfile.ZipFile(output) as z:
        bad=z.testzip()
        if bad:raise ValueError('ZIP integrity failure: '+bad)
        for name,record in manifest['files'].items():
            if sha(z.read('twistronics_v043_connections/'+name))!=record['sha256']:raise ValueError('member hash mismatch')
    print(json.dumps(dict(path=str(output),files=len(payload),bytes=output.stat().st_size,sha256=sha(output.read_bytes())),indent=2))

if __name__=='__main__':main()
