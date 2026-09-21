"""One frozen N8 endpoint case; no network, tests, or publication invoked here."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys,time,traceback
import numpy as np
from evidence import read,sha,write,require,safe
from test_evidence import runtime_identity
from search import search,acceptance,checked
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]


def frozen():
    p=read(ROOT/'NUMERICAL_PLAN.json')
    for name,h in p['runner_sha256'].items():require(sha(safe(ROOT,name))==h,'runner changed: '+name)
    for name,h in p['inputs'].items():require(sha(safe(REPO,name))==h,'input changed: '+name)
    return p


def main(engine):
    plan=frozen();require(engine in plan['engines'],'unknown engine')
    path=ROOT/'results'/f'{engine}_N8.json';require(not path.exists(),'refusing to overwrite numerical run')
    started=time.time();runtime=runtime_identity()
    sys.path.insert(0,str(REPO/plan['model_root']))
    from models import State
    from measure import Sample,GAPS
    from local_domain import gap_objective
    record=dict(engine=engine,N=8,status='RUNNING',started_utc=datetime.now(timezone.utc).isoformat(),state=plan['state'],
                numerical_plan_sha256=sha(ROOT/'NUMERICAL_PLAN.json'),runtime_before=runtime,gaps={})
    write(path,record)
    try:
        sample=Sample(engine,8,State(**plan['state']))
        record['dimension']=sample.model.dim;record['geometry']=sample.model.geometry;record['cutoff_tol']=sample.model.cutoff_tol
        # Confirm the affine fractional Hamiltonian used by analytic gap gradients.
        h0,_=sample.model.real_hamiltonian([0,0]);d=[sample.model.real_hamiltonian(e)[0]-h0 for e in [[1,0],[0,1]]]
        h,_=sample.model.real_hamiltonian([.37,.61]);affine=float(np.max(np.abs(h-h0-.37*d[0]-.61*d[1])))
        require(affine<plan['thresholds']['affine_residual'],'Hamiltonian not affine in chart');record['affine_residual']=affine
        for name,index in GAPS.items():
            fn=gap_objective(sample,index);probe=np.array([.37,.61]);h=1e-5;v,g=checked(fn,probe)
            fd=np.array([(checked(fn,probe+h*e)[0]-checked(fn,probe-h*e)[0])/(2*h) for e in np.eye(2)])
            gradient_error=float(np.max(np.abs(fd-g)));require(gradient_error<plan['thresholds']['gradient_check'],'analytic gradient mismatch')
            row=dict(index_in_eight_bands=index,gradient_check=dict(f=probe.tolist(),step=h,analytic=g.tolist(),finite_difference=fd.tolist(),max_error=gradient_error),trials=[])
            record['gaps'][name]=row
            for grid,edge_grid in zip(plan['grids'],plan['edge_grids']):
                row['trials'].append(search(fn,grid,edge_grid,plan['seeds'][engine][name],plan['thresholds']))
                write(path,record);print(engine,name,grid,row['trials'][-1]['minimum']['gap'],'seconds',round(time.time()-started),flush=True)
            row.update(acceptance(row['trials'],plan['thresholds']));write(path,record)
        require(frozen()==plan,'plan changed during numerical run')
        record['status']='ACCEPT_SAMPLED_ENDPOINT_GAPS'
    except Exception as error:
        record['status']='REJECT';record['failure']=dict(type=type(error).__name__,message=str(error),attempts=getattr(error,'attempts',[]),seed=getattr(error,'seed',None),completed_refinements=getattr(error,'completed_refinements',[]),boundary=getattr(error,'boundary',None),traceback=traceback.format_exc())
    record['runtime_after']=runtime_identity()
    if record['runtime_after']!=record['runtime_before']:record['status']='REJECT_RUNTIME_CHANGED'
    record['seconds']=time.time()-started
    if 'sample' in locals():record['diagnostics']=sample.metrics;record['sampled_points']=len(sample.cache)
    write(path,record);print(engine,record['status'],record['seconds'],flush=True)
    if record['status']!='ACCEPT_SAMPLED_ENDPOINT_GAPS':raise SystemExit(1)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('engine',choices=['bm_lab','ref_lab']);main(p.parse_args().engine)
