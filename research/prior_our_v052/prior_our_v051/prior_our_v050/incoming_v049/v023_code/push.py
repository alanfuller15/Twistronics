import numpy as np, sys, json, os
from bm_strain import BM, frac_dist, sz
from knobs import add_harmonic
from braid import adjacent_nodes
A=0.0; phi=65.0
F1=np.array(json.loads(os.environ['F1'])); F3=np.array(json.loads(os.environ['F3']))
def inv(m,fn,c,r=0.06,n=25):
    pts=sorted((fn(np.array([a,b])),a,b) for a in np.linspace(c[0]-r,c[0]+r,n) for b in np.linspace(c[1]-r,c[1]+r,n)); ex=[]
    for v,a,b in pts[:10]:
        f,vv=m.refine(np.array([a,b]),fn)
        if vv<1e-6 and all(frac_dist(f,g)>0.003 for g in ex): ex.append(f)
    return ex,pts[0][0]
for Bt in [float(b) for b in sys.argv[1:]]:
    m=BM(N=4,eps=0.003,phi_deg=phi,A_scalar=A); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,Bt,mat=sz,use_sin=True,layer_sign=-1)
    mid=lambda f: m.gaps(m.frac_to_k(f))[0]; lo=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2)); up=lambda f:(lambda w:w[3]-w[2])(m.bands_near_zero(m.frac_to_k(f),2))
    c=(F1+F3)/2
    exm,gm=inv(m,mid,c); exl,gl=inv(m,lo,c); exu,gu=inv(m,up,c)
    adj=adjacent_nodes(m,ngrid=24)
    print(f"Btau={Bt:+.3f}: mid nodes in box {[tuple(np.round(f,4)) for f in exm]} (box min {gm:.2e} meV) | lower nodes in box {len(exl)} (min {gl:.2e}) | upper nodes in box {len(exu)} (min {gu:.2e}) | global: up {len(adj['+'])} lo {len(adj['-'])} | bw {m.flat_bandwidth(8):.0f}")
    sys.stdout.flush()
    if len(exm)==2: F1,F3=exm
