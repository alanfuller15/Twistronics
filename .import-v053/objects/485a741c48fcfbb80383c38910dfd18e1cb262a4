from pathlib import Path
import sys,importlib.util
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from models import State,make,BM
from measure import Rejected

def fixed():
    spec=importlib.util.spec_from_file_location('fixed',ROOT/'fixes/bm_strain.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m.BM

@pytest.mark.parametrize('value',[float('nan'),float('inf'),-float('inf')])
def test_patch_and_harness_reject_nonfinite_tunneling(value):
    with pytest.raises(ValueError,match='finite'):fixed()(w_kappa=value)
    with pytest.raises(Rejected,match='nonfinite'):make('bm_lab',1,State(w_kappa=value))

@pytest.mark.parametrize('state',[State(w_kappa=1.),State(w_mode='layer1')])
def test_reference_cannot_silently_ignore_unsupported_sensitivity(state):
    with pytest.raises(Rejected,match='lacks tunneling'):make('ref_lab',1,state)

@pytest.mark.parametrize('mode,kappa',[('average',0.),('average',5.),('layer1',5.),('layer1',-5.)])
def test_input_patch_preserves_valid_hamiltonian(mode,kappa):
    kw=dict(N=2,eps=.003,phi_deg=80,A_scalar=-.3,ratio=1.1,kinetic='lab_nn_full',geometry='exact',w_mode=mode,w_kappa=kappa)
    a=BM(**kw);b=fixed()(**kw)
    np.testing.assert_array_equal(a.H(a.frac_to_k([.3,.4])),b.H(b.frac_to_k([.3,.4])))
