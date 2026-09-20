"""Explicit later-campaign parameters and separately added tau harmonic.

Original and partner engines remain verbatim under engines/. The wrapper adds
the missing layer-odd harmonic in each engine's own ordering. No model correction
is silently substituted. Code makes no network or subprocess calls.
"""
from dataclasses import dataclass,asdict,replace
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'engines'))
import numpy as np
from independent_model import ReciprocalModel,Parameters
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

class Original(ReciprocalModel):
    def __init__(self,N,p):
        super().__init__(Parameters(N=N,theta=p.theta,strain=p.eps,direction=p.phi,
                         ratio=p.ratio,scalar=p.A,sine_mass=p.B))
        delta=self.indices[:,None,:]-self.indices[None,:,:]
        extra=np.zeros((self.orbitals,self.orbitals,2,2),complex)
        for shift in [(1,0),(1,1),(0,1)]:
            a=np.all(delta==shift,axis=2)
            directed=np.kron(a,np.diag([1.,-1.]))[:,:,None,None]*(p.T*110/(2j)*np.diag([1.,-1.]))
            extra+=directed+directed.transpose(1,0,3,2).conj()
        self.static+=extra.transpose(2,0,3,1).reshape(self.dim,self.dim)
    def sewing(self,axis):
        # Original G1 shift=(-1,0); G2 shift=(-1,-1) in native coordinates.
        delta=np.array([-1,0] if axis==0 else [-1,-1]);lookup={tuple(x):i for i,x in enumerate(self.indices)}
        s=np.zeros((self.dim,self.dim))
        for i,x in enumerate(self.indices):
            j=lookup.get(tuple(x+delta))
            if j is not None:
                for spin in range(2):
                    for layer in range(2):s[spin*self.orbitals+2*j+layer,spin*self.orbitals+2*i+layer]=1
        return s

class Partner:
    def __init__(self,N,p):
        self.model=TBG(N=N,theta=p.theta,w0=110*p.ratio,eps=p.eps,phi=p.phi,A=p.A,B=p.B)
        m=self.model;self.dim=m.dim
        for layer in (0,1):
            for mn,i in m.ix.items():
                for shift in [(1,0),(0,1),(-1,1)]:
                    j=m.ix.get(tuple(np.array(mn)+shift))
                    if j is None:continue
                    block=p.T*110/(2j)*(1 if layer==0 else -1)*np.diag([1.,-1.])
                    m._blk(m.Hs,layer,j,layer,i,block);m._blk(m.Hs,layer,i,layer,j,block.conj().T)
        self.spinor=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
    def real_hamiltonian(self,f):
        h=self.model.H(self.model.k(f));require(np.isfinite(h).all(),'nonfinite partner H')
        herm=float(np.max(np.abs(h-h.conj().T)));require(herm<1e-9,'non-Hermitian partner H')
        b=h.reshape(self.dim//2,2,self.dim//2,2)
        real=np.einsum('ai,manb,bj->minj',self.spinor.conj(),b,self.spinor,optimize=True).reshape(self.dim,self.dim)
        imag=float(np.max(np.abs(real.imag)));require(imag<1e-9,'partner C2zT broken')
        return real.real,dict(hermitian_residual=herm,reality_residual=imag)
    def sewing(self,axis):return self.model.shift((-1,0) if axis==0 else (0,-1))

def make(engine,N,p):
    if engine=='original':return Original(N,p)
    if engine=='partner':return Partner(N,p)
    raise ValueError(engine)
