import numpy as np, sys
from bm_strain import BM, frac_dist, s0, sx, sy, sz
from braid import adjacent_nodes
def add_harmonic(m, amp, mat, layer_sign=+1, which=(0,1,2), use_sin=False):
    """add amp*w1*sum_{j in which} cos/sin(G_j.r) * mat (sublattice) with layer sign (+1 symmetric, -1 tau_z)."""
    nG=m.nG; Gs=[(1,0),(0,1),(-1,1)]
    for lay in range(2):
        s=1.0 if lay==0 else layer_sign; off=2*nG*lay
        for j in which:
            dm,dn=Gs[j]
            for sign in (+1,-1):
                coef = 0.5*amp*m.w1*s*( (-1j*sign) if use_sin else 1.0 )
                for (a,b),i in m.pos.items():
                    t=(a+sign*dm,b+sign*dn)
                    if t in m.pos:
                        i2=m.pos[t]; m.Hstat[off+2*i2:off+2*i2+2, off+2*i:off+2*i+2] += coef*mat
    assert np.abs(m.Hstat-m.Hstat.conj().T).max()<1e-12
KNOBS={'tauz':dict(mat=s0,layer_sign=-1),'sx':dict(mat=sx),'sy':dict(mat=sy),'sz_sin':dict(mat=sz,use_sin=True),'single':dict(mat=s0,which=(0,))}
def analyse(m):
    flat=[f for v,f in m.find_nodes(ngrid=36,nkeep=18) if v<1e-6]
    adj=adjacent_nodes(m,ngrid=36); rem=m.min_remote(ngrid=15,nkeep=4)
    # identify F1,F3 as the flat nodes nearest the A=0.2 originals
    F1=min(flat,key=lambda f:frac_dist(f,np.array([0.7695,0.6517]))); F3=min(flat,key=lambda f:frac_dist(f,np.array([0.5915,0.8011])))
    d=F3-F1; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L
    cross=[]
    for _,q in adj['+']+adj['-']:
        rel=((q-F1)+0.5)%1-0.5; t=(rel@d)/L**2; off=rel@n
        cross.append((round(t,2),round(off,3)))
    return flat,adj,rem,F1,F3,cross
if __name__=="__main__":
    name=sys.argv[1]; amps=[float(x) for x in sys.argv[2:]]
    for B in amps:
        m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=0.20); add_harmonic(m,B,**KNOBS[name])
        flat,adj,rem,F1,F3,cross=analyse(m)
        print(f"{name} B={B:+.2f}: flat={len(flat)} adj={len(adj['+'])}+{len(adj['-'])} minrem={rem[0]:.1e} bw={m.flat_bandwidth(10):.0f} | F1 {tuple(np.round(F1,3))} F3 {tuple(np.round(F3,3))} | adj (t,offset) rel. F1->F3: {cross}")
        print("      flat:",[tuple(np.round(f,3)) for f in flat],"adj:",[tuple(np.round(f,3)) for _,f in adj['+']+adj['-']]); sys.stdout.flush()
