"""Thin adapters around the two unchanged uploaded v041 Hamiltonian engines.

Both request lab_nn_full explicitly. BM retains linearized reciprocal
geometry; TBG retains its inverse deformation. No silent geometry matching.
"""
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'engines'))
import numpy as np
from bm_strain import BM,sz
from knobs import add_harmonic
from tbg_ref import TBG
from independent_measurement import require

@dataclass(frozen=True)
class State:
    A:float=0.
    B:float=-.4
    T:float=-.8
    phi:float=80.
    ratio:float=.99
    theta:float=1.05
    eps:float=.003

class Model:
    def __init__(self,engine,N,p):
        require(engine in ['bm_lab','ref_lab'],'unknown engine')
        self.engine=engine
        if engine=='bm_lab':
            self.model=BM(N=N,theta_deg=p.theta,ratio=p.ratio,eps=p.eps,phi_deg=p.phi,A_scalar=p.A,kinetic='lab_nn_full')
            add_harmonic(self.model,p.B,mat=sz,use_sin=True)
            add_harmonic(self.model,p.T,mat=sz,use_sin=True,layer_sign=-1)
            self.k=self.model.frac_to_k
        else:
            self.model=TBG(N=N,theta=p.theta,w0=110*p.ratio,eps=p.eps,phi=p.phi,A=p.A,B=p.B,Bt=p.T,kinetic='lab_nn_full')
            self.k=self.model.k
        self.dim=self.model.dim
        self.spinor=np.array([[1,1j],[1,-1j]])/np.sqrt(2)

    def real_hamiltonian(self,f):
        h=self.model.H(self.k(f));require(np.isfinite(h).all(),'nonfinite Hamiltonian')
        herm=float(np.max(np.abs(h-h.conj().T)));require(herm<1e-9,'non-Hermitian Hamiltonian')
        blocks=h.reshape(self.dim//2,2,self.dim//2,2)
        real=np.einsum('ai,manb,bj->minj',self.spinor.conj(),blocks,self.spinor,optimize=True).reshape(self.dim,self.dim)
        imag=float(np.max(np.abs(real.imag)));require(imag<1e-9,'C2zT broken')
        return real.real,dict(hermitian_residual=herm,reality_residual=imag)

    def sewing(self,axis):
        delta=(-1,0) if axis==0 else (0,-1)
        if self.engine=='ref_lab':return self.model.shift(delta)
        m=self.model;s=np.zeros((self.dim,self.dim))
        for (a,b),i in m.pos.items():
            j=m.pos.get((a+delta[0],b+delta[1]))
            if j is None:continue
            for layer in (0,1):
                for spin in (0,1):s[2*m.nG*layer+2*j+spin,2*m.nG*layer+2*i+spin]=1.
        return s

def make(engine,N,p):return Model(engine,N,p)
