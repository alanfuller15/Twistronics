import numpy as np, sys, json, os
from bm_strain import BM, frac_dist, sz, s0, sx, sy
from knobs import add_harmonic
from braid import adjacent_nodes
MATS={'sz':sz,'s0':s0,'sx':sx,'sy':sy}
BASES=json.loads(os.environ.get('BASE_KNOBS','[]')); A=float(os.environ.get('A','0.20'))
F1=np.array(json.loads(os.environ.get('F1','[0.7695,0.6517]'))); F3=np.array(json.loads(os.environ.get('F3','[0.5915,0.8011]')))
for phi in [float(p) for p in sys.argv[1:]]:
    m=BM(N=4,eps=0.003,phi_deg=phi,A_scalar=A)
    for amp,sp in BASES:
        sp=dict(sp); add_harmonic(m,amp,mat=MATS[sp.pop('mat')],**sp)
    func=lambda f: m.gaps(m.frac_to_k(f))[0]
    a,va=m.refine(F1,func); b,vb=m.refine(F3,func)
    if max(va,vb)>1e-6: print(f"phi={phi}: originals lost ({va:.0e},{vb:.0e})"); break
    fl=[f for v,f in m.find_nodes(ngrid=30,nkeep=16) if v<1e-6]; adj=adjacent_nodes(m,ngrid=30)
    lo=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2))
    fs,vals=m.grid(15,lo); lomin=m.refine(np.array(m.local_minima(fs,vals,1)[0][1:]),lo)[1]
    d=b-a; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L
    allU=[(round(float((((q-a)+0.5)%1-0.5)@d/L**2),2),round(float((((q-a)+0.5)%1-0.5)@n),3)) for _,q in adj['+']]
    print(f"phi={phi:5.1f}: flat={len(fl)} up={len(adj['+'])} lo={len(adj['-'])} lower-gap min={lomin:.2e} sep={frac_dist(a,b):.3f} F1 {tuple(np.round(a,3))} F3 {tuple(np.round(b,3))} | U (t,off): {allU}")
    sys.stdout.flush(); F1,F3=a,b
