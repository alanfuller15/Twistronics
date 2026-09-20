"""Braid 1 and connecting legs; immutable frames and explicit geometry."""
import argparse,itertools,json,time,traceback
from dataclasses import asdict,replace
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from models import State
from measure import Sample,geometry,require,Rejected
from basis import labels,carry
from spatial import transport
from routes import INITIAL,INDICES,schedule
from checkpoints import digest,load_steps,save_step,save_json

ROOT=Path(__file__).resolve().parent

def frozen_protocol():
    plan=json.loads((ROOT/'PLAN.json').read_text())
    for group in ['source_sha256','anchor_sha256']:
        for name,expected in plan[group].items():require(digest(ROOT/name)==expected,'frozen input changed: '+name)
    return digest(ROOT/'PLAN.json')

def loops(sample,a,b,e1,e2,r):
    attempts=[]
    for n in [64,256,1024]:
        trials=[]
        try:
            for radius,points in [(r,n),(r,2*n),(r/2,2*n)]:
                qa=sample.winding(a,e1,3,radius,points);qb=sample.winding(b,e2,3,radius,points)
                trials.append(dict(radius=radius,points=points,a=qa,b=qb,label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
            for side in ['a','b']:require(len({t[side]['charge'] for t in trials})==1,'loop mesh/radius charge disagreement')
            return trials,attempts
        except Rejected as error:
            attempts.append(dict(base_points=n,reason=str(error),completed_trials=trials))
            if str(error)!='loop phase steps unresolved':raise
    raise Rejected('loop phase unresolved at maximum mesh')

def endpoint_join(engine,N,nodes,e1,e2,basis_labels,trials,label):
    path=ROOT/'anchors'/f'v043_start_{engine}_N{N}.json'
    anchor=json.loads(path.read_text());require(anchor['status']=='ACCEPT','unaccepted endpoint anchor')
    target=anchor['nodes'];current=[nodes['F1'],nodes['F3']]
    errors=[dict(permutation=list(order),distances=[float(np.linalg.norm(np.array(current[i]['f'])-target[j]['f'])) for i,j in enumerate(order)]) for order in itertools.permutations(range(2))]
    best=min(errors,key=lambda x:max(x['distances']));require(max(best['distances'])<1e-6,'misses v043 endpoint roots')
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as data:
        require(np.array_equal(basis_labels,data['labels']),'endpoint basis changed')
        frames=[data['e1'],data['e2']];comparisons=[]
        for i,(frame,side) in enumerate(zip([e1,e2],['a','b'])):
            j=best['permutation'][i];o=frame.T@frames[j];s=np.linalg.svd(o,compute_uv=False)
            determinant=float(np.linalg.det(o));sign=int(np.sign(determinant))
            require(s.min()>.999999 and abs(determinant)>.999999,'endpoint two-plane mismatch')
            anchor_charge=anchor['temporal_trials'][1][['a','b'][j]]['charge']
            require(sign*anchor_charge==trials[1][side]['charge'],'endpoint charge cannot be joined by recorded orientation')
            comparisons.append(dict(node=['F1','F3'][i],anchor_node=j,min_overlap=float(s.min()),orientation=sign,
                                    anchor_charge=anchor_charge,carried_charge=trials[1][side]['charge']))
    require(label==anchor['label'],'endpoint relative label differs from v043')
    return dict(**best,max_distance=max(best['distances']),label=label,frame_joins=comparisons)

def locate_crossing(engine,N,rows,shift):
    bracket=[-.30,-.25];cache={}
    def offset(B):
        near=min(rows[:21],key=lambda r:abs(r['state']['B']-B))
        p=replace(State(**near['state']),B=float(B));s=Sample(engine,N,p)
        nodes={k:s.node(near['nodes'][k]['f'],INDICES[k]) for k in ['F1','F3','U1']}
        a=np.array(nodes['F1']['f'])+[shift,0];b=np.array(nodes['F3']['f'])+[shift,0]
        g=geometry(a,b,np.array(nodes['U1']['f']));cache[float(B)]=(s,nodes,g,a,b)
        return g['offset']
    left,right=[offset(B) for B in bracket];require(left*right<0,'upper-node crossing not bracketed')
    critical=float(brentq(offset,*bracket,xtol=1e-11));offset(critical)
    sample,nodes,g,a,b=cache[critical];point=a+g['t']*(b-a)
    require(0<g['t']<1 and abs(g['offset'])<1e-7,'crossing outside comparison segment')
    w,_=sample.at(point);rejected=False
    try:sample.frame(point,3)
    except Rejected:rejected=True
    require(rejected,'singular comparison path accepted')
    return dict(engine=engine,geometry=sample.model.geometry,kinetic='lab_nn_full',N=N,shift=shift,B=critical,
                location=g,nodes=nodes,external_gap=float(w[5]-w[4]),singular_path_rejected=True,
                bracket=bracket,bracket_offsets=[left,right],diagnostics=sample.metrics)

def run(engine,N,max_new=None):
    protocol=frozen_protocol();grid=schedule();folder=ROOT/'results'/f'early_{engine}_N{N}'
    folder.mkdir(parents=True,exist_ok=True);rows,arrays=load_steps(folder,protocol)
    require(len(rows)<=len(grid),'too many saved states')
    for i,row in enumerate(rows):require(row['state']==asdict(grid[i]['state']) and row['engine']==engine and row['N']==N,'saved identity/state mismatch')
    seeds={k:n['f'] for k,n in rows[-1]['nodes'].items()} if rows else INITIAL
    start=len(rows)
    for step in range(start,len(grid)):
        if max_new is not None and step-start>=max_new:break
        tick=time.time();g=grid[step];sample=Sample(engine,N,g['state']);basis_labels=labels(sample.model)
        # Lower nodes are followed through braid/deepening only. Their later
        # collision is not inferred from a failed search or claimed measured.
        names=list(INDICES) if g['leg']<=2 else ['F1','F3','U1','U2']
        nodes={k:sample.node(seeds[k],INDICES[k]) for k in names}
        jumps={k:float(np.linalg.norm(np.array(nodes[k]['f'])-seeds[k])) for k in names}
        require(max(jumps.values())<.08,'node continuation jump too large')
        for x,y in [('F1','F3'),('U1','U2'),('L1','L2')]:
            if x in nodes:require(np.linalg.norm(np.array(nodes[x]['f'])-nodes[y]['f'])>.001,'duplicate or unresolved tracked roots')
        a,b=[np.array(nodes[k]['f']) for k in ['F1','F3']];sep=float(np.linalg.norm(a-b));r=min(.004,sep/8)
        _,q1=sample.frame(a,3);_,q2=sample.frame(b,3);temporal=[];mesh=None
        if arrays is None:
            e1=q1;e2,_=transport(sample,a,b,e1,3,256);c1,c2=e1.copy(),e2.copy();coarse_labels=basis_labels.copy()
        else:
            e1,t1=carry(arrays['e1'],arrays['labels'],q1,basis_labels);e2,t2=carry(arrays['e2'],arrays['labels'],q2,basis_labels)
            temporal=[t1,t2];c1,c2=arrays['c1'],arrays['c2'];coarse_labels=arrays['coarse_labels']
            if g['leg_step']%2==0:
                c1,d1=carry(c1,coarse_labels,q1,basis_labels);c2,d2=carry(c2,coarse_labels,q2,basis_labels)
                orientation=[float(np.linalg.det(c1.T@e1)),float(np.linalg.det(c2.T@e2))]
                require(min(orientation)>.99,'parameter mesh orientation disagreement')
                mesh=dict(orientation=orientation,transport=[d1,d2]);coarse_labels=basis_labels.copy()
        fast,d1=transport(sample,a,b,e1,3,128);fine,d2=transport(sample,a,b,e1,3,256)
        determinant=float(np.linalg.det(fast.T@fine));require(determinant>.99,'spatial mesh orientation disagreement')
        trials,attempts=loops(sample,a,b,e1,e2,r);direct=sample.winding(b,fine,3,r,trials[1]['points'])
        orientation=int(np.sign(np.linalg.det(e2.T@fine)))
        require(direct['charge']==orientation*trials[1]['b']['charge'],'spatial charge versus rectangle holonomy')
        label='SAME' if trials[1]['a']['charge']*direct['charge']>0 else 'OPPOSITE'
        row=dict(status='ACCEPT',step=step,protocol_sha256=protocol,engine=engine,N=N,geometry=sample.model.geometry,
            kinetic='lab_nn_full',state=asdict(g['state']),leg=g['leg'],leg_step=g['leg_step'],varying=g['key'],
            nodes=nodes,node_jumps=jumps,separation=sep,basis_dimension=sample.model.dim,
            adjacent_geometry={k:geometry(a,b,np.array(nodes[k]['f'])) for k in names if k not in ['F1','F3']},
            temporal_transport=temporal,parameter_mesh_check=mesh,spatial_transport=[d1,d2],spatial_mesh_determinant=determinant,
            temporal_trials=trials,rejected_loop_stages=attempts,rectangle_orientation=orientation,
            spatial_direct_charge=direct,label=label,diagnostics=sample.metrics,sampled_points=len(sample.cache),seconds=time.time()-tick)
        if step==len(grid)-1:row['anchor_join']=endpoint_join(engine,N,nodes,e1,e2,basis_labels,trials,label)
        arrays=dict(e1=e1,e2=e2,labels=basis_labels,c1=c1,c2=c2,coarse_labels=coarse_labels)
        row=save_step(folder,step,row,arrays);rows.append(row);seeds={k:z['f'] for k,z in nodes.items()}
        print(engine,N,step,'of',len(grid)-1,g['key'],getattr(g['state'],g['key'],''),label,
              'U1 offset',row['adjacent_geometry']['U1']['offset'],'seconds',round(row['seconds'],2),flush=True)
    complete=len(rows)==len(grid);events=[]
    if complete:
        for shift in [0.,.012]:events.append(locate_crossing(engine,N,rows,shift))
        center=events[0]['B']
        for row in rows:
            expected='SAME' if row['leg']<=1 and row['state']['B']>center else 'OPPOSITE'
            require(row['label']==expected,'label change not accounted for by located crossing')
        for side in ['a','b']:require(len({t[side]['charge'] for row in rows for t in row['temporal_trials']})==1,'individual carried charge changed')
    result=dict(status='ACCEPT' if complete else 'PARTIAL',engine=engine,N=N,
        geometry='linear' if engine=='bm_lab' else 'exact',kinetic='lab_nn_full',protocol_sha256=protocol,
        completed=len(rows),scheduled=len(grid),events=events,states=rows,seconds=sum(r['seconds'] for r in rows))
    save_json(folder/'summary.json',result);return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True)
    ap.add_argument('--N',type=int,choices=[4,6],required=True);ap.add_argument('--max-new',type=int);a=ap.parse_args()
    try:
        result=run(a.engine,a.N,a.max_new);print('FINAL',a.engine,a.N,result['status'],flush=True)
    except Exception as error:
        folder=ROOT/'results'/f'early_{a.engine}_N{a.N}';folder.mkdir(parents=True,exist_ok=True)
        result=dict(status='REJECTED',engine=a.engine,N=a.N,error=type(error).__name__+': '+str(error),traceback=traceback.format_exc())
        save_json(folder/f'failure_{time.time_ns()}.json',result);print(json.dumps(result),flush=True);raise SystemExit(1)
