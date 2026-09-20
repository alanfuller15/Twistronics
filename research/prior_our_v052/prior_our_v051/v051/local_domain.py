"""Bounded local minima and edge searches, with no global-gap inference."""
import numpy as np
from scipy.optimize import least_squares,minimize,minimize_scalar
from measure import require

def bounds_array(box):
 b=np.asarray(box,float)
 require(b.shape==(2,2) and np.isfinite(b).all(),'invalid local box')
 require(np.all(b[:,0]<b[:,1]) and np.all(b>=0) and np.all(b<=1),'invalid local box')
 return b

def inside_margin(f,box):
 b=bounds_array(box);f=np.asarray(f,float)
 require(f.shape==(2,) and np.isfinite(f).all(),'invalid point')
 return float(min(np.min(f-b[:,0]),np.min(b[:,1]-f)))

def outside_distance(f,box):
 b=bounds_array(box);f=np.asarray(f,float)
 require(f.shape==(2,) and np.isfinite(f).all(),'invalid point')
 return float(np.linalg.norm(f-np.clip(f,b[:,0],b[:,1])))

def bounded_node(sample,seed,index,box):
 b=bounds_array(box);seed=np.asarray(seed,float);require(inside_margin(seed,box)>0,'node seed outside local domain')
 _,anchor=sample.frame(seed,index)
 sol=least_squares(lambda f:sample.vector(f,anchor,index)[0],seed,bounds=(b[:,0],b[:,1]),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=150)
 require(sol.success and np.isfinite(sol.x).all(),'local root optimizer failed')
 w,_=sample.frame(sol.x,index);gap=float(w[1]-w[0])
 require(np.isfinite(gap) and gap<1e-6 and inside_margin(sol.x,box)>.005,'local root unresolved or near boundary')
 return dict(f=sol.x.tolist(),gap=gap,index=index,nfev=sol.nfev,domain_margin=inside_margin(sol.x,box))

def gap_objective(sample,index):
 h0,_=sample.model.real_hamiltonian([0,0]);dh=[sample.model.real_hamiltonian(e)[0]-h0 for e in [[1,0],[0,1]]]
 def fn(f):
  w,v=sample.at(f);vec=v[:,index:index+2]
  slope=[np.einsum('ij,ij->j',vec,d@vec) for d in dh]
  gap=float(w[index+1]-w[index]);grad=np.array([s[1]-s[0] for s in slope])
  require(np.isfinite(gap) and np.isfinite(grad).all(),'nonfinite local objective')
  return gap,grad
 return fn

def bounded_minimum(fn,box,ng,extra=()):
 b=bounds_array(box);require(ng>=3,'local grid too small')
 axes=[np.linspace(*x,ng) for x in b];values=np.empty((ng,ng));seeds=[]
 for i,x in enumerate(axes[0]):
  for j,y in enumerate(axes[1]):values[i,j]=fn(np.array([x,y]))[0]
 require(np.isfinite(values).all(),'nonfinite local grid')
 for i,x in enumerate(axes[0]):
  for j,y in enumerate(axes[1]):
   patch=values[max(0,i-1):min(ng,i+2),max(0,j-1):min(ng,j+2)]
   if values[i,j]<=patch.min():seeds.append([x,y])
 for f in extra:
  require(inside_margin(f,box)>=0,'extra seed outside local domain');seeds.append(f)
 seeds.extend([[x,y] for x in b[0] for y in b[1]])
 rows=[]
 for seed in seeds:
  seed=np.asarray(seed,float);initial=float(fn(seed)[0]);attempts=[]
  for method in ['L-BFGS-B','SLSQP']:
   opts=dict(ftol=1e-14,gtol=1e-7,maxiter=300,maxls=40) if method=='L-BFGS-B' else dict(ftol=1e-12,maxiter=500)
   sol=minimize(fn,seed,method=method,jac=True,bounds=b,options=opts)
   valid=bool(sol.success and np.isfinite(sol.fun) and np.isfinite(sol.x).all() and inside_margin(sol.x,box)>=-1e-12 and sol.fun<=initial+1e-7)
   # Keep even invalid diagnostics JSON-serializable; do not promote failed attempts.
   attempts.append(dict(method=method,success=bool(sol.success),valid=valid,message=str(sol.message),value=float(sol.fun) if np.isfinite(sol.fun) else None))
   if valid:break
  require(valid,'local minimum failed or escaped domain or worsened seed')
  rows.append(dict(f=sol.x.tolist(),gap=float(sol.fun),seed=seed.tolist(),attempts=attempts))
 best=min(rows,key=lambda x:x['gap']);require(best['gap']<=float(values.min())+1e-7,'local minimum worse than grid')
 return dict(grid=ng,box=b.tolist(),grid_min=float(values.min()),minimum=best,refinements=rows)

def boundary_minimum(fn,box,ng):
 b=bounds_array(box);require(ng>=3,'boundary grid too small');rows=[]
 for fixed_axis in [0,1]:
  moving=1-fixed_axis
  for fixed in b[fixed_axis]:
   def point(t):
    f=np.zeros(2);f[fixed_axis]=fixed;f[moving]=t;return f
   def objective(t):return float(fn(point(t))[0])
   ts=np.linspace(*b[moving],ng+1);vs=np.array([objective(t) for t in ts]);require(np.isfinite(vs).all(),'nonfinite boundary grid')
   cand=[dict(t=float(ts[i]),gap=float(vs[i]),kind='endpoint') for i in [0,len(ts)-1]]
   for j in range(1,len(ts)-1):
    if vs[j]>min(vs[j-1],vs[j+1]):continue
    sol=minimize_scalar(objective,bounds=(ts[j-1],ts[j+1]),method='bounded',options=dict(xatol=1e-12,maxiter=200))
    require(sol.success and np.isfinite(sol.x) and np.isfinite(sol.fun) and ts[j-1]<=sol.x<=ts[j+1] and sol.fun<=vs[j]+1e-7,'edge minimizer failed or escaped bracket')
    cand.append(dict(t=float(sol.x),gap=float(sol.fun),kind='optimized',bracket=[float(ts[j-1]),float(ts[j+1])]))
   best=min(cand,key=lambda x:x['gap']);require(best['gap']<=float(vs.min())+1e-7,'edge minimum worse than grid')
   rows.append(dict(fixed_axis=fixed_axis,fixed=float(fixed),grid_min=float(vs.min()),minimum=dict(best,f=point(best['t']).tolist()),candidates=cand))
 return dict(grid=ng,box=b.tolist(),minimum=min(x['minimum']['gap'] for x in rows),edges=rows)

def require_positive_agreement(trials,kind):
 require(len(trials)==2,'two refinements required')
 vals=[x['minimum']['gap'] if kind=='interior' else x['minimum'] for x in trials]
 require(np.isfinite(vals).all() and min(vals)>1e-5,'local '+kind+' gap unresolved')
 require(abs(vals[0]-vals[1])<.01,'local '+kind+' mesh disagreement')
 return min(vals)
