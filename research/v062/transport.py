"""Finite path transport with both exterior minima and adjacent-node seeds."""
import numpy as np
from scipy.optimize import minimize_scalar
from evidence import require


def transport(sample,a,b,base,index,steps,adjacent,align):
    a=np.asarray(a);b=np.asarray(b);d=b-a;length=float(np.linalg.norm(d));require(length>1e-5,'collapsed comparison path')
    ts=list(np.linspace(0,1,steps+1))
    for q in adjacent:
        q=np.asarray(q);t=float((q-a)@d/length**2)
        if not 0<t<1:continue
        dist=float(np.linalg.norm(q-a-t*d));scale=max(dist/length,1e-10);ts.append(t)
        for j in range(-2,9):ts.extend([t-scale*2**j,t+scale*2**j])
    ts=sorted(set(t for t in ts if 0<=t<=1));gaps=[]
    for t in ts:
        w,_=sample.at(a+t*d);gaps.append([w[index]-w[index-1],w[index+2]-w[index+1]])
    gaps=np.array(gaps);require(np.isfinite(gaps).all() and gaps.min()>1e-5,'sampled comparison loses isolation')
    minima=[]
    for column,gap_index in enumerate([index-1,index+1]):
        for j in range(1,len(ts)-1):
            if gaps[j,column]>min(gaps[j-1,column],gaps[j+1,column]):continue
            def objective(t):
                w,_=sample.at(a+t*d);v=float(w[gap_index+1]-w[gap_index]);require(np.isfinite(v),'nonfinite exterior gap');return v
            sol=minimize_scalar(objective,bounds=(ts[j-1],ts[j+1]),method='bounded',options=dict(xatol=1e-11,maxiter=200))
            valid=bool(sol.success and np.isfinite([sol.x,sol.fun]).all() and ts[j-1]<=sol.x<=ts[j+1] and sol.fun<=gaps[j,column]+1e-7 and sol.fun>1e-5)
            row=dict(gap_index=gap_index,t=float(sol.x) if np.isfinite(sol.x) else None,gap=float(sol.fun) if np.isfinite(sol.fun) else None,initial=float(gaps[j,column]),bracket=[ts[j-1],ts[j+1]],success=bool(sol.success),status=int(sol.status),message=str(sol.message),nfev=int(sol.nfev),valid=valid)
            minima.append(row)
            if not valid:
                error=ValueError('located comparison minimum rejected');error.attempts=minima;raise error
    h0,_=sample.model.real_hamiltonian(a);h1,_=sample.model.real_hamiltonian(b);bound=max(1.,2*np.linalg.norm(h1-h0));refined=list(ts)
    for row in minima:
        t=row['t'];scale=max(row['gap']/bound,1e-10);refined.append(t)
        for j in range(-2,21):refined.extend([t-scale*2**j,t+scale*2**j])
    refined=sorted(set(t for t in refined if 0<=t<=1));frame=base;minimum_overlap=1.;minimum_gap=float(gaps.min())
    for t in refined[1:]:
        w,_=sample.at(a+t*d);_,q=sample.frame(a+t*d,index);frame,s=align(q,frame)
        minimum_overlap=min(minimum_overlap,s);minimum_gap=min(minimum_gap,float(min(w[index]-w[index-1],w[index+2]-w[index+1])))
    return frame,dict(steps=steps,initial_t=ts,initial_exterior_gaps=gaps.tolist(),min_external_gap=minimum_gap,min_overlap=minimum_overlap,samples=len(refined),located_gap_minima=minima)
