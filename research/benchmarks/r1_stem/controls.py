"""Analytic controls of velocity, geometry, identity and root enclosure."""
import json
import numpy as np
from crossing import ROOT, sha, center_data, certificate, geometry, identity, interval_newton

class Toy:
    dim=5
    def __init__(self, velocity=(0.,-.01), center=(.6,.5), rotation=None, close=False):
        self.A=[np.zeros((5,5)) for _ in range(3)]
        self.A[0][1,1]=1;self.A[0][2,2]=-1
        self.A[1][1,2]=self.A[1][2,1]=1
        self.A[2]=-velocity[0]*self.A[0]-velocity[1]*self.A[1]
        self.h0=np.diag([-30.,0.,0.,15.,35.])-center[0]*self.A[0]-center[1]*self.A[1]
        if close:self.h0[3,3]=.2;self.A[2][3,3]=-1
        if rotation is not None:
            self.h0=rotation.T@self.h0@rotation
            self.A=[rotation.T@x@rotation for x in self.A]
    def H(self,v):return self.h0+v[0]*self.A[0]+v[1]*self.A[1]+(v[2]-38.5)*self.A[2]

checks=[]
def record(name,passed,details):
    checks.append({'name':name,'pass':bool(passed),'details':details});assert passed,name

raw,F=center_data(Toy(),38.5,1,[.6,.5]);cert=certificate(raw,.5)
ends=np.array([[[.2,.5],[.8,.5]],[[.2,.5],[.8,.5]]]);vel=np.zeros((2,2))
g=geometry(raw,cert,ends,vel,38,39)
record('known_transverse_affine_root',g['slope_bounds'][1]<0 and g['along_bounds'][0]>0 and g['along_bounds'][1]<1 and g['slope_bounds'][0]<=-.006<=g['slope_bounds'][1],g)
Q,_=np.linalg.qr(np.random.default_rng(451).normal(size=(5,5)))
rr,_=center_data(Toy(rotation=Q),38.5,1,[.6,.5]);cc=certificate(rr,.5);gg=geometry(rr,cc,ends,vel,38,39)
angle=.61;rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
toy=Toy(rotation=Q);old=toy.A[:2];shift=np.array([.12,-.04])
toy.A[:2]=[sum(rot[j,k]*old[k] for k in range(2)) for j in range(2)]
toy.h0-=sum(shift[j]*toy.A[j] for j in range(2))
fc=rot@np.array([.6,.5])+shift
rr,_=center_data(toy,38.5,1,fc);cc=certificate(rr,.5)
rotated=geometry(rr,cc,ends@rot.T+shift,vel@rot.T,38,39)
record('constant_basis_and_coordinate_rotation',gg['slope_bounds'][1]<0 and rotated['slope_bounds'][0]<=-.006<=rotated['slope_bounds'][1] and np.max(abs(np.array(rotated['side_coefficients'])-g['side_coefficients']))<1e-12,rotated)
rr,_=center_data(Toy(velocity=(0.,.01)),38.5,1,[.6,.5]);cc=certificate(rr,.5);gg=geometry(rr,cc,ends,vel,38,39)
record('parameter_reversal',gg['slope_bounds'][0]>0,gg)
for offset,name in [(0.,'tangency_rejected'),(.04,'two_crossings_not_excluded')]:
    rr,_=center_data(Toy(velocity=(-1.,.5),center=(.5,-offset)),38.5,1,[.5,-offset]);cc=certificate(rr,.3)
    en=np.array([[[0.,0.],[1.,-.3]],[[0.,0.],[1.,.3]]]);vv=np.array([[0.,0.],[0.,1.]])
    gg=geometry(rr,cc,en,vv,38.2,38.8)
    record(name,gg['slope_bounds'][0]<0<gg['slope_bounds'][1] and gg['side_bounds'][0]<=0<=gg['side_bounds'][1],gg)
outside=np.array([[[.1,.5],[.3,.5]],[[.1,.5],[.3,.5]]]);gg=geometry(raw,cert,outside,vel,38,39)
record('supporting_line_is_not_segment',gg['slope_bounds'][1]<0 and gg['along_bounds'][0]>1,gg)
rr,_=center_data(Toy(close=True),38.5,1,[.6,.5]);cc=certificate(rr,.5)
record('complement_closes_inside_interval',not cc['pass'],cc)
wrong=dict(raw,y=[.9,.5,0.]);check=identity(wrong,certificate(wrong,0),raw,cert,38.5,38.5)
record('wrong_identity_rejected',not check['pass'],check)
step=interval_newton(38,39,38.4,[.00059,.00061],[-.00601,-.00599])
record('interval_newton_encloses_known_event',step['pass'] and step['interval'][0]<=38.5<=step['interval'][1],step)
result={'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{n:sha(ROOT/n) for n in ['crossing.py','controls.py']},'all_controls_pass':all(x['pass'] for x in checks),'controls':checks}
(ROOT/'CONTROLS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print('CONTROLS',len(checks),'PASS',result['all_controls_pass'])
