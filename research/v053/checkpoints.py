"""Commit a complete JSON/array pair by atomically renaming its directory."""
import hashlib,json,tempfile
from pathlib import Path
import numpy as np

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save_step(root,step,row,arrays):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    dest=root/f'step_{step:03d}'
    if dest.exists():raise ValueError('refusing to overwrite committed step')
    stage=Path(tempfile.mkdtemp(prefix='pending_',dir=root))
    np.savez_compressed(stage/'frames.npz',**arrays)
    row=dict(row,frames_sha256=digest(stage/'frames.npz'))
    (stage/'record.json').write_text(json.dumps(row,indent=2,allow_nan=False)+'\n')
    stage.rename(dest)
    return row

def load_steps(root,protocol):
    rows=[];arrays=None
    for step,folder in enumerate(sorted(Path(root).glob('step_*'))):
        if folder.name!=f'step_{step:03d}':raise ValueError('noncontiguous checkpoints')
        row=json.loads((folder/'record.json').read_text())
        if row['protocol_sha256']!=protocol or row['step']!=step:raise ValueError('checkpoint protocol/step mismatch')
        if digest(folder/'frames.npz')!=row['frames_sha256']:raise ValueError('checkpoint array digest mismatch')
        with np.load(folder/'frames.npz',allow_pickle=False) as stored:arrays={k:stored[k].copy() for k in stored.files}
        if not all(np.isfinite(v).all() for v in arrays.values()):raise ValueError('nonfinite checkpoint array')
        rows.append(row)
    return rows,arrays

def save_json(path,value):
    path=Path(path);temp=path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');temp.replace(path)
