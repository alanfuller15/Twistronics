"""Fold solver bounded to the explicitly declared full momentum chart."""
from dataclasses import replace
import numpy as np
from scipy.optimize import least_squares
from measure import Sample,require
from local_domain import bounded_node
def spatial_jac(sample,f,anchor,index,h):
    return np.column_stack([(sample.vector(np.asarray(f)+h*e,anchor,index)[0]-sample.vector(np.asarray(f)-h*e,anchor,index)[0])/(2*h) for e in np.eye(2)])

def locate(engine,N,c):
    index=c['index'];initial=Sample(engine,N,c['p']);nodes=[bounded_node(initial,seed,index,c['box']) for seed in c['seeds']]
    a,b=[np.array(n['f']) for n in nodes];require(np.linalg.norm(b-a)>.005,'initial duplicate roots')
    center=(a+b)/2;_,anchor=initial.frame(center,index)
    low,high=sorted([c['pair_at'],c['gapped_at']]);cache={}
    def at(parameter):
        key=float(parameter)
        if key not in cache:
            # Bound memory: only a few fold objective calls need reuse.
            if len(cache)>8:cache.clear()
            cache[key]=Sample(engine,N,replace(c['p'],**{c['key']:key}))
        return cache[key]
    def objective(x,h):
        s=at(x[2]);d=s.vector(x[:2],anchor,index)[0];J=spatial_jac(s,x[:2],anchor,index,h)
        return np.r_[d,.02*np.linalg.det(J)/max(1.,np.linalg.norm(J))]
    records=[];x=np.r_[center,c['guess']]
    for h in [2e-5,1e-5]:
        sol=least_squares(lambda x:objective(x,h),x,bounds=([c['box'][0][0],c['box'][1][0],low],[c['box'][0][1],c['box'][1][1],high]),diff_step=1e-4,xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=160)
        x=sol.x;s=at(x[2]);res=objective(x,h);J=spatial_jac(s,x[:2],anchor,index,h);u,sv,vh=np.linalg.svd(J)
        w,_=s.at(x[:2]);external=float(min(w[index]-w[index-1],w[index+2]-w[index+1]))
        require(sol.success and np.linalg.norm(res[:2])<1e-6,'fold root not converged')
        require(sv[-1]<1e-3 and sv[0]>1.,'fold Jacobian not rank one')
        require(external>1e-5,'fold touches adjacent band')
        records.append(dict(parameter=float(x[2]),f=x[:2].tolist(),h=h,residual=res.tolist(),singular_values=sv.tolist(),null_direction=vh[-1].tolist(),gap=float(w[index+1]-w[index]),external_gap=external,nfev=sol.nfev))
    require(abs(records[0]['parameter']-records[1]['parameter'])<1e-6,'fold location fails derivative refinement')
    return dict(initial_nodes=nodes,fold_trials=records,parameter=records[-1]['parameter'],f=records[-1]['f'])
