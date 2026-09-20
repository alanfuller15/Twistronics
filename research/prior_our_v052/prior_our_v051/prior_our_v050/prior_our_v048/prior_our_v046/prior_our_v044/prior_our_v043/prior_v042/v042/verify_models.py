"""Assembly checks and reciprocal-geometry attribution, not a path substitute."""
import json
from pathlib import Path
from dataclasses import asdict
import numpy as np
from scipy.linalg import eigh
from models import make,State
from independent_measurement import require

def run():
    rows=[]
    states=[State(A=0,B=0,T=0,phi=0,ratio=.8),State(T=-.7,phi=65,ratio=.8),State(),State(A=-.3,T=-1.8,ratio=1.1)]
    for N in [4,6]:
        for p in states:
            aa=make('bm_lab',N,p);bb=make('ref_lab',N,p);a=aa.model;b=bb.model
            require(a.idx==b.mn,'basis memberships differ; direct matrix comparison not justified')
            require(np.max(np.abs(a.Hstat-b.Hs))<1e-10,'static harmonic assemblies disagree')
            for f in [[.31,.27],[.55,1.02]]:
                ha=a.H(a.frac_to_k(f));hb=b.H(b.k(f));lo=a.dim//2-4
                wa=eigh(ha,subset_by_index=[lo,lo+7],eigvals_only=True);wb=eigh(hb,subset_by_index=[lo,lo+7],eigvals_only=True)
                # Diagnostic attribution ONLY: feed exact q/G into an otherwise
                # unchanged BM instance. This object is never used in a replay.
                saved=(a.q,a.G1,a.G2,a.Gvec)
                try:
                    a.q=[q.copy() for q in b.q];a.G1=b.G1.copy();a.G2=b.G2.copy()
                    a.Gvec=np.array([i*a.G1+j*a.G2 for i,j in a.idx])
                    matched=a.H(a.frac_to_k(f))
                finally:a.q,a.G1,a.G2,a.Gvec=saved
                error=float(np.max(np.abs(matched-hb)));require(error<1e-8,'kinetic/harmonic discrepancy survives geometry matching')
                for adapter in [aa,bb]:
                    real,diag=adapter.real_hamiltonian(f)
                    u=np.kron(np.eye(adapter.dim//2),adapter.spinor)
                    expected=u.conj().T@adapter.model.H(adapter.k(f))@u
                    require(np.max(np.abs(real-expected))<1e-9,'real adapter differs from full conjugation')
                require(np.array_equal(aa.sewing(0),bb.sewing(0)) and np.array_equal(aa.sewing(1),bb.sewing(1)),'sewing operators disagree')
                rows.append(dict(N=N,state=asdict(p),f=f,dimension=a.dim,
                  matrix_difference=float(np.max(np.abs(ha-hb))),central_spectrum_difference=float(np.max(np.abs(wa-wb))),
                  reciprocal_difference=float(max(np.max(np.abs(a.G1-b.G1)),np.max(np.abs(a.G2-b.G2)))),
                  geometry_matched_matrix_error=error))
    return dict(status='PASS',comparisons=rows,limit='Exact reciprocal geometry was injected only to attribute discrepancies, never into primary replay instances.')

if __name__=='__main__':
    r=run();p=Path(__file__).resolve().parent/'results/model_verification.json';p.write_text(json.dumps(r,indent=2)+'\n')
    print('PASS',len(r['comparisons']),'matrix/spectrum comparisons; max raw spectrum difference',max(q['central_spectrum_difference'] for q in r['comparisons']))
