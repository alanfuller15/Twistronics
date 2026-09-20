import numpy as np, time, sys
from tbg_ref import TBG
part=sys.argv[1]
m=TBG(N=6,eps=0.003,phi=80,A=-0.30,B=-0.40,Bt=-1.8,w0=110.0*1.1,kinetic='full'); U=m.real_basis(); D=m.dim; t=time.time()
if part=='gaps':
    gaps=[m.gap_min(i,n=15,keep=3) for i in (0,1,2,3,4)]; fl=m.find_nodes(n=18,keep=6)
    print(f"N=6 endpoint gaps: below|lower {gaps[0]:.2f}, lower|flat1 {gaps[1]:.2f}, flat {gaps[2]:.3f}, flat2|upper {gaps[3]:.2f}, upper|next {gaps[4]:.2f} meV; flat nodes {len(fl)} ({time.time()-t:.0f}s)")
else:
    for lab,band in [('flat1',D//2-1),('flat2',D//2)]:
        print(f"N=6 {lab} w1 sign holonomy: k1 {m.band_sign_holonomy(U,band,0,0,n=80):+.2f},{m.band_sign_holonomy(U,band,0,0.5,n=80):+.2f}  k2 {m.band_sign_holonomy(U,band,1,0,n=80):+.2f},{m.band_sign_holonomy(U,band,1,0.5,n=80):+.2f}"); sys.stdout.flush()
    print(f"({time.time()-t:.0f}s)")
