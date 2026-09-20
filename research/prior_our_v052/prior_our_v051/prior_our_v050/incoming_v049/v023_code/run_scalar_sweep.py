import numpy as np, time, sys
from bm_strain import BM, frac_dist
eps=0.003; phi=0.0
Ns=[4,6]
for A in [float(a) for a in sys.argv[1:]]:
    for N in Ns:
        t=time.time(); m=BM(N=N,eps=eps,phi_deg=phi,A_scalar=A)
        nodes=m.find_nodes(ngrid=15, nkeep=6)
        rem=m.min_remote(ngrid=15, nkeep=4)
        ex=[(v,f) for v,f in nodes if v<1e-3]
        sep = frac_dist(ex[0][1],ex[1][1]) if len(ex)>=2 else float('nan')
        # convert to physical distance in units of ktheta
        if len(ex)>=2:
            d=m.frac_to_k(ex[0][1])-m.frac_to_k(ex[1][1]); 
            d=np.array([ (x+0.5)%1-0.5 for x in (ex[0][1]-ex[1][1])]); dk=np.linalg.norm(d[0]*m.G1+d[1]*m.G2)/m.ktheta
        else: dk=float('nan')
        print(f"A={A:+.2f} N={N} nodes(<1e-3)={len(ex)} sep_frac={sep:.4f} sep/ktheta={dk:.3f} min_remote={rem[0]:.4e} at {np.round(rem[1],3)} ({time.time()-t:.0f}s)")
        for v,f in nodes[:3]:
            g=m.gaps(m.frac_to_k(f)); print(f"     f={np.round(f,4)} dmid={v:.2e} locrem={g[1]:.3f}")
        sys.stdout.flush()
