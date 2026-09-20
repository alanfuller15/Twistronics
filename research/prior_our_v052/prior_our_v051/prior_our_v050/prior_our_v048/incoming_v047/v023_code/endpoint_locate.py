import numpy as np, time, sys, json
from scipy.optimize import minimize
from tbg_ref import TBG
N=int(sys.argv[1]); seeds=json.loads(sys.argv[2]) if len(sys.argv)>2 else None
m=TBG(N=N,eps=0.003,phi=80,A=-0.30,B=-0.40,Bt=-1.8,w0=110.0*1.1,kinetic='lab_nn_full')
names={1:'lower|flat1',2:'flat',3:'flat2|upper',4:'upper|next'}
out={}
for i in (1,2,3,4):
    fn=m.gap(i); t=time.time()
    if seeds is None:
        n=12; fs=np.linspace(0,1,n,endpoint=False); V=np.array([[fn(np.array([a,b])) for b in fs] for a in fs])
        cand=sorted([(V[p,q],fs[p],fs[q]) for p in range(n) for q in range(n) if V[p,q]<=min(V[(p+dp)%n,(q+dq)%n] for dp in (-1,0,1) for dq in (-1,0,1))])[:3]
        starts=[np.array([a,b]) for _,a,b in cand]+([np.array([0.992,0.294])] if i==1 else [])
    else: starts=[np.array(seeds[str(i)])]
    best=(np.inf,None)
    for s0 in starts:
        r=minimize(lambda f: fn(np.array(f)),np.clip(s0,0,1),method='Nelder-Mead',bounds=[(0,1),(0,1)],options={'xatol':1e-7,'fatol':1e-9,'maxiter':400})
        if r.success and r.fun<best[0]: best=(r.fun,r.x)
    out[i]=best; print(f"N={N} {names[i]:12s}: {best[0]:.5f} meV at {tuple(np.round(best[1],5))} ({time.time()-t:.0f}s)"); sys.stdout.flush()
print("SEEDS",json.dumps({str(i):out[i][1].tolist() for i in out}))
