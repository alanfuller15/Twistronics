"""Execution-readiness receipt for the bounded v078p record checker.

Runs exactly two record-only checks with the unchanged reviewer checker
(research/benchmarks/migration_contract_review/check_records.py) and its
trusted CONTRACT_EXPECTATIONS.json:

  intact       retained positive RUN from partner_v078p.zip, no mutation
  wrong_label  same RUN after contract_probes.mutate(..., 'wrong_label'),
               which flips the first SAME label and refreshes RUN/MANIFEST.json

Each check extracts the archive into its own fresh temporary directory through
review_inputs.extract, which verifies the archive hash and every member. No
numerical consumer, replay, partner verifier or sweep is run. Only the
receipt, checker outputs and the exact mutation are written to OUT.
"""
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REVIEW=Path(__file__).resolve().parents[2]/'research/benchmarks/migration_contract_review'
OUT=Path(__file__).resolve().parent
TRUSTED_ARCHIVE_SHA256='d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e'
ENV=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
sys.path.insert(0,str(REVIEW))
from review_inputs import extract
from contract_probes import mutate

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(REVIEW.parents[2]).as_posix()
BOUND=['partner_v078p.zip','INPUT_MANIFEST.json','CONTRACT_EXPECTATIONS.json','check_records.py','contract_probes.py','review_inputs.py']

def check(name,tmp):
    work=extract(tmp/name)
    note,refreshed='No mutation',False
    changed=[]
    if name!='intact':
        before={f:(work/'RUN'/f).read_text() for f in ['ROWS.jsonl','MANIFEST.json']}
        note,refreshed=mutate(work/'RUN',name)
        for f,old in before.items():
            new=(work/'RUN'/f).read_text()
            if new!=old:
                diff=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),'a/RUN/'+f,'b/RUN/'+f))
                (OUT/name).mkdir(exist_ok=True);(OUT/name/(f+'.diff')).write_text(diff)
                changed.append(dict(file='RUN/'+f,sha256_before=hashlib.sha256(old.encode()).hexdigest(),sha256_after=sha(work/'RUN'/f),diff=f'{name}/{f}.diff'))
    (OUT/name).mkdir(exist_ok=True)
    cmd=[sys.executable,str(REVIEW/'check_records.py'),str(work/'RUN'),str(work),str(OUT/name/'checker_result.json')]
    p=subprocess.run(cmd,cwd=REVIEW,env=ENV,capture_output=True,timeout=600)
    (OUT/name/'checker.log').write_bytes(b'$ python check_records.py <fresh>/RUN <fresh> '+f'{name}/checker_result.json'.encode()+b'\n'+p.stdout+p.stderr+f'[returncode {p.returncode}]\n'.encode())
    result=json.loads((OUT/name/'checker_result.json').read_text())
    return dict(check=name,mutation=note,manifest_refreshed=refreshed,changed_files=changed,
                command='python check_records.py <fresh extraction>/RUN <fresh extraction> '+f'docs/intake-evidence/{name}/checker_result.json',
                returncode=p.returncode,accepted=result['accepted'],checks=result['checks'],error_count=len(result['errors']),errors=result['errors'][:20])

def main():
    import numpy
    before={f:sha(REVIEW/f) for f in BOUND}
    assert before['partner_v078p.zip']==TRUSTED_ARCHIVE_SHA256,'archive hash mismatch'
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=REVIEW,capture_output=True,text=True).stdout.strip()
    with tempfile.TemporaryDirectory(prefix='v078-intake-') as tmp:
        results=[check(n,Path(tmp)) for n in ['intact','wrong_label']]
    after={f:sha(REVIEW/f) for f in BOUND}
    expected={'intact':True,'wrong_label':False}
    receipt=dict(
        purpose='Execution-readiness check of the existing bounded record checker. Not a new scientific result and not a closure of the partner verifier defect.',
        baseline=dict(branch='migration-contract-review',commit='44dc66951057a995ee0999c785aca3e0e6c67092'),
        repository_head_when_run=head,
        runtime=dict(python=sys.version.split()[0],numpy=numpy.__version__,recorded_review_runtime='python 3.12.14, numpy 2.3.5 (RUNTIME.json)'),
        trusted_archive_sha256=TRUSTED_ARCHIVE_SHA256,
        bound_file_sha256={rel(REVIEW/f):h for f,h in before.items()},
        originals_unchanged=before==after,
        checks=results,
        outcome={r['check']:dict(expected_accepted=expected[r['check']],accepted=r['accepted'],returncode=r['returncode'],as_expected=r['accepted']==expected[r['check']]) for r in results},
        not_run=['numerical consumer','full replay','partner verify_migration.py','other contract_probes mutations','sweeps','implementation repairs'])
    (OUT/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt['outcome'],indent=2))
    return 0 if all(v['as_expected'] for v in receipt['outcome'].values()) and receipt['originals_unchanged'] else 1

if __name__=='__main__':raise SystemExit(main())
