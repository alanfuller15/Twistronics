import numpy as np, sys
from bm_strain import BM, frac_dist
A=0.20
for phi in [float(x) for x in sys.argv[1:]]:
    m=BM(N=4,eps=0.003,phi_deg=phi,A_scalar=A)
    func=lambda f: m.gaps(m.frac_to_k(f))[0]
    f1s=np.linspace(0.46,0.58,25); f2s=np.linspace(0.80,0.94,25)
    vals=np.array([[func(np.array([a,b])) for b in f2s] for a in f1s])
    cand=[]
    for i in range(1,24):
        for j in range(1,24):
            if vals[i,j]<=vals[i-1:i+2,j-1:j+2].min(): cand.append((vals[i,j],f1s[i],f2s[j]))
    found=[]
    for v,a,b in sorted(cand)[:6]:
        f,val=m.refine(np.array([a,b]),func)
        if all(frac_dist(f,g)>0.002 for _,g in found): found.append((val,f))
    print(f"phi={phi}: local minima of mid gap in box:", [(f"{v:.2e}",tuple(np.round(f,4))) for v,f in found])
