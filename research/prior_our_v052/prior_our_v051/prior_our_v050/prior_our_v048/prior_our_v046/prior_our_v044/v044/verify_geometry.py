"""Compare full assembled operators, not only a few central eigenvalues."""
from pathlib import Path
import importlib.util,json
import numpy as np
from models import State,make,sz,add_harmonic
from checkpoints import save_json
from measure import require

ROOT=Path(__file__).resolve().parent
CASES={
 'baseline':State(A=0,B=0,T=0,phi=0,ratio=.8),
 'braid1':State(A=.2,B=-.25,T=0,phi=0,ratio=.8),
 'v028':State(A=.2,B=-.4,T=-.4,phi=0,ratio=.8),
 'first_ann':State(A=0,B=-.4,T=-.7,phi=65,ratio=.8),
 'braid2':State(A=0,B=-.4,T=-.8,phi=80,ratio=.99),
 'endpoint':State(A=-.3,B=-.4,T=-1.8,phi=80,ratio=1.1),
}

def run():
    spec=importlib.util.spec_from_file_location('old_bm',ROOT/'provenance/baseline_v041_bm.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    rows=[]
    for N in [4,6]:
        for name,p in CASES.items():
            a,b,c=[make(e,N,p) for e in ['bm_exact','ref_lab','bm_lab']]
            require(a.model.idx==b.model.mn,'exact engines have different basis labels')
            oldmodel=old.BM(N=N,theta_deg=p.theta,ratio=p.ratio,eps=p.eps,phi_deg=p.phi,A_scalar=p.A,kinetic='lab_nn_full')
            add_harmonic(oldmodel,p.B,mat=sz,use_sin=True);add_harmonic(oldmodel,p.T,mat=sz,use_sin=True,layer_sign=-1)
            for f in [[.31,.27],[1.13,.62]]:
                ha=a.model.H(a.k(f));hb=b.model.H(b.k(f));hc=c.model.H(c.k(f));ho=oldmodel.H(oldmodel.frac_to_k(f))
                err=float(np.max(np.abs(ha-hb)));unchanged=bool(np.array_equal(hc,ho))
                require(err<1e-9,'matched exact-geometry operators disagree')
                require(unchanged,'linear campaign Hamiltonian changed')
                rows.append(dict(N=N,case=name,f=f,dimension=a.dim,exact_matrix_difference=err,
                                 linear_matrix_difference=float(np.max(np.abs(hc-hb))),linear_unchanged_bitwise=unchanged))
    result=dict(status='PASS',checks=len(rows),max_exact_matrix_difference=max(r['exact_matrix_difference'] for r in rows),rows=rows)
    save_json(ROOT/'provenance/geometry_verification.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':run()
