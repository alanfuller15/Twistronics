import numpy as np, sys, json, os
from bm_strain import BM, frac_dist, sz
from knobs import add_harmonic
base=dict(A=0.0,Bsym=-0.40,Btau=-0.74,phi=65.0,eps=0.003,ratio=0.8,theta=1.05,B2=0.0); base.update(json.loads(os.environ.get('BASE','{}')))
U1=np.array(json.loads(os.environ.get('U1','[0.59,0.691]'))); U2=np.array(json.loads(os.environ.get('U2','[0.519,0.965]')))
key=sys.argv[1]; vals=[float(v) for v in sys.argv[2:]]
def mk(p):
    m=BM(N=4,theta_deg=p['theta'],ratio=p['ratio'],eps=p['eps'],phi_deg=p['phi'],A_scalar=p['A']); add_harmonic(m,p['Bsym'],mat=sz,use_sin=True); add_harmonic(m,p['Btau'],mat=sz,use_sin=True,layer_sign=-1)
    if p['B2']:
        # second-shell scalar harmonic: B2*w1*sum cos(G.r) over G in {(1,1),(-1,2),(-2,1)} and negatives, both layers
        nG=m.nG; V=0.5*p['B2']*m.w1
        for lay in range(2):
            off=2*nG*lay
            for (a,b),i in m.pos.items():
                for dm,dn in [(1,1),(-1,-1),(-1,2),(1,-2),(-2,1),(2,-1)]:
                    t=(a+dm,b+dn)
                    if t in m.pos:
                        i2=m.pos[t]; m.Hstat[off+2*i2:off+2*i2+2,off+2*i:off+2*i+2]+=V*np.eye(2)
    return m
def gapfn(m,i): return lambda f:(lambda w:w[i+2]-w[i+1])(m.bands_near_zero(m.frac_to_k(f),3))
def minimum(m,i,ngrid=15,nkeep=4):
    fn=gapfn(m,i); fs,vals=m.grid(ngrid,fn); return min(m.refine(np.array(c[1:]),fn)[1] for c in m.local_minima(fs,vals,nkeep))
def nodes(m,i,ngrid=24,nkeep=10):
    fn=gapfn(m,i); fs,vals=m.grid(ngrid,fn); ex=[]
    for v,a,b in m.local_minima(fs,vals,nkeep):
        f,vv=m.refine(np.array([a,b]),fn)
        if vv<1e-6 and all(frac_dist(f,g)>0.01 for g in ex): ex.append(f)
    return ex
for v in vals:
    p=dict(base); p[key]=v; m=mk(p); fu=gapfn(m,2)
    a,va=m.refine(U1,fu); b,vb=m.refine(U2,fu)
    if max(va,vb)>1e-6: print(f"{key}={v:+.3f}: U pair lost ({va:.0e},{vb:.0e})"); break
    U1,U2=a,b; d=((b-a)+0.5)%1-0.5; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L
    nx=nodes(m,3); offs=[(round(float((((q-a)+0.5)%1-0.5)@d/L**2),2),round(float((((q-a)+0.5)%1-0.5)@n),3)) for q in nx]
    print(f"{key}={v:+.3f}: flat gap min {minimum(m,1):.2e} | lo|f1 min {minimum(m,0):.1f} | U1 {tuple(np.round(a,3))} U2 {tuple(np.round(b,3))} sep {L:.3f} | up|nx nodes {len(nx)} (t,off): {offs} | bw {m.flat_bandwidth(8):.0f}"); sys.stdout.flush()
