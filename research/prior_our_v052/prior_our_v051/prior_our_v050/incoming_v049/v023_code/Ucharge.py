import numpy as np, sys, json, os
from scipy.linalg import eigh
from bm_strain import BM, frac_dist, sz
from knobs import add_harmonic
from final_check import winding, transport2, frame
base=dict(A=0.0,Bsym=-0.40,Btau=-0.80,phi=80.0,eps=0.003,ratio=0.8,theta=1.05); base.update(json.loads(os.environ.get('BASE','{}')))
N=int(os.environ.get('NN','4'))
def mk(p):
    m=BM(N=N,theta_deg=p['theta'],ratio=p['ratio'],eps=p['eps'],phi_deg=p['phi'],A_scalar=p['A']); add_harmonic(m,p['Bsym'],mat=sz,use_sin=True); add_harmonic(m,p['Btau'],mat=sz,use_sin=True,layer_sign=-1); return m
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
key=sys.argv[1]; U1=np.array(json.loads(os.environ['U1'])); U2=np.array(json.loads(os.environ['U2']))
for v in [float(x) for x in sys.argv[2:]]:
    p=dict(base); p[key]=v; m=mk(p); U=np.kron(np.eye(2*m.nG),u2); D=m.dim; lo=D//2
    fu=lambda f:(lambda w:w[3]-w[2])(m.bands_near_zero(m.frac_to_k(f),2)); fn=lambda f:(lambda w:w[5]-w[4])(m.bands_near_zero(m.frac_to_k(f),3))
    a,va=m.refine(U1,fu); b,vb=m.refine(U2,fu); assert max(va,vb)<1e-6,(va,vb)
    U1,U2=a,b
    # up|nx nodes near the segment
    d=((b-a)+0.5)%1-0.5; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L
    fs,vals=m.grid(24,fn); nx=[]
    for vv,x,y in m.local_minima(fs,vals,10):
        f,val=m.refine(np.array([x,y]),fn)
        if val<1e-6 and all(frac_dist(f,g)>0.01 for g in nx): nx.append(f)
    offs=[(round(float((((q-a)+0.5)%1-0.5)@d/L**2),2),round(float((((q-a)+0.5)%1-0.5)@n),3)) for q in nx]
    r=0.012; sa=a+np.array([r,0]); sb=a+d+np.array([r,0]); basef=frame(m,U,m.frac_to_k(sa),lo)
    wa=winding(m,U,a,r,80,basef,lo); wb=winding(m,U,a+d,r,80,transport2(m,U,[sa,sb],basef,lo),lo)
    print(f"{key}={v:.3f} N={N}: U1 {tuple(np.round(a,3))} w={wa:+.2f}  U2 {tuple(np.round(b,3))} w={wb:+.2f}  -> {'SAME' if wa*wb>0 else 'OPPOSITE'} | up|nx (t,off): {offs}")
    sys.stdout.flush()
