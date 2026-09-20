"""Locate pair folds, continue distinct roots, measure charges, check open side.

A solver failure or duplicate root is NEVER an annihilation verdict. A fold
requires two zero Hamiltonian components and a rank-one spatial Jacobian,
stable under derivative-step halving, plus resolved roots and a positive gap
on opposite sides. Global gap statements remain finite numerical searches.
"""
import argparse,json,time
from pathlib import Path
from dataclasses import replace,asdict
import numpy as np
from scipy.optimize import least_squares
from models import State
from measure import Sample,require,Rejected
from replay_second import save
from refined_charge import refined_pair
ROOT=Path(__file__).resolve().parent
CASES={
 'first_ann':dict(p=State(A=0,T=-.70,phi=65,ratio=.8),key='T',pair_at=-.70,gapped_at=-.74,guess=-.71,index=3,seeds=[[.6495,.8384],[.6283,.8343]],delta=.001),
 'upper_ann':dict(p=State(A=-.35,T=-1.8,ratio=1.),key='ratio',pair_at=1.,gapped_at=1.1,guess=1.05,index=4,seeds=[[.582,.880],[.661,.918]],delta=.001),
 'flat_birth':dict(p=State(A=-.35,T=-1.8,ratio=1.1),key='ratio',pair_at=1.1,gapped_at=1.,guess=1.05,index=3,seeds=[[.681,.967],[.682,.875]],delta=.001),
 'final_ann':dict(p=State(A=-.35,T=-1.8,ratio=1.1),key='A',pair_at=-.35,gapped_at=-.30,guess=-.325,index=3,seeds=[[.681,.967],[.682,.875]],delta=.001)
}

def spatial_jac(sample,f,anchor,index,h):
    return np.column_stack([(sample.vector(np.asarray(f)+h*e,anchor,index)[0]-sample.vector(np.asarray(f)-h*e,anchor,index)[0])/(2*h) for e in np.eye(2)])

def locate(engine,N,c):
    index=c['index'];initial=Sample(engine,N,c['p']);nodes=[initial.node(seed,index) for seed in c['seeds']]
    a,b=[np.array(n['f']) for n in nodes];require(np.linalg.norm(b-a)>.005,'initial duplicate roots')
    center=(a+b)/2;_,anchor=initial.frame(center,index)
    low,high=sorted([c['pair_at'],c['gapped_at']]);cache={}
    def at(parameter):
        key=float(parameter)
        if key not in cache:
            # Bound memory: only a few fold objective calls need reuse.
            if len(cache)>8:cache.clear()
            cache[key]=Sample(engine,N,replace(c['p'],**{c['key']:key}))
        return cache[key]
    def objective(x,h):
        s=at(x[2]);d=s.vector(x[:2],anchor,index)[0];J=spatial_jac(s,x[:2],anchor,index,h)
        return np.r_[d,.02*np.linalg.det(J)/max(1.,np.linalg.norm(J))]
    records=[];x=np.r_[center,c['guess']]
    for h in [2e-5,1e-5]:
        sol=least_squares(lambda x:objective(x,h),x,bounds=([0.,0.,low],[1.,1.1,high]),diff_step=1e-4,xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=160)
        x=sol.x;s=at(x[2]);res=objective(x,h);J=spatial_jac(s,x[:2],anchor,index,h);u,sv,vh=np.linalg.svd(J)
        w,_=s.at(x[:2]);external=float(min(w[index]-w[index-1],w[index+2]-w[index+1]))
        require(sol.success and np.linalg.norm(res[:2])<1e-6,'fold root not converged')
        require(sv[-1]<1e-3 and sv[0]>1.,'fold Jacobian not rank one')
        require(external>1e-5,'fold touches adjacent band')
        records.append(dict(parameter=float(x[2]),f=x[:2].tolist(),h=h,residual=res.tolist(),singular_values=sv.tolist(),null_direction=vh[-1].tolist(),gap=float(w[index+1]-w[index]),external_gap=external,nfev=sol.nfev))
    require(abs(records[0]['parameter']-records[1]['parameter'])<1e-6,'fold location fails derivative refinement')
    return dict(initial_nodes=nodes,fold_trials=records,parameter=records[-1]['parameter'],f=records[-1]['f'])

def run(engine,N,case,path,locate_only=False):
    c=CASES[case];result=dict(engine=engine,N=N,case=case,status='RUNNING',definition={**c,'p':asdict(c['p'])})
    event=locate(engine,N,c);result['event']=event;save(path,result)
    print(engine,N,case,'FOLD',event['parameter'],event['f'],flush=True)
    if locate_only:result['status']='LOCATED';return result
    side=np.sign(c['pair_at']-event['parameter']);near=event['parameter']+side*c['delta'];after=event['parameter']-side*c['delta']
    require(min(c['pair_at'],c['gapped_at'])<near<max(c['pair_at'],c['gapped_at']),'near-fold sample out of window')
    seeds=[z['f'] for z in event['initial_nodes']];states=[]
    for value in np.linspace(c['pair_at'],near,9):
        s=Sample(engine,N,replace(c['p'],**{c['key']:float(value)}));nodes=[s.node(seed,c['index']) for seed in seeds]
        points=[np.array(z['f']) for z in nodes];sep=float(np.linalg.norm(points[1]-points[0]));require(sep>.001,'unresolved or duplicate pair')
        require(max(np.linalg.norm(points[i]-seeds[i]) for i in [0,1])<.06,'root continuation jumps')
        seeds=[z['f'] for z in nodes];states.append(dict(parameter=float(value),nodes=nodes,separation=sep,diagnostics=s.metrics))
    # Charge is established at the start and near the event, never at collision.
    result['states']=states;result['charges']=[]
    for row in [states[0],states[-1]]:
        s=Sample(engine,N,replace(c['p'],**{c['key']:row['parameter']}));radius=min(.002,row['separation']/8)
        pair=refined_pair(s,[z['f'] for z in row['nodes']],c['index'],radius)
        require(pair['label']=='OPPOSITE','colliding pair does not have opposite spatial charge')
        result['charges'].append(dict(parameter=row['parameter'],measurement=pair))
    save(path,result)
    # Near-event positive minimum, seeded on meeting point, in a local bounded
    # box through the same global search entry point (extra seeds retained).
    result['gapped_checks']=[]
    for value,grids in [(after,[18]),(c['gapped_at'],[18,24])]:
        s=Sample(engine,N,replace(c['p'],**{c['key']:float(value)}));trials=[]
        for grid in grids:
            row=s.minimum(c['index'],grid,extra=[event['f']]);require(row['minimum']['gap']>1e-5,'open-side gap unresolved')
            trials.append(row)
        if len(trials)>1:require(abs(trials[0]['minimum']['gap']-trials[1]['minimum']['gap'])<.01,'open-side minimum fails grid refinement')
        result['gapped_checks'].append(dict(parameter=float(value),trials=trials,diagnostics=s.metrics));save(path,result)
        print(engine,N,case,'GAPPED',value,trials[-1]['minimum']['gap'],flush=True)
    require(states[-1]['separation']<states[0]['separation'],'pair fails to approach fold')
    result['status']='ACCEPT';return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);ap.add_argument('--N',type=int,choices=[4,6],required=True);ap.add_argument('--case',choices=list(CASES),required=True);ap.add_argument('--locate-only',action='store_true');a=ap.parse_args()
    path=ROOT/'results'/f'{a.case}_{a.engine}_N{a.N}_refined{"_locate" if a.locate_only else ""}.json';start=time.time()
    try:result=run(a.engine,a.N,a.case,path,a.locate_only)
    except Exception as error:
        result=json.loads(path.read_text()) if path.exists() else dict(engine=a.engine,N=a.N,case=a.case)
        result.update(status='REJECTED',error=type(error).__name__+': '+str(error))
    result['seconds']=time.time()-start;save(path,result);print('FINAL',a.engine,a.N,a.case,result['status'],result.get('error'),flush=True)
    raise SystemExit(int(result['status'] not in ['ACCEPT','LOCATED']))
