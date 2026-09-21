import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'recovery'))
import search_recovery as s
T=dict(nonworsening=1e-7,value_consistency=1e-8,projected_gradient=1e-4,newton_max_steps=8,newton_jacobian_step=1e-7,newton_trust_radius=.001,newton_line_steps=8,curvature_steps=[1e-6,5e-7],curvature_relative=.001,curvature_symmetry_relative=.001)


def opening(x):
    d=np.asarray(x)-[.6,.8];a=np.array([.984,.178]);a/=np.linalg.norm(a);b=np.array([-a[1],a[0]])
    soft=float(d@a);hard=float(d@b);g0=.00677+2094*soft**2/2;z=211*hard;value=float(np.hypot(g0,z))
    return value,(g0*2094*soft*a+z*211*b)/value


def test_polishing_resolves_stiff_stationarity_without_relaxing_gate():
    x=[.600000002,.800000001];initial=opening(x)[0];r=s.polish(opening,x,initial,T)
    assert r['success'] and r['valid'] and r['projected_gradient']<=1e-4
    assert r['checked_value']<=initial+1e-7 and len(r['polish_steps'])>1
    assert r['f']==pytest.approx([.6,.8],abs=1e-10)


def test_underresolved_curvature_rejected_and_refinement_agrees():
    coarse=[s.curvature(opening,[.6,.8],h) for h in [1e-4,5e-5]]
    with pytest.raises(ValueError):s.curvature_agreement(coarse,dict(T,curvature_steps=[1e-4,5e-5]))
    fine=[s.curvature(opening,[.6,.8],h) for h in T['curvature_steps']]
    checked=s.curvature_agreement(fine,T)
    assert checked['relative_eigenvalue_difference']<.001
    assert fine[-1]['eigenvalues'][0]==pytest.approx(2094,rel=.001)


def test_stationary_saddle_is_not_a_positive_minimum():
    fn=lambda x:(1+x[0]**2-x[1]**2,np.array([2*x[0],-2*x[1]]))
    curves=[s.curvature(fn,[.4,.4],h) for h in T['curvature_steps']]
    with pytest.raises(ValueError,match='positive curvature'):s.curvature_agreement(curves,T)


def test_newton_failure_is_retained():
    fn=lambda x:(1.,np.ones(2));r=s.polish(fn,[.4,.4],1.,T)
    assert not r['success'] and not r['valid'] and r['message']=='singular Newton Jacobian'
    assert r['polish_steps']


def test_newton_stencil_cannot_leave_chart():
    fn=lambda x:(1.,-np.ones(2));r=s.polish(fn,[0.,.5],1.,T)
    assert not r['valid'] and r['message']=='Newton stencil leaves chart'


@pytest.mark.parametrize('fault',['asymmetry','disagreement','missing'])
def test_curvature_resolution_guards(fault):
    rows=[dict(step=h,eigenvalues=[2.,3.],asymmetry=0.) for h in T['curvature_steps']]
    if fault=='asymmetry':rows[0]['asymmetry']=1.
    elif fault=='disagreement':rows[0]['eigenvalues'][0]=1.
    else:rows.pop()
    with pytest.raises(ValueError):s.curvature_agreement(rows,T)


def test_failed_curvature_retains_the_search_evidence(monkeypatch):
    thresholds=dict(T,mesh_gap=.001,positive_gap=1e-5)
    monkeypatch.setattr(s,'curvature',lambda fn,x,h:dict(step=h,eigenvalues=[-1.,2.],asymmetry=0.))
    def fn(x):
        d=np.asarray(x)-[.6,.4];return 1.+float(d@d),2*d
    with pytest.raises(ValueError,match='positive curvature') as error:s.search(fn,4,8,[],thresholds)
    assert error.value.curvature and error.value.completed_refinements and error.value.partial_search['grid']==4


@pytest.mark.parametrize('fault',['recovery_status','initial_status','initial_reason','initial_hash','recovery_plan','runtime'])
def test_incomplete_or_mismatched_recovery_cannot_promote_original(fault):
    from evidence import read,sha
    from reconcile import combine
    root=Path(__file__).resolve().parents[1];a=root/'results/first_ann_bm_lab_N8.json';b=root/'results/opening_recovery_bm_lab_N8.json'
    old=read(a);new=read(b)
    if fault=='recovery_status':new['status']='REJECT'
    elif fault=='initial_status':old['status']='ACCEPT'
    elif fault=='initial_reason':old['failure']['message']='unrelated error'
    elif fault=='initial_hash':new['initial_result_sha256']='wrong'
    elif fault=='recovery_plan':new['recovery_plan_sha256']='wrong'
    else:new['runtime_after']={}
    with pytest.raises(ValueError):combine(old,new,'bm_lab',sha(a),sha(b))


def test_recovery_preserves_original_acceptance_thresholds():
    from evidence import read
    root=Path(__file__).resolve().parents[1];old=read(root/'NUMERICAL_PLAN.json')['thresholds'];new=read(root/'recovery/NUMERICAL_PLAN.json')['thresholds']
    assert all(new[k]==v for k,v in old.items() if k!='curvature_steps')
    assert max(new['curvature_steps'])<min(old['curvature_steps'])
    assert new['curvature_relative']==.001 and new['curvature_symmetry_relative']==.001
