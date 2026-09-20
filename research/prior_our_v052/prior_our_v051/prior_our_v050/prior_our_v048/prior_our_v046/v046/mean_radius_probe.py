"""Check the claimed average-valley-radius cancellation with rotated exact geometry.
This tests the proposed geometric argument, not a microscopic tunneling law.
"""
import json
from pathlib import Path
import numpy as np
from checkpoints import save_json,digest
ROOT=Path(__file__).resolve().parent

def rotation(t):return np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
def mean_radius(eps,phi,theta,alpha,nu=.16):
    E=eps*rotation(phi)@np.diag([1.,-nu])@rotation(phi).T
    e=rotation(alpha)@np.array([1.,0.])
    vec=[np.linalg.inv(np.eye(2)+sign*E/2).T@rotation(sign*theta/2)@e for sign in [-1,1]]
    return sum(np.linalg.norm(x) for x in vec)/2

def main():
    rows=[];theta=np.radians(1.05)
    for phi_deg in [0.,80.]:
        phi=np.radians(phi_deg)
        for j in range(3):
            alpha=j*2*np.pi/3
            analytical=-(1+.16)/4*np.sin(2*(phi-alpha))*np.sin(theta)
            trials=[dict(epsilon_step=h,derivative=(mean_radius(h,phi,theta,alpha)-mean_radius(-h,phi,theta,alpha))/(2*h)) for h in [1e-5,5e-6]]
            if max(abs(r['derivative']-analytical) for r in trials)>1e-8:raise ValueError('derivative check failed')
            rows.append(dict(phi_deg=phi_deg,j=j,analytic_derivative=float(analytical),finite_difference_trials=trials,mean_radius_ratio_at_eps003=mean_radius(.003,phi,theta,alpha)))
    out=dict(status='PASS',source_sha256=digest(__file__),scope='geometric mean-radius argument only; fixed theta, opposite lab-frame strains, inverse-deformation geometry',rows=rows)
    save_json(ROOT/'provenance/mean_radius_probe.json',out)
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
