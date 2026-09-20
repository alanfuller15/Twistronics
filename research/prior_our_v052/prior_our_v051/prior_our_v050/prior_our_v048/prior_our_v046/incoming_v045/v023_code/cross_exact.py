import numpy as np
from bm_strain import BM
from tbg_ref import TBG
for geom in ['linear','exact']:
    a=BM(N=4,eps=0.003,phi_deg=65,A_scalar=0.0,kinetic='lab_nn_full',geometry=geom); b=TBG(N=4,eps=0.003,phi=65,A=0.0,kinetic='lab_nn_full')
    for f in ([0.31,0.27],[1.13,0.62]):
        wa=a.bands_near_zero(a.frac_to_k(np.array(f)),3); wb=b.bands(b.k(np.array(f)),3)
        print(f"geometry={geom:6s} f={f}: max |E_bm - E_ref| over 6 central bands = {np.abs(wa-wb).max():.2e} meV")
    print(f"   |G1| bm {np.linalg.norm(a.G1):.10f} ref {np.linalg.norm(b.G1):.10f} | |q0| {np.linalg.norm(a.q[0]):.10f} / {np.linalg.norm(b.q[0]):.10f}")
