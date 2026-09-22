"""Frozen endpoint sensitivity and numerical isolation followup.
Sources in sibling r1_reproduction are unchanged. Only frame lookup is instrumented.
Affine real Hamiltonians accelerate frame evaluation after direct checks.
"""
from pathlib import Path
import sys,json,hashlib,time,traceback,argparse,platform
import numpy as np
import scipy
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'r1_reproduction'
sys.path.insert(0,str(SOURCE))
from run import model
from gate import real_basis,classify
from bm_strain import frac_dist
import braid
P=json.loads((ROOT/'PLAN.json').read_text());T=P['thresholds']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def lower_estimate(g0,g1,L,h):return min(g0,g1)-L*h/2-T['floating_allowance_meV']
def bound_intervals(sample,L,initial=16,maxdepth=None):
    """sample(t) is exterior min gap on t in [0,1]; retain every leaf and probe."""
    maxdepth=T['max_isolation_depth'] if maxdepth is None else maxdepth
    samples={};leaves=[]
    def get(t):
        if t not in samples:samples[t]=float(sample(t))
        return samples[t]
    def visit(a,b,depth):
        ga,gb=get(a),get(b);lb=lower_estimate(ga,gb,L,b-a)
        if lb>T['isolation_margin_meV']:
            leaves.append({'a':a,'b':b,'lower_estimate_meV':lb,'depth':depth,'resolved':True});return
        if min(ga,gb)<=T['isolation_margin_meV'] or depth>=maxdepth:
            leaves.append({'a':a,'b':b,'lower_estimate_meV':lb,'depth':depth,'resolved':False});return
        c=(a+b)/2;visit(a,c,depth+1);visit(c,b,depth+1)
    for a,b in zip(np.linspace(0,1,initial+1)[:-1],np.linspace(0,1,initial+1)[1:]):visit(float(a),float(b),0)
    return {'pass':all(x['resolved'] for x in leaves),'L_meV':L,'min_lower_estimate_meV':min(x['lower_estimate_meV'] for x in leaves),'samples':[{'t':k,'gap_meV':v} for k,v in sorted(samples.items())],'leaves':leaves}

class Monitor:
 def __init__(self,m,engine):
    self.m=m;self.engine=engine;self.U=real_basis(m.nG) if engine=='bm' else m.real_basis();self.k=m.frac_to_k if engine=='bm' else m.k;self.lo=m.dim//2-1
    self.cache={};self.phase=[];self.prev=None;self.overlaps=[]
    h0=m.H(np.zeros(2));hx=m.H(np.array([1.,0]))-h0;hy=m.H(np.array([0.,1]))-h0
    converted=[self.U.conj().T@h@self.U for h in (h0,hx,hy)]
    if max(float(np.abs(h.imag).max()) for h in converted)>1e-9:raise RuntimeError('nonreal affine Hamiltonian')
    self.h0,self.hx,self.hy=[h.real for h in converted]
    self.affine_checks=[]
    for f in [[.2,.3],[.7,.6],[.47,.74]]:
        k=self.k(np.array(f));direct=self.U.conj().T@m.H(k)@self.U
        residual=float(np.abs(direct-self.hr(k)).max());self.affine_checks.append({'f':f,'max_residual_meV':residual})
        if residual>T['affine_residual_meV']:raise RuntimeError('affine fidelity check failed')
    self.spectral_checks=[]
    k=self.k(np.array([.71,.62]));direct=eigh(m.H(k),eigvals_only=True,subset_by_index=(self.lo-1,self.lo+2));fast=eigh(self.hr(k),eigvals_only=True,subset_by_index=(self.lo-1,self.lo+2))
    self.spectral_checks.append(float(np.abs(direct-fast).max()))
    if max(self.spectral_checks)>1e-8:raise RuntimeError('affine spectrum differs')
 def hr(self,k):return self.h0+k[0]*self.hx+k[1]*self.hy
 def data(self,k):
    key=tuple(map(float,k))
    if key not in self.cache:
        w,v=eigh(self.hr(k),subset_by_index=(self.lo-1,self.lo+2));self.cache[key]=(v[:,1:3],float(min(w[1]-w[0],w[3]-w[2])))
    return self.cache[key]
 def begin(self,base=None):self.phase=[];self.prev=base;self.overlaps=[]
 def frame(self,k):
    F,g=self.data(k);self.phase.append((np.array(k),g))
    if self.prev is not None:self.overlaps.append(float(np.linalg.svd(self.prev.T@F,compute_uv=False).min()))
    self.prev=F
    return F.copy()
 def norm(self,h):return float(np.max(np.abs(eigh(h,eigvals_only=True))))
 def segment_bound(self,a,b):
    ka,kb=self.k(a),self.k(b);dk=kb-ka;L=2*self.norm(dk[0]*self.hx+dk[1]*self.hy)
    return bound_intervals(lambda t:self.data(self.k(a+t*(b-a)))[1],L)
 def circle_bound(self,c,r):
    # Triangle inequality bounds ||dH/dt|| using both fractional-coordinate axes.
    h1=self.m.G1[0]*self.hx+self.m.G1[1]*self.hy;h2=self.m.G2[0]*self.hx+self.m.G2[1]*self.hy
    L=4*np.pi*r*(self.norm(h1)+self.norm(h2))
    return bound_intervals(lambda t:self.data(self.k(c+r*np.array([np.cos(2*np.pi*t),np.sin(2*np.pi*t)])))[1],L)

def trial(mon,points,cfg):
 m,U,k,lo=mon.m,mon.U,mon.k,mon.lo;p,q=points;d=(q-p+.5)%1-.5;q=p+d;engine=mon.engine
 r=cfg[engine+'_radius'];n=cfg[engine+'_loop_points'];nt=cfg['transport_points'];diags={}
 if engine=='bm':a=p+np.array([r,0]);b=q+np.array([r,0])
 else:off=-1.5*r*d/np.linalg.norm(d);a=p+off;b=q-off
 base=mon.data(k(a))[0].copy()
 braid.real_frame=lambda m,u,k:mon.frame(k)
 m.real_frame=lambda u,k,band,nb=2:mon.frame(k)
 mon.begin(base)
 if engine=='bm':w1=braid.node_winding(m,U,p,r,n,base,exploratory=True)
 else:w1=m.node_charge(U,p,lo,base,r=r,npts=n)
 diags['loop1_step_smin']=min(mon.overlaps);diags['loop1_fixed_frame_smin']=None if engine=='bm' else m.last_smin
 mon.begin(base)
 if engine=='bm':end=braid.transport(m,U,[a,b],base,nstep=nt,exploratory=True)
 else:end=m.transport(U,lo,a,b,base,n=nt)
 diags['transport_step_smin']=min(mon.overlaps)
 mon.begin(end)
 if engine=='bm':w2=braid.node_winding(m,U,q,r,n,end,exploratory=True)
 else:w2=m.node_charge(U,q,lo,end,r=r,npts=n)
 diags['loop2_step_smin']=min(mon.overlaps);diags['loop2_fixed_frame_smin']=None if engine=='bm' else m.last_smin
 # Reference loops omit their repeated endpoint: explicitly monitor the closing overlap.
 for name,c in [('loop1',p),('loop2',q)]:
    F0=mon.data(k(c+r*np.array([1.,0])))[0];Fend=mon.data(k(c+r*np.array([np.cos(2*np.pi*(n-1)/n),np.sin(2*np.pi*(n-1)/n)])))[0]
    diags[name+'_closure_smin']=float(np.linalg.svd(F0.T@Fend,compute_uv=False).min())
 isolation={'transport':mon.segment_bound(a,b),'loop1':mon.circle_bound(p,r),'loop2':mon.circle_bound(q,r)}
 lab=classify(w1,w2) if w1 is not None and w2 is not None else 'INDETERMINATE'
 passed=all(v>=T['step_overlap_smin'] for v in diags.values() if v is not None) and all(x['pass'] for x in isolation.values())
 return {'configuration':cfg,'windings':[w1,w2],'label':lab,'conditioning':diags,'isolation':isolation,'diagnostics_pass':bool(passed)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--N',type=int,choices=P['N_values'],required=True);ap.add_argument('--output',required=True);args=ap.parse_args();dest=ROOT/args.output
 if dest.exists():raise SystemExit('Refusing overwrite')
 result={'status':'RUNNING','N':args.N,'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{str(f.relative_to(ROOT.parent)):sha(f) for f in [ROOT/'validate.py',*SOURCE.glob('*.py'),SOURCE/'PLAN.json']},'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'stations':[]}
 def save():dest.write_text(json.dumps(result,indent=2)+'\n')
 save()
 try:
  for D in P['D_stations_meV']:
   for engine in P['engines']:
    print('START',args.N,D,engine,flush=True);m=model(engine,args.N,D);k=m.frac_to_k if engine=='bm' else m.k
    fn=(lambda f:m.gaps(k(f))[0]) if engine=='bm' else m.flat_gap
    root=[]
    for s in [[.4779,.7396],[.8769,.589]]:
        if engine=='bm':
            f,g,meta=m.refine(np.array(s),fn,return_result=True)
            if not meta['success']:raise RuntimeError('root optimizer rejected')
        else:f,g=m.refine(np.array(s),fn);meta={'success':True,'native_refine_raises_on_failure':True}
        root.append({'f':f.tolist(),'gap_meV':float(g),'optimizer':meta})
    if max(x['gap_meV'] for x in root)>T['root_gap_meV'] or frac_dist(*[np.array(x['f']) for x in root])<T['root_separation']:raise RuntimeError('root gate failed')
    mon=Monitor(m,engine);station={'D_meV':D,'engine':engine,'dimension':m.dim,'roots':root,'affine_checks':mon.affine_checks,'affine_spectrum_errors':mon.spectral_checks,'trials':[]};result['stations'].append(station);save()
    for cfg in P['trials']:
        begin=time.time();row=trial(mon,[np.array(x['f']) for x in root],cfg);row['seconds']=time.time()-begin
        row['diagnostics_pass']=row['diagnostics_pass'] and row['label']==P['expected_labels'][str(D)]
        station['trials'].append(row);save()
        print('RESULT',args.N,D,engine,cfg['name'],row['label'],'pass',row['diagnostics_pass'],'transport_smin',row['conditioning']['transport_step_smin'],'lower',min(x['min_lower_estimate_meV'] for x in row['isolation'].values()),'seconds',round(row['seconds'],1),flush=True)
        if not row['diagnostics_pass']:raise RuntimeError('frozen diagnostic criterion failed')
  result['status']='FOLLOWUP_DIAGNOSTICS_PASS_NOT_FULL_BRAID_ACCEPTANCE'
 except Exception:result['status']='UNRESOLVED';result['error']=traceback.format_exc();print(result['error'],flush=True)
 finally:save()
 return 0 if result['status'].startswith('FOLLOWUP') else 1
if __name__=='__main__':raise SystemExit(main())
