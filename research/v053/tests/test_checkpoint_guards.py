from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from checkpoints import save_step,load_steps

def test_frame_corruption_is_rejected(tmp_path):
    save_step(tmp_path,0,dict(step=0,protocol_sha256='p'),dict(e1=np.eye(2)))
    with (tmp_path/'step_000/frames.npz').open('ab') as f:f.write(b'bad')
    with pytest.raises(ValueError,match='digest'):load_steps(tmp_path,'p')

def test_missing_checkpoint_is_rejected(tmp_path):
    save_step(tmp_path,1,dict(step=1,protocol_sha256='p'),dict(e1=np.eye(2)))
    with pytest.raises(ValueError,match='noncontiguous'):load_steps(tmp_path,'p')

def test_wrong_protocol_is_rejected(tmp_path):
    save_step(tmp_path,0,dict(step=0,protocol_sha256='old'),dict(e1=np.eye(2)))
    with pytest.raises(ValueError,match='protocol'):load_steps(tmp_path,'new')
