"""Euler class of the two flat bands via SO(2) Wilson-loop winding in an explicit real gauge.
C2zT acts as (sigma_x on every plane-wave component) x complex conjugation, so the basis
e1=(1,1)/sqrt2, e2=(i,-i)/sqrt2 per sublattice pair makes H real symmetric."""
import numpy as np, sys, time
from scipy.linalg import eigh
from bm_strain import BM


def shift_matrix(m, dmn):
    S=np.zeros((m.dim,m.dim)); nG=m.nG
    for (a,b),i in m.pos.items():
        t=(a+dmn[0],b+dmn[1])
        if t in m.pos:
            j=m.pos[t]
            for lay in range(2):
                for s in range(2):
                    S[2*nG*lay+2*j+s, 2*nG*lay+2*i+s]=1.0
    return S
def real_frame(m, U, k):
    HR=U.conj().T@m.H(k)@U
    assert np.abs(HR.imag).max()<1e-9, np.abs(HR.imag).max()
    D=m.dim; w,v=eigh(HR.real,subset_by_index=(D//2-1,D//2)); return v
def euler(m, nf1=24, nf2=40):
    u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
    U=np.kron(np.eye(2*m.nG),u2)
    S2=shift_matrix(m,(0,-1)); S1=shift_matrix(m,(-1,0))
    f1s=np.linspace(0,1,nf1,endpoint=False); f2s=np.linspace(0,1,nf2,endpoint=False)
    base_prev=None; phis=[]; dets=[]; base0=None
    for f1 in f1s:
        frames=[real_frame(m,U,m.frac_to_k(np.array([f1,f2]))) for f2 in f2s]
        b=frames[0]
        if base_prev is not None and np.linalg.det(base_prev.T@b)<0: b=b@np.diag([1,-1]); frames[0]=b
        if base0 is None: base0=b
        base_prev=b
        W=np.eye(2)
        for j in range(nf2-1): W=W@(frames[j].T@frames[j+1])
        W=W@(frames[-1].T@(S2@frames[0]))
        # polar decomposition -> nearest orthogonal
        u,s,vt=np.linalg.svd(W); O=u@vt
        dets.append(np.linalg.det(O)); phis.append(np.arctan2(O[1,0],O[0,0]))
    # orientation closure along k1: compare base at f1=1 (= S1-embedded base0) with last base
    closure=np.linalg.det(base_prev.T@(S1@base0))
    phis=np.unwrap(np.array(phis))
    # closing step: phase at f1=1 must equal phase at f1=0 (same loop); winding = total change
    last=phis[-1]; first=phis[0]
    # include the wrap from last sample to f1=1 by continuity with unwrap of [phis..., first]
    ext=np.unwrap(np.append(phis,first)); wind=(ext[-1]-ext[0])/(2*np.pi)
    return phis, dets, closure, wind
if __name__=="__main__":
    eps=float(sys.argv[1]); N=int(sys.argv[2]); A=float(sys.argv[3]) if len(sys.argv)>3 else 0.0
    m=BM(N=N,eps=eps,A_scalar=A); t=time.time()
    phis,dets,closure,wind=euler(m)
    print(f"eps={eps} N={N} A={A}  ({time.time()-t:.0f}s)")
    print("  det(O) along k1:",np.round(dets,3))
    print("  SO(2) angle phi(k1):",np.round(phis,3))
    print(f"  base-frame orientation closure det = {closure:+.3f}   e2 (winding) = {wind:+.3f}")
