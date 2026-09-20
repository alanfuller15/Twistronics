"""One ordered worker per engine; checkpoints commit each cleanup state."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--engine',required=True,choices=['bm_lab','ref_lab']);a=p.parse_args()
    for N in [4,6]:
        for script,case in [('replay.py','cleanup'),('replay_events.py','upper_ann')]:
            subprocess.run([sys.executable,str(ROOT/script),'--engine',a.engine,'--N',str(N),'--case',case],check=True,cwd=ROOT)
