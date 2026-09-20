"""Seven sampled N4 sensitivity configurations, using the full pair gate."""
import json,time,traceback
from pathlib import Path
from dataclasses import asdict
from models import State
from measure import Sample,require
from pair_measure import refined_pair
from boundary_audit import seeds as boundary_seeds
from checkpoints import save_json,digest
ROOT=Path(__file__).resolve().parent

def run():
    out=dict(status='RUNNING',engine='bm_exact',N=4,source_sha256=digest(__file__),scope='three baseline configurations and four braid endpoints; finite samples, not a physical bound',rows=[])
    path=ROOT/'results/sensitivity.json';tick=time.time()
    for kappa in [0.,5.,-5.]:
        p=State(A=0,B=0,T=0,phi=0,ratio=.8,w_kappa=kappa,w_mode='average' if kappa==0 else 'layer1')
        s=Sample('bm_exact',4,p)
        pair=refined_pair(s,[[.5816,.7266],[.7594,.6066]],3,.004)
        gaps={}
        for name,index in [('lower',2),('upper',4)]:
            trials=[]
            for ng in [18,24]:
                previous=[r['f'] for t in trials for r in t['refinements']]
                trials.append(s.minimum(index,ng,extra=boundary_seeds(s,index,previous)))
            require(abs(trials[0]['minimum']['gap']-trials[1]['minimum']['gap'])<.01,'sensitivity gap grid disagreement')
            require(min(t['minimum']['gap'] for t in trials)>1e-5,'baseline remote isolation unresolved')
            gaps[name]=trials
        row=dict(kind='baseline',state=asdict(p),pair=pair,gaps=gaps,remote_gap=min(t['minimum']['gap'] for ts in gaps.values() for t in ts),diagnostics=s.metrics)
        out['rows'].append(row);save_json(path,out);print('sensitivity',kappa,'baseline',pair['label'],row['remote_gap'],flush=True)
    for kappa in [5.,-5.]:
        for B in [-.25,-.30]:
            p=State(A=.2,B=B,T=0,phi=0,ratio=.8,w_kappa=kappa,w_mode='layer1')
            s=Sample('bm_exact',4,p);pair=refined_pair(s,[[.746,.612],[.518,.828]],3,.004)
            out['rows'].append(dict(kind='braid_endpoint',state=asdict(p),pair=pair,diagnostics=s.metrics));save_json(path,out)
            print('sensitivity',kappa,B,pair['label'],flush=True)
    out.update(status='ACCEPT',seconds=time.time()-tick);save_json(path,out)
if __name__=='__main__':
    try:run()
    except Exception as e:
        save_json(ROOT/'results'/f'sensitivity_failure_{time.time_ns()}.json',dict(status='REJECTED',error=str(e),traceback=traceback.format_exc()))
        raise
