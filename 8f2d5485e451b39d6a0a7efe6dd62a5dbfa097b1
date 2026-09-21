from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from unlink_acceptance import validate
from protocol import frozen_protocol
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/lower_unlink_bm_lab_N4.json'

@pytest.mark.parametrize('engine,N',[(e,n) for e in ['bm_lab','ref_lab'] for n in [4,6]])
def test_measured_event_is_publishable(engine,N):
    assert validate(ROOT/'results'/f'lower_unlink_{engine}_N{N}.json',frozen_protocol())['status']=='ACCEPT'

@pytest.mark.parametrize('fault',['scope','index','charge_count','join','side','mesh','zero_gap','protocol','fold_rank','flat_curvature','wrong_side_slope','duplicate_node','missing_boundary','wrong_charge','unresolved_phase','model'])
def test_corrupt_or_incomplete_event_rejected(tmp_path,fault):
    r=json.loads(SOURCE.read_text())
    if fault=='scope':r['scope']='FULL_CHART_FLAT_GAP_SEARCH'
    elif fault=='index':r['states'][0]['nodes'][0]['index']=3
    elif fault=='charge_count':r['charges'].pop()
    elif fault=='join':r['v044_lower_root_join']['max_distance']=.01
    elif fault=='side':r['open_checks'][0]['T']=0.
    elif fault=='mesh':r['open_checks'][0]['trials'].pop()
    elif fault=='zero_gap':r['open_checks'][0]['trials'][0]['minimum']['gap']=0.
    elif fault=='protocol':r['protocol_sha256']='wrong'
    elif fault=='fold_rank':r['event']['fold_trials'][0]['singular_values'][-1]=1.
    elif fault=='flat_curvature':r['nondegeneracy']['trials'][0]['curvature']=0.
    elif fault=='wrong_side_slope':r['nondegeneracy']['trials'][0]['parameter_slope']*=-1
    elif fault=='duplicate_node':r['states'][1]['nodes'][1]=r['states'][1]['nodes'][0]
    elif fault=='missing_boundary':r['open_checks'][0]['boundary'][0]['edges'].pop()
    elif fault=='wrong_charge':r['charges'][0]['measurement']['trials'][0]['b']['charge']*=-1
    elif fault=='unresolved_phase':r['charges'][0]['measurement']['trials'][0]['a']['max_phase_step']=2.
    elif fault=='model':r['kinetic']='none'
    p=tmp_path/'bad.json';p.write_text(json.dumps(r))
    with pytest.raises(ValueError):validate(p,frozen_protocol())
