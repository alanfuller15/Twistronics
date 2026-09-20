"""Validate added harmonic against legacy assembly before event runs."""
import json
from pathlib import Path
import numpy as np
from models import Original,Partner,State
from bm_strain import BM
from tbg_ref import TBG
from independent_measurement import require

def legacy_harmonic(m,amplitude,tau=False):
    for layer in (0,1):
        for mn,i in m.pos.items():
            for shift in [(1,0),(0,1),(-1,1)]:
                for sign in (-1,1):
                    j=m.pos.get(tuple(np.array(mn)+sign*np.array(shift)))
                    if j is None:continue
                    r=2*m.nG*layer+2*j;c=2*m.nG*layer+2*i
                    m.Hstat[r:r+2,c:c+2]+=amplitude*m.w1*.5*(-1j*sign)*(1 if not tau or layer==0 else -1)*np.diag([1.,-1.])

def run():
    rows=[]
    for N in [4,6]:
        for p in [State(T=-.7,phi=65,ratio=.8),State(),State(A=-.3,T=-1.8,ratio=1.1)]:
            original=Original(N,p);old=BM(N=N,eps=p.eps,phi_deg=p.phi,ratio=p.ratio,A_scalar=p.A)
            legacy_harmonic(old,p.B);legacy_harmonic(old,p.T,True)
            permutation=original.reference_permutation(old.idx)
            for f in [[.31,.27],[.55,1.02]]:
                h=original.hamiltonian(original.from_original_fraction(f))[np.ix_(permutation,permutation)]
                error=float(np.max(np.abs(h-old.H(old.frac_to_k(f)))))
                require(error<1e-7,'original extension differs from legacy model')
                rows.append(dict(N=N,state=p.__dict__,f=f,original_matrix_error=error))
        p=State(T=0);partner=Partner(N,p);old=TBG(N=N,eps=p.eps,phi=p.phi,A=p.A,B=p.B,w0=110*p.ratio)
        require(np.array_equal(partner.model.Hs,old.Hs),'partner zero-tau model changed')
        for f in [[.31,.27],[.55,1.02]]:
            _,diag=Partner(N,State()).real_hamiltonian(f);require(diag['reality_residual']<1e-9,'tau harmonic not real')
    return dict(status='PASS',comparisons=rows)

if __name__=='__main__':
    p=Path(__file__).resolve().parent/'results/model_verification.json';p.write_text(json.dumps(run(),indent=2)+'\n');print(p)
