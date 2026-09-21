import numpy as np, sys, json
from bm_strain import BM, frac_dist, sz, s0, sx, sy
from knobs import add_harmonic
from braid import adjacent_nodes
MATS={'sz':sz,'s0':s0,'sx':sx,'sy':sy}
spec=json.loads(sys.argv[1]); amps=[float(a) for a in sys.argv[2:]]
mat=MATS[spec.pop('mat')]
import os
BASES=json.loads(os.environ.get('BASE_KNOBS','[]'))
F1=np.array(json.loads(os.environ.get('F1','[0.7695,0.6517]'))); F3=np.array(json.loads(os.environ.get('F3','[0.5915,0.8011]')))
for B in amps:
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=0.20)
    for amp,sp in BASES:
        sp=dict(sp); add_harmonic(m,amp,mat=MATS[sp.pop('mat')],**sp)
    add_harmonic(m,B,mat=mat,**spec)
    func=lambda f: m.gaps(m.frac_to_k(f))[0]
    a,va=m.refine(F1,func); b,vb=m.refine(F3,func)
    if max(va,vb)>1e-6: print(f"B={B:+.3f}: originals lost ({va:.0e},{vb:.0e})"); break
    fl=[f for v,f in m.find_nodes(ngrid=30,nkeep=16) if v<1e-6]; adj=adjacent_nodes(m,ngrid=30)
    lo=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2))
    fs,vals=m.grid(15,lo); lomin=m.refine(np.array(m.local_minima(fs,vals,1)[0][1:]),lo)[1]
    d=b-a; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L
    ins=[(lab,round(float((((q-a)+0.5)%1-0.5)@d/L**2),2),round(float((((q-a)+0.5)%1-0.5)@n),3)) for lab,lst in (('U',adj['+']),('L',adj['-'])) for _,q in lst if -0.1<float((((q-a)+0.5)%1-0.5)@d/L**2)<1.1]
    print(f"B={B:+.3f}: flat={len(fl)} up={len(adj['+'])} lo={len(adj['-'])} lower-gap min={lomin:.2e} meV sep={frac_dist(a,b):.3f} bw={m.flat_bandwidth(8):.0f} | in-segment (lab,t,off): {ins}")
    sys.stdout.flush()
    F1,F3=a,b
