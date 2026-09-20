from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from lower_acceptance import validate
from protocol import frozen_protocol
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/prep_lower_birth_bm_lab_N4.json'

def test_complete_measured_lower_window_is_publishable():
    assert validate(SOURCE,frozen_protocol())['status']=='ACCEPT'

@pytest.mark.parametrize('fault',['scope','index','charge','join','side','mesh','zero','protocol'])
def test_incomplete_or_mistagged_lower_event_rejected(tmp_path,fault):
    r=json.loads(SOURCE.read_text())
    if fault=='scope':r['scope']='FULL_CHART_FLAT_GAP_SEARCH'
    elif fault=='index':r['states'][0]['nodes'][0]['index']=3
    elif fault=='charge':r['charges'].pop()
    elif fault=='join':r['v044_lower_root_join']['max_distance']=.01
    elif fault=='side':r['open_checks'][0]['B']=-.25
    elif fault=='mesh':r['open_checks'][0]['trials'].pop()
    elif fault=='zero':r['open_checks'][0]['trials'][0]['minimum']['gap']=0.
    elif fault=='protocol':r['protocol_sha256']='wrong'
    p=tmp_path/'bad.json';p.write_text(json.dumps(r))
    with pytest.raises(ValueError):validate(p,frozen_protocol())
