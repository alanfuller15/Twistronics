import numpy as np
from bm_strain import BM, sz
from knobs import add_harmonic
for N in (4,6):
    m=BM(N=N,ratio=1.1,eps=0.003,phi_deg=80,A_scalar=-0.30); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,-1.8,mat=sz,use_sin=True,layer_sign=-1)
    fn=lambda f:(lambda w:w[2]-w[1])(m.bands_near_zero(m.frac_to_k(f),3))     # lower remote | flat1
    fn2=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),3))    # below-lower | lower remote
    for lab,g in (('lower|flat1',fn),('below-lower|lower',fn2)):
        best=(np.inf,None,None)
        for ng in (24,36):
            fs,vals=m.grid(ng,g)
            for v,a,b in m.local_minima(fs,vals,8):
                f,val,info=m.refine(np.array([a,b]),g,return_result=True)
                if val<best[0]: best=(val,f,info)
        val,f,info=best
        print(f"N={N} {lab}: min {val:.6f} meV at {tuple(np.round(f,5))}  value-at-returned-coordinate {g(f):.6f}  wrap_shift {info['wrap_shift']:.1e} success {info['success']}")
