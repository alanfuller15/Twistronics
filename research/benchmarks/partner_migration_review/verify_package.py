"""Check archive integrity and expected review outcomes, not physical validity.

After recomputing a review, use --results-only until generating a new manifest;
the distributed manifest binds the originally retained bytes, including timings.
"""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parent
def load(n): return json.loads((ROOT/n).read_text())

def verify(results_only=False):
    failures=[]
    def check(ok,message):
        if not ok: failures.append(message)
    if not results_only:
        manifest=load('MANIFEST.json')
        for name,rec in manifest['files'].items():
            p=ROOT/name
            check(p.is_file(),'missing '+name)
            if p.is_file(): check(len(p.read_bytes())==rec['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'],'hash/size '+name)
    input_manifest=load('INPUT_MANIFEST.json')
    check(hashlib.sha256((ROOT/'partner_v077p.zip').read_bytes()).hexdigest()==input_manifest['archive_sha256'],'partner archive')
    expected={'REPLAY':0,'CLEAN':0,'TESTS':0,'NEGATIVE':0,'METAMORPHIC':0,'LINT':1,'CONTROL_REJECTED':0,'CONTROL_NO_PAIR':0,'CONTROL_LATE_DISCOVERY_ERROR':1,'CONTROL_METAMORPHIC':0}
    actual=load('EXECUTIONS.json')
    check(len(actual)==len(expected) and {x['name'] for x in actual}==set(expected),'execution inventory')
    for x in actual:
        check(not x['timed_out'] and x['returncode']==expected.get(x['name']),'subprocess '+x['name'])
        for rec in x['generated'].values():
            p=ROOT/rec['file']
            check(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'],'generated '+rec['file'])
    summary=load('SUMMARY.json')
    check(not summary['failed_checks'],'retained reconciliation checks')
    check(len(summary['rows'])==8 and summary['ledger_rows']==16472,'numerical row inventory')
    check('38 passed' in (ROOT/'TESTS.log').read_text(),'helper regression result')
    controls=summary['synthetic_release_controls']
    check(controls['CONTROL_REJECTED']['statuses']==['REJECTED']*8,'all-rejected control')
    check(controls['CONTROL_NO_PAIR']['statuses']==['NO_PAIR']*2,'no-pair control')
    check(not controls['CONTROL_LATE_DISCOVERY_ERROR']['generated'],'late discovery output absence')
    check(controls['CONTROL_METAMORPHIC']['false_relations']==['MR1 strain-angle period 180'],'metamorphic failure control')
    with zipfile.ZipFile(ROOT/'partner_v077p.zip') as z: check(z.testzip() is None,'partner ZIP CRC')
    for error in failures: print('FAIL:',error)
    if failures: raise SystemExit(1)
    print('Review package verified. Expected counterexamples remain unresolved in partner source.')

if __name__=='__main__': verify('--results-only' in sys.argv[1:])
