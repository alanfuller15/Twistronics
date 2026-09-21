"""Resolve both exterior-gap minima along a declared straight comparison path."""
import numpy as np
from scipy.optimize import minimize_scalar
from measure import require,align

def transport(sample,a,b,base,index,steps):
    a=np.asarray(a);b=np.asarray(b);d=b-a;require(np.linalg.norm(d)>1e-5,'collapsed comparison path')
    ts=list(np.linspace(0,1,steps+1));gaps=[]
    for t in ts:
        w,_=sample.at(a+t*d);gaps.append([w[index]-w[index-1],w[index+2]-w[index+1]])
    gaps=np.array(gaps);minima=[]
    h0,_=sample.model.real_hamiltonian(a);h1,_=sample.model.real_hamiltonian(b)
    bound=max(1.,2*np.linalg.norm(h1-h0))
    for column,gap_index in enumerate([index-1,index+1]):
        for i in range(1,len(ts)-1):
            if gaps[i,column]>min(gaps[i-1,column],gaps[i+1,column]):continue
            def objective(t):
                w,_=sample.at(a+t*d);return float(w[gap_index+1]-w[gap_index])
            sol=minimize_scalar(objective,bounds=(ts[i-1],ts[i+1]),method='bounded',options={'xatol':1e-11,'maxiter':150})
            require(sol.success and sol.fun<=gaps[i,column]+1e-7,'connecting-gap minimization failed')
            require(sol.fun>1e-5,'comparison path loses isolation')
            minima.append(dict(t=float(sol.x),gap=float(sol.fun),gap_index=gap_index))
    refined=list(ts)
    for q in minima:
        t=q['t'];scale=max(q['gap']/bound,1e-10);refined.append(t)
        for j in range(-2,21):refined.extend([t-scale*2**j,t+scale*2**j])
    refined=sorted(set(t for t in refined if 0<=t<=1));frame=base;overlap=1.;mingap=float(gaps.min())
    for t in refined[1:]:
        f=a+t*d;w,_=sample.at(f);_,q=sample.frame(f,index);frame,s=align(q,frame)
        overlap=min(overlap,s);mingap=min(mingap,float(min(w[index]-w[index-1],w[index+2]-w[index+1])))
    return frame,dict(min_overlap=overlap,min_external_gap=mingap,samples=len(refined),located_gap_minima=minima)
