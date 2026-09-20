from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from local_acceptance import validate
from protocol import frozen_protocol
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/extra_flat_birth_bm_lab_N4.json'

def test_measured_n4_record_passes():
    assert validate(SOURCE,frozen_protocol())['status']=='ACCEPT'

@pytest.mark.parametrize('fault',['status','scope','missing_boundary','original_inside','open_zero','wrong_box','missing_charge','protocol'])
def test_corrupt_or_incomplete_local_claim_rejected(tmp_path,fault):
    r=json.loads(SOURCE.read_text())
    if fault=='status':r['status']='REJECTED'
    elif fault=='scope':r['scope']='GLOBAL_GAP'
    elif fault=='missing_boundary':r['states'][0]['boundary']['trials'].pop()
    elif fault=='original_inside':r['states'][0]['original_pair']['nodes'][0]['f']=[.5,.56]
    elif fault=='open_zero':r['open_checks'][1]['trials'][0]['minimum']['gap']=0.
    elif fault=='wrong_box':r['open_checks'][1]['trials'][0]['box']=[[0.,1.],[0.,1.]]
    elif fault=='missing_charge':r['charges'].pop()
    elif fault=='protocol':r['protocol_sha256']='changed'
    p=tmp_path/'bad.json';p.write_text(json.dumps(r))
    with pytest.raises(ValueError):validate(p,frozen_protocol())
