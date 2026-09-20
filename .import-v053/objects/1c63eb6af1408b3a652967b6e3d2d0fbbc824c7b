"""Compare uploaded frame order and gauge to an independent bond model."""
import json
from pathlib import Path
import numpy as np
from models import R,A0
from strain_check import cone,run

def audit():
    rows=[];beta=3.14;theta=np.deg2rad(.525)
    for phi in [0.,65.,80.]:
        u=np.array([np.cos(np.deg2rad(phi)),np.sin(np.deg2rad(phi))]);shape=1.16*np.outer(u,u)-.16*np.eye(2)
        for eps in [.0015,.00075,.000375]:
            e=eps*shape;rot=R(theta);v=np.eye(2)+(1-beta)*e
            shift,metric=cone(e,theta,beta)
            uploaded=v@rot.T;lab=rot.T@v
            a0=np.sqrt(3)*beta/(2*A0)*np.array([e[0,0]-e[1,1],-2*e[0,1]])
            ec=rot.T@e@rot;alab=rot@(np.sqrt(3)*beta/(2*A0)*np.array([ec[0,0]-ec[1,1],-2*ec[0,1]]))
            rows.append(dict(phi=phi,eps=eps,theta_degrees=.525,
                uploaded_metric_error=float(np.max(np.abs(metric-uploaded.T@uploaded))),
                lab_metric_error=float(np.max(np.abs(metric-lab.T@lab))),
                uploaded_gauge_error=float(np.max(np.abs(shift-a0))),
                lab_gauge_error=float(np.max(np.abs(shift-alab))),
                matrix_order_difference=float(np.max(np.abs(uploaded-lab))),
                gauge_difference=float(np.max(np.abs(alab-a0)))))
    return dict(independent_monolayer_checks=run(),comparison=rows,
                limit='Specified nearest-neighbor monolayer expansion; no tunneling strain law or physical bilayer validation.')

if __name__=='__main__':
    r=audit();p=Path(__file__).resolve().parent/'results/strain_audit.json';p.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(r['independent_monolayer_checks']['rows']),'monolayer checks;',len(r['comparison']),'comparisons')
