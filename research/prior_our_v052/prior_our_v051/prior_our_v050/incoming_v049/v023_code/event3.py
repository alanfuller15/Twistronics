import numpy as np, sys
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS
xa=np.array([-0.0014,-0.3358,-0.0126,-0.3396,0.1222,6.8518,0.0013]); xb=np.array([-0.0104,-0.3294,-0.0197,-0.3786,0.1467,6.9313,0.0009])
F1=np.array([0.665,0.734]); F3=np.array([0.622,0.732])
for lam in [1.1,1.2,1.3,1.4,1.5,1.6,1.8,2.0]:
    x=xa+lam*(xb-xa); m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
    a,va=m.refine(F1,func); b,vb=m.refine(F3,func); mid=(F1+F3)/2; c,vc=m.refine(mid,func)
    # dense 1D scan along the line through F1,F3 for the minimum gap
    ts=np.linspace(-0.5,1.5,81); line=[(func(F1+t*(F3-F1)),t) for t in ts]; lm=min(line)
    print(f"lam={lam:.1f}: F1 {tuple(np.round(a,3))} ({va:.1e}) F3 {tuple(np.round(b,3))} ({vb:.1e}) sep={frac_dist(a,b):.4f} | min gap on line {lm[0]:.2e} at t={lm[1]:.2f} | eps={x[6]:.4f} A={x[0]:.3f}")
    sys.stdout.flush()
    if max(va,vb)>1e-6 or frac_dist(a,b)<0.003: print("   >>> pair gone / merged"); 
    else: F1,F3=a,b
