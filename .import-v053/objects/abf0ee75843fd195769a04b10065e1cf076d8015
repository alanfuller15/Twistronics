"""Frozen, resumable numerical sequence. No subprocesses or network calls.

Use at most two primary processes, each with OPENBLAS_NUM_THREADS=1.
Each job is saved before moving to the next; failures stop the sequence.
"""
import argparse,json,time,hashlib
from pathlib import Path
from models import State
from measure import Sample,GAPS,require
from replay_second import run as braid,save
from replay_events_refined import run as event,locate,CASES
from fold_character import check as fold_check
from check_gapped import cycle
from boundary_audit import seeds

ROOT=Path(__file__).resolve().parent

def checkpoint(engine,N,which,path):
    p=State(A=-.35 if which=='bridge' else -.30,T=-1.8,ratio=1.04 if which=='bridge' else 1.1)
    from dataclasses import asdict
    s=Sample(engine,N,p);r=dict(engine=engine,N=N,which=which,state=asdict(p),status='RUNNING',gaps={},cycles={})
    for name,index in {**GAPS,'outer_lower':1}.items():
        # Explicit edges and opposite-seam seeds, from the outset. Fine search
        # includes all coarse refined basins and their seam counterparts.
        coarse=s.minimum(index,18,extra=seeds([]))
        fine=s.minimum(index,24,extra=seeds([coarse]))
        require(abs(coarse['minimum']['gap']-fine['minimum']['gap'])<.01,'gap grid refinement '+name)
        require(min(t['minimum']['gap'] for t in [coarse,fine])>1e-5,'unresolved gap '+name)
        r['gaps'][name]=[coarse,fine];save(path,r)
        print(engine,N,which,name,fine['minimum']['gap'],flush=True)
    for name,index,nb in [('lower_remote',2,1),('flat1',3,1),('flat2',4,1),('upper_remote',5,1),('flat_pair',3,2)]:
        rows=[]
        for axis in [0,1]:
            for offset in [0.,.5]:
                trials=[cycle(s,index,nb,axis,offset,n) for n in [64,128]]
                require(trials[0]['sign']==trials[1]['sign'],'cycle mesh refinement')
                rows.append(dict(axis=axis,offset=offset,trials=trials))
        for axis in [0,1]:require(len({q['trials'][-1]['sign'] for q in rows if q['axis']==axis})==1,'cycle offset disagreement')
        r['cycles'][name]=rows;save(path,r)
    r['status']='ACCEPT';r['diagnostics']=s.metrics;return r

def post_transfer(engine,N,path):
    from dataclasses import asdict
    p=State(A=0,B=-.4,T=-.74,phi=65,ratio=.8);s=Sample(engine,N,p)
    pair=s.pair([[.590,.691],[.521,.964]],4,r=.004)
    # The measured label is reported; a changed valid label is not a failed
    # numerical measurement merely because it differs from the older model.
    return dict(status='ACCEPT',engine=engine,N=N,state=asdict(p),pair=pair,diagnostics=s.metrics)

def run(engine,N):
    plan=json.loads((ROOT/'PLAN.json').read_text())
    for name,digest in plan['source_sha256'].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'source changed after plan: '+name)
    tasks=[('second',lambda p:braid(engine,N,p)),
           ('first_ann',lambda p:event(engine,N,'first_ann',p)),
           ('bridge',lambda p:checkpoint(engine,N,'bridge',p)),
           ('endpoint',lambda p:checkpoint(engine,N,'endpoint',p)),
           ('post_transfer',lambda p:post_transfer(engine,N,p))]
    for name,fn in tasks:
        path=ROOT/'results'/f'{name}_{engine}_N{N}.json'
        if path.exists() and json.loads(path.read_text()).get('status')=='ACCEPT':continue
        start=time.time()
        try:
            r=fn(path)
            if name=='first_ann':r['nondegeneracy']=fold_check(engine,N,name,r)
        except Exception as error:
            r=json.loads(path.read_text()) if path.exists() else dict(engine=engine,N=N,case=name)
            r.update(status='REJECTED',error=type(error).__name__+': '+str(error))
            r['seconds']=time.time()-start;save(path,r);raise
        r['seconds']=time.time()-start;save(path,r)
        print('FINAL',name,engine,N,r['status'],r['seconds'],flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['bm_lab','ref_lab'],default='ref_lab');ap.add_argument('--N',type=int,choices=[4,6],required=True);a=ap.parse_args();run(a.engine,a.N)
