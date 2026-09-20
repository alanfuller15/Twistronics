import numpy as np, time, sys
from bm_strain import BM, sz
eps=0.003; phi=0.0
# add layer-antisymmetric mass option by monkeypatching the static part
def add_mass(m, mass, layer_sign):
    nG=m.nG
    for lay in range(2):
        s = 1.0 if lay==0 else layer_sign
        for i in range(nG):
            r=2*nG*lay+2*i
            m.Hstat[r:r+2,r:r+2] += s*mass*sz
for N in [4]:
    for layer_sign,label in [(+1,'uniform m*sz (breaks C2zT and P)'),(-1,'m*tz*sz (breaks C2zT, preserves P)')]:
        for mass in [0.5,1.0,2.0]:
            t=time.time(); m=BM(N=N,eps=eps,phi_deg=phi); add_mass(m,mass,layer_sign)
            nodes=m.find_nodes(ngrid=15,nkeep=4)
            rem=m.min_remote(ngrid=12,nkeep=3)
            print(f"N={N} {label} m={mass} meV: min dmid={nodes[0][0]:.4f} meV at {np.round(nodes[0][1],4)}; 2nd min={nodes[1][0]:.4f} at {np.round(nodes[1][1],4)}; min remote={rem[0]:.3f} ({time.time()-t:.0f}s)")
            sys.stdout.flush()
