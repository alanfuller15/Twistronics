import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from models import make,State
from measure import Sample,Rejected

@pytest.mark.parametrize('engine',['v039_full','lab_nn_full'])
def test_real_adapter_preserves_complex_hamiltonian(engine):
    m=make(engine,3,State());u=m.model.real_basis()
    for f in [[.4,.7],[.6,1.013]]:
        want=u.conj().T@m.model.H(m.model.k(f))@u
        got,d=m.real_hamiltonian(f)
        assert np.max(np.abs(got-want))<1e-10

def test_variants_agree_without_strain():
    a=make('v039_full',3,State(eps=0));b=make('lab_nn_full',3,State(eps=0))
    assert np.max(np.abs(a.real_hamiltonian([.3,.4])[0]-b.real_hamiltonian([.3,.4])[0]))<1e-10

def test_variants_agree_without_rotation():
    # The moire basis collapses at theta=eps=0; retain strain here.
    a=make('v039_full',3,State(theta=0));b=make('lab_nn_full',3,State(theta=0))
    assert np.max(np.abs(a.real_hamiltonian([.3,.4])[0]-b.real_hamiltonian([.3,.4])[0]))<1e-10

def test_explicit_variant_changes_lab_cone_metric():
    from tbg_ref import R
    m=make('v039_full',3,State()).model;e=m.El[0];rot=R(-m.thl[0]);v=np.eye(2)+(1-m.beta)*e
    a=v@rot;b=rot@v
    assert np.max(np.abs(a.T@a-b.T@b))>1e-5

def test_gate_rejects_nonisolated_group():
    s=Sample('v039_full',4,State(eps=0,A=0,B=0,T=0,ratio=.8))
    with pytest.raises(Rejected,match='isolation'):s.frame([0,0],3,1)
