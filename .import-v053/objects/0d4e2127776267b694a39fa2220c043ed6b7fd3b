"""Explicitly named variants of the uploaded v039 engine.

v039_full: uploaded H verbatim, kinetic='full' explicitly requested.
lab_nn_full: same graph/tunneling; lab-frame monolayer tensor and gauge.
These are two model variants, NOT two independent Hamiltonian engines.
"""
from dataclasses import dataclass
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'engines'))
import numpy as np
from tbg_ref import TBG,R,HV,PX,PY,A0
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

class LabNN(TBG):
    """F=(I+E_lab)R; crystal Pauli axes; fixed interlayer matrices.

    Intralayer terms follow the specified first-order nearest-neighbor model.
    This is a sensitivity variant, not a validated complete physical bilayer.
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        for l in (0,1):
            rot=R(self.thl[l]);ec=rot.T@self.El[l]@rot
            self.Al[l]=rot@(np.sqrt(3)*self.beta/(2*A0)*np.array([ec[0,0]-ec[1,1],-2*ec[0,1]]))

    def H(self,k):
        h=self.Hs.copy()
        for l in (0,1):
            matrix=R(-self.thl[l])@(np.eye(2)+(1-self.beta)*self.El[l])
            q=(self.origin+k[None,:]+self.Gv-self.Kl[l][0]-self.Al[l])@matrix.T
            for i in range(self.nG):self._blk(h,l,i,l,i,HV*(q[i,0]*PX+q[i,1]*PY))
        return h

class Model:
    def __init__(self,engine,N,p):
        require(engine in ['v039_full','lab_nn_full'],'unknown model variant')
        factory=TBG if engine=='v039_full' else LabNN
        self.model=factory(N=N,theta=p.theta,w0=110*p.ratio,eps=p.eps,phi=p.phi,A=p.A,B=p.B,Bt=p.T,kinetic='full')
        self.dim=self.model.dim
        self.spinor=np.array([[1,1j],[1,-1j]])/np.sqrt(2)

    def real_hamiltonian(self,f):
        h=self.model.H(self.model.k(f));require(np.isfinite(h).all(),'nonfinite Hamiltonian')
        herm=float(np.max(np.abs(h-h.conj().T)));require(herm<1e-9,'non-Hermitian Hamiltonian')
        blocks=h.reshape(self.dim//2,2,self.dim//2,2)
        real=np.einsum('ai,manb,bj->minj',self.spinor.conj(),blocks,self.spinor,optimize=True).reshape(self.dim,self.dim)
        imag=float(np.max(np.abs(real.imag)));require(imag<1e-9,'C2zT broken')
        return real.real,dict(hermitian_residual=herm,reality_residual=imag)

    def sewing(self,axis):return self.model.shift((-1,0) if axis==0 else (0,-1))

def make(engine,N,p):return Model(engine,N,p)
