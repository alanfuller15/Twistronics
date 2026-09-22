"""Post-production analytic check of genuinely nonlinear Schur velocity."""
import json
import numpy as np
from crossing import ROOT, sha, center_data, certificate, velocity_bound

class Curved:
    dim=4
    def __init__(self):
        x=np.diag([0.,1.,-1.,0.]);y=np.zeros((4,4));y[1,2]=y[2,1]=1.
        d=np.zeros((4,4));d[1,3]=d[3,1]=1.
        self.A=[x,y,d];self.h0=np.diag([-10.,0.,0.,10.])-.4*x-.6*y
    def H(self,v):return self.h0+v[0]*self.A[0]+v[1]*self.A[1]+(v[2]-38)*self.A[2]

plan=json.loads((ROOT/'VELOCITY_CONTROL_PLAN.json').read_text());records=[]
for a,b in plan['intervals_meV']:
    mid=(a+b)/2;d=mid-38;x=np.sqrt(25+d*d/2)-5
    raw,F=center_data(Curved(),mid,1,[.4+x,.6]);cert=certificate(raw,(b-a)/2);bound=velocity_bound(raw,cert)
    assert cert['pass'] and bound['pass']
    exact=[]
    for D in [a,b]:
        d=D-38;v=d/(2*np.sqrt(25+d*d/2));exact.append([v,0.,-v])
    lo=np.min(exact,axis=0);hi=np.max(exact,axis=0)
    blo=np.array(raw['velocity'])-bound['velocity_radius'];bhi=np.array(raw['velocity'])+bound['velocity_radius']
    margins=np.minimum(lo-blo,bhi-hi);passed=bool(np.min(margins)>0)
    records.append({'a':a,'b':b,'raw':raw,'certificate':cert,'bound':bound,'analytic_velocity_bounds':[lo.tolist(),hi.tolist()],'containment_margins':margins.tolist(),'pass':passed})
    assert passed
out={'status':'POST_PRODUCTION_NONLINEAR_VELOCITY_CONTROLS_PASS','all_controls_pass':all(r['pass'] for r in records),'controls':records,
     'source_hashes':{n:sha(ROOT/n) for n in ['VELOCITY_CONTROL_PLAN.json','velocity_control.py','crossing.py','PLAN.json']}}
(ROOT/'VELOCITY_CONTROLS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('NONLINEAR VELOCITY CONTROLS',len(records),'PASS',out['all_controls_pass'])
