import numpy as np, sys
from bm_strain import BM
from braid import adjacent_nodes
for A in [0.30,0.40,0.50]:
    m=BM(N=4,eps=0.003,A_scalar=A)
    flat=[f for v,f in m.find_nodes(ngrid=30,nkeep=16) if v<1e-6]
    adj=adjacent_nodes(m,ngrid=36)
    print(f"A={A}: flat-gap nodes {len(flat)} {[np.round(f,3) for f in flat]}; upper-gap {len(adj['+'])}; lower-gap {len(adj['-'])}; bandwidth {m.flat_bandwidth(12):.1f} meV")
