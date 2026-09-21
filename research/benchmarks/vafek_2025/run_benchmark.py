"""Run finite projected-model checks. No archived project code is imported."""
import hashlib,json,platform,sys,time
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq,least_squares
from scipy.ndimage import minimum_filter
from model import Model,PARAMETERS
ROOT=Path(__file__).resolve().parent

def locate(m,Q,gap,n,extent):
 xs=np.linspace(-extent,extent,n); coords=np.array([[x,y] for x in xs for y in xs]);
 vals=np.array([np.linalg.eigvalsh(m.real(k,Q)) for k in coords]);g=(vals[:,gap+1]-vals[:,gap]).reshape(n,n)
 candidates=np.argwhere(g==minimum_filter(g,size=3,mode='constant',cval=np.inf))
 roots=[];attempts=[]
 for i,j in candidates:
  seed=np.array([xs[i],xs[j]]);_,v=np.linalg.eigh(m.real(seed,Q));anchor=v[:,gap:gap+2]
  def field(k):
   h=m.real(k,Q);_,v=np.linalg.eigh(h);frame=v[:,gap:gap+2]
   u,_,vt=np.linalg.svd(frame.T@anchor);frame=frame@u@vt;a=frame.T@h@frame
   return np.array([(a[0,0]-a[1,1])/2,a[0,1]])
  sol=least_squares(field,seed,bounds=(-extent,extent),xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=120)
  ev=np.linalg.eigvalsh(m.real(sol.x,Q));actual=float(ev[gap+1]-ev[gap]);ok=bool(sol.success and actual<1e-7 and np.max(abs(sol.x))<extent-1e-4)
  attempts.append(dict(seed=seed.tolist(),success=bool(sol.success),status=int(sol.status),nfev=sol.nfev,gap_meV=actual,accepted=ok))
  if ok and all(np.linalg.norm(sol.x-np.array(r['K']))>1e-5 for r in roots):roots.append(dict(K=sol.x.tolist(),gap_meV=actual))
 return sorted(roots,key=lambda r:r['K'][0]),float(g.min()),attempts

def main():
 started=time.time();plan=json.loads((ROOT/'PLAN.json').read_text());m=Model(plan['parameters']);p=m.p
 checks={};qs=np.linspace(*plan['Q_range'],plan['Q_count'])
 checks['gamma_spectrum_max_error_meV']=max(float(np.max(abs(np.linalg.eigvalsh(m.h([0,0],q))-np.sort(m.gamma_branches(q))))) for q in qs)
 checks['unboosted_axis_max_error_meV']=max(float(np.max(abs(np.linalg.eigvalsh(m.h([x,0],0))-m.axis_spectrum(x)))) for x in np.linspace(-1,1,41))
 checks['hermiticity_max_error']=max(float(np.max(abs(m.h([.23,-.17],q)-m.h([.23,-.17],q).conj().T))) for q in qs)
 assert max(checks.values())<1e-10
 def threshold(which,model=m,tol=1e-12):
  def f(Q):
   e=model.gamma_branches(Q);return e[which]-e[2]
  return brentq(f,0,1.5,xtol=tol)
 qn=threshold(1);qg=threshold(0);qn_approx=2*np.sqrt((p['J']-4*p['M'])/p['U1']);qg_approx=(p['J']+p['M'])/np.sqrt(p['J']*p['U1']/2)
 thresholds=dict(Qn=qn,Qg=qg,Qn_eq23=qn_approx,Qg_eq23=qg_approx,eq23_relative_errors=dict(n=abs(qn_approx/qn-1),g=abs(qg_approx/qg-1)),root_tolerance_difference=max(abs(qn-threshold(1,tol=1e-10)),abs(qg-threshold(0,tol=1e-10))),units='Q=v*q/gamma; divide by v/gamma to obtain inverse Angstrom')
 zero=Model(dict(p,strain=0));exact0=np.sqrt(2*p['J']*(p['J']+4*p['M'])/(p['U1']*(p['J']+2*p['M'])))
 thresholds['zero_strain_crossing_check']=dict(numerical=threshold(0,zero),derived_from_eq87=float(exact0),difference=float(abs(threshold(0,zero)-exact0)))
 states=[]
 for iq,Q in enumerate(qs):
  row=dict(Q=float(Q),gamma_branches_meV=m.gamma_branches(Q).tolist(),gaps={})
  for gap in [0,1]:
   roots,g,attempts=locate(m,Q,gap,plan['grid_n'],plan['extent'])
   row['gaps'][str(gap)]=dict(nodes=roots,sampled_min_gap_meV=g,optimizer_attempts=attempts)
  states.append(row)
  if iq%10==0:print('state',iq,'Q',round(Q,3),'node counts',[len(row['gaps'][str(g)]['nodes']) for g in [0,1]],flush=True)
 probes=[]
 for Q in [qn*.8,(qn+qg)/2,qg*1.12]:
  for gap in [0,1]:
   roots,_,_=locate(m,Q,gap,plan['grid_n'],plan['extent']);fine,_,_=locate(m,Q,gap,plan['refine_grid_n'],plan['refine_extent'])
   shift=max((min(np.linalg.norm(np.array(r['K'])-t['K']) for t in fine) for r in roots),default=0.) if fine or not roots else None
   probes.append(dict(Q=float(Q),gap=gap,coarse_count=len(roots),refined_count=len(fine),max_nearest_shift=shift))
   # Retain unresolved searches instead of discarding all measurements on failure.
 # Finite-domain searches must reproduce the expected node-count sequence at separated stations.
 checks['initial_count_hypothesis']={'expected':[2,0,2,2,0,2],'observed':[p['coarse_count'] for p in probes],'holds':[p['coarse_count'] for p in probes]==[2,0,2,2,0,2],'scope':'Our provisional whole-domain hypothesis, not a published global node-count assertion.'}
 checks['root_search_refinement']=probes
 checks['zero_strain_threshold_error']=thresholds['zero_strain_crossing_check']['difference'];assert checks['zero_strain_threshold_error']<1e-10
 checks['off_axis_projection_discrepancy_meV']=float(np.max(abs(m.h([.23,-.17],.5)-m.direct_projection([.23,-.17],.5))))
 out=dict(status='SPECTRAL_CHECKS_PASS_NODE_BENCHMARK_UNRESOLVED',parameters=p,epsilon_minus=m.eps,thresholds=thresholds,checks=checks,states=states,seconds=time.time()-started,runtime=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform()),source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['model.py','run_benchmark.py','PLAN.json']},limits=['No non-Abelian frame-charge transport or Euler-class computation in this benchmark.','No self-consistent Hartree-Fock, global Brillouin-zone gap certificate, or experimental prediction.','Finite searches can miss nodes; counts refer to the specified search domain.','This projected model is not the v067 single-valley continuum model.'])
 (ROOT/'RESULTS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(json.dumps(thresholds,indent=2));print(out['status'])
if __name__=='__main__':main()
