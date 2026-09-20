"""Re-run the four decisive charge measurements of v026/v029/v031/v033 through the acceptance gate."""
import numpy as np, sys, platform, scipy
from bm_strain import BM, frac_dist, sz, segment_geometry
from knobs import add_harmonic, KNOBS
from gate import real_basis, classify, REAL_TOL
from final_check import winding, transport2, frame
from braid import node_winding, transport
from euler import real_frame
print(f"python {platform.python_version()} numpy {np.__version__} scipy {scipy.__version__} | {np.show_config.__module__}")
try:
    import numpy as _n; cfg=_n.__config__.CONFIG['Build Dependencies']['blas']['name']; print("blas:",cfg)
except Exception as e: print("blas: (unavailable)",e)
def pair(m,U,F1,F3,lo,r,label):
    func=lambda f:(lambda w:w[lo-m.dim//2+4]-w[lo-m.dim//2+3])(m.bands_near_zero(m.frac_to_k(f),3))  # bands lo,lo+1 with 6 bands returned
    a,va,ia=m.refine(F1,func,return_result=True); b,vb,ib=m.refine(F3,func,return_result=True)
    assert ia['success'] and ib['success'], (ia,ib)
    sa=a+np.array([r,0]); d=((b-a)+0.5)%1-0.5; sb=a+d+np.array([r,0]); base=frame(m,U,m.frac_to_k(sa),lo)
    wa=winding(m,U,a,r,96,base,lo); wb=winding(m,U,a+d,r,96,transport2(m,U,[sa,sb],base,lo,n=250),lo)
    print(f"  {label}: nodes {tuple(np.round(a,4))} ({va:.0e}) {tuple(np.round(a+d,4))} ({vb:.0e}) sep {np.linalg.norm(d):.4f} | w = {wa:+.3f}, {wb:+.3f} -> {classify(wa,wb)} | refine nfev {ia['nfev']},{ib['nfev']} wrap-shift {ia['wrap_shift']:.1e},{ib['wrap_shift']:.1e}")
# (1) v026: first braid, B_sym -0.25 -> -0.30 at A=0.2 phi=0
print("v026 first braid (flat pair, straight segment):")
for B in [-0.25,-0.30]:
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=0.20); add_harmonic(m,B,**KNOBS['sz_sin']); U=real_basis(m.nG)
    pair(m,U,np.array([0.74,0.61]),np.array([0.52,0.83]),m.dim//2-1,0.012,f"B_sym={B:+.2f}")
# (2) v029: pre-annihilation state
print("v029 pre-annihilation (flat pair):")
m=BM(N=4,eps=0.003,phi_deg=65,A_scalar=0.0); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,-0.70,mat=sz,use_sin=True,layer_sign=-1); U=real_basis(m.nG)
pair(m,U,np.array([0.6495,0.8384]),np.array([0.6283,0.8343]),m.dim//2-1,0.004,"Btau=-0.70")
# (3) v031: U-pair braid via ratio 0.99 -> 1.00
print("v031 second braid (U pair, (flat2,upper) frame):")
for ratio in [0.99,1.00]:
    m=BM(N=4,ratio=ratio,eps=0.003,phi_deg=80,A_scalar=0.0); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,-0.80,mat=sz,use_sin=True,layer_sign=-1); U=real_basis(m.nG)
    pair(m,U,np.array([0.53,0.77]),np.array([0.467,0.013]),m.dim//2,0.012,f"w0/w1={ratio:.2f}")
# (4) v033 endpoint: per-band w1 with gated frames
print("v033 endpoint (per-band sign holonomy, gated frames):")
m=BM(N=4,ratio=1.1,eps=0.003,phi_deg=80,A_scalar=-0.30); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,-1.8,mat=sz,use_sin=True,layer_sign=-1); U=real_basis(m.nG)
from euler import shift_matrix
S={0:shift_matrix(m,(-1,0)),1:shift_matrix(m,(0,-1))}
def hol(lo,axis,c,n=100):
    ts=np.linspace(0,1,n+1); prev=None; first=None
    for t in ts:
        q=np.array([t,c]) if axis==0 else np.array([c,t]); v=frame(m,U,m.frac_to_k(q),lo)  # gated 2-frame of bands lo,lo+1
        v=v[:,:1]
        if prev is not None and prev[:,0]@v[:,0]<0: v=-v
        if first is None: first=v
        prev=v
    return float(prev[:,0]@(S[axis]@first)[:,0])
D=m.dim
for lab,lo in [('flat1',D//2-1),('flat2',D//2)]:
    print(f"  {lab}: k1 {hol(lo,0,0):+.3f},{hol(lo,0,0.5):+.3f}   k2 {hol(lo,1,0):+.3f},{hol(lo,1,0.5):+.3f}")
print(f"gate: real-basis residual tolerance {REAL_TOL} meV enforced on every frame above (no GateError raised)")
