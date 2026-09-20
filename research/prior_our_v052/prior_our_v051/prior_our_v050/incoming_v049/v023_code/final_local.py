import numpy as np, sys
from bm_strain import BM, sz, frac_dist
from knobs import add_harmonic
def bm(A,ratio):
    m=BM(N=4,ratio=ratio,eps=0.003,phi_deg=80,A_scalar=A,kinetic='lab_nn_full',geometry='exact'); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,-1.8,mat=sz,use_sin=True,layer_sign=-1); return m
def local(m,c,R=0.03,n=25):
    fn=lambda f: m.gaps(m.frac_to_k(f))[0]
    pts=sorted((fn(np.array([a,b])),a,b) for a in np.linspace(c[0]-R,c[0]+R,n) for b in np.linspace(c[1]-R,c[1]+R,n)); ex=[]
    for v,a,b in pts[:8]:
        f,val=m.refine(np.array([a,b]),fn)
        if val<1e-6 and all(frac_dist(f,g)>5e-4 for g in ex): ex.append(f)
    return ex,pts[0][0]
print("flat birth, local search around (0.680,0.923), A=-0.35:")
for ratio in [1.060,1.058,1.056,1.054,1.052]:
    ex,gm=local(bm(-0.35,ratio),np.array([0.680,0.923])); s=f"sep {frac_dist(ex[0],ex[1]):.5f}" if len(ex)==2 else ""
    print(f"  ratio={ratio:.3f}: exact nodes {[tuple(np.round(f,5)) for f in ex]} {s} (box grid min {gm:.2e})"); sys.stdout.flush()
print("final annihilation, local search around (0.677,0.920), ratio 1.10:")
for A in [-0.320,-0.318,-0.316,-0.314,-0.312]:
    ex,gm=local(bm(A,1.10),np.array([0.677,0.920])); s=f"sep {frac_dist(ex[0],ex[1]):.5f}" if len(ex)==2 else ""
    print(f"  A={A:+.3f}: exact nodes {[tuple(np.round(f,5)) for f in ex]} {s} (box grid min {gm:.2e})"); sys.stdout.flush()
