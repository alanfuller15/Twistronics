"""Guarded three-band reference chart and Spin(3) lift; see METHOD.md."""
import sys,json
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'PLAN.json').read_text());T=P['thresholds']
sys.path.insert(0,str(ROOT.parent/'r1_holonomy'))
from measure import Family,polar,sha

def multiply(a,b):
    w,x=a[0],np.array(a[1:]);v,y=b[0],np.array(b[1:])
    return np.r_[w*v-x@y,w*y+v*x+np.cross(x,y)]

def inverse(q):return np.asarray(q)*[1,-1,-1,-1]

def quat(R):
    q=Rotation.from_matrix(R).as_quat()
    return np.r_[q[3],q[:3]]

def nearest(q):
    units=np.concatenate([np.eye(4),-np.eye(4)])
    names=['+1','+i','+j','+k','-1','-i','-j','-k']
    i=int(np.argmin(np.linalg.norm(units-q,axis=1)))
    name=names[i]
    return name,('+-'+name[-1] if name[-1]!='1' else name),float(np.linalg.norm(units[i]-q))

def lift(raw,check=True):
    raw=np.asarray(raw)
    frames=[raw[0].copy()]
    if np.linalg.det(frames[0])<0:frames[0][:,0]*=-1
    proper=True;angles=[];minimum_diagonal=1.;path=[np.array([1.,0,0,0])]
    for Q in raw[1:]:
        diagonal=np.diag(frames[-1].T@Q)
        minimum_diagonal=min(minimum_diagonal,float(np.abs(diagonal).min()))
        U=Q*np.where(diagonal>=0,1.,-1.)
        R=frames[-1].T@U
        det=float(np.linalg.det(R))
        if det<0:proper=False
        # Never turn an improper step into a quaternion and hide the failure.
        if det<0:return {'valid':False,'failure':'improper sign-aligned step'},None
        dq=quat(R)
        if dq[0]<0:dq=-dq
        angles.append(float(2*np.arctan2(np.linalg.norm(dq[1:]),dq[0])))
        q=multiply(inverse(path[-1]),dq)
        q/=np.linalg.norm(q)
        path.append(inverse(q));frames.append(U)
    path=np.array(path);frames=np.array(frames)
    absolute=[np.array([1.,0,0,0])]
    for U in frames[1:]:
        q=inverse(quat(frames[0].T@U))
        if q@absolute[-1]<0:q=-q
        absolute.append(q)
    errors={'two_lifts':float(np.max(np.abs(path-absolute))),
            'orthogonality':float(np.max(np.abs(np.transpose(frames,(0,2,1))@frames-np.eye(3)))),
            'endpoint_offdiagonal':float(np.max(np.abs(frames[0].T@frames[-1]-np.diag(np.diag(frames[0].T@frames[-1])))))}
    name,cls,distance=nearest(path[-1])
    valid=proper and distance<T['quaternion_distance'] and max(errors.values())<T['cross_check_error']
    result={'valid':bool(valid),'quaternion':path[-1].tolist(),'nearest_label':name,'conjugacy_class':cls,
            'distance_to_Q8':distance,'maximum_step_radians':max(angles,default=0.),
            'minimum_sign_overlap':minimum_diagonal,'cross_checks':errors}
    if check:
        rev,_=lift(raw[::-1],False)
        rng=np.random.default_rng(P['gauge_seed'])
        signs=rng.choice([-1.,1.],size=(len(raw),3));signs[0]=1;signs[-1]=signs[0]
        gauged,_=lift(raw*signs[:,None,:],False)
        C=Rotation.from_rotvec([.2,-.4,.3]).as_matrix()
        rotated,_=lift(C@raw,False)
        errors['reversal']=float(np.max(np.abs(np.array(rev['quaternion'])-inverse(path[-1]))))
        errors['local_sign_gauge']=float(np.max(np.abs(np.array(gauged['quaternion'])-path[-1])))
        errors['constant_reference_rotation']=float(np.max(np.abs(np.array(rotated['quaternion'])-path[-1])))
        result['valid']=bool(valid and rev['valid'] and gauged['valid'] and rotated['valid'] and max(errors.values())<T['cross_check_error'])
    return result,path

class Chart:
    def __init__(self,family,D,base,B=None):
        self.family=family;self.D=D;self.base=np.asarray(base);self.cache={}
        self.B=self.eigen(base)[1] if B is None else B
    def eigen(self,f):
        w,F=eigh(self.family.H([*f,self.D]),subset_by_index=(self.family.lo-1,self.family.lo+3))
        return w,F[:,1:4]
    def data(self,f):
        key=tuple(map(float,f))
        if key not in self.cache:
            w,F=self.eigen(f);Q,s=polar(self.B.T@F)
            self.cache[key]={'f':list(key),'w':w.tolist(),'gaps':np.diff(w).tolist(),'Q':Q,
                             'smin':float(s.min()),'frame_orthogonality_error':float(np.max(np.abs(F.T@F-np.eye(3))))}
        return self.cache[key]
    def norm(self,a,b):return self.family.edge_norm([*a,self.D],[*b,self.D])

def rectangle(chart,bounds,n):
    bounds=np.asarray(bounds);width=(bounds[1]-bounds[0])/n
    norms=[float(np.abs(eigh(A,eigvals_only=True)).max()) for A in chart.family.A[:2]]
    delta=float(width@np.array(norms)/2)
    cells=[]
    for i in range(n):
        for j in range(n):
            f=bounds[0]+(np.array([i,j])+.5)*width
            d=chart.data(f);g=min(d['gaps'][0],d['gaps'][3])
            lower=g-2*delta-T['floating_allowance_meV']
            displacement=float(np.sqrt(3)*delta/lower) if lower>0 else None
            s2=d['smin']**2-displacement-T['floating_allowance_meV'] if displacement is not None else -1.
            ok=lower>T['gap_margin_meV'] and s2>T['chart_smin']**2
            cells.append({'center':f.tolist(),'exterior_gap_meV':g,'anchor_smin':d['smin'],
                          'exterior_lower_meV':lower,'projector_displacement_bound':displacement,
                          'chart_smin_squared_lower':s2,'pass':bool(ok)})
    return {'bounds':bounds.tolist(),'n':n,'halfcell_H_variation_meV':delta,'coordinate_norms_meV':norms,'cells':cells,
            'minimum_exterior_lower_meV':min(x['exterior_lower_meV'] for x in cells),
            'minimum_chart_smin_lower':float(np.sqrt(max(0,min(x['chart_smin_squared_lower'] for x in cells)))),
            'pass':all(x['pass'] for x in cells)}

def edge(chart,a,b,cfg,initial=1):
    a,b=np.array(a),np.array(b);norm=chart.norm(a,b);cache={};leaves=[]
    def get(t):
        if t not in cache:cache[t]=chart.data(a if t==0 else b if t==1 else a+t*(b-a))
        return cache[t]
    def visit(l,r,depth):
        L,R=get(l),get(r);delta=norm*(r-l)
        lower=float(min(*L['gaps'],*R['gaps'])-delta-T['floating_allowance_meV'])
        diagonal=np.diag(L['Q'].T@R['Q'])
        step=L['Q'].T@(R['Q']*np.where(diagonal>=0,1.,-1.))
        proper=np.linalg.det(step)>0
        angle=float(Rotation.from_matrix(step).magnitude()) if proper else float(np.pi)
        ok=(lower>T['gap_margin_meV'] and delta/lower<=cfg['variation_over_lower_max'] and
            min(L['smin'],R['smin'])>=T['chart_smin'] and proper and angle<=cfg['maximum_frame_step_radians'])
        terminal=(min(*L['gaps'],*R['gaps'])<=T['gap_margin_meV'] or
                  min(L['smin'],R['smin'])<T['chart_smin'] or depth>=T['max_depth'])
        if ok or terminal:
            leaves.append({'a':l,'b':r,'depth':depth,'variation_meV':delta,'gap_lower_meV':lower,
                           'frame_step_radians':angle,'proper':bool(proper),'pass':bool(ok)})
        else:
            mid=(l+r)/2;visit(l,mid,depth+1);visit(mid,r,depth+1)
    grid=np.linspace(0,1,initial+1)
    for l,r in zip(grid[:-1],grid[1:]):visit(float(l),float(r),0)
    used=sorted({v[k] for v in leaves for k in ['a','b']})
    samples=[get(t) for t in used]
    return {'start':a.tolist(),'end':b.tolist(),'norm_meV':norm,'leaves':leaves,'pass':all(l['pass'] for l in leaves)},samples

def loop(chart,center,radius,cfg):
    n=cfg['polygon_edges'];center=np.array(center)
    ring=[center+radius*np.array([np.cos(t),np.sin(t)]) for t in np.linspace(0,2*np.pi,n+1)]
    ring[-1]=ring[0].copy();vertices=[chart.base,*ring,chart.base]
    edges=[];samples=[]
    for j,(a,b) in enumerate(zip(vertices[:-1],vertices[1:])):
        report,points=edge(chart,a,b,cfg,cfg['stem_subintervals'] if j in [0,len(vertices)-2] else 1)
        edges.append(report);samples.extend(points if not samples else points[1:])
    raw=np.array([x['Q'] for x in samples]);lift_result,path=lift(raw)
    passed=all(e['pass'] for e in edges) and lift_result['valid']
    return {'vertices':np.array(vertices).tolist(),'edges':edges,'sample_points':len(samples),'lift':lift_result,
            'diagnostics_pass':bool(passed),'accepted_label':lift_result['nearest_label'] if passed else None,
            'accepted_class':lift_result['conjugacy_class'] if passed else None,
            'minimum_gap_lower_meV':min(l['gap_lower_meV'] for e in edges for l in e['leaves']),
            'minimum_sample_anchor_smin':min(x['smin'] for x in samples)},samples,path

def words(a,b):
    rawA=np.array([x['Q'] for x in a]);rawB=np.array([x['Q'] for x in b])
    words={'A':rawA,'B':rawB,'AB':np.concatenate([rawA,rawB[1:]]),
           'BA':np.concatenate([rawB,rawA[1:]]),
           'commutator':np.concatenate([rawA,rawB[1:],rawA[-2::-1],rawB[-2::-1]])}
    results={};paths={}
    for name,raw in words.items():results[name],paths[name]=lift(raw)
    qa=np.array(results['A']['quaternion']);qb=np.array(results['B']['quaternion'])
    expected={'AB':multiply(qa,qb),'BA':multiply(qb,qa),'commutator':multiply(multiply(multiply(qa,qb),inverse(qa)),inverse(qb))}
    for name,q in expected.items():
        error=float(np.max(np.abs(np.array(results[name]['quaternion'])-q)))
        results[name]['word_product_error']=error
        results[name]['valid']=bool(results[name]['valid'] and error<T['cross_check_error'])
    return results,paths
