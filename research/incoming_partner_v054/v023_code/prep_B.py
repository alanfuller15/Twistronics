import numpy as np, sys
from bm_strain import BM, sz, frac_dist
from knobs import add_harmonic
from braid import adjacent_nodes
for B in [0.0,-0.02,-0.04,-0.05,-0.06,-0.08,-0.10,-0.25]:
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=0.20,kinetic='lab_nn_full',geometry='exact'); add_harmonic(m,B,mat=sz,use_sin=True)
    ex=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]
    if len(ex)>=2:
        pr=min(((frac_dist(a,b),a,b) for i,a in enumerate(ex) for b in ex[i+1:]),key=lambda t:t[0])
    adj=adjacent_nodes(m,ngrid=24)
    print(f"  B={B:+.2f}: flat nodes {len(ex)} {[tuple(np.round(f,4)) for f in ex]} closest pair sep {pr[0]:.4f} | upper {[tuple(np.round(f,3)) for _,f in adj['+']]} lower {len(adj['-'])}"); sys.stdout.flush()
