import numpy as np, sys, json
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS
st=json.load(open('descend4_state.json')); x0=np.array(st['x']); P=st['P']
F1=np.array(P['F1']); F3=np.array(P['F3']); L1=np.array(P['L1'])
print("x0=",np.round(x0,4).tolist(),"F1",np.round(F1,4).tolist(),"F3",np.round(F3,4).tolist())
ki=int(sys.argv[1]); kj=int(sys.argv[2]); di=float(sys.argv[3]); dj=float(sys.argv[4]); n=int(sys.argv[5])
def low(m): return lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2))
for a in np.linspace(-di,di,n):
    row=[]
    for b in np.linspace(-dj,dj,n):
        x=x0.copy(); x[ki]+=a; x[kj]+=b; m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
        p,vp=m.refine(F1,func); q,vq=m.refine(F3,func); mid,vm=m.refine((F1+F3)/2,func)
        l,vl=m.refine(L1,low(m))
        d=F3-F1; L=np.linalg.norm(d); nn=np.array([-d[1],d[0]])/L; rel=((l-F1)+0.5)%1-0.5
        s=frac_dist(p,q) if max(vp,vq)<1e-6 else float('nan')
        row.append(f"{s:.3f}/{vm:.1e}/L{rel@nn:+.3f}" )
    print(f"{KEYS[ki]}={x0[ki]+a:+.4f}: "+"  ".join(row)); sys.stdout.flush()
