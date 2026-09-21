import numpy as np, sys, time
from bm_strain import BM, frac_dist
from braid import adjacent_nodes
mk=lambda A: BM(N=4,eps=0.003,phi_deg=0,A_scalar=A,kinetic='lab_nn_full',geometry='exact')
print("U-pair birth: SAMPLED remote-gap minima at five A values (no bisection or root solve; candidate bracket only):")
for A in [0.11,0.12,0.125,0.13,0.135]:
    m=mk(A); r=m.min_remote(ngrid=15,nkeep=4); print(f"  A={A:.3f}: min remote {r[0]:.4f} meV at {tuple(np.round(r[1],4))}"); sys.stdout.flush()
print("flat-gap node inventory at A=0.20 (global 36x36 search + cone-style check):")
m=mk(0.20); fl=[(v,f) for v,f in m.find_nodes(ngrid=36,nkeep=18)]; ex=[f for v,f in fl if v<1e-6]
print(f"  exact flat nodes {len(ex)}: {[tuple(np.round(f,4)) for f in ex]}; next smallest gap {min([v for v,_ in fl if v>=1e-6] or [np.nan]):.2e}")
adj=adjacent_nodes(m,ngrid=30); print(f"  upper nodes {[tuple(np.round(f,4)) for _,f in adj['+']]} lower {[tuple(np.round(f,4)) for _,f in adj['-']]}")
print("flat-gap node inventory at A=0.16 and 0.18:")
for A in (0.16,0.18):
    m=mk(A); ex=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]; print(f"  A={A:.2f}: {len(ex)} flat nodes {[tuple(np.round(f,4)) for f in ex]}"); sys.stdout.flush()
