"""Small retained claim-binding fixtures for the changed v078p linter."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from review_inputs import ROOT,extract

def run():
    results=[]
    with tempfile.TemporaryDirectory(prefix='v078-lint-') as tmp:
        tmp=Path(tmp);source=extract(tmp/'source',True)
        spec=importlib.util.spec_from_file_location('review_partner_lint',source/'claim_lint.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        cases=[
            ('correct_rounding',{'gap_meV':1.5259312e-10},'Node gap 1.53e-10 meV from `REC.json`.\n',True),
            ('correct_four_digits',{'gap_meV':1.5259312e-10},'Node gap 1.526e-10 meV from `REC.json`.\n',True),
            ('stale_third_digit',{'gap_meV':1.5259312e-10},'Node gap 1.61e-10 meV from `REC.json`.\n',False),
            ('wrong_field',{'overlap':.995703,'unrelated':.73},'Measured overlap 0.730 from `REC.json`.\n',False),
            ('incorrect_trailing_zero_precision',{'gap_meV':1.5259312e-10},'Node gap 1.530e-10 meV from `REC.json`.\n',False)]
        for name,data,prose,valid in cases:
            d=tmp/name;d.mkdir();(d/'REC.json').write_text(json.dumps(data));(d/'README.md').write_text(prose)
            flags=module.lint(str(d),[str(d/'README.md')]);accepted=not flags
            results.append(dict(case=name,record=data,prose=prose,valid_claim=valid,linter_accepted=accepted,expected_behavior=accepted==valid,findings=flags))
    (ROOT/'LINT_PROBES.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((source/'claim_lint.py').read_bytes()).hexdigest() if source.exists() else json.loads((ROOT/'SOURCE_COMPARISON.json').read_text())['claim_lint.py']['sha256'],cases=results),indent=2)+'\n')
    for r in results:print(r['case'],'valid',r['valid_claim'],'accepted',r['linter_accepted'])

if __name__=='__main__':run()
