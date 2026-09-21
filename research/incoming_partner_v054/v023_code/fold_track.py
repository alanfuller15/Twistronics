"""Two-seed fold tracker for the preparation-route event candidates (v051). For each event: track both roots of the
pair through the event in bm (lab_nn_full, exact) with tbg_ref root cross-check, record separation and gaps, fit
sep^2 linear on the last open-side points, report the fold estimate and the pair's relative charge on the open side.
Candidates, not accepted events: the team gate (rank-one zero, curvature, transverse slope, open-side minima) is theirs."""
import numpy as np, json, sys, time
from scipy.linalg import eigh
from bm_strain import BM, sz, frac_dist
from knobs import add_harmonic
from gate import real_basis, classify
from final_check import winding, transport2, frame
from tbg_ref import TBG
def bm_model(A,B,T=0.0): 
    m=BM(N=4,eps=0.003,phi_deg=0,A_scalar=A,kinetic='lab_nn_full',geometry='exact')
    if B: add_harmonic(m,B,mat=sz,use_sin=True)
    if T: add_harmonic(m,T,mat=sz,use_sin=True,layer_sign=-1)
    return m
def ref_model(A,B,T=0.0): return TBG(N=4,eps=0.003,phi=0,A=A,B=B,Bt=T,kinetic='lab_nn_full')
def gapfn(m,gi): return lambda f:(lambda w:w[gi+1]-w[gi])(m.bands_near_zero(m.frac_to_k(f),3))   # six bands E-3..E+3; gi: 1 lower|f1 = w2-w1, 2 flat = w3-w2, 3 f2|upper = w4-w3
def charge_pair(m,p,gi):
    U=real_basis(m.nG); lo={1:m.dim//2-2,2:m.dim//2-1,3:m.dim//2}[gi]
    d=((p[1]-p[0])+0.5)%1-0.5; r=min(0.01,0.3*np.linalg.norm(d)); sa=p[0]+np.array([r,0]); sb=p[0]+d+np.array([r,0]); base=frame(m,U,m.frac_to_k(sa),lo)
    w1=winding(m,U,p[0],r,80,base,lo); w2=winding(m,U,p[0]+d,r,80,transport2(m,U,[sa,sb],base,lo,n=250),lo); return w1,w2,classify(w1,w2)
def local_roots(m,fn,c,R=0.06,n=21):
    pts=sorted((fn(np.array([a,b])),a,b) for a in np.linspace(c[0]-R,c[0]+R,n) for b in np.linspace(c[1]-R,c[1]+R,n)); ex=[]
    for v,a,b in pts[:10]:
        f,val=m.refine(np.array([a,b]),fn)
        if val<1e-6 and all(frac_dist(f,g)>1e-3 for g in ex): ex.append(f)
    return ex, pts[0][0]
def track(name,gi,seeds,params,pname,fixed):
    rows=[]; p=[np.array(s) for s in seeds]; label=None
    for v in params:
        kw=dict(fixed); kw[pname]=v; m=bm_model(**kw); fn=gapfn(m,gi)
        rs=[m.refine(s,fn,return_result=True) for s in p]; q=[r[0] for r in rs]; g=[r[1] for r in rs]; ok=[r[2]['success'] for r in rs]
        if frac_dist(q[0],q[1])<1e-3 or max(g)>1e-6:                       # seat/re-seat both roots by local dense search
            ex,bmin=local_roots(m,fn,0.5*(p[0]+p[1]))
            if len(ex)>=2: q=sorted(ex,key=lambda f:frac_dist(f,p[0]))[:2]; g=[fn(x) for x in q]; ok=[True,True]
            else: q=(ex+[ex[0]])[:2] if ex else p; g=[fn(x) for x in q]; ok=[False,False]; print(f"    (local search: {len(ex)} roots, box min {bmin:.2e})")
        sep=frac_dist(q[0],q[1]); rr=ref_model(**kw); fr=rr.gap(gi); qq=[rr.refine(s,fr)[0] for s in p]; gq=[fr(x) for x in qq]
        alive = max(g)<1e-6 and sep>1e-3
        row=dict(**{pname:v},bm_roots=[x.tolist() for x in q],bm_gaps=[float(x) for x in g],refine_ok=ok,sep=float(sep),ref_roots=[x.tolist() for x in qq],ref_gaps=[float(x) for x in gq],ref_root_diff=float(max(np.linalg.norm(a-b) for a,b in zip(q,qq))),alive=bool(alive))
        if alive and label is None: w1,w2,label=charge_pair(m,q,gi); row['charge']=[w1,w2,label]
        rows.append(row); print(f"  {name} {pname}={v:+.4f}: sep {sep:.5f} gaps {g[0]:.0e},{g[1]:.0e} ref-diff {row['ref_root_diff']:.1e} {'' if alive else '<- pair gone / merged'}"); sys.stdout.flush()
        if not alive: break
        p=q
    op=[(r[pname],r['sep']) for r in rows if r['alive']][-3:]
    est=None
    if len(op)>=2:
        x=np.array([a for a,_ in op]); y=np.array([s*s for _,s in op]); k,c=np.polyfit(x,y,1); est=float(-c/k)
    print(f"  => {name}: open-side charge {label}; fold estimate {pname}* ≈ {est}")
    return dict(event=name,gap_index=gi,parameter=pname,fixed=fixed,rows=rows,open_side_label=label,fold_estimate=est)
out=[]
t=time.time()
out.append(track('U_birth',3,[[0.684,0.816],[0.637,0.844]],[0.145,0.142,0.140,0.139,0.138,0.1375,0.137],'A',dict(B=0.0)))
out.append(track('extra_flat_birth',2,[[0.565,0.573],[0.509,0.568]],[0.18,0.175,0.172,0.170,0.169,0.168,0.167,0.166],'A',dict(B=0.0)))
json.dump(out,open('fold_track_prep_A.json','w'),indent=1); print(f"({time.time()-t:.0f}s)")
