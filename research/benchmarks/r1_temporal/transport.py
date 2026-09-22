"""Three-dimensional chart and explicitly sampled temporal contour transport."""
import sys,json,itertools
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'PLAN.json').read_text());T=PLAN['thresholds']
sys.path.insert(0,str(ROOT.parent/'r1_three_band'))
from frame import Family,polar,sha,edge,lift,multiply,inverse

def geometry(s,r,n):
    D=s['D_meV'];p,q,u=[np.array(x['f']) for x in s['roots']]
    e=(q-p)/np.linalg.norm(q-p);normal=np.array([-e[1],e[0]])
    base=p+.55*(q-p);kink=u-.006*normal
    angle=np.arctan2(-e[1],-e[0]);ring=[q+r*np.array([np.cos(t),np.sin(t)]) for t in np.linspace(angle,angle+2*np.pi,n+1)]
    ring[-1]=ring[0].copy()
    return {'base':np.r_[base,D],'kink':np.r_[kink,D],'ring':np.c_[ring,np.full(n+1,D)],'normal':normal}

class Chart3:
    def __init__(self,family,reference):
        self.family=family;self.reference=np.array(reference);self.cache={}
        w,F=self.eigen(reference);self.B=F
        self.norms=np.array([float(np.abs(eigh(A,eigvals_only=True)).max()) for A in family.A])
    def eigen(self,v):
        w,F=eigh(self.family.H(v),subset_by_index=(self.family.lo-1,self.family.lo+3))
        return w,F[:,1:4]
    def data(self,v):
        key=tuple(map(float,v))
        if key not in self.cache:
            w,F=self.eigen(v);Q,s=polar(self.B.T@F)
            if not np.isfinite(w).all() or not np.isfinite(F).all() or np.max(np.abs(F.T@F-np.eye(3)))>1e-8:raise RuntimeError('Invalid real eigenframe')
            self.cache[key]={'f':list(key),'w':w.tolist(),'gaps':np.diff(w).tolist(),'Q':Q,'smin':float(s.min())}
        return self.cache[key]
    def norm(self,a,b):return self.family.edge_norm(a,b)

def volume(chart,bounds,grid):
    bounds=np.array(bounds);width=(bounds[1]-bounds[0])/grid;cells=[]
    def visit(a,b,depth):
        center=(a+b)/2;d=chart.data(center);delta=float(((b-a)/2)@chart.norms)
        g=min(d['gaps'][0],d['gaps'][3]);lower=g-2*delta-T['floating_allowance']
        change=np.sqrt(3)*delta/lower if lower>0 else None
        s2=d['smin']**2-change-T['floating_allowance'] if change is not None else -1.
        ok=lower>T['gap_margin_meV'] and s2>T['chart_smin']**2
        if ok or g<=T['gap_margin_meV'] or d['smin']<T['chart_smin'] or depth>=T['maximum_volume_depth']:
            cells.append({'a':a.tolist(),'b':b.tolist(),'depth':depth,'center':center.tolist(),'gap_meV':g,'smin':d['smin'],'delta_meV':delta,'gap_lower_meV':lower,'smin_squared_lower':s2,'pass':bool(ok)})
        else:
            j=int(np.argmax((b-a)*chart.norms));mid=(a[j]+b[j])/2
            end=b.copy();end[j]=mid;start=a.copy();start[j]=mid
            visit(a,end,depth+1);visit(start,b,depth+1)
    for index in itertools.product(*(range(n) for n in grid)):
        a=bounds[0]+np.array(index)*width;b=a+width;visit(a,b,0)
    return {'bounds':bounds.tolist(),'initial_grid':grid,'norms_meV':chart.norms.tolist(),'cells':cells,'pass':all(c['pass'] for c in cells),
            'minimum_gap_lower_meV':min(c['gap_lower_meV'] for c in cells),'minimum_smin_lower':float(np.sqrt(max(0,min(c['smin_squared_lower'] for c in cells))))}

def route(chart,vertices,cfg,initial=1):
    edges=[];points=[]
    for a,b in zip(vertices[:-1],vertices[1:]):
        report,samples=edge(chart,a,b,cfg,initial)
        edges.append(report);points.extend(samples if not points else samples[1:])
    return {'vertices':np.array(vertices).tolist(),'edges':edges,'pass':all(e['pass'] for e in edges)},points

def join(*parts):
    out=list(parts[0])
    for part in parts[1:]:
        if not np.array_equal(out[-1]['f'],part[0]['f']):raise ValueError('Path seam does not close exactly')
        out.extend(part[1:])
    return out

def align(points,seed=None):
    out=[]
    for point in points:
        Q=point['Q'].copy()
        if seed is None:
            if np.linalg.det(Q)<0:Q[:,0]*=-1
        else:
            Q*=np.where(np.diag(seed.T@Q)>=0,1.,-1.)
            if np.linalg.det(seed.T@Q)<0:raise RuntimeError('Improper temporal frame step')
        out.append(Q);seed=Q
    return np.array(out)

def charge(points,base_frame):
    if not np.array_equal(points[0]['f'],points[-1]['f']):raise ValueError('Not a closed contour')
    raw=np.array([x['Q'] for x in points])
    signs=np.where(np.diag(raw[0].T@base_frame)>=0,1.,-1.)
    if np.max(np.abs(raw[0]*signs-base_frame))>T['cross_check_error']:raise RuntimeError('Base frame does not match loop')
    result,path=lift(raw*signs)
    return result,path

def station_paths(chart,g,cfg):
    tr,tp=route(chart,[g['base'],g['kink'],g['ring'][0]],cfg,cfg['stem_subintervals'])
    cr,cp=route(chart,g['ring'],cfg)
    return {'stem':tr,'circle':cr,'pass':tr['pass'] and cr['pass']},tp,cp

def array_points(arrays,key,points):
    for suffix,field in [('v','f'),('w','w'),('Q','Q'),('smin','smin')]:arrays[key+'_'+suffix]=np.array([x[field] for x in points])
