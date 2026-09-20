"""Finite sampled, gapped connectors; no continuum/global completeness claim."""
import argparse,json,time,traceback
from dataclasses import replace,asdict
from pathlib import Path
import numpy as np
from models import State
from measure import Sample,require,GAPS
from cycles import cycle
from boundary_audit import seeds
from protocol import frozen_protocol
from checkpoints import save_json
ROOT=Path(__file__).resolve().parent
GROUPS=[('lower_remote',2,1),('flat1',3,1),('flat2',4,1),('upper_remote',5,1),('flat_pair',3,2)]

def accepted(path):
    r=json.loads(path.read_text());require(r['status']=='ACCEPT','unaccepted source: '+str(path));return r

def labels(record):return {name:[int(next(x for x in rows if x['axis']==axis)['trials'][-1]['sign']<0) for axis in [0,1]] for name,rows in record['cycles'].items()}

def schedule(engine,N):
    upper=accepted(ROOT/'anchors'/f'upper_ann_{engine}_N{N}_refined.json')
    birth=accepted(ROOT/'results'/f'flat_birth_{engine}_N{N}_refined.json')
    end=accepted(ROOT/'results'/f'final_ann_{engine}_N{N}_refined.json')
    low=upper['event']['parameter']+.001;high=birth['event']['parameter']-.001
    require(low<1.04<high,'bridge not inside proposed gapped interval')
    ratios=list(np.linspace(low,1.04,3))+list(np.linspace(1.04,high,3))[1:]
    p=State(A=-.35,B=-.4,T=-1.8,phi=80)
    out=[dict(leg='between_folds',state=replace(p,ratio=float(x)),anchor='bridge' if i==2 else None) for i,x in enumerate(ratios)]
    first=end['event']['parameter']+.001
    require(first<-.30,'final fold open side beyond endpoint')
    out += [dict(leg='to_endpoint',state=replace(p,A=float(x),ratio=1.1),anchor='endpoint' if i==2 else None) for i,x in enumerate(np.linspace(first,-.30,3))]
    return out

def run(engine,N):
    protocol=frozen_protocol();grid=schedule(engine,N);folder=ROOT/'results'/f'gapped_{engine}_N{N}';folder.mkdir(exist_ok=True)
    rows=[]
    for step,g in enumerate(grid):
        path=folder/f'state_{step:03d}.json'
        if path.exists():
            old=json.loads(path.read_text())
            require(old['protocol_sha256']==protocol and old['state']==asdict(g['state']),'gapped checkpoint mismatch')
            if old['status']=='ACCEPT':rows.append(old);continue
        tick=time.time();s=Sample(engine,N,g['state']);r=dict(status='RUNNING',engine=engine,N=N,step=step,leg=g['leg'],state=asdict(g['state']),protocol_sha256=protocol,gaps={},cycles={})
        for name,index in {**GAPS,'outer_lower':1}.items():
            trials=[]
            for ng in [18,24]:
                prior=[x['f'] for t in trials for x in t['refinements']]
                trial=s.minimum(index,ng,extra=seeds(s,index,prior));require(trial['minimum']['gap']>1e-5,'gap unresolved: '+name);trials.append(trial)
            require(abs(trials[0]['minimum']['gap']-trials[1]['minimum']['gap'])<.01,'minimum grid disagreement: '+name)
            r['gaps'][name]=trials;save_json(path,r)
        for name,index,nb in GROUPS:
            trials=[]
            for axis in [0,1]:
                for offset in [0.,.5]:
                    ts=[cycle(s,index,nb,axis,offset,n) for n in [64,128]]
                    require(ts[0]['sign']==ts[1]['sign'],'cycle mesh disagreement')
                    trials.append(dict(axis=axis,offset=offset,trials=ts))
            for axis in [0,1]:require(len({t['trials'][-1]['sign'] for t in trials if t['axis']==axis})==1,'cycle offset disagreement')
            r['cycles'][name]=trials;save_json(path,r)
        r['w1']=labels(r)
        if g['anchor']:
            old=accepted(ROOT/'anchors'/f"{g['anchor']}_{engine}_N{N}.json")
            gapdiff={k:min(t['minimum']['gap'] for t in r['gaps'][k])-min(t['minimum']['gap'] for t in old['gaps'][k]) for k in r['gaps']}
            require(max(abs(x) for x in gapdiff.values())<1e-6,'gapped anchor gap changed')
            require(r['w1']==labels(old),'gapped anchor w1 changed')
            r['anchor_join']=dict(name=g['anchor'],gap_differences=gapdiff,w1_agrees=True)
        r.update(status='ACCEPT',diagnostics=s.metrics,seconds=time.time()-tick);save_json(path,r);rows.append(r)
        print(engine,N,g['leg'],step,'PASS','min gap',min(t['minimum']['gap'] for ts in r['gaps'].values() for t in ts),'w1',r['w1'],flush=True)
    out=dict(status='ACCEPT',engine=engine,N=N,states=rows,protocol_sha256=protocol,w1_constant=all(r['w1']==rows[0]['w1'] for r in rows))
    save_json(folder/'summary.json',out)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--engine',required=True);p.add_argument('--N',required=True,type=int);a=p.parse_args()
    try:run(a.engine,a.N)
    except Exception as e:
        save_json(ROOT/'results'/f'gapped_failure_{a.engine}_N{a.N}_{time.time_ns()}.json',dict(status='REJECTED',error=str(e),traceback=traceback.format_exc()));raise
