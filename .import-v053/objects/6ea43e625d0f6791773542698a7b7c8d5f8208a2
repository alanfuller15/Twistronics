"""Two-root continuation, explicit basis pullback and resumable gated records."""
import argparse,itertools,json,time,traceback
from dataclasses import asdict
from pathlib import Path
import numpy as np
from measure import Sample,require,Rejected
from basis import labels,carry
from spatial import transport
from routes import CASES,schedule
from checkpoints import digest,load_steps,save_step,save_json

ROOT=Path(__file__).resolve().parent

def frozen_protocol():
    plan=json.loads((ROOT/'PLAN.json').read_text())
    for name,expected in plan['source_sha256'].items():
        require(digest(ROOT/name)==expected,'source changed after protocol freeze: '+name)
    for name,expected in plan['anchor_sha256'].items():
        require(digest(ROOT/name)==expected,'anchor changed after protocol freeze: '+name)
    return digest(ROOT/'PLAN.json')

def anchor(name,engine,N):
    x=json.loads((ROOT/'anchors'/f'{name}_{engine}_N{N}.json').read_text())
    require(x['status']=='ACCEPT','unaccepted anchor');return x

def match(nodes,target):
    distances=[]
    for order in itertools.permutations(range(2)):
        d=[float(np.linalg.norm(np.array(nodes[i]['f'])-target[j]['f'])) for i,j in enumerate(order)]
        distances.append(dict(permutation=list(order),distances=d,max_distance=max(d)))
    best=min(distances,key=lambda x:x['max_distance'])
    require(best['max_distance']<1e-6,'continuation misses accepted endpoint roots')
    return best

def loops(sample,a,b,e1,e2,index,r):
    attempts=[]
    for n in [64,256,1024]:
        trials=[]
        try:
            for radius,points in [(r,n),(r,2*n),(r/2,2*n)]:
                qa=sample.winding(a,e1,index,radius,points)
                qb=sample.winding(b,e2,index,radius,points)
                trials.append(dict(radius=radius,points=points,a=qa,b=qb,
                    label='SAME' if qa['charge']*qb['charge']>0 else 'OPPOSITE'))
            for side in ['a','b']:
                require(len({t[side]['charge'] for t in trials})==1,'charge fails mesh/radius refinement')
            return trials,attempts
        except Rejected as error:
            attempts.append(dict(base_points=n,reason=str(error),completed_trials=trials))
            if str(error)!='loop phase steps unresolved':raise
    raise Rejected('loop phase unresolved at maximum mesh')

def run(engine,N,case,max_new=None):
    protocol=frozen_protocol();definition=CASES[case];index=definition['index'];grid=schedule(case)
    folder=ROOT/'results'/f'{case}_{engine}_N{N}';folder.mkdir(parents=True,exist_ok=True)
    rows,arrays=load_steps(folder,protocol)
    require(len(rows)<=len(grid),'too many checkpoints')
    for k,row in enumerate(rows):
        require(row['engine']==engine and row['N']==N and row['case']==case,'checkpoint identity mismatch')
        require(row['state']==asdict(grid[k]['state']),'checkpoint state differs from protocol')
    if rows:seeds=[x['f'] for x in rows[-1]['nodes']]
    elif case=='post_ann':seeds=[x['f'] for x in anchor('post_transfer',engine,N)['pair']['nodes']]
    else:seeds=definition['seeds']
    start=len(rows)
    for step in range(start,len(grid)):
        if max_new is not None and step-start>=max_new:break
        tick=time.time();g=grid[step];sample=Sample(engine,N,g['state']);basis_labels=labels(sample.model)
        nodes=[sample.node(seed,index) for seed in seeds]
        jumps=[float(np.linalg.norm(np.array(node['f'])-seed)) for node,seed in zip(nodes,seeds)]
        require(max(jumps)<.08,'node continuation jump exceeds protocol bound')
        a,b=[np.array(x['f']) for x in nodes];sep=float(np.linalg.norm(a-b))
        require(sep>.001,'duplicate or unresolved close roots');radius=min(.004,sep/8)
        _,q1=sample.frame(a,index);_,q2=sample.frame(b,index)
        temporal=[];mesh=None
        if arrays is None:
            e1=q1
            e2,_=transport(sample,a,b,e1,index,256)
            c1,c2=e1.copy(),e2.copy();coarse_labels=basis_labels.copy()
        else:
            e1,t1=carry(arrays['e1'],arrays['labels'],q1,basis_labels)
            e2,t2=carry(arrays['e2'],arrays['labels'],q2,basis_labels)
            temporal=[t1,t2];c1,c2=arrays['c1'],arrays['c2'];coarse_labels=arrays['coarse_labels']
            if g['leg_step']%2==0:
                c1,d1=carry(c1,coarse_labels,q1,basis_labels);c2,d2=carry(c2,coarse_labels,q2,basis_labels)
                orientation=[float(np.linalg.det(c1.T@e1)),float(np.linalg.det(c2.T@e2))]
                require(min(orientation)>.99,'parameter mesh orientation disagreement')
                mesh=dict(orientation=orientation,transport=[d1,d2]);coarse_labels=basis_labels.copy()
        fast,d1=transport(sample,a,b,e1,index,128);fine,d2=transport(sample,a,b,e1,index,256)
        determinant=float(np.linalg.det(fast.T@fine));require(determinant>.99,'spatial mesh orientation disagreement')
        trials,attempts=loops(sample,a,b,e1,e2,index,radius)
        orientation=int(np.sign(np.linalg.det(e2.T@fine)))
        direct=sample.winding(b,fine,index,radius,trials[1]['points'])
        require(direct['charge']==orientation*trials[1]['b']['charge'],'spatial charge versus rectangle holonomy')
        label='SAME' if trials[1]['a']['charge']*direct['charge']>0 else 'OPPOSITE'
        row=dict(status='ACCEPT',step=step,protocol_sha256=protocol,engine=engine,N=N,case=case,
            state=asdict(g['state']),leg=g['leg'],leg_step=g['leg_step'],varying=g['key'],
            nodes=nodes,node_jumps=jumps,separation=sep,basis_dimension=sample.model.dim,
            temporal_transport=temporal,parameter_mesh_check=mesh,spatial_transport=[d1,d2],
            spatial_mesh_determinant=determinant,temporal_trials=trials,rejected_loop_stages=attempts,
            rectangle_orientation=orientation,spatial_direct_charge=direct,label=label,
            diagnostics=sample.metrics,sampled_points=len(sample.cache),seconds=time.time()-tick)
        if step==0 and case=='post_ann':
            row['anchor_match']=match(nodes,anchor('post_transfer',engine,N)['pair']['nodes'])
        if step==len(grid)-1:
            if case=='pre_ann':target=anchor('first_ann',engine,N)['event']['initial_nodes']
            else:
                target_map=anchor('second',engine,N)['states'][0]['nodes'];target=[target_map[k] for k in ['U1','U2']]
            row['anchor_match']=match(nodes,target)
        arrays=dict(e1=e1,e2=e2,labels=basis_labels,c1=c1,c2=c2,coarse_labels=coarse_labels)
        row=save_step(folder,step,row,arrays);rows.append(row);seeds=[x['f'] for x in nodes]
        print(engine,N,case,step,'of',len(grid)-1,g['key'],getattr(g['state'],g['key'],''),label,
              'gap',d2['min_external_gap'],'seconds',round(row['seconds'],2),flush=True)
    complete=len(rows)==len(grid)
    # A valid changed label is evidence, not automatically a numerical rejection.
    events=[dict(step=r['step'],label=r['label']) for i,r in enumerate(rows) if i and r['label']!=rows[i-1]['label']]
    charges={s:sorted({t[s]['charge'] for r in rows for t in r['temporal_trials']}) for s in ['a','b']}
    result=dict(status='ACCEPT' if complete else 'PARTIAL',engine=engine,N=N,case=case,
                protocol_sha256=protocol,completed=len(rows),scheduled=len(grid),label_changes=events,
                temporal_charges=charges,labels=sorted({r['label'] for r in rows}),
                expected_label=definition['expected_label'],matches_expected=all(r['label']==definition['expected_label'] for r in rows),
                anchor_matches=[r['anchor_match'] for r in rows if 'anchor_match' in r],
                states=rows,seconds=sum(r['seconds'] for r in rows))
    save_json(folder/'summary.json',result);return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=['bm_lab','ref_lab'],required=True)
    ap.add_argument('--N',type=int,choices=[4,6],required=True);ap.add_argument('--case',choices=list(CASES),required=True)
    ap.add_argument('--max-new',type=int);args=ap.parse_args()
    try:
        result=run(args.engine,args.N,args.case,args.max_new)
        print('FINAL',result['engine'],result['N'],result['case'],result['status'],flush=True)
    except Exception as error:
        folder=ROOT/'results'/f'{args.case}_{args.engine}_N{args.N}';folder.mkdir(parents=True,exist_ok=True)
        result=dict(status='REJECTED',engine=args.engine,N=args.N,case=args.case,
                    error=type(error).__name__+': '+str(error),traceback=traceback.format_exc())
        save_json(folder/f'failure_{time.time_ns()}.json',result);print(json.dumps(result),flush=True)
        raise SystemExit(1)
