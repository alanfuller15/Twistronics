"""Check the revised public helper against already accepted N4 minima."""
import json,time
from pathlib import Path
from models import TBG
ROOT=Path(__file__).resolve().parent

def run():
    prior=json.loads((ROOT/'provenance/v040_summary.json').read_text())
    current=json.loads((ROOT/'results/endpoint_ref_lab_N4.json').read_text())
    target={'full':prior['cutoffs']['4']['endpoint_gaps']['lower'],
            'lab_nn_full':min(q['minimum']['gap'] for q in current['gaps']['lower'])}
    rows=[]
    for kinetic in ['full','lab_nn_full']:
        m=TBG(N=4,eps=.003,phi=80,A=-.30,B=-.4,Bt=-1.8,w0=121.,kinetic=kinetic)
        for n,keep in [(18,4),(15,3)]:
            value=float(m.gap_min(1,n=n,keep=keep));rows.append(dict(kinetic=kinetic,N=4,grid=n,keep=keep,
             helper_gap=value,accepted_gap=target[kinetic],difference=value-target[kinetic]))
    return dict(scope='N4 recorded endpoint lower gap, two public-helper configurations; not a global completeness proof',rows=rows)

if __name__=='__main__':
    start=time.time();r=run();r['seconds']=time.time()-start
    (ROOT/'results/gap_helper_check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
