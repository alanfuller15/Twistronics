"""Independent nearest-neighbor monolayer TB slope, using explicit bonds.

Compare gauge-invariant cone metric J.T J so spinor phase conventions cannot
hide a velocity error. This verifies a specified monolayer approximation, not
a complete bilayer model or its interlayer tunneling.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import root
from models import State
from independent_model import rotation
from independent_measurement import require

def cone(E,theta,beta):
    a=2.46/np.sqrt(3);bonds=a*np.array([[np.sqrt(3)/2,.5],[-np.sqrt(3)/2,.5],[0,-1.]])
    R=rotation(theta);F=(np.eye(2)+E)@R;deformed=bonds@F.T
    hopping=np.exp(-beta*(np.linalg.norm(deformed,axis=1)/a-1))
    k0=np.linalg.solve(F.T,np.array([4*np.pi/(3*np.sqrt(3)*a),0.]))
    def off(k):return np.sum(hopping*np.exp(1j*(deformed@k)))
    sol=root(lambda k:np.array([off(k).real,off(k).imag]),k0,tol=1e-11)
    require(np.linalg.norm([off(sol.x).real,off(sol.x).imag])<1e-10,'TB Dirac root')
    derivative=np.sum((1j*hopping*np.exp(1j*(deformed@sol.x)))[:,None]*deformed,axis=0)
    J=np.array([derivative.real,derivative.imag])/(1.5*a)
    metric=J.T@J;u,s,vh=np.linalg.svd(J)
    return sol.x-k0,metric

def run():
    rows=[]
    for beta in [0.,3.14]:
        for phi in [0.,37.,80.]:
            u=np.array([np.cos(np.deg2rad(phi)),np.sin(np.deg2rad(phi))]);shape=1.16*np.outer(u,u)-.16*np.eye(2)
            for theta in [0.,np.deg2rad(.525)]:
                previous=None
                for eps in [.0015,.00075,.000375]:
                    E=eps*shape;shift,metric=cone(E,theta,beta);R=rotation(theta)
                    M=R.T@(np.eye(2)+(1-beta)*E);pred=M.T@M
                    wrong=(np.eye(2)-E)@R.T
                    Ecr=R.T@E@R;a=2.46/np.sqrt(3)
                    Alab=R@(beta/(2*a)*np.array([Ecr[0,0]-Ecr[1,1],-2*Ecr[0,1]]))
                    err=float(np.max(np.abs(metric-pred)));aerr=float(np.max(np.abs(shift-Alab)))
                    require(err<15*eps**2,'first-order cone metric disagrees with tight binding')
                    require(aerr<15*eps**2,'first-order gauge shift disagrees with tight binding')
                    if previous is not None and beta:require(previous/err>3.5,'metric residual not second order')
                    rows.append(dict(beta=beta,phi=phi,theta_degrees=float(np.rad2deg(theta)),eps=eps,metric_error=err,gauge_error=aerr,I_minus_E_metric_error=float(np.max(np.abs(metric-wrong.T@wrong))),error_halving_ratio=None if previous is None else previous/max(err,1e-30)))
                    previous=err
    return dict(status='PASS',definition='Lab strain E, layer rotation R, real-space deformation F=(I+E)R. Linear kinetic M=R.T (I+(1-beta)E); crystal-frame gauge rotated back to lab.',rows=rows)

if __name__=='__main__':
    result=run();path=Path(__file__).resolve().parent/'results/strain_check.json';path.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(result['rows']))
