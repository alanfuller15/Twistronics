"""Synthetic regressions for the intake runner's pass/fail logic.

No checker, archive extraction or numerical code runs here: evaluate() and
load_result() are exercised with fabricated check records only.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_intake_checks as R

LABEL_ERROR='label from winding product B-0.25_v+1_r0.012'
def rec(name,rc,accepted,errors,checks=51050,**kw):return dict(check=name,returncode=rc,accepted=accepted,errors=errors,checks=checks,**kw)
def good():return [rec('intact',0,True,[]),rec('wrong_label',1,False,[LABEL_ERROR])]
def passed(results):return all(v['as_expected'] for v in R.evaluate(results).values())

class Evaluate(unittest.TestCase):
    def test_expected_outcomes_pass(self):
        self.assertTrue(passed(good()))
    def test_swapped_returncodes_fail(self):
        r=good();r[0]['returncode'],r[1]['returncode']=1,0
        self.assertFalse(passed(r))
    def test_wrong_refusal_reason_fails(self):
        r=good();r[1]['errors']=['required files']
        self.assertFalse(passed(r))
    def test_extra_refusal_reason_fails(self):
        r=good();r[1]['errors']=[LABEL_ERROR,'required files']
        self.assertFalse(passed(r))
    def test_intact_with_errors_fails(self):
        r=good();r[0]['errors']=['file hash ROWS.jsonl']
        self.assertFalse(passed(r))
    def test_missing_check_fails(self):
        self.assertFalse(passed(good()[:1]))
    def test_output_error_fails(self):
        r=good();r[0].update(accepted=None,checks=None,errors=None,output_error='missing checker output checker_result.json')
        self.assertFalse(passed(r))
    def test_zero_checks_fails(self):
        r=good();r[0]['checks']=0
        self.assertFalse(passed(r))

class LoadResult(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)/'checker_result.json'
    def tearDown(self):self.tmp.cleanup()
    def test_missing_output_refused(self):
        with self.assertRaises(ValueError):R.load_result(self.p)
    def test_malformed_json_refused(self):
        self.p.write_text('{not json')
        with self.assertRaises(ValueError):R.load_result(self.p)
    def test_wrong_schema_refused(self):
        for bad in [[],{'accepted':'true','checks':1,'errors':[]},{'accepted':True,'checks':1.0,'errors':[]},{'accepted':True,'checks':1,'errors':'x'},{'accepted':True,'checks':1}]:
            self.p.write_text(json.dumps(bad))
            with self.assertRaises(ValueError,msg=bad):R.load_result(self.p)
    def test_well_formed_accepted(self):
        self.p.write_text(json.dumps(dict(accepted=False,checks=3,errors=[LABEL_ERROR],metrics=[])))
        self.assertEqual(R.load_result(self.p)['errors'],[LABEL_ERROR])

if __name__=='__main__':unittest.main(verbosity=2)
