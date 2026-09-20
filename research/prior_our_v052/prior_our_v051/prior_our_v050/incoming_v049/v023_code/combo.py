import numpy as np, sys
from bm_strain import BM, frac_dist
from braid import adjacent_nodes
from knobs import add_harmonic, KNOBS
Bz=float(sys.argv[1])
for Bt in [float(x) for x in sys.argv[2:]]:
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=0.20); add_harmonic(m,Bz,**KNOBS['sz_sin']); add_harmonic(m,Bt,**KNOBS['tauz'])
    flat=[(v,f) for v,f in m.find_nodes(ngrid=36,nkeep=18)]
    ex=[f for v,f in flat if v<1e-6]
    adj=adjacent_nodes(m,ngrid=36); rem=m.min_remote(ngrid=15,nkeep=4)
    print(f"sz_sin={Bz:+.2f} tauz={Bt:+.2f}: flat nodes={len(ex)} {[tuple(np.round(f,3)) for f in ex]}  smallest mid gaps={[f'{v:.1e}' for v,_ in flat[:3]]}  adj={len(adj['+'])}+{len(adj['-'])}  minrem={rem[0]:.1e}  bw={m.flat_bandwidth(10):.0f}")
    sys.stdout.flush()
