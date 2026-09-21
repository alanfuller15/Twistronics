"""One fresh N8 critical-event worker, with no network or subprocess calls."""
import argparse,time,traceback
from datetime import datetime,timezone
from dataclasses import replace
from pathlib import Path
import sys
import numpy as np
from evidence import read,sha,write,require,safe,pair_distance
from test_evidence import runtime_identity
from fold import root,locate,character,separation_law
from search import search,acceptance
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]


def frozen():
    p=read(ROOT/'NUMERICAL_PLAN.json')
    for name,h in p['runner_sha256'].items():require(sha(safe(ROOT,name))==h,'runner changed: '+name)
    for name,h in p['inputs'].items():require(sha(safe(REPO,name))==h,'input changed: '+name)
    return p


def main(engine):
    p=frozen();require(engine in p['engines'],'unknown engine');path=ROOT/'results'/f'lower_unlink_{engine}_N8.json'
    require(not path.exists(),'refusing to overwrite numerical event');start=time.time();runtime=runtime_identity()
    sys.path.insert(0,str(REPO/p['model_root']))
    from models import State
    from measure import Sample
    from local_domain import gap_objective
    from pair_measure import refined_pair
    state=State(**p['state']);make=lambda state:Sample(engine,8,state)
    r=dict(engine=engine,N=8,case='lower_unlink',kinetic='lab_nn_full',geometry=p['geometry'][engine],cutoff_tol=p['cutoff_tol'][engine],state=p['state'],
           status='RUNNING',started_utc=datetime.now(timezone.utc).isoformat(),numerical_plan_sha256=sha(ROOT/'NUMERICAL_PLAN.json'),runtime_before=runtime,states=[],charges=[],open_checks=[])
    write(path,r)
    try:
        event=locate(make,state,p['seeds'][engine],p['guesses'][engine],p['box'],p['T_window'],2);r['event']=event;write(path,r)
        require(p['T_window'][1]<event['parameter']-p['opening_offset']<event['parameter']<state.T,'event outside declared window')
        r['nondegeneracy']=character(make,state,event,2)
        print(engine,'FOLD',event['parameter'],event['f'],flush=True);write(path,r)
        regular=np.linspace(state.T,event['parameter']+p['regular_last_offset'],p['regular_states']).tolist()
        stations=sorted(set(regular+[event['parameter']+x for x in p['extra_root_offsets']]),reverse=True)
        seeds=[n['f'] for n in event['initial_nodes']]
        for T in stations:
            s=make(replace(state,T=T));nodes=[root(s,f,2,p['box']) for f in seeds]
            separation=float(np.linalg.norm(np.array(nodes[0]['f'])-nodes[1]['f']));jump=max(float(np.linalg.norm(np.array(n['f'])-f)) for n,f in zip(nodes,seeds))
            require(separation>p['minimum_separation'] and jump<p['max_root_jump'],'duplicate pair or root jump')
            r['dimension']=s.model.dim
            row=dict(T=T,nodes=nodes,separation=separation,max_jump=jump,diagnostics=s.metrics)
            if any(abs(T-event['parameter']-off)<1e-12 for off in p['law_offsets']):
                row['separation_law']=separation_law(separation,T-event['parameter'],r['nondegeneracy']['trials'][-1]['squared_separation_coefficient'],p['law_tolerance'])
            r['states'].append(row);seeds=[n['f'] for n in nodes];write(path,r);print(engine,'ROOT',len(r['states']),T,separation,flush=True)
        require(r['states'][-1]['separation']<r['states'][0]['separation'],'pair not closing')
        for T in [state.T,event['parameter']+p['charge_offset']]:
            row=next(q for q in r['states'] if q['T']==T);s=make(replace(state,T=T));radius=min(.002,row['separation']/8)
            m=refined_pair(s,[n['f'] for n in row['nodes']],2,radius);join=pair_distance(m['nodes'],row['nodes'])
            require(join<1e-6,'charge roots changed');require(m['label']=='OPPOSITE','charge pair does not support annihilation')
            r['charges'].append(dict(T=T,measurement=m,root_join=join));write(path,r);print(engine,'CHARGE',T,m['label'],flush=True)
        for T in [event['parameter']-p['opening_offset'],p['T_window'][1]]:
            s=make(replace(state,T=T));fn=gap_objective(s,2);row=dict(T=T,trials=[]);r['open_checks'].append(row)
            extra=[event['f']]+[(np.array(event['f'])+d).tolist() for d in [[.002,.002],[-.002,-.002]]]
            for grid,edge in zip(p['grids'],p['edge_grids']):
                row['trials'].append(search(fn,grid,edge,extra,p['thresholds']));write(path,r);print(engine,'OPEN',T,grid,row['trials'][-1]['minimum']['gap'],flush=True)
            row.update(acceptance(row['trials'],p['thresholds']));row['diagnostics']=s.metrics;row['sampled_points']=len(s.cache);write(path,r)
        require(frozen()==p,'numerical plan changed during run');r['status']='ACCEPT_SAMPLED_LOWER_UNLINK'
    except Exception as error:
        r['status']='REJECT';r['failure']=dict(type=type(error).__name__,message=str(error),attempts=getattr(error,'attempts',[]),completed_refinements=getattr(error,'completed_refinements',[]),seed=getattr(error,'seed',None),boundary=getattr(error,'boundary',None),traceback=traceback.format_exc())
    r['runtime_after']=runtime_identity()
    if r['runtime_after']!=r['runtime_before']:r['status']='REJECT_RUNTIME_CHANGED'
    r['seconds']=time.time()-start;write(path,r);print(engine,r['status'],r['seconds'],flush=True)
    if r['status']!='ACCEPT_SAMPLED_LOWER_UNLINK':raise SystemExit(1)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('engine',choices=['bm_lab','ref_lab']);main(p.parse_args().engine)
