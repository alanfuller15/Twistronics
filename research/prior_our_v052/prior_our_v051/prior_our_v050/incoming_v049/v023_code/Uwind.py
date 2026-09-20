import numpy as np, sys, json, os
from bm_strain import BM, frac_dist
from check_iso import mk, base
from final_check import winding, transport2, frame
u2=np.array([[1,1j],[1,-1j]])/np.sqrt(2)
p=dict(base); p.update(json.loads(os.environ.get('P','{}'))); m=mk(p); U=np.kron(np.eye(2*m.nG),u2); D=m.dim; lo=D//2
fu=lambda f:(lambda w:w[3]-w[2])(m.bands_near_zero(m.frac_to_k(f),2))
U1,v1=m.refine(np.array(json.loads(os.environ['U1'])),fu); U2,v2=m.refine(np.array(json.loads(os.environ['U2'])),fu); assert max(v1,v2)<1e-6
d=((U2-U1)+0.5)%1-0.5; U2s=U1+d
r=0.012; sa=U1+np.array([r,0]); basef=frame(m,U,m.frac_to_k(sa),lo); wa=winding(m,U,U1,r,80,basef,lo)
print(f"params {p}\nU1 {tuple(np.round(U1,3))} w={wa:+.2f}; U2 {tuple(np.round(U2s,3))} sep {np.linalg.norm(d):.3f}")
for lab,shift in [('short segment',np.array([0,0])),('winding once along f1',np.array([1,0])),('winding once along f2',np.array([0,1])),('winding along -f1',np.array([-1,0]))]:
    tgt,vt=m.refine(U2s+shift,fu); sb=tgt+np.array([r,0])
    wb=winding(m,U,tgt,r,80,transport2(m,U,[sa,sb],basef,lo,n=400),lo)
    print(f"   path {lab:24s}: node refined to {tuple(np.round(tgt,4))} (gap {vt:.0e}); w(U2)={wb:+.2f} -> {'SAME' if wa*wb>0 else 'OPPOSITE'}"); sys.stdout.flush()
