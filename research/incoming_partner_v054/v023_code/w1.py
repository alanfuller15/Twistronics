import numpy as np, sys, json, os
from scipy.linalg import eigh
from bm_strain import BM, frac_dist
import check_iso
from check_iso import mk, base, inv
from euler import shift_matrix
from final_check import frame
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
p=dict(base); p.update(json.loads(os.environ.get('P','{}'))); N=int(os.environ.get('NN','4')); check_iso.N=N
m=mk(p); U=np.kron(np.eye(2*m.nG),u2); D=m.dim; lo=D//2-1
S1=shift_matrix(m,(-1,0)); S2=shift_matrix(m,(0,-1))
def w1_cycle(axis,c,n=int(os.environ.get("NPTS","120"))):
    """orientation of the flat 2-frame transported once around the cycle along `axis` at offset c."""
    ts=np.linspace(0,1,n+1)
    pts=[np.array([t,c]) if axis==0 else np.array([c,t]) for t in ts]
    fr=[frame(m,U,m.frac_to_k(q),lo) for q in pts]
    prev=fr[0]
    for f in fr[1:]:
        if np.linalg.det(prev.T@f)<0: f=f@np.diag([1,-1])
        prev=f
    S=S1 if axis==0 else S2
    return np.linalg.det(prev.T@(S@fr[0]))
gaps=[inv(m,i)[1] for i in range(4)] if N<=4 else [float("nan")]*4
print(f"N={N} {p}\n  gap minima: lo|f1 {gaps[0]:.2f} f1|f2 {gaps[1]:.2e} f2|up {gaps[2]:.2f} up|nx {gaps[3]:.2f} meV")
for axis,lab in [(0,'k1'),(1,'k2')]:
    print(f"  w1 along {lab} (orientation closure) at offsets 0,0.25,0.5,0.75:",[f"{w1_cycle(axis,c):+.2f}" for c in [0,0.25,0.5,0.75]])
