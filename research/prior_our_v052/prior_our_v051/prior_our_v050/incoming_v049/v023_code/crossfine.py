import numpy as np
from bm_strain import BM
from knobs import add_harmonic, KNOBS, analyse
for B in [-0.26,-0.27,-0.28,-0.29]:
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=0.20); add_harmonic(m,B,**KNOBS['sz_sin'])
    flat,adj,rem,F1,F3,cross=analyse(m)
    print(f"B={B:+.2f}: adj (t,offset) rel. F1->F3: {cross}  flat={len(flat)}")
