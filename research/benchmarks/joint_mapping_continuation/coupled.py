"""Uniform ten-variable Schur/segment contraction; floating-point conditional."""
import itertools
import numpy as np
from scipy.linalg import eigh,qr
from deformation import CFG

def components(a):return np.array([np.trace(a)/2,(a[0,0]-a[1,1])/2,a[0,1]])
def opnorm(a):return float(np.linalg.svd(a,compute_uv=False)[0])
def symnorm(a):return float(np.max(abs(eigh(a,eigvals_only=True))))
def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])
def shifts(f):return (-np.floor(np.array([f[1]-f[0],f[2]-f[0]])+.5)).astype(int)

def area_and_gradient(f,lifts):
    e=f[1]-f[0]+lifts[0];w=f[2]-f[0]+lifts[1]
    grad=np.array([[e[1]-w[1],w[0]-e[0]],[w[1],-w[0]],[-e[1],e[0]]])
    return cross(e,w),grad

def center_data(families,s,D,roots,frames=None):
    roots=np.asarray(roots);lifts=shifts(roots);scale=CFG['geometry_residual_scale']
    J=np.zeros((10,10));g0=np.zeros(10);gs=np.zeros(10);y=np.zeros(10);y[-1]=D
    entries=[];saved=[];temporary=[]
    for k,(family,f) in enumerate(zip(families,roots)):
        lo=family.dim//2-1+int(k==2)
        H=family.H([*f,D]);w,V=eigh(H,subset_by_index=(lo-1,lo+2))
        F=qr(V[:,1:3],mode='full')[0][:,:2] if frames is None else np.array(frames[k])
        Q=qr(F,mode='full')[0][:,2:];W=np.column_stack([F,Q])
        orth=float(np.max(abs(W.T@W-np.eye(family.dim))))
        if orth>CFG['orthogonality_tolerance']:raise ValueError('nonorthogonal_frame')
        E=float(np.trace(F.T@H@F)/2);K=Q.T@H@Q-E*np.eye(family.dim-2);kw=eigh(K,eigvals_only=True)
        A=family.A;Hs=family.derivative(f)
        if any(not np.isfinite(a).all() or np.max(abs(a-a.T))>CFG['matrix_tolerance_meV'] for a in [H,Hs,*A]):
            raise ValueError('invalid_matrix')
        local=np.column_stack([components(F.T@a@F) for a in A[:2]]+[components(-np.eye(2))])
        J[3*k:3*k+3,3*k:3*k+3]=local;J[3*k:3*k+3,9]=components(F.T@A[2]@F)
        g0[3*k:3*k+3]=components(F.T@H@F-E*np.eye(2));gs[3*k:3*k+3]=components(F.T@Hs@F)
        y[3*k:3*k+3]=[*f,E]
        p=CFG['norm_allowance']
        entry=dict(lo=lo,dimension=family.dim,w4=w.tolist(),orthogonality_error=orth,
                   complement_spectrum=kw.tolist(),inertia=[int(np.sum(kw<0)),int(np.sum(kw>0))],
                   inertia_correct=bool(np.sum(kw<0)==lo and np.sum(kw>0)==family.dim-lo-2),
                   G0=float(min(abs(kw))-CFG['energy_allowance_meV']),b0=opnorm(Q.T@H@F)+p,
                   a=[symnorm(a)+p for a in A],b=[opnorm(Q.T@a@F)+p for a in A])
        entries.append(entry);saved.append(F);temporary.append((family,Hs,Q,F))
    area,grad=area_and_gradient(roots,lifts);g0[9]=scale*area
    for k in range(3):J[9,3*k:3*k+2]=scale*grad[k]
    sv=np.linalg.svd(J,compute_uv=False)
    if sv[-1]<CFG['inverse_smin_min']:raise ValueError('singular_coupled_map')
    C=np.linalg.inv(J);v=-C@gs
    for k,(family,Hs,Q,F) in enumerate(temporary):
        T=Hs+v[3*k]*family.A[0]+v[3*k+1]*family.A[1]+v[9]*family.A[2]
        entries[k].update(b_velocity=opnorm(Q.T@T@F)+CFG['norm_allowance'],
                          k_velocity=symnorm(T-v[3*k+2]*np.eye(family.dim))+CFG['norm_allowance'])
    return dict(s=float(s),y=y.tolist(),J=J.tolist(),C=C.tolist(),g0=g0.tolist(),gs=gs.tolist(),
                velocity=v.tolist(),J_singular_values=sv.tolist(),lifts=lifts.tolist(),pairs=entries),saved

def product(a,b):return [min(x*y for x in a for y in b),max(x*y for x in a for y in b)]
def square(a):return [0. if a[0]<=0<=a[1] else min(x*x for x in a),max(x*x for x in a)]

def geometry_bounds(raw,h,r):
    y=np.array(raw['y']);v=np.array(raw['velocity']);f=np.array([y[3*k:3*k+2] for k in range(3)])
    vf=np.array([v[3*k:3*k+2] for k in range(3)]);rf=np.array([r[3*k:3*k+2] for k in range(3)])
    lifts=np.array(raw['lifts']);e=f[1]-f[0]+lifts[0];w=f[2]-f[0]+lifts[1]
    re=h*abs(vf[1]-vf[0])+rf[1]+rf[0];rw=h*abs(vf[2]-vf[0])+rf[2]+rf[0]
    ep=np.column_stack([e-re,e+re]);wp=np.column_stack([w-rw,w+rw])
    den=np.sum([square(a) for a in ep],axis=0);num=np.sum([product(a,b) for a,b in zip(ep,wp)],axis=0)
    pad=CFG['geometry_allowance'];den+=np.array([-pad,pad]);num+=np.array([-pad,pad])
    along=None if den[0]<=0 else [min(a/b for a in num for b in den),max(a/b for a in num for b in den)]
    domain_margin=float(min(np.min(f-h*abs(vf)-rf),np.min(1-f-h*abs(vf)-rf)))
    image_margin=float(min(np.min(.5-abs(e)-re),np.min(.5-abs(w)-rw)))
    separation=[]
    for i,j in itertools.combinations(range(3),2):
        margins=[float(np.max(abs(f[j]-f[i]+shift)-h*abs(vf[j]-vf[i])-rf[j]-rf[i]))
                 for shift in map(np.array,itertools.product([-1,0,1],repeat=2))]
        separation.append(min(margins))
    ok=along is not None and along[0]>CFG['segment_margin'] and along[1]<1-CFG['segment_margin']
    ok=bool(ok and domain_margin>pad and image_margin>pad and min(separation)>pad)
    return dict(pass_check=ok,along=along,length_squared=den.tolist(),domain_margin=domain_margin,
                image_margin=image_margin,pair_separation_margins=separation)

def certificate(raw,h,remainders,radius_override=None):
    h=float(h);C=np.array(raw['C']);J=np.array(raw['J']);v=np.array(raw['velocity']);c=np.sum(abs(C),axis=1)
    out=dict(pass_check=False,reason=None,halfwidth=h,remainders=remainders)
    remainder=np.zeros(10);lines=[]
    for k,(p,bound) in enumerate(zip(raw['pairs'],remainders)):
        R=.5*h*h*bound['second_norm'];G=p['G0']-h*p['k_velocity']-R;B=p['b0']+h*p['b_velocity']+R
        if not p['inertia_correct'] or G<=CFG['complement_margin_meV']:
            out['reason']='complement_line_or_inertia';return out
        remainder[3*k:3*k+3]=R+B*B/G+CFG['energy_allowance_meV'];lines.append((G,B))
    vp,vq,vu=[v[3*k:3*k+2] for k in range(3)]
    remainder[9]=CFG['geometry_residual_scale']*(h*h*abs(cross(vq-vp,vu-vp))+CFG['geometry_allowance'])
    Y=abs(C@raw['g0'])+h*abs(C@(np.array(raw['gs'])+J@v))+abs(C)@remainder
    rho=max(CFG['minimum_rho_meV'],CFG['radius_factor']*float(np.max(Y/c)))
    r=rho*c if radius_override is None else np.asarray(radius_override)
    out.update(Y=Y.tolist(),rho=rho,radii=r.tolist())
    if not np.isfinite(r).all() or np.any(r<=0):out['reason']='invalid_radii';return out
    error=np.zeros((10,10));full=[]
    for k,(p,bound,(Gl,Bl)) in enumerate(zip(raw['pairs'],remainders,lines)):
        a=np.array(p['a']);b=np.array(p['b']);da=h*np.array(bound['axis_derivative_norms'])
        a[:2]+=da;b[:2]+=da
        rr=np.r_[r[3*k:3*k+2],r[9]]
        G=Gl-a@rr-r[3*k+2];B=Bl+b@rr
        full.append(dict(Gline=Gl,Bline=Bl,Gfull=G,Bfull=B))
        if G<=CFG['complement_margin_meV']:
            out.update(reason='complement_tube',pairs=full);return out
        nonlinear=2*b*B/G+B*B*a/G**2
        columns=[3*k,3*k+1,9]
        for j,col in enumerate(columns):error[3*k:3*k+3,col]=nonlinear[j]+(da[j] if j<2 else 0.)
        error[3*k:3*k+3,3*k+2]=B*B/G**2
    # Area gradient is affine in the other node coordinates; bound it exactly by radii.
    for k,(a,b) in enumerate([(1,2),(2,0),(1,0)]):
        delta=h*abs(v[3*a:3*a+2]-v[3*b:3*b+2])+r[3*a:3*a+2]+r[3*b:3*b+2]
        error[9,3*k:3*k+2]=CFG['geometry_residual_scale']*delta[::-1]
    inverse_error=abs(np.eye(10)-C@J)+CFG['dimensionless_allowance']
    qrows=((inverse_error+abs(C)@error)@r)/r;q=float(max(qrows));yn=float(max(Y/r))
    beta=yn/(1-q) if q<1 else None
    geom=geometry_bounds(raw,h,r)
    ok=bool(q<=CFG['contraction_max'] and yn+q<=CFG['self_map_max'] and geom['pass_check'])
    out.update(pass_check=ok,reason='accepted' if ok else 'contraction_self_map_or_geometry',pairs=full,
               derivative_error=error.tolist(),q=q,Ynorm=yn,self_map=yn+q,beta=beta,
               contraction_rows=qrows.tolist(),inner_radii=(beta*r).tolist() if beta is not None else None,geometry=geom)
    return out

def enclosure(raw,cert,s,inner=False):
    y=np.array(raw['y'])+(s-raw['s'])*np.array(raw['velocity'])
    r=np.array(cert['inner_radii' if inner else 'radii']);return y-r,y+r

def containment(point,pc,tube,tc,s):
    if not pc['pass_check'] or not tc['pass_check']:return dict(pass_check=False,reason='unaccepted_certificate')
    pl,pu=enclosure(point,pc,s,True);tl,tu=enclosure(tube,tc,s)
    margin=np.minimum(pl-tl,tu-pu)
    return dict(pass_check=bool(min(margin)>0),margins=margin.tolist(),reason='strict_containment' if min(margin)>0 else 'not_contained')
