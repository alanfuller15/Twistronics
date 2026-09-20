"""Reproduce the cutoff-padding counterexample without an eigensolve."""
import json
from pathlib import Path
import numpy as np
from models import State,make

ROOT=Path(__file__).resolve().parent
p=State(A=0,B=0,T=0,phi=15.843560625048124,ratio=.8)
a,b=[make(e,4,p) for e in ['bm_exact','ref_lab']]
delta=float(np.linalg.norm(-4*a.model.G1+3*a.model.G2)-4*np.linalg.norm(a.model.G1))
print(json.dumps(dict(N=4,phi=p.phi,kinetic='lab_nn_full',geometry='exact',boundary_excess=delta,
                     bm_dimension=a.dim,ref_dimension=b.dim,bm_only=sorted(set(a.model.idx)-set(b.model.mn)),
                     bm_padding=1e-6,ref_padding=1e-9),indent=2))
