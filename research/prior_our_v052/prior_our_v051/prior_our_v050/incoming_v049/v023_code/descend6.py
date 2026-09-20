import numpy as np, json, os, sys
from bm_strain import BM, frac_dist, sz, s0, sx
from knobs import add_harmonic
KEYS=['A','Bsym','Btz','Bx','Bt','phi','eps']; SC=np.array([0.01,0.02,0.02,0.02,0.02,1.5,0.0002])
STATE='descend6_state.json'
def make(A,Bsym,Btz,Bx,Bt,phi,eps):
    m=BM(N=4,eps=eps,phi_deg=phi,A_scalar=A)
    add_harmonic(m,Bsym,mat=sz,use_sin=True); add_harmonic(m,Btz,mat=sz,use_sin=True,layer_sign=-1)
    if Bx: add_harmonic(m,Bx,mat=sx)
    if Bt: add_harmonic(m,Bt,mat=s0,layer_sign=-1)
    return m
def gf(m,idx): return lambda f:(lambda w:w[idx[1]]-w[idx[0]])(m.bands_near_zero(m.frac_to_k(f),2))
def lower_min(m):
    fn=gf(m,(0,1)); fs,vals=m.grid(12,fn); return min(m.refine(np.array(c[1:]),fn)[1] for c in m.local_minima(fs,vals,3))
def softplus(z,k=200.0): return np.log1p(np.exp(k*z))/k
def evaluate(x,P):
    m=make(**dict(zip(KEYS,x)))
    F1,v1=m.refine(np.array(P['F1']),gf(m,(1,2))); F3,v3=m.refine(np.array(P['F3']),gf(m,(1,2))); U1,vu=m.refine(np.array(P['U1']),gf(m,(2,3)))
    d=F3-F1; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L; rel=((U1-F1)+0.5)%1-0.5; t=float((rel@d)/L**2); off=float(rel@n)
    sep=frac_dist(F1,F3); lm=lower_min(m); J=sep+6.0*softplus(0.03-off)+0.5*np.log1p(np.exp(5*(1.5-lm)))/5
    return J,sep,(t,off,lm),dict(F1=(F1,v1),F3=(F3,v3),U1=(U1,vu)),m
if __name__=='__main__':
    if os.path.exists(STATE): st=json.load(open(STATE))
    else: st=dict(x=[0.20,-0.40,-0.40,0.0,0.0,0.0,0.003],P=dict(F1=[0.7686,0.6476],F3=[0.5277,0.9319],U1=[0.651,0.755]),step=1.0)
    x=np.array(st['x']); P=st['P']; step=st['step']
    for it in range(int(sys.argv[1]) if len(sys.argv)>1 else 5):
        J0,s0_,uo0,out0,_=evaluate(x,P); g=np.zeros(len(KEYS))
        for i in range(len(KEYS)):
            xp=x.copy(); xp[i]+=SC[i]; Jp,sp,_,o,_=evaluate(xp,P)
            g[i]=Jp-J0 if (max(o['F1'][1],o['F3'][1],o['U1'][1])<1e-6 and sp>0.003) else 0.0
        dd=-g/(np.linalg.norm(g)+1e-12); xn=x+step*dd*SC; Jn,sn,uon,outn,mn=evaluate(xn,P)
        gaps=(outn['F1'][1],outn['F3'][1],outn['U1'][1])
        if max(gaps[:2])>1e-6:
            print(f"GAP OPENED after step: x={np.round(xn,4).tolist()} F gaps {gaps[0]:.2e},{gaps[1]:.2e} pts {tuple(np.round(outn['F1'][0],4))} {tuple(np.round(outn['F3'][0],4))}"); st['event']=dict(x_before=x.tolist(),x_after=xn.tolist(),P=P); x=xn; break
        lm=uon[2]
        ok = Jn<J0 and sn>0.003 and lm>0.3 and gaps[2]<1e-6
        print(f"J {J0:.4f}->{Jn:.4f} sep {s0_:.4f}->{sn:.4f} U1(t,off)=({uon[0]:.2f},{uon[1]:+.3f}) lower-min={lm:.2f} step={step:.2f} {'ACCEPT' if ok else 'REJECT'} x={np.round(xn,4).tolist()}"); sys.stdout.flush()
        if ok: x=xn; P={k:v[0].tolist() for k,v in outn.items()}; step=min(step*1.3,3.0)
        else: step*=0.5
    st.update(x=x.tolist(),P=P,step=step); (lambda: (json.dump(dict(st,env=__import__('platform').python_version()+' numpy '+np.__version__),open(STATE+'.tmp','w')), os.replace(STATE+'.tmp',STATE)))()
