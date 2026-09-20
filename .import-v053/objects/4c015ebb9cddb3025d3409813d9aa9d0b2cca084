import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from models import State,make
from measure import Sample,Rejected
from independent_measurement import phase_winding

@pytest.mark.parametrize('engine',['bm_lab','ref_lab'])
def test_gate_rejects_nonisolated_band(engine):
    s=Sample(engine,4,State(A=0,B=0,T=0,eps=0,ratio=.8))
    with pytest.raises(Rejected,match='isolation'):s.frame([0,0],3,1)

@pytest.mark.parametrize('engine',['bm_lab','ref_lab'])
def test_actual_model_breaking_mass_is_rejected(engine):
    m=make(engine,3,State());static=m.model.Hstat if engine=='bm_lab' else m.model.Hs
    static[0,0]+=.1;static[1,1]-=.1
    with pytest.raises(Rejected,match='C2zT'):m.real_hamiltonian([.2,.3])

def test_invalid_uploaded_projection_returns_none():
    m=make('ref_lab',3,State(A=0,B=0,T=0,phi=0,ratio=.8)).model
    u=m.real_basis();node=np.array([.755,.608]);lo=m.dim//2-1
    # Valid orthonormal eigenframe of the wrong, remote subspace: projection
    # onto the target subspace is singular/poor, regardless of winding.
    remote=m.real_frame(u,m.k(node),lo-3)
    q=m.node_charge(u,node,lo,remote,r=.001,npts=12)
    assert q is None and m.last_smin<.9

def test_unresolved_loop_is_rejected_before_label():
    angles=np.linspace(0,2*np.pi,4)
    with pytest.raises(Rejected,match='phase steps'):phase_winding(np.column_stack([np.cos(angles),np.sin(angles)]))

def test_coincident_uploaded_pair_rejected():
    m=make('ref_lab',3,State()).model
    with pytest.raises(ValueError,match='coincident'):m.relative_charge(None,np.array([.2,.3]),np.array([.2,.3]),m.dim//2-1)
