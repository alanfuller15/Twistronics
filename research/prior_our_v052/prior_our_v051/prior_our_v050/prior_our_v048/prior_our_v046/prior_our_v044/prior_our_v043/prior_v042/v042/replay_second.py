"""Second braid: tracked upper and upper-next nodes, fixed reciprocal chart."""
import argparse,json,time
from pathlib import Path
from dataclasses import replace,asdict
import numpy as np
from scipy.optimize import brentq
from models import State
from measure import Sample,geometry,align,require,Rejected
ROOT=Path(__file__).resolve().parent

def save(path,result):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');temp.replace(path)

def run(engine,N,path):
    pilot=next(r for r in json.loads((ROOT/'results/discovery.json').read_text()) if r['engine']==engine)
    names=['U1','U2','X1','X2','X3','X4'];seeds=dict(zip(names,[r['f'] for r in pilot['U']+pilot['next']]))
    indices=dict(U1=4,U2=4,X1=5,X2=5,X3=5,X4=5)
    result=dict(engine=engine,N=N,status='RUNNING',states=[],event=None);previous=None;coarse=None
    for step,ratio in enumerate(np.linspace(.99,1.,11)):
        p=State(ratio=float(ratio));sample=Sample(engine,N,p)
        nodes={k:sample.node(seeds[k],indices[k]) for k in names}
        for k in names:require(np.linalg.norm(np.array(nodes[k]['f'])-seeds[k])<.035,'node continuation jumps: '+k)
        for a in names:
            for b in names:
                if a<b and indices[a]==indices[b]:require(np.linalg.norm(np.array(nodes[a]['f'])-nodes[b]['f'])>.003,'duplicate tracked roots')
        seeds={k:z['f'] for k,z in nodes.items()};a,b=nodes['U1']['f'],nodes['U2']['f'];adj=[nodes[k] for k in names[2:]]
        _,q1=sample.frame(a,4);_,q2=sample.frame(b,4)
        if previous is None:
            e1=q1;e2,_=sample.transport(a,b,e1,4,adj,256);overlaps=[1.,1.];coarse=(e1.copy(),e2.copy())
        else:
            e1,s1=align(q1,previous[0]);e2,s2=align(q2,previous[1]);overlaps=[s1,s2]
        previous=(e1,e2);trials=[]
        for radius,n in [(.006,64),(.006,128),(.003,128)]:
            qa=sample.winding(a,e1,4,radius,n);qb=sample.winding(b,e2,4,radius,n)
            trials.append(dict(radius=radius,points=n,a=qa,b=qb,label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
        require(len({t['label'] for t in trials})==1,'temporal loop refinement')
        fast,d1=sample.transport(a,b,e1,4,adj,128);fine,d2=sample.transport(a,b,e1,4,adj,256)
        require(np.linalg.det(fast.T@fine)>.99,'spatial transport refinement')
        orientation=int(np.sign(np.linalg.det(e2.T@fine)));direct=sample.winding(b,fine,4,.006,128)
        require(direct['charge']==orientation*trials[1]['b']['charge'],'spatial charge versus rectangle holonomy')
        label='SAME' if trials[1]['a']['charge']*direct['charge']>0 else 'OPPOSITE'
        row=dict(ratio=float(ratio),nodes=nodes,geometry={k:geometry(a,b,nodes[k]['f']) for k in names[2:]},temporal_trials=trials,temporal_overlaps=overlaps,spatial_transport=[d1,d2],spatial_direct_charge=direct,label=label,rectangle_orientation=orientation,diagnostics=sample.metrics)
        if step%2==0 and step:
            c1,o1=align(q1,coarse[0]);c2,o2=align(q2,coarse[1]);coarse=(c1,c2)
            require(np.linalg.det(c1.T@e1)>.99 and np.linalg.det(c2.T@e2)>.99,'parameter mesh refinement')
            row['parameter_mesh_check']=dict(fine=.001,coarse=.002,min_overlap=min(o1,o2))
        result['states'].append(row);save(path,result)
        print(engine,N,ratio,label,'X1 offset',row['geometry']['X1']['offset'],flush=True)
    cache={}
    def offset(ratio):
        near=min(result['states'],key=lambda r:abs(r['ratio']-ratio));s=Sample(engine,N,State(ratio=ratio))
        nodes={k:s.node(near['nodes'][k]['f'],indices[k]) for k in ['U1','U2','X1']}
        g=geometry(nodes['U1']['f'],nodes['U2']['f'],nodes['X1']['f']);cache[ratio]=(s,nodes,g);return g['offset']
    critical=float(brentq(offset,.99,1.,xtol=1e-10));offset(critical);s,nodes,g=cache[critical]
    a=np.array(nodes['U1']['f']);b=np.array(nodes['U2']['f']);point=a+g['t']*(b-a)
    w,_=s.at(point);require(0<g['t']<1 and abs(g['offset'])<1e-7,'crossing outside segment')
    rejected=False
    try:s.frame(point,4)
    except Rejected:rejected=True
    require(rejected,'singular transport not rejected')
    result['event']=dict(ratio=critical,geometry=g,nodes=nodes,external_gap=float(w[6]-w[5]),singular_path_rejected=rejected)
    for row in result['states']:
        require(row['label']==('SAME' if row['ratio']<critical else 'OPPOSITE'),'flip does not track crossing')
    for side in ['a','b']:
        require(len({t[side]['charge'] for row in result['states'] for t in row['temporal_trials']})==1,'individual temporal charge changed')
    result['status']='ACCEPT';return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True);ap.add_argument('--N',type=int,choices=[4,6],required=True);a=ap.parse_args()
    path=ROOT/'results'/f'second_{a.engine}_N{a.N}.json';start=time.time()
    try:result=run(a.engine,a.N,path)
    except Exception as error:
        result=json.loads(path.read_text()) if path.exists() else dict(engine=a.engine,N=a.N)
        result.update(status='REJECTED',error=type(error).__name__+': '+str(error))
    result['seconds']=time.time()-start;save(path,result);print('FINAL',a.engine,a.N,result['status'],result.get('error'),flush=True)
    raise SystemExit(int(result['status']!='ACCEPT'))
