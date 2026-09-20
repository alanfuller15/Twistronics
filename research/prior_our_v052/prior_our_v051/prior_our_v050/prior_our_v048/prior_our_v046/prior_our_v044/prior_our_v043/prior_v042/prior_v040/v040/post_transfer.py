"""Check the remaining v029 U-pair checkpoint through the existing gate."""
import argparse,json,time
from pathlib import Path
from dataclasses import asdict
from models import State
from measure import Sample,require
from replay_second import save

def run(N):
    p=State(A=0,B=-.4,T=-.74,phi=65,ratio=.8)
    s=Sample('v039_full',N,p)
    pair=s.pair([[.590,.691],[.521,.964]],4,r=.004)
    require(pair['label']=='SAME','post-transfer U-pair label')
    return dict(status='ACCEPT',engine='v039_full',N=N,state=asdict(p),pair=pair,diagnostics=s.metrics,
                limit='Checkpoint only; connecting strain/transfer leg not traced.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--N',type=int,choices=[4,6],required=True);a=ap.parse_args()
    path=Path(__file__).resolve().parent/'results'/f'post_transfer_N{a.N}.json';start=time.time()
    try:r=run(a.N)
    except Exception as e:r=dict(status='REJECTED',N=a.N,error=type(e).__name__+': '+str(e))
    r['seconds']=time.time()-start;save(path,r);print(r['status'],a.N,r.get('error'),flush=True)
    raise SystemExit(int(r['status']!='ACCEPT'))
