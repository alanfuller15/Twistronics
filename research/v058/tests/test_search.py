from pathlib import Path
import copy,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from scipy.optimize import OptimizeResult
import search
from evidence import read
T=read(Path(__file__).resolve().parents[1]/'NUMERICAL_PLAN.json')['thresholds']

def quadratic(x):
    d=np.asarray(x)-[.97,.29]
    return 2+float(d@d),2*d

def test_bounded_chart_search_recovers_near_edge_minimum():
    trials=[search.search(quadratic,n,2*n,[],T) for n in [4,8]]
    result=search.acceptance(trials,T)
    assert result['gap']==pytest.approx(2,abs=1e-10)
    assert trials[0]['minimum']['f']==pytest.approx([.97,.29],abs=1e-6)
    assert result['boundary_minimum']==pytest.approx(2+.03**2,abs=1e-9)

@pytest.mark.parametrize('point',[[np.nan,0],[-.1,.5],[.5,1.1],[.3]])
def test_invalid_chart_points_rejected(point):
    with pytest.raises(ValueError):search.checked(quadratic,point)

def test_nonfinite_objective_rejected():
    with pytest.raises(ValueError):search.checked(lambda x:(np.nan,np.zeros(2)),[.5,.5])

def test_projected_gradient_respects_inward_descent():
    assert search.projected_gradient([0,1],[2,-3])==0
    assert search.projected_gradient([0,1],[-2,3])==3

@pytest.mark.parametrize('fault',['failed','nonfinite','escaped','stale_value','not_stationary','worsened'])
def test_failed_first_attempt_preserved_and_final_metadata_used(monkeypatch,fault):
    first=OptimizeResult(x=np.array([.97,.29]),fun=2.,success=True,status=0,message='first',nfev=2,nit=1)
    if fault=='failed':first.success=False;first.status=9
    elif fault=='nonfinite':first.fun=np.nan
    elif fault=='escaped':first.x=np.array([1.1,.29])
    elif fault=='stale_value':first.fun=3.
    elif fault=='not_stationary':first.x=np.array([.8,.29]);first.fun=quadratic(first.x)[0]
    else:first.x=np.array([.1,.1]);first.fun=quadratic(first.x)[0]
    final=OptimizeResult(x=np.array([.97,.29]),fun=2.,success=True,status=0,message='final',nfev=4,nit=3)
    calls=iter([first,final]);monkeypatch.setattr(search,'minimize',lambda *a,**k:next(calls))
    r=search.refine(quadratic,[.95,.27],T)
    assert len(r['attempts'])==2 and not r['attempts'][0]['valid']
    assert r['attempts'][-1]['message']=='final' and r['attempts'][-1]['nfev']==4
    assert r['gap']==2 and r['f']==[.97,.29]

def test_all_failed_attempts_are_retained(monkeypatch):
    bad=OptimizeResult(x=np.array([.97,.29]),fun=2.,success=False,status=9,message='failed',nfev=2,nit=1)
    monkeypatch.setattr(search,'minimize',lambda *a,**k:bad)
    with pytest.raises(ValueError) as error:search.refine(quadratic,[.95,.27],T)
    assert len(error.value.attempts)==3

@pytest.mark.parametrize('fault',['one_mesh','negative','nan','mesh','edge_mesh'])
def test_unresolved_mesh_evidence_rejected(fault):
    trials=[dict(minimum={'gap':2.},boundary={'minimum':2.1}) for _ in range(2)]
    if fault=='one_mesh':trials.pop()
    elif fault=='negative':trials[0]['minimum']['gap']=-1
    elif fault=='nan':trials[0]['minimum']['gap']=np.nan
    elif fault=='mesh':trials[0]['minimum']['gap']=2.01
    else:trials[0]['boundary']['minimum']=2.2
    with pytest.raises(ValueError):search.acceptance(trials,T)

def test_edge_optimizer_failure_is_not_promoted(monkeypatch):
    bad=OptimizeResult(x=.29,fun=2.,success=False,status=1,message='failed',nfev=3)
    monkeypatch.setattr(search,'minimize_scalar',lambda *a,**k:bad)
    with pytest.raises(ValueError) as error:search.edge_search(quadratic,8,T)
    assert error.value.attempts[0]['success'] is False
