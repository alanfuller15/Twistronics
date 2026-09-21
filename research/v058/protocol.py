"""Freeze current batch sources and the supplied historical tree separately."""
from pathlib import Path
from evidence import read,sha,safe,require
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]

def verify_preserved(repo,manifest,expected):
    require(sha(manifest)==expected,'preserved manifest changed')
    rows=read(manifest)['files']
    for name,r in rows.items():
        p=safe(repo,name)
        require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'preserved file changed: '+name)
    return len(rows)

def frozen_protocol():
    plan=read(ROOT/'PLAN.json');require(plan['version']=='our_v058','wrong batch')
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.rglob('*.py') if '__pycache__' not in p.parts}
    require(sources==plan['source_sha256'],'batch source changed or omitted')
    for name,h in plan['anchor_sha256'].items():require(sha(safe(ROOT,name))==h,'batch input changed')
    baseline=read(ROOT/'BASELINE.json')
    count=verify_preserved(REPO,ROOT/'PRESERVED_TREE.json',baseline['preserved_manifest_sha256'])
    require(count==baseline['preserved_files'],'preserved file count mismatch')
    return sha(ROOT/'PLAN.json')
