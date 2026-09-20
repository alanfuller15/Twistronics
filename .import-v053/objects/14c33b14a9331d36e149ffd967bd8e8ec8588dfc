"""Full-matrix invariance and the new public parameter's nonfinite witness."""
import importlib.util,json,warnings
from pathlib import Path
import numpy as np
from models import BM,sz
from knobs import add_harmonic
from checkpoints import save_json,digest
ROOT=Path(__file__).resolve().parent

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def run():
    old=load(ROOT/'provenance/prior_bm_strain.py','old_bm')
    states=[dict(phi_deg=0,A_scalar=0,B=0,T=0,ratio=.8),dict(phi_deg=0,A_scalar=.2,B=-.30,T=0,ratio=.8),dict(phi_deg=80,A_scalar=0,B=-.4,T=-.8,ratio=1.),dict(phi_deg=80,A_scalar=-.35,B=-.4,T=-1.8,ratio=1.1)]
    rows=[]
    for N in [4,6]:
        for state in states:
            kw={k:v for k,v in state.items() if k not in ['B','T']};kw.update(N=N,eps=.003,kinetic='lab_nn_full',geometry='exact')
            models=[old.BM(**kw),BM(**kw),BM(**kw,w_kappa=5),BM(**kw,w_kappa=-5)]
            for m in models:
                add_harmonic(m,state['B'],mat=sz,use_sin=True);add_harmonic(m,state['T'],mat=sz,use_sin=True,layer_sign=-1)
            for f in [[.3,.4],[1.02,-.02]]:
                hs=[m.H(m.frac_to_k(f)) for m in models]
                exact=[bool(np.array_equal(hs[0],h)) for h in hs[1:]]
                if not all(exact):raise ValueError('default/average changes prior Hamiltonian')
                rows.append(dict(N=N,state=state,f=f,default_and_average_plus_minus_five_bitwise=exact,dimension=models[0].dim))
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');bad=BM(N=1,eps=.003,kinetic='lab_nn_full',w_kappa=float('nan'))
    witness=dict(input='NaN',constructor_rejects=False,tunneling_finite=bool(np.isfinite(bad.T).all()))
    save_json(ROOT/'provenance/default_probe.json',dict(status='PASS',source_sha256=digest(__file__),prior_sha256=digest(ROOT/'provenance/prior_bm_strain.py'),rows=rows,nonfinite_witness=witness))
    print('PASS',len(rows),'matrix comparisons; average +/-5 identical; raw NaN coefficient accepted')
if __name__=='__main__':run()
