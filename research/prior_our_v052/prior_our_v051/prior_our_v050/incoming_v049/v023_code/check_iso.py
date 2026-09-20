import numpy as np, sys, json, os
from bm_strain import BM, frac_dist, sz
from knobs import add_harmonic
base=dict(A=0.0,Bsym=-0.40,Btau=-0.80,phi=80.0,eps=0.003,ratio=1.0,theta=1.05); base.update(json.loads(os.environ.get('BASE','{}')))
N=int(os.environ.get('NN','4'))
def mk(p):
    m=BM(N=N,theta_deg=p['theta'],ratio=p['ratio'],eps=p['eps'],phi_deg=p['phi'],A_scalar=p['A']); add_harmonic(m,p['Bsym'],mat=sz,use_sin=True); add_harmonic(m,p['Btau'],mat=sz,use_sin=True,layer_sign=-1); return m
def gapfn(m,i): return lambda f:(lambda w:w[i+2]-w[i+1])(m.bands_near_zero(m.frac_to_k(f),3))
def inv(m,i,ngrid=24,nkeep=10):
    fn=gapfn(m,i); fs,vals=m.grid(ngrid,fn); ex=[]; best=np.inf
    for v,a,b in m.local_minima(fs,vals,nkeep):
        f,vv=m.refine(np.array([a,b]),fn); best=min(best,vv)
        if vv<1e-6 and all(frac_dist(f,g)>0.01 for g in ex): ex.append(f)
    return ex,best
if __name__=='__main__':
  key=sys.argv[1]
  for v in [float(x) for x in sys.argv[2:]]:
    p=dict(base); p[key]=v; m=mk(p); out=[]
    for i,lab in enumerate(['lo|f1','f1|f2','f2|up','up|nx']):
      ex,best=inv(m,i); out.append(f"{lab}: {len(ex)} nodes"+(f" {[tuple(np.round(f,3)) for f in ex]}" if 0<len(ex)<=4 else "")+f" (min {best:.2e})")
    print(f"{key}={v:.3f} N={N} | "+" | ".join(out)+f" | bw {m.flat_bandwidth(8):.0f}"); sys.stdout.flush()
