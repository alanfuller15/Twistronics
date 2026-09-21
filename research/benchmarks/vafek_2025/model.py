"""Projected nu=-2, one-spin THF benchmark, arXiv:2502.08700v2.
Energy: meV. Momentum K=v*k/gamma and boost Q=v*q/gamma are dimensionless.
Equations 57, 73, 74, 85-87; v'=0, no damping, mu or subleading strain terms.
"""
import numpy as np
from scipy.linalg import block_diag
I=np.eye(2); X=np.array([[0,1],[1,0]]); Y=np.array([[0,-1j],[1j,0]]); Z=np.diag([1,-1])
PARAMETERS=dict(gamma=-24.8,v_meV_A=-4300.,M=3.7,Mf=4380.,strain=.0015,poisson=.16,U1=58.,U2=2.3,W3=50.2,J=16.4,cpp=-3362.)
B2=np.array([[1,1j],[1,-1j]])/np.sqrt(2); B=block_diag(B2,B2)
class Model:
 def __init__(self,params=None):
  self.p=PARAMETERS.copy(); self.p.update(params or {});p=self.p
  self.eps=-(1+p['poisson'])*p['strain']/2
  self.delta=p['Mf']*self.eps
  z=np.array([1,1j,1j,1])/2;P=np.outer(z,z.conj());a=P-.5*np.eye(4)
  t3=np.kron(Z,I);s3=np.kron(I,Z)
  self.hc=-2*p['W3']*np.eye(4)-p['J']/2*(t3@a@t3+s3@a@s3)
  self.hf=-p['U1']*a-2*(p['U1']+6*p['U2'])*np.eye(4)
 def valley(self,x,y):
  return (2*self.p['cpp']*self.eps*y*I+self.delta*(-2*x*y*X+(x*x-y*y)*Y)+self.p['M']*X)/(1+x*x+y*y)
 def h(self,k,Q):
  x,y=k;xp=x+Q/2;xm=x-Q/2
  np_=np.sqrt(1+xp*xp+y*y);nm=np.sqrt(1+xm*xm+y*y)
  C=np.diag([1/np_,1/np_,1/nm,1/nm])
  F=np.diag([-(xp+1j*y)/np_,-(xp-1j*y)/np_,(xm-1j*y)/nm,(xm+1j*y)/nm])
  return block_diag(self.valley(xp,y),self.valley(-xm,-y).conj())+C@self.hc@C+F.conj().T@self.hf@F
 def real(self,k,Q):
  h=B.conj().T@self.h(k,Q)@B
  if np.max(np.abs(h.imag))>1e-10:raise ValueError('C2T reality failed')
  return h.real
 def gamma_branches(self,Q):
  p=self.p;M,J,U,V,W=[p[n] for n in ['M','J','U1','U2','W3']];t=Q*Q;d=8+2*t
  a=(-16*W-3*t*(U+8*V))/d;ar=2*np.sqrt(16*M*M+self.delta**2*t*t)/d
  b=(4*(J-4*W)-4*t*(U+6*V))/d;br=np.sqrt(64*M*M+t*t*(U-2*self.delta)**2)/d
  return np.array([a-ar,a+ar,b-br,b+br])
 def axis_spectrum(self,x):
  p=self.p;M,J,U,V,W=[p[n] for n in ['M','J','U1','U2','W3']];t=x*x
  a=((J-4*W)-3*t*(U+8*V))/(2*(1+t));ar=np.sqrt(t*t*self.delta**2+M*M)/(1+t)
  b=(-2*W-2*t*(U+6*V))/(1+t);br=np.sqrt(t*t*(U/2-self.delta)**2+M*M)/(1+t)
  return np.sort([a-ar,a+ar,b-br,b+br])

 def direct_projection(self,k,Q):
  """Separate assembly from Eqs28,35,57,74,85. Tests Eq73 transcription.
  Both implementations authored here; agreement is not independent validation.
  """
  x,y=k;p=self.p;G=p['gamma'];I4=np.eye(4);a=np.diag([x+Q/2+1j*y,x+Q/2-1j*y,-x+Q/2+1j*y,-x+Q/2-1j*y])
  c=G*a;f=G*I4;h12=np.zeros((12,12),complex)
  h12[:4,4:8]=c;h12[4:8,:4]=c.conj().T;h12[:4,8:]=f;h12[8:,:4]=f
  h12[4:8,4:8]=p['M']*np.kron(I,X)+self.hc
  h12[8:,8:]=self.delta*np.kron(Z,Y)+self.hf
  cf=-1j*p['cpp']*self.eps*np.kron(Z,Z)
  h12[4:8,8:]=cf;h12[8:,4:8]=cf.conj().T
  n=np.diag(1/np.sqrt(1+abs(np.diag(a))**2))
  u=np.vstack([np.zeros((4,4)),n,-a@n])
  return u.conj().T@h12@u
