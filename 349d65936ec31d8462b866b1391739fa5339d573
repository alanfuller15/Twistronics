"""Frozen N8 braid-2 continuation from retained temporal frames. No network/subprocess."""
import argparse,time,traceback,sys
from datetime import datetime,timezone
from dataclasses import replace
from pathlib import Path
import numpy as np
from evidence import read,sha,write,require,safe
from test_evidence import runtime_identity
from numerics import root
from joins import anchor,measure_join
from transport import transport
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]


def frozen():
    p=read(ROOT/'NUMERICAL_PLAN.json')
    for name,h in p['runner_sha256'].items():require(sha(safe(ROOT,name))==h,'runner changed: '+name)
    for name,h in p['inputs'].items():require(sha(safe(REPO,name))==h,'input changed: '+name)
    return p


def charges(sample,a,b,fa,fb,spatial,radius,orientation):
    stages=[]
    for n in [64,256]:
        trials=[]
        try:
            for r,points in [(radius,n),(radius,2*n),(radius/2,2*n)]:
                qa=sample.winding(a,fa,4,r,points);qb=sample.winding(b,fb,4,r,points);direct=sample.winding(b,spatial,4,r,points)
                require(direct['charge']==orientation*qb['charge'],'spatial charge disagrees with rectangle')
                trials.append(dict(radius=r,points=points,a=qa,b=qb,spatial_b=direct,label='SAME' if qa['charge']*direct['charge']>0 else 'OPPOSITE'))
            require(all(len({t[k]['charge'] for t in trials})==1 for k in ['a','b','spatial_b']),'loop mesh/radius disagreement')
            return dict(trials=trials,rejected_stages=stages)
        except ValueError as error:
            stages.append(dict(base_points=n,reason=str(error),completed_trials=trials))
            if str(error)!='loop phase steps unresolved':error.attempts=stages;raise
    error=ValueError('loop phase unresolved at maximum mesh');error.attempts=stages;raise error


def main(engine):
    p=frozen();require(engine in p['engines'],'unknown engine');path=ROOT/'results'/f'second_{engine}_N8.json';folder=ROOT/'results'/f'{engine}_N8'
    require(not path.exists() and not folder.exists(),'refusing to overwrite numerical window');start=time.time()
    sys.path.insert(1,str(REPO/p['model_root']))
    from models import State
    from measure import Sample,geometry,align
    from checkpoints import save_step
    state=State(**p['state']);make=lambda ratio:Sample(engine,8,replace(state,ratio=float(ratio)))
    r=dict(engine=engine,N=8,case=p['case'],kinetic=p['kinetic'],geometry=p['geometry'][engine],cutoff_tol=p['cutoff_tol'][engine],state=p['state'],status='RUNNING',started_utc=datetime.now(timezone.utc).isoformat(),numerical_plan_sha256=sha(ROOT/'NUMERICAL_PLAN.json'),runtime_before=runtime_identity(),states=[])
    write(path,r);seeds=p['seeds'][engine]
    try:
        old,arrays=anchor(REPO,p,engine);previous=[arrays['frame_a'],arrays['frame_b']];coarse=[arrays['coarse_a'],arrays['coarse_b']];initial_charges=p['anchors'][engine]['temporal_charges']
        r['anchor']=p['anchors'][engine]
        for step,ratio in enumerate(p['ratios']):
            s=make(ratio);nodes={name:root(s,seeds[name],index,p['box']) for name,index in p['node_indices'].items()};r['dimension']=s.model.dim
            jump=max(float(np.linalg.norm(np.asarray(n['f'])-seeds[name])) for name,n in nodes.items());require(jump<p['max_root_jump'],'root jump')
            for name,n in nodes.items():
                for other,m in nodes.items():
                    if name<other and n['index']==m['index']:require(np.linalg.norm(np.asarray(n['f'])-m['f'])>p['minimum_separation'],'duplicate tracked roots')
            a,b=[np.array(nodes[name]['f']) for name in ['U1','U2']];require(np.linalg.norm(a-b)>3*p['radius'],'overlapping node loops')
            _,qa=s.frame(a,4);_,qb=s.frame(b,4)
            fa,oa=align(qa,previous[0]);fb,ob=align(qb,previous[1]);overlaps=[oa,ob]
            join=measure_join(old,nodes,[qa,qb],[fa,fb],arrays,p['join_root_tolerance'],p['join_frame_tolerance']) if step==0 else None
            adjacent=[nodes[name]['f'] for name in nodes if name.startswith('X')]
            fast,d1=transport(s,a,b,fa,4,128,adjacent,align);spatial,d2=transport(s,a,b,fa,4,256,adjacent,align)
            spatial_det=float(np.linalg.det(fast.T@spatial));require(spatial_det>.99,'spatial mesh disagreement')
            rectangle_det=float(np.linalg.det(spatial.T@fb));require(abs(rectangle_det)>.99,'rectangle unresolved');orientation=1 if rectangle_det>0 else -1
            check=None
            if step in p['coarse_checks']:
                ca,oa=align(qa,coarse[0]);cb,ob=align(qb,coarse[1]);dets=[float(np.linalg.det(ca.T@fa)),float(np.linalg.det(cb.T@fb))];require(min(dets)>.99,'parameter mesh disagreement')
                coarse=[ca,cb];check=dict(overlaps=[oa,ob],determinants=dets)
            q=charges(s,a,b,fa,fb,spatial,p['radius'],orientation);temporal=[q['trials'][0][k]['charge'] for k in ['a','b']]
            if step==0:require(q['trials'][0]['label']==old['label'],'anchor spatial label changed')
            require(temporal==initial_charges,'temporally carried node charge changed')
            row=dict(step=step,ratio=ratio,protocol_sha256=r['numerical_plan_sha256'],nodes=nodes,max_jump=jump,join=join,geometry={name:geometry(a,b,nodes[name]['f']) for name in nodes if name.startswith('X')},temporal_overlaps=overlaps,coarse_check=check,spatial_transport=[d1,d2],spatial_mesh_determinant=spatial_det,rectangle_determinant=rectangle_det,rectangle_orientation=orientation,charge=q,label=q['trials'][0]['label'],diagnostics=s.metrics,sampled_points=len(s.cache))
            row=save_step(folder,step,row,dict(frame_a=fa,frame_b=fb,spatial=spatial,spatial_fast=fast,coarse_a=coarse[0],coarse_b=coarse[1]))
            r['states'].append(row);previous=[fa,fb];seeds={name:n['f'] for name,n in nodes.items()};write(path,r)
            print(engine,'STATE',step,ratio,row['label'],d2['min_external_gap'],len(s.cache),flush=True)
        require(frozen()==p,'numerical plan changed during run');r['status']='ACCEPT_SAMPLED_BRAID2_CONTINUATION'
    except Exception as error:
        r['status']='REJECT';r['failure']=dict(type=type(error).__name__,message=str(error),attempts=getattr(error,'attempts',[]),traceback=traceback.format_exc())
    r['runtime_after']=runtime_identity()
    if r['runtime_after']!=r['runtime_before']:r['status']='REJECT_RUNTIME_CHANGED'
    r['seconds']=time.time()-start;write(path,r);print(engine,r['status'],len(r['states']),r['seconds'],flush=True)
    if r['status']!='ACCEPT_SAMPLED_BRAID2_CONTINUATION':raise SystemExit(1)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('engine',choices=['bm_lab','ref_lab']);main(p.parse_args().engine)
