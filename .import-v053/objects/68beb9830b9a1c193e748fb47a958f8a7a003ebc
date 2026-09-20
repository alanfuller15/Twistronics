"""Compare a split real numerical pilot with the saved uninterrupted pilot.

One-step run followed by a two-step resume must reproduce the original three
states, every stored frame, and every diagnostic except wall-clock duration.
This is an execution experiment, separate from the seven unit tests.
"""
import json,shutil,time
from pathlib import Path
import numpy as np
import replay
from checkpoints import load_steps,save_json

ROOT=Path(__file__).resolve().parent

def main():
    probe=ROOT/'provenance'/'resume_probe'
    if probe.exists():raise ValueError('preserve existing resume probe rather than overwrite')
    probe.mkdir()
    plan=json.loads((ROOT/'PLAN.json').read_text())
    for name in list(plan['source_sha256'])+list(plan['anchor_sha256'])+['PLAN.json']:
        out=probe/name;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,out)
    replay.ROOT=probe
    first=replay.run('bm_lab',4,'pre_ann',max_new=1)
    second=replay.run('bm_lab',4,'pre_ann',max_new=2)
    protocol=replay.frozen_protocol()
    reference=ROOT/'results'/'pre_ann_bm_lab_N4';split=probe/'results'/'pre_ann_bm_lab_N4'
    ref_rows,_=load_steps(reference,protocol);split_rows,_=load_steps(split,protocol)
    if len(first['states'])!=1 or len(second['states'])!=3:raise ValueError('resume ran wrong number of states')
    comparisons=[]
    for step,got in enumerate(split_rows):
        expected=ref_rows[step]
        strip=lambda x:{k:v for k,v in x.items() if k not in ['seconds','frames_sha256']}
        if strip(expected)!=strip(got):raise ValueError('resumed numerical record differs: '+str(step))
        with np.load(reference/f'step_{step:03d}'/'frames.npz',allow_pickle=False) as a,np.load(split/f'step_{step:03d}'/'frames.npz',allow_pickle=False) as b:
            if set(a.files)!=set(b.files):raise ValueError('frame keys differ')
            for k in a.files:
                if not np.array_equal(a[k],b[k]):raise ValueError('resumed frame differs: '+k)
            comparisons.append(dict(step=step,record_equal_except_time_and_array_container_hash=True,arrays_bitwise_equal=True,array_names=sorted(a.files)))
    result=dict(status='PASS',engine='bm_lab',N=4,case='pre_ann',split_after_step=0,compared_steps=3,protocol_sha256=protocol,comparisons=comparisons)
    save_json(ROOT/'provenance'/'resume_verification.json',result)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
