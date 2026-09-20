import numpy as np, sys
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS
from braid import adjacent_nodes
xs=[[0.20,-0.30,0.0,0.0,0.0,80.0,0.003],
    [0.1871,-0.3094,0.009,-0.0048,0.0026,80.1756,0.0029],
    [0.1716,-0.3234,0.02,-0.0108,0.0056,80.8762,0.0029],
    [0.1525,-0.3439,0.0285,-0.0164,0.0092,82.4305,0.0029],
    [0.1326,-0.3661,0.0045,-0.02,0.0113,84.3659,0.003]]
F1=np.array([0.729,0.643]); F3=np.array([0.578,0.578])
for i,x in enumerate(xs):
    m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
    F1,v1=m.refine(F1,func); F3,v3=m.refine(F3,func)
    fl=[f for v,f in m.find_nodes(ngrid=40,nkeep=20) if v<1e-6]
    print(f"x{i}: tracked F1 {tuple(np.round(F1,3))} F3 {tuple(np.round(F3,3))} sep={frac_dist(F1,F3):.3f} | all flat nodes ({len(fl)}): {[tuple(np.round(f,3)) for f in fl]}")
    sys.stdout.flush()
