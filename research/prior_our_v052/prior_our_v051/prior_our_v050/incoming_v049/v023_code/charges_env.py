import numpy as np, sys, json, os
from bm_strain import BM, frac_dist, sz, s0, sx, sy
from knobs import add_harmonic
from braid import node_winding, transport, adjacent_nodes
from euler import real_frame
MATS={'sz':sz,'s0':s0,'sx':sx,'sy':sy}
BASES=json.loads(os.environ.get('BASE_KNOBS','[]')); A=float(os.environ.get('A','0.20')); phi=float(sys.argv[1])
m=BM(N=4,eps=0.003,phi_deg=phi,A_scalar=A)
for amp,sp in BASES:
    sp=dict(sp); add_harmonic(m,amp,mat=MATS[sp.pop('mat')],**sp)
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
flat=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]
up=lambda f:(lambda w:w[3]-w[2])(m.bands_near_zero(m.frac_to_k(f),2)); lo=lambda f:(lambda w:w[1]-w[0])(m.bands_near_zero(m.frac_to_k(f),2))
mins={}
for nm,fn in [('upper',up),('lower',lo)]:
    fs,vals=m.grid(18,fn); best=min(m.refine(np.array(c[1:]),fn)[1] for c in m.local_minima(fs,vals,4)); mins[nm]=best
print(f"phi={phi}: flat nodes {[tuple(np.round(f,3)) for f in flat]}  upper-gap min {mins['upper']:.3f} meV  lower-gap min {mins['lower']:.3f} meV")
r=0.015; starts=[f+np.array([r,0]) for f in flat]; base=real_frame(m,U,m.frac_to_k(starts[0]))
ws=[node_winding(m,U,flat[0],r,64,base)]+[node_winding(m,U,flat[i],r,64,transport(m,U,[starts[0],starts[i]],base)) for i in range(1,len(flat))]
for f,w in zip(flat,ws): print(f"   {tuple(np.round(f,3))}  w={w:+.2f}")
print(f"   sum = {sum(round(w) for w in ws):+d}")
