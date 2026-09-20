import numpy as np, sys, json, os
from scipy.linalg import eigh
from bm_strain import BM
import check_iso
from check_iso import mk, base, inv
from euler import shift_matrix
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
p=dict(base); p.update(json.loads(os.environ.get('P','{}'))); N=int(os.environ.get('NN','4')); check_iso.N=N; NP=int(os.environ.get('NPTS','120'))
m=mk(p); U=np.kron(np.eye(2*m.nG),u2); D=m.dim
S={0:shift_matrix(m,(-1,0)),1:shift_matrix(m,(0,-1))}
def vecs(k,lo,nb):
    HR=U.conj().T@m.H(k)@U; w,v=eigh(HR.real,subset_by_index=(lo,lo+nb-1)); return v
def holonomy(lo,nb,axis,c):
    ts=np.linspace(0,1,NP+1); pts=[np.array([t,c]) if axis==0 else np.array([c,t]) for t in ts]
    fr=[vecs(m.frac_to_k(q),lo,nb) for q in pts]; prev=fr[0]
    for f in fr[1:]:
        if nb==1:
            if prev[:,0]@f[:,0]<0: f=-f
        else:
            if np.linalg.det(prev.T@f)<0: f=f@np.diag([1,-1])
        prev=f
    M=prev.T@(S[axis]@fr[0]); return float(M[0,0]) if nb==1 else float(np.linalg.det(M))
if N<=4:
    g=[inv(m,i)[1] for i in range(4)]; print(f"N={N} {p}\n  gap minima lo|f1 {g[0]:.2f} f1|f2 {g[1]:.2f} f2|up {g[2]:.2f} up|nx {g[3]:.2f} meV")
else: print(f"N={N} {p}")
for lab,lo,nb in [('flat1 (band 2) alone',D//2-1,1),('flat2 (band 3) alone',D//2,1),('upper (band 4) alone',D//2+1,1),('lower (band 1) alone',D//2-2,1),('flat pair 2-frame',D//2-1,2)]:
    row=[]
    for axis in (0,1):
        row.append(f"{'k1' if axis==0 else 'k2'}: "+",".join(f"{holonomy(lo,nb,axis,c):+.2f}" for c in (0,0.5)))
    print(f"  {lab:24s} sign/orientation holonomy  "+"   ".join(row)); sys.stdout.flush()
