import argparse,json,subprocess,sys
from pathlib import Path
from protocol import frozen_protocol
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);a=p.parse_args();protocol=frozen_protocol()
    for N in [4,6]:
        for case in ['flat_birth','final_ann']:
            path=ROOT/'results'/f'{case}_{a.engine}_N{N}_refined.json'
            if path.exists():
                r=json.loads(path.read_text())
                if r.get('status')=='ACCEPT' and r.get('protocol_sha256')==protocol:continue
            subprocess.run([sys.executable,'replay_events.py','--engine',a.engine,'--N',str(N),'--case',case],check=True,cwd=ROOT)
        subprocess.run([sys.executable,'gapped_legs.py','--engine',a.engine,'--N',str(N)],check=True,cwd=ROOT)
