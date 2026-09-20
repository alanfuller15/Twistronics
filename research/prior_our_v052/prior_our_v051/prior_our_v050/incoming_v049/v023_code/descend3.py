import numpy as np, json, os, sys
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS, SCALE
STATE='descend3_state.json'; W=4.0; MARGIN=0.04
def gapfun(m,idx): return lambda f: (lambda w: w[idx[1]]-w[idx[0]])(m.bands_near_zero(m.frac_to_k(f),2))
def evaluate(x,P):
    m=make(**dict(zip(KEYS,x))); out={}
    for name,idx in [('F1',(1,2)),('F3',(1,2)),('U1',(2,3)),('L1',(0,1))]:
        f,v=m.refine(np.array(P[name]),gapfun(m,idx)); out[name]=(f,v)
    from bm_strain import segment_geometry
    F1,F3=out['F1'][0],out['F3'][0]
    offs={}
    for name in ('U1','L1'):
        t,o,L=segment_geometry(F1,F3,out[name][0]); offs[name]=(t,o)
    sep=frac_dist(F1,F3); pen=sum(max(0.0,MARGIN-o) for t,o in offs.values() if 0<t<1)
    return sep+W*pen, sep, offs, out
if __name__=='__main__':
    if os.path.exists(STATE): st=json.load(open(STATE))
    else: st=dict(x=[0.20,-0.30,0.0,0.0,0.0,0.0,0.003],P=dict(F1=[0.738,0.611],F3=[0.518,0.827],U1=[0.61,0.70],L1=[0.66,0.72]),step=1.0)
    x=np.array(st['x']); P=st['P']; step=st['step']
    J0,sep,offs,out=evaluate(x,P)
    print("start:",{k:(tuple(np.round(v[0],3)),f"{v[1]:.0e}") for k,v in out.items()},"offs",{k:tuple(np.round(v,3)) for k,v in offs.items()})
    P={k:v[0].tolist() for k,v in out.items()}
    for it in range(int(sys.argv[1]) if len(sys.argv)>1 else 5):
        J0,s0,offs0,out0=evaluate(x,P)
        if max(out0['F1'][1],out0['F3'][1])>1e-6: print(f"GAP OPENED at x={np.round(x,4).tolist()} F1/F3 gaps {out0['F1'][1]:.1e},{out0['F3'][1]:.1e} dist {s0:.4f}"); break
        g=np.zeros(len(KEYS))
        for i in range(len(KEYS)):
            xp=x.copy(); xp[i]+=SCALE[i]; Jp,_,_,o=evaluate(xp,P); g[i]=Jp-J0 if max(o['F1'][1],o['F3'][1])<1e-6 else 0.0
        d=-g/(np.linalg.norm(g)+1e-12); xn=x+step*d*SCALE; Jn,sn,offn,outn=evaluate(xn,P)
        if max(outn['F1'][1],outn['F3'][1])>1e-6:
            print(f"GAP OPENED after step: x={np.round(xn,4).tolist()} F1/F3 gaps {outn['F1'][1]:.1e},{outn['F3'][1]:.1e} refined-pts dist {sn:.4f}"); x=xn; P={k:v[0].tolist() for k,v in outn.items()}; break
        ok=Jn<J0
        print(f"J {J0:.4f}->{Jn:.4f} sep {s0:.4f}->{sn:.4f} U1(t,off)={tuple(np.round(offn['U1'],3))} L1={tuple(np.round(offn['L1'],3))} step={step:.2f} {'ACCEPT' if ok else 'REJECT'} x={np.round(xn,4).tolist()}"); sys.stdout.flush()
        if ok: x=xn; P={k:v[0].tolist() for k,v in outn.items()}; step=min(step*1.3,3.0)
        else: step*=0.5
    st.update(x=x.tolist(),P=P,step=step); (lambda: (json.dump(dict(st,env=__import__('platform').python_version()+' numpy '+np.__version__),open(STATE+'.tmp','w')), os.replace(STATE+'.tmp',STATE)))()
