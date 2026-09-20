"""Guarded local three-start endpoint minima at N6/N8; no global N8 claim."""
import json,time,traceback
from dataclasses import asdict
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from models import State
from measure import Sample,require,GAPS
from checkpoints import save_json,digest
ROOT=Path(__file__).resolve().parent
SEEDS={
'lower':[.99073257052202,.28845422529655934],
'flat':[.6767776492194484,.9188749642137635],
'upper':[.6123307014554817,.9221554859731114],
'next':[.19900288378045922,.751706795703863]}

def run(N):
    p=State(A=-.30,B=-.4,T=-1.8,phi=80,ratio=1.1);s=Sample('ref_lab',N,p)
    h0=s.model.real_hamiltonian([0,0])[0]
    dh=[s.model.real_hamiltonian(e)[0]-h0 for e in [[1,0],[0,1]]]
    out=dict(status='RUNNING',N=N,engine='ref_lab',state=asdict(p),dimension=s.model.dim,scope='local multistart at four previously located minima',source_sha256=digest(__file__),gaps={})
    path=ROOT/'results'/f'endpoint_local_N{N}.json';tick=time.time()
    for name,index in GAPS.items():
        def objective(f):
            w,v=s.at(f);v=v[:,index:index+2]
            slopes=[np.einsum('ij,ij->j',v,d@v) for d in dh]
            return float(w[index+1]-w[index]),np.array([a[1]-a[0] for a in slopes])
        rows=[]
        for offset in [[0,0],[.002,-.002],[-.002,.002]]:
            seed=np.clip(np.array(SEEDS[name])+offset,0,1);initial=objective(seed)[0];attempts=[]
            for method,opts in [('L-BFGS-B',dict(ftol=1e-14,gtol=1e-8,maxiter=300,maxls=40)),('SLSQP',dict(ftol=1e-13,maxiter=500))]:
                sol=minimize(objective,seed,method=method,jac=True,bounds=[(0,1),(0,1)],options=opts)
                gap,grad=objective(sol.x);projected=sol.x-np.clip(sol.x-grad,0,1)
                ok=bool(sol.success and np.isfinite(gap) and gap<=initial+1e-7 and np.linalg.norm(projected,np.inf)<1e-4)
                attempts.append(dict(method=method,success=bool(sol.success),message=str(sol.message),gap=gap,f=sol.x.tolist(),projected_gradient=float(np.linalg.norm(projected,np.inf)),accepted=ok))
                if ok:break
            require(ok,'endpoint local refinement fails guard')
            h=1e-5;hess=np.column_stack([(objective(sol.x+h*e)[1]-objective(sol.x-h*e)[1])/(2*h) for e in np.eye(2)])
            curvature=np.linalg.eigvalsh((hess+hess.T)/2);require(curvature.min()>0,'endpoint candidate not a local minimum')
            rows.append(dict(seed=seed.tolist(),seed_gap=initial,f=sol.x.tolist(),gap=gap,gradient=grad.tolist(),curvatures=curvature.tolist(),attempts=attempts))
        require(max(r['gap'] for r in rows)-min(r['gap'] for r in rows)<1e-7,'local multistart disagreement')
        out['gaps'][name]=dict(minimum=min(rows,key=lambda r:r['gap']),trials=rows)
        out['diagnostics']=dict(s.metrics);save_json(path,out)
        print('endpoint',N,name,out['gaps'][name]['minimum']['gap'],flush=True)
        s.cache.clear()
    out.update(status='ACCEPT',seconds=time.time()-tick);save_json(path,out)
    return out
if __name__=='__main__':
    try:
        for N in [6,8]:run(N)
    except Exception as e:
        save_json(ROOT/'results'/f'endpoint_local_failure_{time.time_ns()}.json',dict(status='REJECTED',error=str(e),traceback=traceback.format_exc()))
        raise
