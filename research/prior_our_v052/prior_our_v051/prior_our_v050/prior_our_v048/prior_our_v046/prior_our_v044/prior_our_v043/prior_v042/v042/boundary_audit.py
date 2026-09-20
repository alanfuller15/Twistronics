"""Amendment: seed both sides of finite-cutoff chart seams explicitly.

The first endpoint lower-gap estimate reproduced a constrained x=0 minimum,
missing a slightly lower x~0.991 minimum. Periodic grid-neighbor selection is
insufficient with bounded refinement. Keep the original evidence and recheck
all gapped-state gap minima, including the lower-remote outer gap.
"""
import argparse,json,time
from pathlib import Path
import numpy as np
from models import State
from measure import Sample,require,GAPS
from replay_second import save
ROOT=Path(__file__).resolve().parent

def seeds(prior):
    points=[[x,y] for x in [0.,.5,1.] for y in [0.,.5,1.] if x in [0.,1.] or y in [0.,1.]]
    for trial in prior:
        for row in trial['refinements']:
            f=np.asarray(row['f']);points.append(f.tolist())
            for axis in [0,1]:
                if f[axis]<.1 or f[axis]>.9:
                    q=f.copy();q[axis]=1. if f[axis]<.1 else 0.;points.append(q.tolist())
    return [list(t) for t in sorted(set(tuple(p) for p in points))]

def run(engine,N):
    outer=[]
    for which in ['bridge','endpoint']:
        source=json.loads((ROOT/'results'/f'{which}_{engine}_N{N}.json').read_text());require(source['status']=='ACCEPT','unaccepted gapped state')
        sample=Sample(engine,N,State(**source['state']));r=dict(engine=engine,N=N,which=which,status='RUNNING',gaps={});path=ROOT/'results'/f'boundary_{which}_{engine}_N{N}.json'
        for name,index in {**GAPS,'outer_lower':1}.items():
            prior=source['gaps'].get(name,[]);extra=seeds(prior);trials=[sample.minimum(index,n,extra=extra) for n in [18,24]]
            require(min(t['minimum']['gap'] for t in trials)>1e-5,'boundary audit finds unresolved gap '+name)
            require(abs(trials[0]['minimum']['gap']-trials[1]['minimum']['gap'])<.01,'boundary audit grid refinement '+name)
            old=min((t['minimum']['gap'] for t in prior),default=None);new=min(t['minimum']['gap'] for t in trials)
            if old is not None:require(new<=old+1e-7,'boundary audit worsens best known minimum')
            r['gaps'][name]=dict(trials=trials,old_minimum=old,new_minimum=new,change=None if old is None else new-old,extra_seeds=extra);save(path,r)
            print(engine,N,which,name,new,'change',None if old is None else new-old,flush=True)
        r['status']='ACCEPT';save(path,r);outer.append(dict(which=which,trials=r['gaps']['outer_lower']['trials']))
    save(ROOT/'results'/f'outer_isolation_{engine}_N{N}.json',dict(status='ACCEPT',engine=engine,N=N,rows=outer,source='boundary_audit.py'))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);ap.add_argument('--N',type=int,choices=[4,6],required=True);a=ap.parse_args();run(a.engine,a.N)
