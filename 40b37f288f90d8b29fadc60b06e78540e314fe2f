"""Bounded two-root continuation and explicitly diagnosed fold location."""
from dataclasses import replace
import numpy as np
from scipy.optimize import least_squares
from evidence import require


def margin(f,box):
    b=np.asarray(box,float);f=np.asarray(f,float)
    require(f.shape==(2,) and np.isfinite(f).all(),'nonfinite root coordinate')
    return float(min(np.min(f-b[:,0]),np.min(b[:,1]-f)))


def root(sample,seed,index,box):
    require(margin(seed,box)>.005,'seed outside declared domain')
    _,anchor=sample.frame(seed,index);b=np.asarray(box,float)
    sol=least_squares(lambda f:sample.vector(f,anchor,index)[0],seed,bounds=(b[:,0],b[:,1]),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=150)
    finite=bool(np.isfinite(sol.x).all() and np.isfinite(sol.fun).all())
    row=dict(seed=list(seed),success=bool(sol.success),status=int(sol.status),message=str(sol.message),nfev=int(sol.nfev),f=sol.x.tolist() if finite else None,
             residual=float(np.linalg.norm(sol.fun)) if finite else None,index=index)
    if not sol.success or not finite or row['residual']>=1e-6:
        error=ValueError('root optimizer failed/nonfinite/unresolved');error.attempts=[row];raise error
    w,_=sample.frame(sol.x,index);row['gap']=float(w[1]-w[0]);row['domain_margin']=margin(sol.x,box)
    require(row['gap']<1e-6 and row['domain_margin']>.005,'root residual or domain gate failed')
    return row


def spatial_jac(sample,f,anchor,index,h):
    return np.column_stack([(sample.vector(np.asarray(f)+h*e,anchor,index)[0]-sample.vector(np.asarray(f)-h*e,anchor,index)[0])/(2*h) for e in np.eye(2)])


def locate(make_sample,initial_state,seeds,guess,box,window,index):
    initial=make_sample(initial_state);nodes=[root(initial,f,index,box) for f in seeds]
    a,b=[np.array(n['f']) for n in nodes];require(np.linalg.norm(b-a)>.005,'initial duplicate roots')
    center=(a+b)/2;_,anchor=initial.frame(center,index);cache={}
    def at(T):
        key=float(T)
        if key not in cache:
            if len(cache)>8:cache.clear()
            cache[key]=make_sample(replace(initial_state,T=key))
        return cache[key]
    def objective(x,h):
        s=at(x[2]);d=s.vector(x[:2],anchor,index)[0];J=spatial_jac(s,x[:2],anchor,index,h)
        return np.r_[d,.02*np.linalg.det(J)/max(1.,np.linalg.norm(J))]
    trials=[];x=np.r_[center,guess];low,high=sorted(window)
    for h in [2e-5,1e-5]:
        sol=least_squares(lambda x:objective(x,h),x,bounds=([box[0][0],box[1][0],low],[box[0][1],box[1][1],high]),diff_step=1e-4,xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=160)
        finite=bool(np.isfinite(sol.x).all() and np.isfinite(sol.fun).all())
        metadata=dict(success=bool(sol.success),status=int(sol.status),message=str(sol.message),nfev=int(sol.nfev),h=h)
        if not sol.success or not finite:
            error=ValueError('fold optimizer failed or nonfinite');error.attempts=trials+[metadata];raise error
        x=sol.x;s=at(x[2]);res=objective(x,h);J=spatial_jac(s,x[:2],anchor,index,h);u,sv,vh=np.linalg.svd(J)
        w,_=s.at(x[:2]);external=float(min(w[index]-w[index-1],w[index+2]-w[index+1]))
        row=dict(metadata,parameter=float(x[2]),f=x[:2].tolist(),residual=res.tolist(),singular_values=sv.tolist(),null_direction=vh[-1].tolist(),gap=float(w[index+1]-w[index]),external_gap=external,diagnostics=dict(s.metrics))
        valid=bool(np.linalg.norm(res[:2])<1e-6 and row['gap']<1e-6 and sv[-1]<1e-3 and sv[0]>1 and external>1e-5 and margin(x[:2],box)>.005)
        trials.append(row)
        if not valid:
            error=ValueError('fold residual/rank/isolation/domain rejected');error.attempts=trials;raise error
    require(abs(trials[0]['parameter']-trials[1]['parameter'])<1e-6,'fold derivative refinement failed')
    return dict(initial_nodes=nodes,fold_trials=trials,parameter=trials[-1]['parameter'],f=trials[-1]['f'])


def require_character(rows,pair_side):
    require(len(rows)==2,'two character meshes required')
    for r in rows:
        a,b=r['curvature'],r['parameter_slope']
        require(np.isfinite([a,b]).all() and abs(a)>1 and abs(b)>.01,'degenerate fold character')
        require(-2*b*pair_side/a>0,'fold predicts wrong pair side')
        require(abs(r['squared_separation_coefficient']+8*b/a)<1e-12,'fold coefficient mismatch')
    for name in ['curvature','parameter_slope']:
        require(abs(rows[1][name]-rows[0][name])<.01*abs(rows[1][name]),'fold character refinement failed')


def character(make_sample,state,event,index):
    state=replace(state,T=event['parameter']);f=np.array(event['f']);s=make_sample(state);_,anchor=s.frame(f,index)
    J=spatial_jac(s,f,anchor,index,1e-5);u,sv,vh=np.linalg.svd(J);null=vh[-1];left=u[:,-1];rows=[]
    for h in [2e-4,1e-4]:
        d0=s.vector(f,anchor,index)[0];dp=s.vector(f+h*null,anchor,index)[0];dm=s.vector(f-h*null,anchor,index)[0]
        curvature=float(left@(dp-2*d0+dm)/h**2)
        plus=make_sample(replace(state,T=state.T+h));minus=make_sample(replace(state,T=state.T-h))
        slope=float(left@(plus.vector(f,anchor,index)[0]-minus.vector(f,anchor,index)[0])/(2*h))
        rows.append(dict(step=h,curvature=curvature,parameter_slope=slope,squared_separation_coefficient=-8*slope/curvature if curvature else None))
    require_character(rows,1.)
    return dict(status='PASS',trials=rows)


def separation_law(separation,offset,coefficient,tolerance):
    require(np.isfinite([separation,offset,coefficient]).all() and min(separation,offset,coefficient)>0,'invalid separation law inputs')
    ratio=separation**2/(coefficient*offset)
    require(abs(ratio-1)<=tolerance,'near-fold separation disagrees with normal form')
    return dict(offset=offset,separation=separation,predicted_squared_separation=coefficient*offset,observed_to_predicted_ratio=ratio,relative_error=abs(ratio-1))
