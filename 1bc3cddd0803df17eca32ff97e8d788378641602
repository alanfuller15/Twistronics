from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
import fold_character

class NormalForm:
    power=2
    slope=-1
    def __init__(self,engine,N,p):self.p=p
    def frame(self,f,index):return np.zeros(2),np.eye(2)
    def vector(self,f,anchor,index):
        x,y=np.asarray(f)-[.65,.6]
        return np.array([x**self.power+self.slope*(self.p.T+.3),2*y]),1.

def run(monkeypatch,cls):
    monkeypatch.setattr(fold_character,'Sample',cls)
    return fold_character.check('bm_lab',4,'lower_unlink',{'event':{'parameter':-.3,'f':[.65,.6]}})

def test_analytic_fold_curvature_slope_and_pair_side(monkeypatch):
    r=run(monkeypatch,NormalForm)
    for t in r['trials']:
        assert abs(t['curvature'])==pytest.approx(2.)
        assert abs(t['parameter_slope'])==pytest.approx(1.)
        assert t['squared_separation_coefficient']==pytest.approx(4.)

def test_rank_one_but_quartic_contact_is_rejected(monkeypatch):
    class Quartic(NormalForm):power=4
    with pytest.raises(ValueError,match='nondegenerate'):run(monkeypatch,Quartic)

def test_pair_on_wrong_parameter_side_is_rejected(monkeypatch):
    class WrongSide(NormalForm):slope=1
    with pytest.raises(ValueError,match='wrong side'):run(monkeypatch,WrongSide)
