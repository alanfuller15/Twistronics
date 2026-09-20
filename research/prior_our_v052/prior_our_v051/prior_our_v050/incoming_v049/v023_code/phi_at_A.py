import numpy as np, sys
from bm_strain import BM
from braid import adjacent_nodes
A=float(sys.argv[1]); phis=[float(x) for x in sys.argv[2:]]
for phi in phis:
    m=BM(N=4,eps=0.003,phi_deg=phi,A_scalar=A)
    flat=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]
    adj=adjacent_nodes(m,ngrid=36)
    rem=m.min_remote(ngrid=15,nkeep=4)
    print(f"phi={phi:5.1f} flat={len(flat)} up={len(adj['+'])} lo={len(adj['-'])} minrem={rem[0]:.2e} bw={m.flat_bandwidth(10):.1f}")
    print("    flat:",[tuple(np.round(f,3)) for f in flat])
    print("    up  :",[tuple(np.round(f,3)) for _,f in adj['+']], " lo:",[tuple(np.round(f,3)) for _,f in adj['-']])
    sys.stdout.flush()
