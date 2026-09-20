import numpy as np, sys
from bm_strain import BM, frac_dist
from braid import adjacent_nodes
from knobs import add_harmonic, KNOBS
Bz=float(sys.argv[1])
for A in [float(x) for x in sys.argv[2:]]:
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=A); add_harmonic(m,Bz,**KNOBS['sz_sin'])
    fl=m.find_nodes(ngrid=36,nkeep=18); ex=[f for v,f in fl if v<1e-6]
    adj=adjacent_nodes(m,ngrid=36); rem=m.min_remote(ngrid=15,nkeep=4)
    sep=frac_dist(ex[0],ex[1]) if len(ex)==2 else float('nan')
    print(f"B={Bz:+.2f} A={A:.2f}: flat={len(ex)} {[tuple(np.round(f,3)) for f in ex]} sep={sep:.3f} smallest mid={fl[0][0]:.1e} | adj={len(adj['+'])}+{len(adj['-'])} minrem={rem[0]:.2e} at {tuple(np.round(rem[1],3))} | bw={m.flat_bandwidth(10):.0f}")
    sys.stdout.flush()
