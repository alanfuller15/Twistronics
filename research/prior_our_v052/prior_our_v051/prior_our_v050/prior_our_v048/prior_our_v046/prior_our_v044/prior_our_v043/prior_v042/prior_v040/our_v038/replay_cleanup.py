"""Fixed-phi cleanup continuation from braid 2 to the upper-collision leg.

The adjacent X nodes may annihilate. Connecting-path refinement therefore
locates minima of BOTH exterior gaps along the path instead of assuming a
fixed adjacent-node inventory. No failed node refinement is treated as a death.
"""
import argparse,json,time
from pathlib import Path
from dataclasses import replace,asdict
import numpy as np
from scipy.optimize import minimize_scalar
from models import State
from measure import Sample,align,require
from replay_second import save
ROOT=Path(__file__).resolve().parent

def schedule():
    state=State(ratio=1.);out=[state]
    for key,end in [('T',-1.2),('A',-.2),('T',-1.8),('A',-.35)]:
        start=getattr(state,key)
        for x in np.linspace(start,end,5)[1:]:out.append(replace(state,**{key:float(x)}))
        state=out[-1]
    return out

def transport(sample,a,b,base,steps):
    a=np.asarray(a);b=np.asarray(b);d=b-a
    ts=list(np.linspace(0,1,steps+1));gaps=[]
    for t in ts:
        w,_=sample.at(a+t*d);gaps.append([w[4]-w[3],w[6]-w[5]])
    gaps=np.array(gaps);minima=[]
    h0,_=sample.model.real_hamiltonian(a);h1,_=sample.model.real_hamiltonian(b)
    bound=max(1.,2*np.linalg.norm(h1-h0))
    for column,index in enumerate([3,5]):
        for i in range(1,len(ts)-1):
            if gaps[i,column]>min(gaps[i-1,column],gaps[i+1,column]):continue
            def objective(t):
                w,_=sample.at(a+t*d);return float(w[index+1]-w[index])
            sol=minimize_scalar(objective,bounds=(ts[i-1],ts[i+1]),method='bounded',options={'xatol':1e-11,'maxiter':150})
            require(sol.success and sol.fun<=gaps[i,column]+1e-7,'connecting-gap minimum failed')
            require(sol.fun>1e-5,'connecting path loses selected-pair isolation')
            minima.append(dict(t=float(sol.x),gap=float(sol.fun),gap_index=index))
    refined=list(ts)
    for q in minima:
        t=q['t'];scale=max(q['gap']/bound,1e-10);refined.append(t)
        for j in range(-2,21):refined.extend([t-scale*2**j,t+scale*2**j])
    refined=sorted(set(t for t in refined if 0<=t<=1));frame=base;overlap=1.;mingap=float(gaps.min())
    for t in refined[1:]:
        f=a+t*d;w,_=sample.at(f);_,q=sample.frame(f,4);frame,s=align(q,frame)
        overlap=min(overlap,s);mingap=min(mingap,float(min(w[4]-w[3],w[6]-w[5])))
    return frame,dict(min_overlap=overlap,min_external_gap=mingap,samples=len(refined),located_gap_minima=minima)

def run(engine,N,path):
    source=json.loads((ROOT/'results'/f'second_{engine}_N{N}.json').read_text());require(source['status']=='ACCEPT','second braid not accepted')
    last=source['states'][-1];seeds=[last['nodes'][name]['f'] for name in ['U1','U2']]
    result=dict(engine=engine,N=N,status='RUNNING',states=[]);previous=None;coarse=None
    for step,p in enumerate(schedule()):
        s=Sample(engine,N,p);nodes=[s.node(seed,4) for seed in seeds];a,b=[np.array(z['f']) for z in nodes]
        require(np.linalg.norm(b-a)>.01,'cleanup pair unresolved or duplicate')
        require(max(np.linalg.norm(np.array(nodes[i]['f'])-seeds[i]) for i in [0,1])<.08,'cleanup root jump')
        seeds=[z['f'] for z in nodes];_,q1=s.frame(a,4);_,q2=s.frame(b,4)
        if previous is None:e1=q1;e2,_=transport(s,a,b,e1,256);overlaps=[1.,1.];coarse=(e1.copy(),e2.copy())
        else:e1,o1=align(q1,previous[0]);e2,o2=align(q2,previous[1]);overlaps=[o1,o2]
        previous=(e1,e2)
        fast,t1=transport(s,a,b,e1,128);fine,t2=transport(s,a,b,e1,256)
        require(np.linalg.det(fast.T@fine)>.99,'cleanup spatial orientation refinement')
        trials=[]
        for radius,n in [(.004,128),(.004,256),(.002,256)]:
            qa=s.winding(a,e1,4,radius,n);qb=s.winding(b,e2,4,radius,n)
            trials.append(dict(radius=radius,points=n,a=qa,b=qb,label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
        require(len({t['label'] for t in trials})==1,'cleanup loop refinement')
        direct=s.winding(b,fine,4,.004,256);orientation=int(np.sign(np.linalg.det(e2.T@fine)))
        require(direct['charge']==trials[1]['b']['charge']*orientation,'cleanup direct versus temporal orientation')
        label='SAME' if direct['charge']*trials[1]['a']['charge']>0 else 'OPPOSITE'
        row=dict(step=step,state=asdict(p),nodes=nodes,separation=float(np.linalg.norm(b-a)),temporal_trials=trials,temporal_overlaps=overlaps,spatial_transport=[t1,t2],spatial_direct_charge=direct,label=label,rectangle_orientation=orientation,diagnostics=s.metrics)
        if step%2==0 and step:
            c1,o1=align(q1,coarse[0]);c2,o2=align(q2,coarse[1]);coarse=(c1,c2)
            require(np.linalg.det(c1.T@e1)>.99 and np.linalg.det(c2.T@e2)>.99,'cleanup parameter refinement')
            row['parameter_refinement']=dict(min_overlap=min(o1,o2),agrees=True)
        result['states'].append(row);save(path,result);print(engine,N,step,p.A,p.T,label,flush=True)
    for side in ['a','b']:
        require(len({t[side]['charge'] for row in result['states'] for t in row['temporal_trials']})==1,'cleanup temporal charge changes')
    require(all(row['label']=='OPPOSITE' for row in result['states']),'cleanup spatial label changes')
    target=json.loads((ROOT/'results'/f'upper_ann_{engine}_N{N}.json').read_text());require(target['status']=='ACCEPT','upper collision not accepted')
    wanted=np.array([z['f'] for z in target['event']['initial_nodes']]);actual=np.array([z['f'] for z in result['states'][-1]['nodes']])
    error=min(float(np.max(np.linalg.norm(actual-wanted,axis=1))),float(np.max(np.linalg.norm(actual-wanted[::-1],axis=1))))
    require(error<1e-6,'cleanup endpoint does not match upper-annihilation roots')
    result['collision_seed_match']=error;result['status']='ACCEPT';return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['original','partner'],required=True);ap.add_argument('--N',type=int,choices=[4,6],required=True);a=ap.parse_args();start=time.time()
    path=ROOT/'results'/f'cleanup_{a.engine}_N{a.N}.json'
    try:r=run(a.engine,a.N,path)
    except Exception as error:
        r=json.loads(path.read_text()) if path.exists() else dict(engine=a.engine,N=a.N)
        r.update(status='REJECTED',error=type(error).__name__+': '+str(error))
    r['seconds']=time.time()-start;save(path,r);print('FINAL',a.engine,a.N,r['status'],r.get('error'),flush=True)
    raise SystemExit(int(r['status']!='ACCEPT'))
