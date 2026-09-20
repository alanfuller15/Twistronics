"""Tests for the optional helper patch; primary engines remain untouched."""
from pathlib import Path
import importlib.util
from types import SimpleNamespace
import numpy as np
import pytest

spec=importlib.util.spec_from_file_location('guard_patch',Path(__file__).resolve().parents[1]/'fixes/tbg_ref.py')
patch=importlib.util.module_from_spec(spec);spec.loader.exec_module(patch)

@pytest.mark.parametrize('r',[-1.,0.,np.nan,np.inf])
def test_invalid_radius_rejected_before_frame_access(r):
    m=object.__new__(patch.TBG)
    with pytest.raises(ValueError,match='positive and finite'):
        m.relative_charge(None,np.array([.1,.1]),np.array([.2,.1]),0,r=r)

def dummy():
    m=object.__new__(patch.TBG);m.gap=lambda i:lambda f:4.+np.sum((np.asarray(f)-[.3,.4])**2)
    return m

@pytest.mark.parametrize('success,value',[(False,4.),(True,np.nan),(True,100.)])
def test_failed_or_untrustworthy_optimizer_cannot_return_gap(monkeypatch,success,value):
    monkeypatch.setattr(patch,'minimize',lambda *a,**k:SimpleNamespace(success=success,fun=value,message='injected'))
    with pytest.raises(RuntimeError,match='refinement'):dummy().gap_min(1,n=3,keep=1)

def test_valid_bounded_search_retains_known_minimum():
    m=dummy();assert abs(m.gap_min(1,n=5,keep=2)-4.)<1e-9
    assert m.gap_min_log and all(q['success'] for q in m.gap_min_log)

@pytest.mark.parametrize('kinetic,expected',[('full',23.03669105510484),('lab_nn_full',23.02919135160227)])
def test_endpoint_seam_minimum_matches_independent_gradient_search(kinetic,expected):
    m=patch.TBG(N=4,eps=.003,phi=80,A=-.30,B=-.4,Bt=-1.8,w0=121.,kinetic=kinetic)
    assert abs(m.gap_min(1,n=15,keep=3)-expected)<1e-6
