"""Full sampled gap inventory and gated cycle signs at specified states."""
import argparse,json,time
from pathlib import Path
from dataclasses import asdict
import numpy as np
from models import State
from measure import Sample,align,require,GAPS
from replay_second import save
ROOT=Path(__file__).resolve().parent

def cycle(sample,index,nb,axis,offset,n):
    first=None;previous=None;overlap=1.;gap=1e100
    for t in np.linspace(0,1,n+1):
        f=[t,offset] if axis==0 else [offset,t];w,_=sample.at(f)
        _,q=sample.frame(f,index,nb)
        gap=min(gap,float(min(w[index]-w[index-1],w[index+nb]-w[index+nb-1])))
        if first is None:first=q;previous=q
        else:previous,s=align(q,previous);overlap=min(overlap,s)
    sewn=sample.model.sewing(axis)@first;norm=float(np.max(np.abs(sewn.T@sewn-np.eye(nb))))
    closing=previous.T@sewn;seam=float(np.linalg.svd(closing,compute_uv=False)[-1]);det=float(np.linalg.det(closing))
    require(norm<=.02,'cycle sewing norm loss');require(seam>=.95,'cycle sewing overlap')
    return dict(sign=1 if det>0 else -1,determinant=det,min_overlap=overlap,seam_overlap=seam,seam_norm_error=norm,min_external_gap=gap)

def run(engine,N,which,path):
    p=State(A=-.35 if which=='bridge' else -.30,T=-1.8,ratio=1.04 if which=='bridge' else 1.1)
    s=Sample(engine,N,p);r=dict(engine=engine,N=N,which=which,state=asdict(p),status='RUNNING',gaps={},cycles={})
    for name,index in GAPS.items():
        trials=[s.minimum(index,n) for n in [18,24]]
        require(abs(trials[0]['minimum']['gap']-trials[1]['minimum']['gap'])<.01,'gap grid refinement '+name)
        require(min(t['minimum']['gap'] for t in trials)>1e-5,'state is not resolved gapped: '+name)
        r['gaps'][name]=trials;save(path,r);print(engine,N,which,name,trials[-1]['minimum']['gap'],flush=True)
    for name,index,nb in [('lower_remote',2,1),('flat1',3,1),('flat2',4,1),('upper_remote',5,1),('flat_pair',3,2)]:
        rows=[]
        for axis in [0,1]:
            for offset in [0.,.5]:
                trials=[cycle(s,index,nb,axis,offset,n) for n in [64,128]]
                require(trials[0]['sign']==trials[1]['sign'],'cycle sign fails mesh refinement')
                rows.append(dict(axis=axis,offset=offset,trials=trials))
        for axis in [0,1]:require(len({row['trials'][-1]['sign'] for row in rows if row['axis']==axis})==1,'cycle sign depends on offset')
        r['cycles'][name]=rows;save(path,r)
    r['diagnostics']=s.metrics;r['status']='ACCEPT';return r

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);ap.add_argument('--N',choices=[4,6],type=int,required=True);ap.add_argument('--state',choices=['bridge','endpoint'],required=True);a=ap.parse_args()
    path=ROOT/'results'/f'{a.state}_{a.engine}_N{a.N}.json';start=time.time()
    try:r=run(a.engine,a.N,a.state,path)
    except Exception as error:
        r=json.loads(path.read_text()) if path.exists() else dict(engine=a.engine,N=a.N,which=a.state)
        r.update(status='REJECTED',error=type(error).__name__+': '+str(error))
    r['seconds']=time.time()-start;save(path,r);print('FINAL',a.engine,a.N,a.state,r['status'],r.get('error'),flush=True)
    raise SystemExit(int(r['status']!='ACCEPT'))
