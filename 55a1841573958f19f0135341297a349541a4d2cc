from pathlib import Path
import copy,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from evidence import read,sha
from reconcile import validate_case
ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('engine',['bm_lab','ref_lab'])
def test_fresh_case_evidence_reconciles(engine):
    case=read(ROOT/'results'/f'{engine}_N8.json');p=read(ROOT/'NUMERICAL_PLAN.json')
    result=validate_case(case,engine,p,sha(ROOT/'NUMERICAL_PLAN.json'))
    assert len(result['gaps'])==4 and result['refinements']>0

@pytest.mark.parametrize('fault',['rejected','wrong_cutoff','wrong_state','wrong_geometry','wrong_plan','runtime_change','bad_residual','missing_gap','missing_trial','grid_tamper','missing_edge','failed_final','stale_value','large_gradient','bad_curvature','wrong_summary'])
def test_corrupted_measurements_cannot_be_published(fault):
    case=read(ROOT/'results/bm_lab_N8.json');p=read(ROOT/'NUMERICAL_PLAN.json');trial=case['gaps']['lower']['trials'][0];r=trial['refinements'][0]
    if fault=='rejected':case['status']='REJECT'
    elif fault=='wrong_cutoff':case['N']=6
    elif fault=='wrong_state':case['state']['T']=-1.7
    elif fault=='wrong_geometry':case['geometry']='exact'
    elif fault=='wrong_plan':case['numerical_plan_sha256']='changed'
    elif fault=='runtime_change':case['runtime_after']['python']='changed'
    elif fault=='bad_residual':case['diagnostics']['max_eigen_residual']=1.
    elif fault=='missing_gap':case['gaps'].pop('next')
    elif fault=='missing_trial':case['gaps']['lower']['trials'].pop()
    elif fault=='grid_tamper':trial['grid_values'][0][0]=-1.
    elif fault=='missing_edge':trial['boundary']['edges'].pop()
    elif fault=='failed_final':r['attempts'][-1]['success']=False
    elif fault=='stale_value':r['gap']+=.01
    elif fault=='large_gradient':r['gradient']=[1e6,1e6]
    elif fault=='bad_curvature':trial['curvature'][0]['eigenvalues'][0]=-1.
    else:case['gaps']['lower']['gap']+=.01
    with pytest.raises(ValueError):validate_case(case,'bm_lab',p,sha(ROOT/'NUMERICAL_PLAN.json'))
