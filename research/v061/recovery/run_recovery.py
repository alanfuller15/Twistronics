"""Resume only rejected opening and unmeasured upper-pair witnesses."""
import sys,json,time,traceback
from pathlib import Path
from datetime import datetime,timezone
from dataclasses import replace
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'recovery'));sys.path.insert(1,str(ROOT));sys.path.insert(2,str(REPO/'research/v055'))
import numpy as np
from evidence import read,sha,write,require,safe
from run_event import frozen
from test_evidence import runtime_identity
from search_recovery import search,acceptance


def recovery_plan():
    p=read(ROOT/'recovery/NUMERICAL_PLAN.json')
    for name,h in p['source_sha256'].items():require(sha(safe(ROOT,name))==h,'recovery source changed: '+name)
    for name,h in p['input_sha256'].items():require(sha(safe(ROOT,name))==h,'recovery input changed: '+name)
    return p


def main(engine):
    rp=recovery_plan();p=frozen();require(engine in p['engines'],'unknown engine');source=ROOT/'results'/f'first_ann_{engine}_N8.json';old=read(source)
    require(old['status']=='REJECT' and old['failure']['message']==rp['expected_rejections'][engine],'unexpected original failure')
    require(len(old['states'])==p['root_states'] and len(old['charges'])==p['charge_stations'],'incomplete reusable event prefix')
    path=ROOT/'results'/f'opening_recovery_{engine}_N8.json';require(not path.exists(),'refusing to overwrite recovery');start=time.time();runtime=runtime_identity()
    require(old['runtime_before']==old['runtime_after']==json.loads(json.dumps(runtime)),'recovery runtime differs from initial run')
    from models import State
    from measure import Sample
    from local_domain import gap_objective
    from pair_measure import refined_pair
    state=State(**p['state']);event=old['event'];r=dict(engine=engine,N=8,status='RUNNING',started_utc=datetime.now(timezone.utc).isoformat(),recovery_plan_sha256=sha(ROOT/'recovery/NUMERICAL_PLAN.json'),initial_result_sha256=sha(source),runtime_before=runtime,open_checks=[]);write(path,r)
    try:
        for T in [event['parameter']-p['opening_offset'],p['T_window'][1]]:
            s=Sample(engine,8,replace(state,T=T));fn=gap_objective(s,p['gap_index']);row=dict(T=T,trials=[]);r['open_checks'].append(row)
            extra=[event['f']]+[(np.array(event['f'])+d).tolist() for d in [[.002,.002],[-.002,-.002]]]
            for grid,edge in zip(p['grids'],p['edge_grids']):
                row['trials'].append(search(fn,grid,edge,extra,rp['thresholds']));write(path,r);print(engine,'RECOVERY OPEN',T,grid,row['trials'][-1]['minimum']['gap'],flush=True)
            row.update(acceptance(row['trials'],rp['thresholds']));row['diagnostics']=s.metrics;row['sampled_points']=len(s.cache);write(path,r)
        s=Sample(engine,8,replace(state,T=p['T_window'][1]));m=refined_pair(s,p['upper_seeds'][engine],4,p['upper_radius'],p['box']);r['post_transfer']=dict(T=p['T_window'][1],index=4,measurement=m);write(path,r)
        require(m['label']=='SAME','post-transfer upper pair differs from target');require(recovery_plan()==rp and frozen()==p,'plan changed during recovery');r['status']='ACCEPT_RECOVERED_WITNESSES'
    except Exception as error:
        r['status']='REJECT';r['failure']=dict(type=type(error).__name__,message=str(error),attempts=getattr(error,'attempts',[]),completed_refinements=getattr(error,'completed_refinements',[]),boundary=getattr(error,'boundary',None),seed=getattr(error,'seed',None),curvature=getattr(error,'curvature',[]),partial_search=getattr(error,'partial_search',None),traceback=traceback.format_exc())
    r['runtime_after']=runtime_identity()
    if r['runtime_after']!=r['runtime_before']:r['status']='REJECT_RUNTIME_CHANGED'
    r['seconds']=time.time()-start;write(path,r);print(engine,r['status'],r['seconds'],flush=True)
    if r['status']!='ACCEPT_RECOVERED_WITNESSES':raise SystemExit(1)

if __name__=='__main__':main(sys.argv[1])
