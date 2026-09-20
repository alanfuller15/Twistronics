from pathlib import Path
import sys,types
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
import local_domain as ld
from measure import Rejected
BOX=[[.4,.6],[.5,.7]]
def quadratic(center,offset=0):
 def fn(f):
  d=np.asarray(f)-center;return float(d@d+offset),2*d
 return fn

def test_outside_zero_does_not_make_local_minimum_zero():
    fn=quadratic([.8,.6]);r=ld.bounded_minimum(fn,BOX,7)
    assert r['minimum']['gap']==pytest.approx(.04,abs=1e-9)
    assert r['minimum']['f']==pytest.approx([.6,.6],abs=1e-5)

def test_interior_zero_cannot_pass_open_side_gate():
    fn=quadratic([.51,.61]);trials=[ld.bounded_minimum(fn,BOX,n) for n in [7,11]]
    with pytest.raises(Rejected,match='unresolved'):ld.require_positive_agreement(trials,'interior')

def test_boundary_zero_is_detected_between_grid_samples():
    fn=quadratic([.4,.6137]);trials=[ld.boundary_minimum(fn,BOX,n) for n in [8,16]]
    assert min(x['minimum'] for x in trials)<1e-14
    with pytest.raises(Rejected,match='unresolved'):ld.require_positive_agreement(trials,'boundary')

def test_external_seed_rejected_not_clipped():
    with pytest.raises(Rejected,match='outside'):ld.bounded_minimum(quadratic([.5,.6]),BOX,5,extra=[[.8,.6]])

def test_failed_or_escaped_optimizer_cannot_pass(monkeypatch):
    monkeypatch.setattr(ld,'minimize',lambda *args,**kw:types.SimpleNamespace(success=True,fun=-1.,x=np.array([.8,.6]),message='escaped'))
    with pytest.raises(Rejected,match='escaped'):ld.bounded_minimum(quadratic([.8,.6]),BOX,5)

@pytest.mark.parametrize('bad',[float('nan'),float('inf')])
def test_nonfinite_grid_rejected(bad):
    with pytest.raises(Rejected,match='nonfinite'):ld.bounded_minimum(lambda f:(bad,np.zeros(2)),BOX,5)

def test_grid_disagreement_rejected():
    with pytest.raises(Rejected,match='disagreement'):ld.require_positive_agreement([dict(minimum=.1),dict(minimum=.2)],'boundary')

def test_bounded_root_does_not_relabel_external_root():
    class FakeSample:
        def frame(self,f,index):return np.array([0.,np.linalg.norm(np.asarray(f)-[.8,.6])]),np.eye(2)
        def vector(self,f,anchor,index):return np.asarray(f)-[.8,.6],1.
    with pytest.raises(Rejected,match='unresolved'):ld.bounded_node(FakeSample(),[.5,.6],3,BOX)

def test_inside_outside_distances_have_distinct_meaning():
    assert ld.inside_margin([.5,.6],BOX)==pytest.approx(.1)
    assert ld.outside_distance([.5,.6],BOX)==0
    assert ld.outside_distance([.8,.6],BOX)==pytest.approx(.2)
