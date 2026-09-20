from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from checkpoints import save_step,load_steps

def test_roundtrip_preserves_fine_and_coarse_frames_and_detects_corruption(tmp_path):
    arrays={'e1':np.eye(4)[:,:2],'c1':np.eye(6)[:,:2],'labels':np.arange(16).reshape(4,4)}
    save_step(tmp_path,0,dict(step=0,protocol_sha256='frozen'),arrays)
    # An incomplete write must not appear as an accepted continuation step.
    (tmp_path/'pending_interruption').mkdir()
    rows,loaded=load_steps(tmp_path,'frozen')
    assert len(rows)==1
    for k in arrays:np.testing.assert_array_equal(loaded[k],arrays[k])
    with pytest.raises(ValueError,match='overwrite'):save_step(tmp_path,0,dict(step=0,protocol_sha256='frozen'),arrays)
    with pytest.raises(ValueError,match='protocol'):load_steps(tmp_path,'changed')
    with (tmp_path/'step_000'/'frames.npz').open('ab') as f:f.write(b'corruption')
    with pytest.raises(ValueError,match='digest'):load_steps(tmp_path,'frozen')
