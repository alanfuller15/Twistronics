import numpy as np, sys
from bm_strain import BM, frac_dist
for phi in [0,15,30,45,60,90]:
    m=BM(N=4,eps=0.003,phi_deg=phi)
    nodes=[(v,f) for v,f in m.find_nodes(ngrid=15,nkeep=6) if v<1e-6]
    rem=m.min_remote(ngrid=15,nkeep=4)
    sep=frac_dist(nodes[0][1],nodes[1][1]) if len(nodes)>=2 else float('nan')
    print(f"phi={phi:3d}  bandwidth={m.flat_bandwidth(12):6.2f} meV  nodes={len(nodes)}  sep={sep:.4f}  min remote={rem[0]:.3f} meV at {np.round(rem[1],3)}")
