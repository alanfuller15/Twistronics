import numpy as np, json, os, sys
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS, SCALE
import os as _o
STATE='descend4_state.json'; W=float(_o.environ.get('W','4')); MARGIN=float(_o.environ.get('MARGIN','0.03')); SC=SCALE*0.5
def gapfun(m,idx): return lambda f: (lambda w: w[idx[1]]-w[idx[0]])(m.bands_near_zero(m.frac_to_k(f),2))
def evaluate(x,P):
    m=make(**dict(zip(KEYS,x))); out={}
    for name,pos in P.items():
        idx=(1,2) if name.startswith('F') else ((2,3) if name.startswith('U') else (0,1))
        f,v=m.refine(np.array(pos),gapfun(m,idx)); out[name]=(f,v)
    F1,F3=out['F1'][0],out['F3'][0]; d=F3-F1; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L
    offs={}
    for name in P:
        if name.startswith('F'): continue
        rel=((out[name][0]-F1)+0.5)%1-0.5; offs[name]=(float((rel@d)/L**2),float(rel@n))
    sep=frac_dist(F1,F3); pen=sum(max(0.0,MARGIN-abs(o)) for t,o in offs.values() if -0.2<t<1.2)
    return sep+W*pen, sep, offs, out
if __name__=='__main__':
    if os.path.exists(STATE): st=json.load(open(STATE))
    else:
        xa=np.array([-0.0014,-0.3358,-0.0126,-0.3396,0.1222,6.8518,0.0013]); xb=np.array([-0.0104,-0.3294,-0.0197,-0.3786,0.1467,6.9313,0.0009])
        st=dict(x=(xa+1.2*(xb-xa)).tolist(),P=dict(F1=[0.654,0.743],F3=[0.621,0.730],U1=[0.667,0.656],U2=[0.51,0.844],L1=[0.624,0.758],L2=[0.537,0.75]),step=1.0)
    x=np.array(st['x']); P=st['P']; step=st['step']
    for it in range(int(sys.argv[1]) if len(sys.argv)>1 else 5):
        J0,s0,offs0,out0=evaluate(x,P)
        g=np.zeros(len(KEYS))
        for i in range(len(KEYS)):
            xp=x.copy(); xp[i]+=SC[i]; Jp,sp,_,o=evaluate(xp,P)
            valid = max(o['F1'][1],o['F3'][1])<1e-6 and sp>0.003
            g[i]=Jp-J0 if valid else 0.0
        d=-g/(np.linalg.norm(g)+1e-12); xn=x+step*d*SC; Jn,sn,offn,outn=evaluate(xn,P)
        gapped=max(outn['F1'][1],outn['F3'][1])>1e-6
        if gapped:
            print(f"GAP OPENED after step: x={np.round(xn,4).tolist()} gaps {outn['F1'][1]:.2e},{outn['F3'][1]:.2e} refined pts {tuple(np.round(outn['F1'][0],4))} {tuple(np.round(outn['F3'][0],4))}"); 
            st['event']=dict(x_before=x.tolist(),x_after=xn.tolist(),P=P); x=xn; break
        collapsed = sn<0.003
        ok = (Jn<J0) and not collapsed
        print(f"J {J0:.4f}->{Jn:.4f} sep {s0:.4f}->{sn:.4f} offs={ {k:round(v[1],3) for k,v in offn.items() if -0.2<v[0]<1.2} } step={step:.2f} {'ACCEPT' if ok else ('COLLAPSE-REJECT' if collapsed else 'REJECT')}"); sys.stdout.flush()
        if ok: x=xn; P={k:v[0].tolist() for k,v in outn.items()}; step=min(step*1.3,3.0)
        else: step*=0.5
    st.update(x=x.tolist(),P=P,step=step); (lambda: (json.dump(dict(st,env=__import__('platform').python_version()+' numpy '+np.__version__),open(STATE+'.tmp','w')), os.replace(STATE+'.tmp',STATE)))()
    print("x=",np.round(x,4).tolist())
