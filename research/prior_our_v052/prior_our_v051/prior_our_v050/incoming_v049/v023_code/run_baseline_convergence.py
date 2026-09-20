import numpy as np, time, sys
from bm_strain import BM
eps=0.003; phi=float(sys.argv[1]) if len(sys.argv)>1 else 0.0
for N in [3,4,5,6,7]:
    t=time.time(); m=BM(N=N,eps=eps,phi_deg=phi)
    nodes=m.find_nodes(ngrid=15, nkeep=6)
    rem=m.min_remote(ngrid=15, nkeep=4)
    bw=m.flat_bandwidth(12)
    print(f"N={N} dim={m.dim} bandwidth={bw:.3f} meV  min remote gap={rem[0]:.4f} meV at f={np.round(rem[1],4)}  ({time.time()-t:.0f}s)")
    for val,f in nodes[:4]:
        d=m.gaps(m.frac_to_k(f))
        print(f"   node f={np.round(f,5)}  dmid={val:.3e}  local remote={d[1]:.3f}  E={d[2][1]:.3f}")
    sys.stdout.flush()
