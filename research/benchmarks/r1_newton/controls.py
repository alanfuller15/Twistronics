"""Acceptance and rejection controls for the new variant; no science labels."""
import json,copy,sys
import numpy as np
from scipy.linalg import eigh
from solver import ROOT,PLAN,DEFAULT,solve,sha
class Toy:
    dim=4
    def __init__(self,condition=1.):
        self.A=[np.diag([0.,1,-1,0]),np.zeros((4,4)),np.zeros((4,4))]
        self.A[1][1,2]=self.A[1][2,1]=condition
        self.h0=np.diag([-10.,0,0,10.])-.4*self.A[0]-.6*self.A[1]
    def H(self,v):return self.h0+v[0]*self.A[0]+v[1]*self.A[1]+(v[2]-38)*self.A[2]
def fresh_gap(m,r):
    if r['f'] is None:return None
    w=eigh(np.real(m.H([*r['f'],38.])),eigvals_only=True,subset_by_index=(1,2));return float(w[1]-w[0])
def main():
    cases=[]
    def add(name,m,r,expected,extra=True):
        g=fresh_gap(m,r) if r['f'] is not None and np.isfinite(m.h0).all() else None
        consistent=g is None or abs(g-r['gap_meV'])<1e-12
        bounds=True if r['box'] is None else all(np.all(np.array(h['f'])>=r['box'][0]) and np.all(np.array(h['f'])<=r['box'][1]) for h in r['history'])
        cases.append({'name':name,'result':r,'fresh_gap_meV':g,'gap_consistent':consistent,'within_box':bool(bounds),'pass':bool(r['accepted']==expected and extra and consistent and bounds)})
    m=Toy();r=solve(m,38,1,[.43,.58]);add('known_node',m,r,True,np.linalg.norm(np.array(r['f'])-[.4,.6])<1e-10)
    for tag,O in [('signs',np.diag([1,-1,1,-1])),('constant_basis',np.linalg.qr(np.random.default_rng(2026).normal(size=(4,4)))[0])]:
        n=Toy();n.h0=O@n.h0@O.T;n.A=[O@a@O.T for a in n.A];r=solve(n,38,1,[.43,.58]);add(tag,n,r,True,np.linalg.norm(np.array(r['f'])-[.4,.6])<1e-10)
    r=solve(m,38,1,[.46,.62],config={'newton_iterations':1},fallback=False);add('exhausted_budget_pair_consistency',m,r,False,r['reason']=='iteration_budget' and np.linalg.norm(np.array(r['f'])-[.46,.62])>0)
    r=solve(m,38,1,[.43,.58],config={'newton_iterations':0});add('forced_fallback_success',m,r,True,r['fallback_attempted'] and r['method']=='bounded_least_squares')
    n=Toy();n.h0[3,3]=0.;r=solve(n,38,1,[.4,.6]);add('nonisolated_initial_rejected',n,r,False,r['reason']=='pair_not_isolated' and not r['fallback_attempted'])
    for small,name in [(0.,'singular_final_root'),(1e-7,'ill_conditioned_final_root')]:
        n=Toy(small);r=solve(n,38,1,[.4,.6]);add(name,n,r,False,r['reason']=='final_jacobian_rejected')
    r=solve(m,38,1,[.55,.6],box=[[.5,.5],[.6,.7]]);add('outside_box_root_rejected',m,r,False)
    r=solve(m,38,1,[np.nan,.6]);add('nonfinite_input_rejected',m,r,False,r['reason']=='nonfinite_or_invalid_input')
    n=Toy();n.h0[0,0]=np.nan;r=solve(n,38,1,[.4,.6]);add('nonfinite_coefficients_rejected',n,r,False,r['reason']=='nonfinite_or_invalid_coefficients')
    n=Toy();n.h0=n.h0.astype(complex);n.h0[1,2]+=1j;n.h0[2,1]-=1j;r=solve(n,38,1,[.4,.6]);add('nonreal_coefficients_rejected',n,r,False,r['reason']=='nonreal_coefficients')
    n=Toy();n.h0[1,2]+=.2;r=solve(n,38,1,[.4,.6]);add('nonsymmetric_coefficients_rejected',n,r,False,r['reason']=='nonsymmetric_coefficients')
    # Reproduce the supplied implementation's stale-gap return without altering it.
    sys.path.insert(0,str(ROOT.parent/'r1_reproduction'));from partner_fast_engine import RealEngine
    class Adapter:
        def HR(self,f):return m.H([*f,38.])
        def dHR_proj(self,F,a):return F.T@m.A[a]@F
    f,g,info=RealEngine.newton_node(Adapter(),[.46,.62],1,maxit=1)
    w=eigh(m.H([*f,38]),eigvals_only=True,subset_by_index=(1,2));actual=float(w[1]-w[0]);mismatch=abs(actual-g)
    cases.append({'name':'original_partner_maxit_bug_reproduced','reported_gap_meV':float(g),'actual_gap_meV':actual,'mismatch_meV':mismatch,'converged':info['converged'],'pass':bool(not info['converged'] and mismatch>.01)})
    result={'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{n:sha(ROOT/n) for n in ['solver.py','controls.py','partner_fast_engine.py']},'controls':cases,'all_controls_pass':all(x['pass'] for x in cases)}
    (ROOT/'CONTROLS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    for x in cases:print(x['name'],x['pass'])
    return 0 if result['all_controls_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
