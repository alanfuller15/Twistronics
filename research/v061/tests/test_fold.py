from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from scipy.optimize import OptimizeResult
import fold


def character_rows(a=2,b=-1):
    return [dict(step=h,curvature=a,parameter_slope=b,squared_separation_coefficient=-8*b/a if a else None) for h in [2e-4,1e-4]]

def test_quadratic_normal_form_has_expected_separation():
    rows=character_rows();fold.require_character(rows,1.)
    for delta in [.004,.001,.00025]:
        r=fold.separation_law(2*np.sqrt(delta),delta,rows[0]['squared_separation_coefficient'],.02)
        assert r['observed_to_predicted_ratio']==pytest.approx(1.)

@pytest.mark.parametrize('fault',['quartic','no_parameter','wrong_side','nan','incomplete','mesh','coefficient'])
def test_degenerate_or_inconsistent_fold_rejected(fault):
    rows=character_rows()
    if fault=='quartic':rows=character_rows(a=0)
    elif fault=='no_parameter':rows=character_rows(b=0)
    elif fault=='wrong_side':rows=character_rows(b=1)
    elif fault=='nan':rows[0]['curvature']=np.nan
    elif fault=='incomplete':rows.pop()
    elif fault=='mesh':rows[1]=character_rows(a=3)[1]
    else:rows[0]['squared_separation_coefficient']=3
    with pytest.raises(ValueError):fold.require_character(rows,1.)

@pytest.mark.parametrize('values',[(0,.001,4),(.1,-.001,4),(.1,.001,-4),(np.nan,.001,4),(.1,.001,4)])
def test_separation_law_rejects_unresolved_or_wrong_scaling(values):
    with pytest.raises(ValueError):fold.separation_law(*values,.02)

class Toy:
    def frame(self,f,index):return np.array([0.,0.]),np.eye(2)
    def vector(self,f,anchor,index):return np.asarray(f)-[.3,.4],1.

def test_root_records_current_optimizer_status(monkeypatch):
    result=OptimizeResult(x=np.array([.3,.4]),fun=np.zeros(2),success=True,status=3,message='current attempt',nfev=7)
    monkeypatch.setattr(fold,'least_squares',lambda *a,**k:result)
    r=fold.root(Toy(),[.31,.41],2,[[0,1],[0,1]])
    assert r['status']==3 and r['message']=='current attempt' and r['nfev']==7

@pytest.mark.parametrize('fault',['failed','nonfinite','unresolved'])
def test_bad_root_attempt_is_retained(monkeypatch,fault):
    result=OptimizeResult(x=np.array([.3,.4]),fun=np.zeros(2),success=True,status=0,message='recorded failure',nfev=7)
    if fault=='failed':result.success=False
    elif fault=='nonfinite':result.fun=np.array([np.nan,0.])
    else:result.fun=np.array([1.,0.])
    monkeypatch.setattr(fold,'least_squares',lambda *a,**k:result)
    with pytest.raises(ValueError) as error:fold.root(Toy(),[.31,.41],2,[[0,1],[0,1]])
    assert error.value.attempts[0]['message']=='recorded failure'
