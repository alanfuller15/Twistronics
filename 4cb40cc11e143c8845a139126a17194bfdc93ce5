import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from joins import measure_join

def fixture():
    old={'nodes':{'U1':{'f':[.5,.8]},'U2':{'f':[.4,1.02]}}}
    nodes={k:dict(v) for k,v in old['nodes'].items()}
    a=np.eye(4)[:,:2];arrays={k:a.copy() for k in ['frame_a','frame_b','coarse_a','coarse_b']}
    return old,nodes,[a.copy(),a.copy()],[a.copy(),a.copy()],arrays

def test_join_keeps_temporal_gauge_and_unwrapped_roots():
    args=fixture();r=measure_join(*args,1e-8,1e-7)
    assert r['root_shifts']=={'U1':0.,'U2':0.} and min(r['subspace_overlaps'].values())==1.

@pytest.mark.parametrize('fault',['wrapped','moved','wrong_subspace','reflected_temporal','rotated_temporal','wrong_coarse_subspace'])
def test_join_rejects_wrong_seed_basis_or_gauge(fault):
    old,nodes,raw,aligned,arrays=fixture()
    if fault=='wrapped':nodes['U2']['f']=[.4,.02]
    elif fault=='moved':nodes['U1']['f']=[.5001,.8]
    elif fault=='wrong_subspace':raw[0]=np.eye(4)[:,2:]
    elif fault=='reflected_temporal':aligned[1][:,0]*=-1
    elif fault=='rotated_temporal':aligned[1]*=-1
    else:arrays['coarse_b']=np.eye(4)[:,2:]
    with pytest.raises(ValueError,match='join failed'):measure_join(old,nodes,raw,aligned,arrays,1e-8,1e-7)
