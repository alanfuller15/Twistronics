from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from evidence import read,sha
from reconcile import validate_case
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('engine',['bm_lab','ref_lab'])
def test_fresh_event_reconciles(engine):
    r=validate_case(read(ROOT/'results'/f'lower_unlink_{engine}_N8.json'),engine,read(ROOT/'NUMERICAL_PLAN.json'),sha(ROOT/'NUMERICAL_PLAN.json'))
    assert r['root_states']==11 and len(r['charges'])==2 and len(r['openings'])==2

@pytest.mark.parametrize('fault',['status','cutoff','state','plan','geometry','runtime','fold_success','fold_gap','fold_rank','fold_isolation','character','missing_state','root_gap','root_jump','law','charge_label','loop_mesh','loop_winding','transport_gap','radius','missing_open','open_value','open_optimizer','open_grid','open_edge','open_gradient'])
def test_corrupt_event_cannot_publish(fault):
    c=read(ROOT/'results/lower_unlink_bm_lab_N8.json');p=read(ROOT/'NUMERICAL_PLAN.json')
    if fault=='status':c['status']='REJECT'
    elif fault=='cutoff':c['N']=6
    elif fault=='state':c['state']['B']=0
    elif fault=='plan':c['numerical_plan_sha256']='changed'
    elif fault=='geometry':c['geometry']='exact'
    elif fault=='runtime':c['runtime_after']['python']='changed'
    elif fault=='fold_success':c['event']['fold_trials'][-1]['success']=False
    elif fault=='fold_gap':c['event']['fold_trials'][-1]['gap']=.1
    elif fault=='fold_rank':c['event']['fold_trials'][-1]['singular_values'][-1]=2.
    elif fault=='fold_isolation':c['event']['fold_trials'][-1]['external_gap']=0.
    elif fault=='character':c['nondegeneracy']['trials'][0]['curvature']=0.
    elif fault=='missing_state':c['states'].pop()
    elif fault=='root_gap':c['states'][0]['nodes'][0]['gap']=.1
    elif fault=='root_jump':c['states'][0]['max_jump']=1.
    elif fault=='law':c['states'][-1]['separation_law']['observed_to_predicted_ratio']=2.
    elif fault=='charge_label':c['charges'][0]['measurement']['label']='SAME'
    elif fault=='loop_mesh':c['charges'][0]['measurement']['trials'][0]['points']=16
    elif fault=='loop_winding':c['charges'][0]['measurement']['trials'][0]['a']['winding']=.5
    elif fault=='transport_gap':c['charges'][0]['measurement']['spatial_transport'][0]['min_external_gap']=0.
    elif fault=='radius':c['charges'][0]['measurement']['trials'][-1]['radius']*=2
    elif fault=='missing_open':c['open_checks'].pop()
    elif fault=='open_value':c['open_checks'][0]['gap']+=.01
    elif fault=='open_optimizer':c['open_checks'][0]['trials'][0]['refinements'][0]['attempts'][-1]['success']=False
    elif fault=='open_grid':c['open_checks'][0]['trials'][0]['grid_values'][0][0]=-1.
    elif fault=='open_edge':c['open_checks'][0]['trials'][0]['boundary']['edges'].pop()
    else:c['open_checks'][0]['trials'][0]['refinements'][0]['gradient']=[1e6,1e6]
    with pytest.raises(ValueError):validate_case(c,'bm_lab',p,sha(ROOT/'NUMERICAL_PLAN.json'))
