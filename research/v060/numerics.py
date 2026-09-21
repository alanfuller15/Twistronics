"""Bounded roots in a declared unwrapped chart and diagnosed crossing solves."""
import numpy as np
from scipy.optimize import least_squares,brentq
from evidence import require


def margin(f,box):
    f=np.asarray(f,float);b=np.asarray(box,float)
    require(f.shape==(2,) and np.isfinite(f).all(),'invalid root coordinate')
    return float(min(np.min(f-b[:,0]),np.min(b[:,1]-f)))


def root(sample,seed,index,box):
    require(margin(seed,box)>.005,'seed outside declared lift')
    _,anchor=sample.frame(seed,index);b=np.asarray(box,float)
    sol=least_squares(lambda f:sample.vector(f,anchor,index)[0],seed,bounds=(b[:,0],b[:,1]),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=150)
    finite=bool(np.isfinite(sol.x).all() and np.isfinite(sol.fun).all())
    row=dict(seed=list(seed),success=bool(sol.success),status=int(sol.status),message=str(sol.message),nfev=int(sol.nfev),f=sol.x.tolist() if finite else None,residual=float(np.linalg.norm(sol.fun)) if finite else None,index=index)
    valid=bool(sol.success and finite and row['residual']<1e-6 and margin(sol.x,box)>.005)
    if valid:
        w,_=sample.frame(sol.x,index);row['gap']=float(w[1]-w[0]);row['domain_margin']=margin(sol.x,box);valid=bool(np.isfinite(row['gap']) and row['gap']<1e-6)
    if not valid:
        error=ValueError('root optimizer/residual/domain rejected');error.attempts=[row];raise error
    return row


def crossing(fn,bracket,xtols):
    vals=[float(fn(x)) for x in bracket];require(np.isfinite(vals).all() and vals[0]*vals[1]<0,'crossing not bracketed')
    trials=[]
    for tol in xtols:
        value,sol=brentq(fn,*bracket,xtol=tol,full_output=True,disp=False,maxiter=100)
        residual=float(fn(value));row=dict(ratio=float(value),xtol=tol,converged=bool(sol.converged),iterations=int(sol.iterations),function_calls=int(sol.function_calls),flag=str(sol.flag),offset=residual)
        trials.append(row)
        if not sol.converged or not np.isfinite([value,residual]).all() or abs(residual)>=1e-7:
            error=ValueError('crossing solve unresolved');error.attempts=trials;raise error
    require(abs(trials[-1]['ratio']-trials[0]['ratio'])<1e-8,'crossing tolerance disagreement')
    return dict(ratio=trials[-1]['ratio'],bracket=bracket,endpoint_offsets=vals,trials=trials)


def require_isolation_rejection(sample,point,index):
    try:sample.frame(point,index)
    except ValueError as error:
        require(str(error)=='selected group loses isolation','crossing failed for an unrelated reason')
        return str(error)
    raise ValueError('singular comparison was not rejected')
