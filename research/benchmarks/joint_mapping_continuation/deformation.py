"""Analytic strain derivatives and uniform norm bounds for a fixed index set."""
from pathlib import Path
import json
import sys
import numpy as np
ROOT=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'PLAN.json').read_text());CFG=PLAN['bounds']
sys.path.insert(0,str(ROOT.parent/'joint_mapping_guarded'))
import jm_model as model
from bm_strain import rot, A_LAT, HBARV

def geometry(eps,theta,phi):
    ph=np.radians(phi);nu=.16;beta=3.14
    C=np.array([[np.cos(ph)**2-nu*np.sin(ph)**2,(1+nu)*np.sin(ph)*np.cos(ph)],
                [(1+nu)*np.sin(ph)*np.cos(ph),np.sin(ph)**2-nu*np.cos(ph)**2]])
    KD=np.array([4*np.pi/(3*A_LAT),0.]);th=np.radians(theta)
    layers=[]
    for sign,angle in [(-1,-th/2),(1,th/2)]:
        L=sign*C/2;P=np.linalg.inv(np.eye(2)+eps*L)
        Pp=-P@L@P;Ppp=2*P@L@P@L@P
        Ec=rot(-angle)@L@rot(angle)
        gauge=rot(angle)@(np.sqrt(3)*beta/(2*A_LAT)*np.array([Ec[0,0]-Ec[1,1],-2*Ec[0,1]]))
        K=[rot(angle)@rot(2*np.pi*j/3)@KD for j in range(3)]
        layers.append(dict(L=L,P=P,Pp=Pp,Ppp=Ppp,K=K,gauge=gauge,
                           M=rot(-angle)@(np.eye(2)+(1-beta)*eps*L),Mp=rot(-angle)@((1-beta)*L)))
    qs=[]
    for key in ('P','Pp','Ppp'):
        qs.append(np.array([layers[0][key]@layers[0]['K'][j]-layers[1][key]@layers[1]['K'][j] for j in range(3)]))
    return layers,qs

class StrainFamily(model.Family):
    def __init__(self,x,cfg):
        super().__init__(x,cfg)
        if self.cfg['indices'] is None:raise ValueError('fixed indices required')
        if self.x['theta']!=1. or self.x['phi']!=15. or self.x['P']!=1.:
            raise ValueError('only the frozen strain line is supported')
        self.s=self.x['eps'];self.layers,self.qjets=geometry(self.s,self.x['theta'],self.x['phi'])
        self.Gjets=[np.array([q[1]-q[0],q[2]-q[0]]) for q in self.qjets]

    def derivative(self,f):
        H=np.zeros((self.dim,self.dim));n=len(self.indices)
        weights=np.array(self.indices)+np.array(f)
        for l,L in enumerate(self.layers):
            p=weights@self.Gjets[0]+(self.qjets[0][0] if l else 0)-self.s*L['gauge']
            pp=weights@self.Gjets[1]+(self.qjets[1][0] if l else 0)-L['gauge']
            v=HBARV*(p@L['Mp'].T+pp@L['M'].T)
            ids=2*n*l+2*np.arange(n)
            H[ids,ids]=v[:,0];H[ids+1,ids+1]=-v[:,0]
            H[ids,ids+1]=-v[:,1];H[ids+1,ids]=-v[:,1]
        return H

    def remainder_bounds(self,f,velocity,h):
        """Bounds H'' along affine f(s), and ||A_j(s)-A_j(s0)||/h.

        ||L_l||=1/2; ||(I+s L_l)^-1|| <= 1/(1-max|s|/2).
        Constant tunnel and affine D terms contribute no second derivative.
        """
        emax=abs(self.s)+h;den=1-emax/2
        if den<=0:raise ValueError('inverse deformation may be singular')
        kd=4*np.pi/(3*A_LAT);qp=kd/den**2;qpp=kd/den**3
        gp=np.full(2,2*qp);gpp=np.full(2,2*qpp)
        gmax=np.linalg.norm(self.Gjets[0],axis=1)+h*gp
        mm=1+abs(1-3.14)*emax/2;mp=abs(1-3.14)/2
        axis_change=HBARV*(mp*gmax+mm*gp)+CFG['norm_allowance']
        weights=np.abs(np.array(self.indices)+np.asarray(f))+h*np.abs(velocity[:2])
        norms=[]
        for l,L in enumerate(self.layers):
            pp=weights@gp+np.abs(velocity[:2])@gmax+(qp if l else 0)+np.linalg.norm(L['gauge'])
            ppp=weights@gpp+2*np.abs(velocity[:2])@gp+(qpp if l else 0)
            norms.append(float(np.max(HBARV*(2*mp*pp+mm*ppp))))
        return dict(second_norm=max(norms)+CFG['norm_allowance'],axis_derivative_norms=axis_change.tolist(),inverse_denominator=den)

def make_family(engine,eps,D):
    indices=json.loads((ROOT.parent/'joint_mapping_guarded/BASIS.json').read_text())['union']
    return StrainFamily(dict(eps=eps,phi=15.,theta=1.,D=D,P=1.),dict(N=6,engine=engine,indices=indices))
