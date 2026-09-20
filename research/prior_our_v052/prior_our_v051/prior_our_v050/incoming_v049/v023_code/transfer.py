import numpy as np, sys
from scipy.linalg import eigh
from bm_strain import BM, frac_dist, sz
from knobs import add_harmonic
from euler import shift_matrix
N=int(sys.argv[1]) if len(sys.argv)>1 else 4
m=BM(N=N,eps=0.003,phi_deg=65,A_scalar=0.0); add_harmonic(m,-0.40,mat=sz,use_sin=True); add_harmonic(m,-0.74,mat=sz,use_sin=True,layer_sign=-1)
D=m.dim; u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); U=np.kron(np.eye(2*m.nG),u2)
def bands(k,nb=3):
    return eigh(m.H(k),eigvals_only=True,subset_by_index=(D//2-nb,D//2+nb-1))
# gap minima on a grid: g12 (lower|flat1), g23 (flat gap), g34 (flat2|upper), g45 (upper|next)
fs=np.linspace(0,1,21,endpoint=False); mins=np.full(4,np.inf)
for a in fs:
    for b in fs:
        w=bands(m.frac_to_k(np.array([a,b]))); g=np.array([w[2]-w[1],w[3]-w[2],w[4]-w[3],w[5]-w[4]]); mins=np.minimum(mins,g)
print(f"N={N}: grid gap minima (meV): lower|flat1 {mins[0]:.2f}, flat gap {mins[1]:.3f}, flat2|upper {mins[2]:.2e}, upper|next {mins[3]:.2f}")
def frame(k,lo):
    HR=U.conj().T@m.H(k)@U; w,v=eigh(HR.real,subset_by_index=(lo,lo+1)); return v
def euler(lo,nf1=24,nf2=40):
    S2=shift_matrix(m,(0,-1)); S1=shift_matrix(m,(-1,0)); base_prev=None; base0=None; phis=[]; dets=[]
    for f1 in np.linspace(0,1,nf1,endpoint=False):
        fr=[frame(m.frac_to_k(np.array([f1,f2])),lo) for f2 in np.linspace(0,1,nf2,endpoint=False)]
        b=fr[0]
        if base_prev is not None and np.linalg.det(base_prev.T@b)<0: b=b@np.diag([1,-1]); fr[0]=b
        if base0 is None: base0=b
        base_prev=b; W=np.eye(2)
        for j in range(nf2-1): W=W@(fr[j].T@fr[j+1])
        W=W@(fr[-1].T@(S2@fr[0])); u,s,vt=np.linalg.svd(W); O=u@vt; dets.append(np.linalg.det(O)); phis.append(np.arctan2(O[1,0],O[0,0]))
    ext=np.unwrap(np.append(np.unwrap(phis),phis[0])); return (ext[-1]-ext[0])/(2*np.pi), np.linalg.det(base_prev.T@(S1@base0)), min(dets)
for lab,lo in [('(flat2, upper)',D//2),('(flat1, flat2) [not isolated above - for reference only]',D//2-1),('(lower, flat1) [not isolated above]',D//2-2)]:
    e,cl,md=euler(lo); print(f"   Euler winding of {lab}: e2 = {e:+.3f}  (orientation closure {cl:+.2f}, min det {md:+.2f})")
