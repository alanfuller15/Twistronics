import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pair_measure as pm
import transport as tr

class PairSample:
    metrics={};cache={}
    def frame(self,*a):return np.zeros(2),np.eye(2)
    def winding(self,*a):return {'charge':1}


def setup_pair(monkeypatch):
    monkeypatch.setitem(sys.modules,'measure',SimpleNamespace(align=lambda q,e:(q,1.)))
    monkeypatch.setattr(pm,'root',lambda s,f,index,box:dict(f=list(f),index=index))
    monkeypatch.setattr(pm,'transport',lambda *a:(np.eye(2),{}))


def measure(sample):return pm.refined_pair(sample,[[.2,.4],[.8,.4]],3,.004,[[0,1],[0,1]])


@pytest.mark.parametrize('radius',[0.,-.01,1.,np.nan])
def test_invalid_radius_rejected(monkeypatch,radius):
    setup_pair(monkeypatch)
    with pytest.raises(ValueError,match='radius'):pm.refined_pair(PairSample(),[[.2,.4],[.8,.4]],3,radius,[[0,1],[0,1]])


def test_spatial_orientation_disagreement_rejects(monkeypatch):
    setup_pair(monkeypatch);frames=iter([np.eye(2),np.diag([1.,-1.])]);monkeypatch.setattr(pm,'transport',lambda *a:(next(frames),{}))
    with pytest.raises(ValueError,match='spatial mesh'):measure(PairSample())


def test_phase_only_retry_uses_declared_meshes(monkeypatch):
    setup_pair(monkeypatch)
    class S(PairSample):
        calls=0
        def winding(self,*a):
            self.calls+=1
            if self.calls==1:raise ValueError('loop phase steps unresolved')
            return {'charge':1}
    r=measure(S());assert [q['points'] for q in r['trials']]==[1024,2048,2048]
    assert len(r['rejected_stages'])==1 and r['rejected_stages'][0]['completed_trials']==[]


@pytest.mark.parametrize('reason',['unresolved loop gap','selected group loses isolation','projection/transport overlap too small'])
def test_other_failure_never_gets_phase_retry(monkeypatch,reason):
    setup_pair(monkeypatch)
    class S(PairSample):
        def winding(self,*a):raise ValueError(reason)
    with pytest.raises(ValueError) as error:measure(S())
    assert str(error.value)==reason and len(error.value.attempts)==1


def test_charge_mismatch_across_mesh_rejects(monkeypatch):
    setup_pair(monkeypatch)
    class S(PairSample):
        def winding(self,center,anchor,index,r,n):return {'charge':-1 if center[0]<.5 and n==512 else 1}
    with pytest.raises(ValueError,match='mesh/radius disagreement'):measure(S())

class PathSample:
    model=SimpleNamespace(real_hamiltonian=lambda f:(np.diag([f[0],2*f[0]]),{}))
    def at(self,f):
        t=f[0];lo=.02+(t-.31)**2;hi=.03+(t-.69)**2
        return np.array([-lo,0.,.1,.1+hi]),np.eye(4)
    def frame(self,f,index):return self.at(f)[0][1:3],np.eye(2)


def test_both_exterior_minima_are_located():
    _,d=tr.transport(PathSample(),[0,0],[1,0],np.eye(2),1,8,[],lambda q,e:(q,1.))
    minima={q['gap_index']:q['gap'] for q in d['located_gap_minima']}
    assert minima[0]==pytest.approx(.02,abs=1e-9) and minima[2]==pytest.approx(.03,abs=1e-9)


def test_failed_spatial_optimizer_is_rejected(monkeypatch):
    monkeypatch.setattr(tr,'minimize_scalar',lambda *a,**k:SimpleNamespace(x=.31,fun=.02,success=False,status=2,message='failed',nfev=200))
    with pytest.raises(ValueError,match='minimum rejected'):tr.transport(PathSample(),[0,0],[1,0],np.eye(2),1,8,[],lambda q,e:(q,1.))
