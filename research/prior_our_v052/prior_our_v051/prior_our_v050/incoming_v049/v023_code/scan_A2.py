import numpy as np, sys, json, os
from bm_strain import BM, frac_dist, sz, s0, sx, sy
from knobs import add_harmonic
from braid import adjacent_nodes
MATS={'sz':sz,'s0':s0,'sx':sx,'sy':sy}
BASES=json.loads(os.environ.get('BASE_KNOBS','[]')); phi=float(os.environ.get('PHI','0'))
F1=np.array(json.loads(os.environ['F1'])); F3=np.array(json.loads(os.environ['F3']))
for A in [float(a) for a in sys.argv[1:]]:
    m=BM(N=4,eps=0.003,phi_deg=phi,A_scalar=A)
    for amp,sp in BASES:
        sp=dict(sp); add_harmonic(m,amp,mat=MATS[sp.pop('mat')],**sp)
    func=lambda f: m.gaps(m.frac_to_k(f))[0]
    a,va=m.refine(F1,func); b,vb=m.refine(F3,func); mid,vm=m.refine((F1+F3)/2,func)
    lo=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2)); fs,vals=m.grid(12,lo); lomin=min(m.refine(np.array(c[1:]),lo)[1] for c in m.local_minima(fs,vals,3))
    adj=adjacent_nodes(m,ngrid=24); d=b-a; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L
    Us=[(round(float((((q-a)+0.5)%1-0.5)@d/L**2),2),round(float((((q-a)+0.5)%1-0.5)@n),3)) for _,q in adj['+']]
    print(f"A={A:+.3f}: F1 {tuple(np.round(a,3))} ({va:.0e}) F3 {tuple(np.round(b,3))} ({vb:.0e}) sep={frac_dist(a,b):.4f} midgap={vm:.2e} | lower-min {lomin:.2f} lo-nodes {len(adj['-'])} | U (t,off) {Us}")
    sys.stdout.flush()
    if max(va,vb)<1e-6 and frac_dist(a,b)>0.003: F1,F3=a,b
    else: print("   >>> pair gone or collapsed"); 
