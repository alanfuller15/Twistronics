import numpy as np, json, os, sys
from bm_strain import BM, frac_dist
from sep import make
KEYS=['A','Bz','Bt','Bx','Bz_single','phi','eps']
SCALE=np.array([0.02,0.02,0.02,0.02,0.02,2.0,0.0002])   # finite-difference step & natural step size per knob
STATE='descend_state.json'
def nodes(x,F1,F3):
    m=make(**dict(zip(KEYS,x))); func=lambda f: m.gaps(m.frac_to_k(f))[0]
    F1n,v1=m.refine(F1,func); F3n,v3=m.refine(F3,func); return F1n,F3n,v1,v3
if __name__=='__main__':
    if os.path.exists(STATE): st=json.load(open(STATE))
    else: st=dict(x=[0.20,-0.30,0.0,0.0,0.0,80.0,0.003],F1=[0.729,0.643],F3=[0.578,0.578],step=1.0,hist=[])
    x=np.array(st['x']); F1=np.array(st['F1']); F3=np.array(st['F3']); step=st['step']
    nsteps=int(sys.argv[1]) if len(sys.argv)>1 else 6
    for it in range(nsteps):
        F1,F3,v1,v3=nodes(x,F1,F3)
        if max(v1,v3)>1e-6:
            print(f"GAP OPENED at x={np.round(x,4).tolist()}: v1={v1:.2e} v3={v3:.2e}, refined pts dist={frac_dist(F1,F3):.4f}"); st['hist'].append('gap opened'); break
        s0=frac_dist(F1,F3); g=np.zeros(len(KEYS))
        for i in range(len(KEYS)):
            xp=x.copy(); xp[i]+=SCALE[i]; a,b,va,vb=nodes(xp,F1,F3)
            g[i]=(frac_dist(a,b)-s0)/1.0 if max(va,vb)<1e-6 else 0.0   # per natural step
        d=-g/ (np.linalg.norm(g)+1e-12)
        xn=x+step*d*SCALE; a,b,va,vb=nodes(xn,F1,F3); sn=frac_dist(a,b)
        print(f"it{it}: sep={s0:.4f} grad={np.round(g,3).tolist()} -> new sep={sn:.4f}  gaps=({va:.0e},{vb:.0e})  x={np.round(xn,4).tolist()}"); sys.stdout.flush()
        if max(va,vb)>1e-6:
            print(f"  GAP OPENED after step: refined pts dist={frac_dist(a,b):.4f}"); x=xn; F1,F3=a,b; st['hist'].append('gap opened'); break
        if sn<s0: x=xn; F1,F3=a,b; step=min(step*1.3,3.0)
        else: step*=0.5; print("  no improvement, halving step")
    st.update(x=x.tolist(),F1=F1.tolist(),F3=F3.tolist(),step=step); (lambda: (json.dump(dict(st,env=__import__('platform').python_version()+' numpy '+np.__version__),open(STATE+'.tmp','w')), os.replace(STATE+'.tmp',STATE)))()
