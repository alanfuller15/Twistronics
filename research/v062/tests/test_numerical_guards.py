import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numerics
import transport as tr
from run_window import charges

class Cone:
    def frame(self,f,index):return np.array([0.,np.linalg.norm(np.array(f)-[.4,1.02])]),np.eye(2)
    def vector(self,f,anchor,index):return np.array(f)-[.4,1.02],1.


def test_unwrapped_root_is_preserved():
    r=numerics.root(Cone(),[.39,1.01],4,[[0,1],[0,1.1]])
    assert r['success'] and np.allclose(r['f'],[.4,1.02]) and r['f'][1]>1


@pytest.mark.parametrize('fault',['failed','nonfinite','outside','residual'])
def test_invalid_final_root_rejected(monkeypatch,fault):
    sol=SimpleNamespace(success=fault!='failed',status=1,message='fixture',nfev=3,x=np.array([.4,1.02]),fun=np.zeros(2))
    if fault=='nonfinite':sol.x[0]=np.nan
    if fault=='outside':sol.x[1]=1.2
    if fault=='residual':sol.fun[0]=1e-3
    monkeypatch.setattr(numerics,'least_squares',lambda *a,**k:sol)
    with pytest.raises(ValueError,match='root optimizer') as error:numerics.root(Cone(),[.4,1.01],4,[[0,1],[0,1.1]])
    assert error.value.attempts[0]['success']==sol.success


def test_crossing_tolerance_agreement():
    r=numerics.crossing(lambda x:x-.99077,[.9905,.991],[1e-10,5e-12])
    assert abs(r['ratio']-.99077)<1e-12 and all(t['converged'] for t in r['trials'])


def test_unbracketed_crossing_rejected():
    with pytest.raises(ValueError,match='not bracketed'):numerics.crossing(lambda x:x*x+1,[-1,1],[1e-10,5e-12])


def test_failed_crossing_does_not_return_a_root(monkeypatch):
    monkeypatch.setattr(numerics,'brentq',lambda *a,**k:(.5,SimpleNamespace(converged=False,iterations=100,function_calls=102,flag='failed')))
    with pytest.raises(ValueError,match='unresolved'):numerics.crossing(lambda x:x-.5,[0,1],[1e-10,5e-12])


@pytest.mark.parametrize('reason',['eigen residual','projection/transport overlap too small',None])
def test_unrelated_error_is_not_isolation_evidence(reason):
    class S:
        def frame(self,*args):
            if reason:raise ValueError(reason)
    with pytest.raises(ValueError):numerics.require_isolation_rejection(S(),[0,0],4)


def test_explicit_isolation_failure_is_retained():
    class S:
        def frame(self,*args):raise ValueError('selected group loses isolation')
    assert numerics.require_isolation_rejection(S(),[0,0],4)=='selected group loses isolation'

class PathSample:
    model=SimpleNamespace(real_hamiltonian=lambda f:(np.diag([f[0],2*f[0]]),{}))
    def at(self,f):
        t=f[0];lo=.02+(t-.31)**2;hi=.03+(t-.69)**2
        return np.array([-lo,0.,.1,.1+hi]),np.eye(4)
    def frame(self,f,index):return self.at(f)[0][1:3],np.eye(2)


def test_both_exterior_minima_located():
    _,d=tr.transport(PathSample(),[0,0],[1,0],np.eye(2),1,8,[[.31,.001],[.69,.001]],lambda q,e:(q,1.))
    mins={q['gap_index']:q['gap'] for q in d['located_gap_minima']}
    assert mins[0]==pytest.approx(.02,abs=1e-9) and mins[2]==pytest.approx(.03,abs=1e-9)


def test_failed_exterior_minimizer_is_rejected(monkeypatch):
    monkeypatch.setattr(tr,'minimize_scalar',lambda *a,**k:SimpleNamespace(x=.31,fun=.02,success=False,status=2,message='fixture fail',nfev=200))
    with pytest.raises(ValueError,match='minimum rejected'):tr.transport(PathSample(),[0,0],[1,0],np.eye(2),1,8,[],lambda q,e:(q,1.))


def test_wrong_rectangle_cannot_certify_spatial_charge():
    class S:
        def winding(self,*a):return {'charge':1}
    with pytest.raises(ValueError,match='rectangle'):charges(S(),[0,0],[1,0],None,None,None,.006,-1)


def test_only_phase_resolution_allows_retry():
    class S:
        def winding(self,*a):raise ValueError('unresolved loop gap')
    with pytest.raises(ValueError,match='unresolved loop gap') as error:charges(S(),[0,0],[1,0],None,None,None,.006,1)
    assert len(error.value.attempts)==1
