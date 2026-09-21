"""Bounded diagnostic of the rejected opening station; not acceptance evidence."""
import sys,json,hashlib
from pathlib import Path
from dataclasses import replace
import numpy as np
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(1,str(REPO/'research/v055'))
from evidence import read,sha,write,require,safe
from run_event import frozen
from models import State
from measure import Sample
from local_domain import gap_objective
from search import curvature

def main(engine):
    plan=read(ROOT/'recovery/DIAGNOSTIC_PLAN.json')
    for name,h in plan['source_sha256'].items():require(sha(safe(ROOT,name))==h,'diagnostic source changed')
    p=frozen();source=ROOT/'results'/f'first_ann_{engine}_N8.json';require(sha(source)==plan['rejected_sha256'][engine],'rejected evidence changed')
    initial=read(source);T=initial['event']['parameter']-.001;s=Sample(engine,8,replace(State(**p['state']),T=T));fn=gap_objective(s,3);f=np.array(plan['seeds'][engine]);rows=[]
    for i in range(plan['newton_steps']+1):
        value,g=fn(f);row=dict(iteration=i,f=f.tolist(),gap=value,gradient=g.tolist(),gradient_norm=float(np.max(np.abs(g))));rows.append(row)
        if row['gradient_norm']<=1e-6:break
        h=plan['jacobian_step'];J=np.column_stack([(fn(f+h*e)[1]-fn(f-h*e)[1])/(2*h) for e in np.eye(2)])
        d=np.linalg.solve(J,-g);require(np.isfinite(d).all() and np.linalg.norm(d)<.001,'diagnostic Newton step too large');f=f+d;require(np.all(f>0) and np.all(f<1),'diagnostic left chart')
    curves=[curvature(fn,f,h) for h in plan['curvature_steps']]
    write(ROOT/'results'/f'opening_diagnostic_{engine}_N8.json',dict(status='DIAGNOSTIC_ONLY',engine=engine,N=8,T=T,diagnostic_plan_sha256=sha(ROOT/'recovery/DIAGNOSTIC_PLAN.json'),rejected_source_sha256=sha(source),newton=rows,curvature=curves,diagnostics=s.metrics,sampled_points=len(s.cache)))
    print(engine,json.dumps(dict(newton=rows,curvature=curves)),flush=True)

if __name__=='__main__':main(sys.argv[1])
