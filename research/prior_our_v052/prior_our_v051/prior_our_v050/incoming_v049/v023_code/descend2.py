import numpy as np, json, os, sys
from bm_strain import BM, frac_dist
from sep import make
from descend import KEYS, SCALE, nodes
from braid import adjacent_nodes
STATE='descend2_state.json'
def guard(x,F1,F3):
    m=make(**dict(zip(KEYS,x)))
    fl=[f for v,f in m.find_nodes(ngrid=30,nkeep=16) if v<1e-6]
    adj=adjacent_nodes(m,ngrid=30)
    d=F3-F1; L=np.linalg.norm(d); n=np.array([-d[1],d[0]])/L; offs=[]
    for _,q in adj['+']+adj['-']:
        rel=((q-F1)+0.5)%1-0.5; t=(rel@d)/L**2
        if 0<t<1: offs.append(round(float(rel@n),3))
    return len(fl), sorted(offs), len(adj['+'])+len(adj['-'])
if __name__=='__main__':
    if os.path.exists(STATE): st=json.load(open(STATE))
    else:
        st=dict(x=[0.20,-0.30,0.0,0.0,0.0,0.0,0.003],F1=[0.738,0.611],F3=[0.518,0.827],step=1.0,log=[])
        nf,offs,na=guard(np.array(st['x']),np.array(st['F1']),np.array(st['F3'])); st['nflat']=nf; st['offs']=offs
        print(f"start: flat={nf} adj={na} in-segment offsets={offs}")
    x=np.array(st['x']); F1=np.array(st['F1']); F3=np.array(st['F3']); step=st['step']
    for it in range(int(sys.argv[1]) if len(sys.argv)>1 else 5):
        F1,F3,v1,v3=nodes(x,F1,F3); s0=frac_dist(F1,F3); g=np.zeros(len(KEYS))
        for i in range(len(KEYS)):
            xp=x.copy(); xp[i]+=SCALE[i]; a,b,va,vb=nodes(xp,F1,F3); g[i]=(frac_dist(a,b)-s0) if max(va,vb)<1e-6 else 0.0
        d=-g/(np.linalg.norm(g)+1e-12); xn=x+step*d*SCALE; a,b,va,vb=nodes(xn,F1,F3); sn=frac_dist(a,b)
        if max(va,vb)>1e-6:
            print(f"it: GAP OPENED at x={np.round(xn,4).tolist()}, pts dist {sn:.4f}, gaps {va:.1e},{vb:.1e}"); st['log'].append(['gap',xn.tolist()]); x=xn; F1,F3=a,b; break
        nf,offs,na=guard(xn,a,b)
        ok = sn<s0 and nf==st['nflat'] and all(o*p>0 for o,p in zip(offs,st['offs'])) and len(offs)==len(st['offs'])
        print(f"sep {s0:.4f}->{sn:.4f} flat={nf} adj={na} offs={offs} step={step:.2f} {'ACCEPT' if ok else 'REJECT'} x={np.round(xn,4).tolist()}"); sys.stdout.flush()
        if ok: x=xn; F1,F3=a,b; st['offs']=offs; step=min(step*1.3,3.0)
        else: step*=0.5
    st.update(x=x.tolist(),F1=F1.tolist(),F3=F3.tolist(),step=step); json.dump(st,open(STATE,'w'))
