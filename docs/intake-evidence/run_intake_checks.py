"""Execution-readiness receipt for the bounded v078p record checker.

Runs exactly two record-only checks with the unchanged reviewer checker
(research/benchmarks/migration_contract_review/check_records.py) and its
trusted CONTRACT_EXPECTATIONS.json:

  intact       retained positive RUN from partner_v078p.zip, no mutation
  wrong_label  same RUN after contract_probes.mutate(..., 'wrong_label'),
               which flips the first SAME label and refreshes RUN/MANIFEST.json

Each check extracts the archive into its own fresh temporary directory through
review_inputs.extract, which verifies the archive hash and every member. No
numerical consumer, replay, partner verifier or sweep is run.

Each invocation writes a new directory runs/<UTC timestamp>/ and refuses to
reuse an existing one, so earlier receipts are retained as history and a
stale checker_result.json can never stand in for the current subprocess.
Success requires, per check, the expected exit code, a well-formed current
result and the expected outcome: the intact run accepted with no errors, and
wrong_label refused for exactly the intended label error.
"""
import datetime
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REVIEW=Path(__file__).resolve().parents[2]/'research/benchmarks/migration_contract_review'
HERE=Path(__file__).resolve().parent
TRUSTED_ARCHIVE_SHA256='d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e'
ENV=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
BOUND=['partner_v078p.zip','INPUT_MANIFEST.json','CONTRACT_EXPECTATIONS.json','check_records.py','contract_probes.py','review_inputs.py']
EXPECTED={
    'intact':dict(returncode=0,accepted=True,errors=[]),
    'wrong_label':dict(returncode=1,accepted=False,errors=['label from winding product B-0.25_v+1_r0.012']),
}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(REVIEW.parents[2]).as_posix()

def load_result(path):
    """Read the current subprocess's checker JSON; refuse missing or malformed output."""
    path=Path(path)
    if not path.is_file():raise ValueError('missing checker output '+path.name)
    r=json.loads(path.read_text())
    if not (isinstance(r,dict) and type(r.get('accepted')) is bool and type(r.get('checks')) is int
            and isinstance(r.get('errors'),list) and all(isinstance(e,str) for e in r['errors'])):
        raise ValueError('malformed checker output '+path.name)
    return r

def evaluate(results):
    """Compare each check with its exact expected exit code and outcome."""
    outcome={}
    for name,want in EXPECTED.items():
        got=next((r for r in results if r.get('check')==name),None)
        if got is None:outcome[name]=dict(as_expected=False,reasons=['check missing']);continue
        reasons=[]
        if got.get('output_error'):reasons.append(got['output_error'])
        if got.get('returncode')!=want['returncode']:reasons.append(f"returncode {got.get('returncode')} != {want['returncode']}")
        if got.get('accepted') is not want['accepted']:reasons.append(f"accepted {got.get('accepted')} != {want['accepted']}")
        if got.get('errors')!=want['errors']:reasons.append(f"errors {got.get('errors')} != {want['errors']}")
        if not (isinstance(got.get('checks'),int) and got['checks']>0):reasons.append('no checks performed')
        outcome[name]=dict(expected=want,returncode=got.get('returncode'),accepted=got.get('accepted'),as_expected=not reasons,reasons=reasons)
    return outcome

def check(name,tmp,out):
    from review_inputs import extract
    from contract_probes import mutate
    work=extract(tmp/name)
    dest=out/name;dest.mkdir()
    note,refreshed='No mutation',False
    changed=[]
    if name!='intact':
        before={f:(work/'RUN'/f).read_text() for f in ['ROWS.jsonl','MANIFEST.json']}
        note,refreshed=mutate(work/'RUN',name)
        for f,old in before.items():
            new=(work/'RUN'/f).read_text()
            if new!=old:
                (dest/(f+'.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),'a/RUN/'+f,'b/RUN/'+f)))
                changed.append(dict(file='RUN/'+f,sha256_before=hashlib.sha256(old.encode()).hexdigest(),sha256_after=sha(work/'RUN'/f),diff=f'{name}/{f}.diff'))
    result_path=dest/'checker_result.json'
    cmd=[sys.executable,str(REVIEW/'check_records.py'),str(work/'RUN'),str(work),str(result_path)]
    p=subprocess.run(cmd,cwd=REVIEW,env=ENV,capture_output=True,timeout=600)
    (dest/'checker.log').write_bytes(b'$ python check_records.py <fresh>/RUN <fresh> '+f'{name}/checker_result.json'.encode()+b'\n'+p.stdout+p.stderr+f'[returncode {p.returncode}]\n'.encode())
    record=dict(check=name,mutation=note,manifest_refreshed=refreshed,changed_files=changed,
                command='python check_records.py <fresh extraction>/RUN <fresh extraction> '+f'{name}/checker_result.json',
                returncode=p.returncode)
    try:
        r=load_result(result_path)
        record.update(accepted=r['accepted'],checks=r['checks'],errors=r['errors'])
    except ValueError as e:
        record.update(accepted=None,checks=None,errors=None,output_error=str(e))
    return record

def main():
    import numpy
    sys.path.insert(0,str(REVIEW))
    run_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out=HERE/'runs'/run_id;out.mkdir(parents=True)  # refuses an existing run directory
    before={f:sha(REVIEW/f) for f in BOUND}
    assert before['partner_v078p.zip']==TRUSTED_ARCHIVE_SHA256,'archive hash mismatch'
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=REVIEW,capture_output=True,text=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix='v078-intake-') as tmp:
        results=[check(n,Path(tmp),out) for n in EXPECTED]
    after={f:sha(REVIEW/f) for f in BOUND}
    outcome=evaluate(results)
    ok=all(v['as_expected'] for v in outcome.values()) and before==after
    receipt=dict(
        purpose='Execution-readiness check of the existing bounded record checker. Not a new scientific result and not a closure of the partner verifier defect.',
        run_id=run_id,
        baseline=dict(branch='migration-contract-review',commit='44dc66951057a995ee0999c785aca3e0e6c67092'),
        repository_head_when_run=head,
        runner_sha256=sha(__file__),
        runtime=dict(python=sys.version.split()[0],numpy=numpy.__version__,recorded_review_runtime='python 3.12.14, numpy 2.3.5 (RUNTIME.json)'),
        trusted_archive_sha256=TRUSTED_ARCHIVE_SHA256,
        bound_file_sha256={rel(REVIEW/f):h for f,h in before.items()},
        originals_unchanged=before==after,
        checks=results,
        outcome=outcome,
        runner_returncode=0 if ok else 1,
        not_run=['numerical consumer','full replay','partner verify_migration.py','other contract_probes mutations','sweeps','implementation repairs'])
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(f'receipt runs/{run_id}/RECEIPT.json')
    print(json.dumps({k:dict(as_expected=v['as_expected'],reasons=v['reasons']) for k,v in outcome.items()},indent=2))
    return receipt['runner_returncode']

if __name__=='__main__':raise SystemExit(main())
