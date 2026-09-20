from pathlib import Path
import sys,json,copy,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from models import State
import frame_join
ROOT=Path(__file__).resolve().parents[1]
P=State(A=.2,B=-.25,T=0,phi=0,ratio=.8)
def inputs():
    a=json.loads((ROOT/'anchors/v044_start_bm_lab_N4.json').read_text())
    with np.load(ROOT/'anchors/v044_start_bm_lab_N4.npz',allow_pickle=False) as z:
        frames=[z['e1'].copy(),z['e2'].copy()];lab=z['labels'].copy()
    return [a['nodes']['F1'],a['nodes']['F3']],frames,lab,a['temporal_trials']

def test_identical_endpoint_frames_join():
    args=inputs();r=frame_join.join('bm_lab',4,P,*args,'SAME');assert r['relative_orientation']==1 and r['common_orientation']==1

def test_common_orientation_flip_is_allowed():
    nodes,frames,lab,trials=inputs();frames=[f@np.diag([-1,1]) for f in frames]
    for t in trials:
        for s in ['a','b']:t[s]['charge']*=-1
    r=frame_join.join('bm_lab',4,P,nodes,frames,lab,trials,'SAME');assert r['common_orientation']==-1

def test_one_sided_flip_is_not_a_relative_frame_join():
    nodes,frames,lab,trials=inputs();frames[1]=frames[1]@np.diag([-1,1])
    for t in trials:t['b']['charge']*=-1
    with pytest.raises(ValueError,match='relative'):frame_join.join('bm_lab',4,P,nodes,frames,lab,trials,'SAME')

def test_misreported_charge_is_rejected():
    nodes,frames,lab,trials=inputs();trials[1]['b']['charge']*=-1
    with pytest.raises(ValueError,match='charge'):frame_join.join('bm_lab',4,P,nodes,frames,lab,trials,'SAME')

def test_root_permutation_is_matched_with_frames():
    nodes,frames,lab,trials=inputs()
    for t in trials:t['a'],t['b']=t['b'],t['a']
    r=frame_join.join('bm_lab',4,P,nodes[::-1],frames[::-1],lab,trials,'SAME');assert r['root_join']['permutation']==[1,0]

def test_basis_mismatch_is_rejected():
    nodes,frames,lab,trials=inputs();lab=lab[::-1]
    with pytest.raises(ValueError,match='basis'):frame_join.join('bm_lab',4,P,nodes,frames,lab,trials,'SAME')

def test_incompatible_parameter_state_is_rejected():
    with pytest.raises(ValueError,match='state'):frame_join.join('bm_lab',4,State(A=.19,B=-.25,T=0,phi=0,ratio=.8),*inputs(),'SAME')

def test_anchor_frame_bytes_must_match_record(monkeypatch,tmp_path):
    (tmp_path/'anchors').mkdir()
    for ext in ['json','npz']:shutil.copy2(ROOT/f'anchors/v044_start_bm_lab_N4.{ext}',tmp_path/f'anchors/v044_start_bm_lab_N4.{ext}')
    with (tmp_path/'anchors/v044_start_bm_lab_N4.npz').open('ab') as f:f.write(b'changed')
    args=inputs();monkeypatch.setattr(frame_join,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='digest'):frame_join.join('bm_lab',4,P,*args,'SAME')
