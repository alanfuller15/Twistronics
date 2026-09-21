import numpy as np, sys
from bm_strain import BM
from braid import adjacent_nodes
for A in [float(x) for x in sys.argv[1:]]:
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=A)
    flat=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]
    adj=adjacent_nodes(m,ngrid=36)
    print(f"A={A}: flat {[tuple(np.round(f,3)) for f in flat]}")
    print(f"       up {[tuple(np.round(f,3)) for _,f in adj['+']]} lo {[tuple(np.round(f,3)) for _,f in adj['-']]}")
    sys.stdout.flush()
