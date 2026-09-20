import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from models import State,make
from measure import Rejected,Sample
from basis import carry,labels

def lab(n):return np.array([(0,i,0,0) for i in range(n)])

def test_row_permutation_does_not_change_frame():
    q=np.eye(5)[:,:2];order=[4,1,3,0,2]
    got,d=carry(q,lab(5),q[order]@np.diag([-1,1]),lab(5)[order])
    assert np.allclose(got,q[order]) and d['min_overlap']==1

def test_zero_weight_basis_change_is_safe():
    q=np.eye(5)[:,:2];new=np.vstack([q[:4],np.zeros((2,2))]);nl=np.vstack([lab(4),[[0,8,0,0],[0,9,0,0]]])
    got,d=carry(q,lab(5),new,nl)
    assert np.allclose(got,new) and d['old_norm_loss']==0 and d['removed']==1 and d['added']==2

def test_lost_occupied_basis_is_rejected():
    with pytest.raises(Rejected,match='loses too much'):carry(np.eye(5)[:,:2],lab(5),np.eye(4)[:,:2],lab(5)[1:])

def test_duplicate_basis_is_rejected():
    with pytest.raises(Rejected,match='duplicate'):carry(np.eye(3)[:,:2],lab(3),np.eye(3)[:,:2],np.zeros((3,4),int))

@pytest.mark.parametrize('engine',['bm_lab','ref_lab'])
def test_same_model_embedding_matches_direct_overlap(engine):
    s=Sample(engine,3,State());_,q=s.frame([.3,.4],4);_,v=s.frame([.301,.4],4)
    out,d=carry(q,labels(s.model),v,labels(s.model));u,sv,vh=np.linalg.svd(v.T@q)
    assert np.allclose(out,v@u@vh) and abs(d['min_overlap']-sv.min())<1e-12
