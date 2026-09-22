"""Interior gap bounds on a complete bilinear face; no node-worldline claim."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'PLAN.json').read_text());T=PLAN['thresholds']
sys.path.insert(0,str(ROOT.parent/'r1_temporal'))
from transport import Family,geometry
COLUMNS=['u0','u1','t0','t1','depth','parent','left','right','state','v0','v1','D','w0','w1','w2','w3','w4','delta','lower0','lower1','lower2','lower3']
STATES={0:'split',1:'accepted',-2:'center_gap_violation',-3:'depth_exhausted',-4:'budget_exhausted'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def point(c,u,t):
    # c[t endpoint, spatial endpoint, coordinate]
    return (1-t)*((1-u)*c[0,0]+u*c[0,1])+t*((1-u)*c[1,0]+u*c[1,1])
def corners(c,a,b):return np.array([[point(c,u,t) for u in a] for t in b])
def operator_norms(family):return np.array([float(np.max(np.abs(eigh(a,eigvals_only=True)))) for a in family.A])
class Spectrum:
    def __init__(self,family):self.family=family
    def __call__(self,v):
        w=eigh(self.family.H(v),eigvals_only=True,subset_by_index=(self.family.lo-1,self.family.lo+3))
        if not np.isfinite(w).all():raise RuntimeError('Nonfinite spectrum')
        return w

def cover(c,spectrum,norms,thresholds=T):
    c=np.asarray(c,float);norms=np.asarray(norms);rows=[]
    def visit(a,b,depth,parent):
        i=len(rows);v=point(c,sum(a)/2,sum(b)/2);cc=corners(c,a,b)
        delta=float(np.max(np.abs(cc-v)@norms));w=spectrum(v)
        lower=np.diff(w)-2*delta-thresholds['floating_allowance_meV'];g=float(np.diff(w).min())
        state=1 if lower.min()>thresholds['gap_margin_meV'] else -2 if g<=thresholds['gap_margin_meV'] else -3 if depth>=thresholds['maximum_depth'] else -4 if len(rows)>=thresholds['maximum_evaluations_per_face'] else 0
        rows.append([*a,*b,depth,parent,-1,-1,state,*v,*w,delta,*lower])
        if state==0:
            du=float(np.max(np.abs(cc[:,1]-cc[:,0])@norms));dt=float(np.max(np.abs(cc[1]-cc[0])@norms))
            if du>=dt:
                m=sum(a)/2;l=visit((a[0],m),b,depth+1,i);r=visit((m,a[1]),b,depth+1,i)
            else:
                m=sum(b)/2;l=visit(a,(b[0],m),depth+1,i);r=visit(a,(m,b[1]),depth+1,i)
            rows[i][6:8]=[l,r]
        return i
    visit((0.,1.),(0.,1.),0,-1)
    return np.asarray(rows,float)

def summaries(rows):
    leaf=rows[rows[:,8]!=0];bad=leaf[leaf[:,8]!=1]
    return {'evaluations':len(rows),'leaves':len(leaf),'unresolved_leaves':len(bad),'pass':len(bad)==0,
            'minimum_lower_meV':float(leaf[:,18:22].min()),'minimum_center_gap_meV':float(np.diff(rows[:,12:17],axis=1).min()),
            'maximum_depth':int(rows[:,4].max()),'leaf_parameter_area':float(np.sum((leaf[:,1]-leaf[:,0])*(leaf[:,3]-leaf[:,2])))}

def face_geometry(stations,r,n):
    gg=[geometry(s,r,n) for s in stations]
    for j,(a,b) in enumerate(zip(gg[:-1],gg[1:])):
        av=np.array([a['base'],a['kink'],*a['ring']]);bv=np.array([b['base'],b['kink'],*b['ring']])
        for k in range(n+2):yield j,k,np.array([[av[k],av[k+1]],[bv[k],bv[k+1]]])
