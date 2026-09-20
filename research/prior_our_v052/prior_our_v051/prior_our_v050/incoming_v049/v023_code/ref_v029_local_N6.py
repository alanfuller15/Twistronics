import numpy as np
from tbg_ref import TBG
m=TBG(N=6,eps=0.003,phi=65,A=0.0,B=-0.40,Bt=-0.70,kinetic='full'); U=m.real_basis(); lo=m.dim//2-1; fn=m.flat_gap
ex=[m.refine(np.array(s),fn)[0] for s in [(0.6464,0.8378),(0.6273,0.834)]]
print("N=6 Btau=-0.70 flat pair:",[tuple(np.round(f,4)) for f in ex],"gaps",[f"{fn(f):.0e}" for f in ex],"sep %.4f"%np.linalg.norm(ex[0]-ex[1]))
w1,w2,lab=m.relative_charge(U,ex[0],ex[1],lo); print("   charges",w1,w2,"->",lab,"frame overlap smin %.3f"%m.last_smin)
