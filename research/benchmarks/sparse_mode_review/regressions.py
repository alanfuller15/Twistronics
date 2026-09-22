"""Bounded review of unchanged v071p; mocked cases are labeled explicitly."""
import json,platform,time
from unittest.mock import patch
import numpy as np
import scipy
from scipy.linalg import eigh
from sparse_inputs import ROOT,PLAN,originals,binding
O=originals()
from bm_strain import BM
from tbg_ref import TBG
from sparse_engine import SparseEngine,WindowError
import atlas,locate_event as le

def main():
 out={'scope':'Review of unchanged partner code; defect reproductions are not fixes.','source_hashes':binding(['regressions.py']),
      'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'cases':{},'windows':[]}
 c=out['cases'];m=BM(N=6,eps=.007,phi_deg=15,theta_deg=1.,kinetic='lab_nn_full',geometry='exact',Dfield=38.)
 E=SparseEngine(m);probe=np.array([.31,.27]);wd=E.bands(probe)
 def window_check(f,sigma):
  dense=eigh(E.HR(f),eigvals_only=True)
  r={'f':list(map(float,f)),'sigma':sigma,'target_indices':list(range(E.D//2-3,E.D//2+3)),'target':dense[E.D//2-3:E.D//2+3].tolist()}
  try:
   ws,V=E.window(f,sigma);r.update(accepted=True,returned=ws.tolist(),matched_indices=[int(np.argmin(abs(dense-w))) for w in ws],error_meV=float(max(abs(ws-dense[E.D//2-3:E.D//2+3]))),residual_norm=float(np.linalg.norm(E.HR(f)@V-V*ws,ord=np.inf)))
  except Exception as e:r.update(accepted=False,error=repr(e))
  return r
 for a in PLAN['controls']['grid_f']:
  for b in PLAN['controls']['grid_f']:out['windows'].append(window_check(np.array([a,b]),0.))
 shifted=window_check(probe,PLAN['controls']['shift_counterexample_meV']);out['windows'].append(shifted)
 c['shifted_window_mislabels_absolute_bands']={'reproduced':bool(shifted['accepted'] and shifted['error_meV']>1.),'evidence':shifted}
 wrong=[r for r in out['windows'][:-1] if r['accepted'] and r['error_meV']>1e-8]
 c['zero_shift_grid_mislabels_absolute_bands']={'reproduced':bool(wrong),'count':len(wrong),'tested':25,'note':'Negative result means this finite grid did not reproduce the defect at zero shift, not a global guarantee.'}
 v=E.certify(probe,sigma=100.)
 c['certify_returns_disagreement_without_refusal']={'reproduced':bool(v>E.cert_tol),'returned_error_meV':v,'threshold':E.cert_tol,'note':'Callers must compare the number themselves; the locator never calls this at its root states.'}
 f,g,info=E.newton_node([.7704,.6288],E.D//2,maxit=1,tol=1e-18)
 w=eigh(E.HR(f),eigvals_only=True,subset_by_index=(E.D//2,E.D//2+1));fresh=float(w[1]-w[0])
 c['exhausted_newton_stale_gap']={'reproduced':bool(not info['converged'] and abs(g-fresh)>1e-7),'f':f.tolist(),'reported_gap':g,'fresh_gap':fresh,'info':info,'note':'Caller rejects converged=False; this is a return-contract defect, not demonstrated accepted false physics.'}
 idx=[(0,0),(1.9,0),(-1.9,0)];a=BM(N=4,index_set=idx);b=TBG(N=4,index_set=idx,kinetic='lab_nn_full')
 c['fractional_indices_silently_truncated']={'reproduced':bool(a.idx==b.mn==[(0,0),(1,0),(-1,0)]),'input':idx,'bm':a.idx,'ref':b.mn}
 seed={'flat':[[.2,.5],[.6,.5]],'node':[.25,.5]}
 class Fake:
  last=None
  def __init__(self,m):self.D=20;self.nS=1;self.certified=0.;self.calls=0;Fake.last=self
  def newton_node(self,f,lo):
   self.calls+=1;self.nS+=2
   return (f+np.array([.2,0]) if self.calls==3 else f),0.,{'converged':True}
 acc={'solves':0,'certs':[]}
 with patch.object(le,'BM',lambda **kw:object()),patch.object(le,'SparseEngine',Fake):
  r=le.measure({'theta':1.,'P':1.,'eps':.0071,'phi':15.,'D':38.},seed,6,[(0,0)],acc)
 c['upper_root_box_omitted']={'reproduced':r is not None,'mock':True,'returned':r,'upper_motion':.2,'box':le.BOX}
 c['cumulative_sparse_solves_overcounted']={'reproduced':acc['solves']!=Fake.last.nS,'mock':True,'reported':acc['solves'],'actual_window_calls':Fake.last.nS,'dense_constructor_calls_omitted':1}
 def measurement(x,seeds,N,index_set,acc):
  d=x['D'];acc['solves']+=1;acc['certs'].append(0.)
  return {'offset':(d-.2)*1e-8,'t':.5,'sep':.4,'flat':[[d,0],[d,.4]],'node':[d,.2],'seeds':seeds}
 def brent_returns_prior_evaluation(fn,a,b,**kw):fn(.2);fn(.21);return .2
 with patch.object(le,'measure',measurement),patch.object(le,'brentq',brent_returns_prior_evaluation):
  r=le.locate({'D':0.},seed,4,[(0,0)],span=1.)
 c['returned_D_not_bound_to_measurement']={'reproduced':bool(r['status']=='ok' and r['flat'][0][0]!=r['D']),'mock':True,'record':r,'note':'Exercises a solver allowed to return an earlier evaluated parameter; not asserted to occur in the supplied production run.'}
 class Tracked(SparseEngine):
  calls=[];instances=[]
  def __init__(self,*a,**kw):super().__init__(*a,**kw);Tracked.instances.append(self)
  def certify(self,f,sigma=0.):Tracked.calls.append(list(map(float,f)));return super().certify(f,sigma)
 supplied=json.loads((O/'locate_event_results.json').read_text())[0]
 seed2={'flat':supplied['flat'],'node':supplied['node']};acc={'solves':0,'certs':[]}
 with patch.object(le,'SparseEngine',Tracked):r=le.measure({'theta':1.,'P':1.,'eps':.0071,'phi':15.,'D':supplied['D']},seed2,6,None,acc)
 c['no_solve_state_recertification']={'reproduced':bool(r is not None and Tracked.calls==[[.31,.27]]),'certify_points':Tracked.calls,'measured_roots':r,'actual_sparse_calls':sum(e.nS for e in Tracked.instances),'reported_sparse_calls':acc['solves']}
 basis={}
 spec=PLAN['candidate_check'];x=dict(spec['state'],D=supplied['D']);region=[dict(x,eps=e) for e in spec['union_strains']]
 for N in spec['N']:
  U=atlas.common_index_set(region,N,'union');basis[str(N)]={'indices':U,'dimension':4*len(U),'basis_vectors':len(U),'sampled_strains':spec['union_strains']}
 (ROOT/'BASIS.json').write_text(json.dumps({'source_hashes':binding(['regressions.py']),'sets':basis},indent=2)+'\n')
 out['supplied_records']={'count':2,'cutoffs':[r['N'] for r in json.loads((O/'locate_event_results.json').read_text())],'missing_seed_path':'/home/claude/joint/seeds_legA.json'}
 (ROOT/'REGRESSIONS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
 for k,v in c.items():print(k,v['reproduced'],flush=True)
 print('basis sizes',{k:v['basis_vectors'] for k,v in basis.items()},flush=True)
if __name__=='__main__':main()
