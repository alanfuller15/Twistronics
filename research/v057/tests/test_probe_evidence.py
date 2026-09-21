from pathlib import Path
import sys,copy,ast
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
import numpy as np
import probe_evidence as pe
from evidence import read,sha
from run_probe import definitions


def fixture():
    return read(pe.ROOT/'results/probe_N4.json'),read(pe.ROOT/'NUMERICAL_PLAN.json'),sha(pe.ROOT/'NUMERICAL_PLAN.json')


def test_complete_probe_has_observed_second_attempts():
    r,p,h=fixture();v=pe.validate(r,p,h)
    assert v['variants'][0]['second_attempt_calls']>0
    assert all(x['node_candidates']>len(x['resolved_nodes']) for x in v['variants'])
    assert not v['comparison_changed']


@pytest.mark.parametrize('fault',['status','identity','cutoff','runtime','variant','stage','model','value','stale','missing_attempt','failed_optimizer','seed','best','detached'])
def test_incomplete_or_inconsistent_measurements_rejected(fault):
    r,p,h=fixture();v=r['variants'][1];call=v['refine_calls'][0]
    if fault=='status':r['status']='RUNNING'
    elif fault=='identity':r['plan_sha256']='bad'
    elif fault=='cutoff':r['N']=8
    elif fault=='runtime':r['runtime_after']['python']='different'
    elif fault=='variant':r['variants'].reverse()
    elif fault=='stage':v['baseline_nodes']['status']='REJECTED'
    elif fault=='model':v['baseline_model_sha256']='different'
    elif fault=='value':call['recomputed_value']=1
    elif fault=='stale':call['metadata']['status']=3
    elif fault=='missing_attempt':call['attempts']=[]
    elif fault=='failed_optimizer':call['attempts'][-1]['success']=False;call['metadata']['optimizer_success']=False
    elif fault=='seed':v['endpoint_lower']['value']['grids'][0]['seeds']=[]
    elif fault=='best':v['endpoint_lower']['value']['best']['value']=999
    else:v['baseline_nodes']['value'][0][1]=[.5,.5]
    with pytest.raises(ValueError):pe.validate(r,p,h)


@pytest.mark.parametrize('fault',['missing_mesh','mesh','rejected','orientation','determinant','gap','overlap','seam','norm','phase','residual','refine_call'])
def test_raw_euler_number_cannot_override_failed_gates(fault):
    r,p,h=fixture();e=r['euler'];m=e['gated'][0]['value']['measurement']
    if fault=='missing_mesh':e['gated'].pop()
    elif fault=='mesh':e['gated'][0]['value']['mesh']=[12,12]
    elif fault=='rejected':e['gated'][0]['status']='REJECTED'
    elif fault=='orientation':m['k1_cycle']['sign']=-1
    elif fault=='determinant':m['loop_determinants'][0]=-1
    elif fault=='gap':m['min_external_gap']=0
    elif fault=='overlap':m['min_overlap']=0
    elif fault=='seam':m['min_seam_overlap']=0
    elif fault=='norm':m['k1_cycle']['seam_norm_error']=.5
    elif fault=='phase':m['phases'][1]+=3
    elif fault=='residual':e['gated'][0]['value']['metrics']['eigen_relative_residual']=1
    else:e['refine_calls']=[{'unexpected':True}]
    with pytest.raises(ValueError):pe.validate(r,p,h)


def test_retained_euler_gate_rejects_nonorientable_cycle_before_frame_use():
    _,plan,_=fixture();ns={'np':np};path=pe.REPO/plan['paths']['gate']
    definitions(path,['GateError','require','euler_measurement'],ns)
    class Nonorientable:
        def cycle(self,*args):return {'sign':-1}
        def frame(self,*args):pytest.fail('frames reached after failed orientability')
    with pytest.raises(ValueError,match='nonorientable'):
        ns['euler_measurement'](Nonorientable(),1,24,40,None,None)


def test_nonfinite_is_not_a_number():
    for x in [float('nan'),float('inf'),{'nonfinite':'nan'},True]:
        with pytest.raises(ValueError):pe.numeric(x)
