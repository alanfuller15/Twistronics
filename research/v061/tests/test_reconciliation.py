from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from evidence import read,sha
from reconcile import validate_case,load_case
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('engine',['bm_lab','ref_lab'])
def test_fresh_event_reconciles(engine):
    r=validate_case(load_case(engine),engine,read(ROOT/'NUMERICAL_PLAN.json'),sha(ROOT/'NUMERICAL_PLAN.json'))
    assert r['root_states']==11 and len(r['charges'])==2 and len(r['openings'])==2 and r['post_transfer']['label']=='SAME'

@pytest.mark.parametrize('fault',['status','cutoff','state','plan','geometry','runtime','fold_success','fold_gap','fold_rank','fold_isolation','character','missing_state','root_gap','root_jump','law','charge_label','loop_mesh','loop_winding','transport_gap','radius','missing_open','open_value','open_optimizer','open_grid','open_edge','open_gradient','post_missing','post_label','post_index','post_T','post_seed','post_loop','spatial_optimizer'])
def test_corrupt_event_cannot_publish(fault):
    c=load_case('bm_lab');p=read(ROOT/'NUMERICAL_PLAN.json')
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
    elif fault=='open_gradient':
        q=c['open_checks'][0]['trials'][0]['refinements'][0];q['gradient']=[1e6 if x>0 else -1e6 for x in q['f']]
    elif fault=='post_missing':c.pop('post_transfer')
    elif fault=='post_label':c['post_transfer']['measurement']['label']='OPPOSITE'
    elif fault=='post_index':c['post_transfer']['index']=3
    elif fault=='post_T':c['post_transfer']['T']=-.7
    elif fault=='post_seed':c['post_transfer']['measurement']['nodes'][0]['seed'][0]=.1
    elif fault=='post_loop':c['post_transfer']['measurement']['trials'][0]['a']['charge']=0
    else:c['charges'][0]['measurement']['spatial_transport'][0]['located_gap_minima'].append(dict(gap_index=2,success=False,status=1,valid=False,nfev=200))
    with pytest.raises(ValueError):validate_case(c,'bm_lab',p,sha(ROOT/'NUMERICAL_PLAN.json'))
