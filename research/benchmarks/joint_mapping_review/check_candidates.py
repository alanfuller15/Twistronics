"""Sampled, bounded two-engine N4/N6 checks of supplied geometric events."""
import json
import platform
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.linalg import eigh
from scipy.optimize import brentq
from inputs import ROOT, PLAN, sha, originals, binding

ORIGINAL=originals()
from bm_strain import BM, segment_geometry
from tbg_ref import TBG
from fast_engine import RealEngine
sys.path.insert(0,str(ROOT.parent/'r1_newton'))
from solver import solve
T=PLAN['thresholds']

def build(x,N,engine):
    kw=dict(N=N,w1=110*x['P'],eps=x['eps'],Dfield=x['D'],kinetic='lab_nn_full',cutoff_tol=1e-6)
    return BM(theta_deg=x['theta'],phi_deg=x['phi'],ratio=.8,geometry='exact',**kw) if engine=='bm' else TBG(theta=x['theta'],phi=x['phi'],w0=88*x['P'],**kw)

class Family:
    def __init__(self,x,N,engine):
        self.x=dict(x);self.N=N;self.engine=engine;self.m=build(x,N,engine);self.dim=self.m.dim
        self.indices=self.m.idx if engine=='bm' else self.m.mn
        self.real=RealEngine(self.m);self.h0=self.real.HR([0.,0.])
        self.A=[self.real.HR([1.,0.])-self.h0,self.real.HR([0.,1.])-self.h0,np.diag(np.r_[np.ones(self.dim//2),-np.ones(self.dim//2)])]
        u=np.array([[1,1j],[1,-1j]])/np.sqrt(2);self.U=np.kron(np.eye(self.dim//2),u)
        self.native_models={float(x['D']):self.m}
    def H(self,v):return self.h0+v[0]*self.A[0]+v[1]*self.A[1]+(v[2]-self.x['D'])*self.A[2]
    def native(self,D):
        if D not in self.native_models:self.native_models[D]=build(dict(self.x,D=D),self.N,self.engine)
        return self.native_models[D]
    def checks(self,D,f,lo):
        m=self.native(D);k=m.frac_to_k(f) if self.engine=='bm' else m.k(f);H=m.H(k)
        transformed=self.U.conj().T@H@self.U;affine=self.H([*f,D]);w=eigh(H,eigvals_only=True,subset_by_index=(lo-1,lo+2));wr=eigh(affine,eigvals_only=True,subset_by_index=(lo-1,lo+2))
        err=float(np.max(abs(transformed-affine)));se=float(max(abs(w-wr)))
        return {'matrix_error_meV':err,'spectrum_error_meV':se,'w4':w.tolist(),'gap_meV':float(w[2]-w[1]),'pair_exterior_gap_meV':float(min(w[1]-w[0],w[3]-w[2])),
                'numerical_model_check_pass':bool(err<T['native_matrix_tolerance_meV'] and se<T['native_matrix_tolerance_meV'])}

def image_shifts(roots):
    p,q,u=np.array(roots)
    return np.array([-np.floor(q-p+.5),-np.floor(u-p+.5)],int).tolist()

def main():
    dest=ROOT/'CANDIDATES.json'
    if dest.exists():raise SystemExit('Refusing overwrite of retained candidate checks')
    states=[];seen={}
    for filename in ['trace_phi_A.json','trace_eps_A.json']:
        for i,p in enumerate(json.loads((ORIGINAL/filename).read_text())['points']):
            key=json.dumps(p['x'],sort_keys=True)
            if key in seen:states[seen[key]]['input_rows'].append([filename,i])
            else:seen[key]=len(states);states.append({'id':len(states),'x':p['x'],'flat':p['flat'],'node':p['node'],'input_rows':[[filename,i]]})
    assert len(states)==6
    sources=binding(['check_candidates.py']);sources['../r1_newton/solver.py']=sha(ROOT.parent/'r1_newton/solver.py');sources['../r1_newton/PLAN.json']=sha(ROOT.parent/'r1_newton/PLAN.json')
    out={'status':'RUNNING','source_hashes':sources,'states':states,'rows':[],'errors':[],
         'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'blas_threads':1},'scope':PLAN['scope']}
    start=time.perf_counter()
    def save():
        out['elapsed_seconds']=time.perf_counter()-start;dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    save()
    for state in states:
        for N in [4,6]:
            for engine in ['bm','ref']:
                row={'state_id':state['id'],'engine':engine,'N':N,'measurements':[],'scalar_calls':[],'event':None,'pass':False,'errors':[]}
                out['rows'].append(row)
                try:
                    family=Family(state['x'],N,engine);roots=np.array([*state['flat'],state['node']]);shifts=image_shifts(roots)
                    row['dimension']=family.dim;row['basis_indices']=family.indices;row['basis_sha256']=__import__('hashlib').sha256(json.dumps(family.indices).encode()).hexdigest()
                    row['seed_image_shifts']=shifts;row['model']={'kinetic':'lab_nn_full','geometry':'exact','cutoff_tol':1e-6,'w1_meV':110*state['x']['P'],'w0_meV':88*state['x']['P'],'D_convention':'opposite layer potentials +/-D meV'}
                    los=[family.dim//2-1,family.dim//2-1,family.dim//2]
                    row['supplied_coordinate_checks']=[family.checks(state['x']['D'],f,lo) for f,lo in zip(roots,los)]
                    st,so,sl=segment_geometry(*roots);row['supplied_geometry']={'t':st,'offset':so,'separation':float(sl)}
                    cache={}
                    def measure(D):
                        D=float(D)
                        if D in cache:return row['measurements'][cache[D]]
                        m={'D_meV':D,'roots':[],'native':[],'pass':False};cache[D]=len(row['measurements']);row['measurements'].append(m)
                        for seed,lo in zip(roots,los):
                            rr=solve(family,D,lo,seed,box=[np.maximum(seed-T['coordinate_seed_radius'],0),np.minimum(seed+T['coordinate_seed_radius'],1)])
                            m['roots'].append(rr)
                            if not rr['accepted']:m['reason']='guarded_root_rejected';return m
                            native=family.checks(D,np.array(rr['f']),lo);m['native'].append(native)
                            if not native['numerical_model_check_pass'] or native['gap_meV']>T['native_gap_tolerance_meV']:
                                m['reason']='native_check_rejected';return m
                        f=np.array([r['f'] for r in m['roots']]);newshifts=image_shifts(f);t,offset,L=segment_geometry(*f)
                        m.update(t=float(t),offset=float(offset),separation=float(L),image_shifts=newshifts)
                        m['pass']=bool(newshifts==shifts and L>1e-3 and T['segment_interior_margin']<t<1-T['segment_interior_margin'])
                        m['reason']='accepted_sample' if m['pass'] else 'segment_or_image_change'
                        return m
                    center=measure(state['x']['D']);row['supplied_D_refinement_index']=0
                    a=state['x']['D']-T['event_D_halfwidth_meV'];b=state['x']['D']+T['event_D_halfwidth_meV'];left,right=measure(a),measure(b)
                    row['event_bracket_meV']=[a,b]
                    if not (center['pass'] and left['pass'] and right['pass']):row['reason']='initial_or_bracket_sample_rejected'
                    elif left['offset']*right['offset']>=0:row['reason']='no_sign_bracket_within_frozen_range'
                    else:
                        def residual(D):
                            row['scalar_calls'].append(float(D));m=measure(D)
                            if not m['pass']:raise RuntimeError('event evaluation rejected')
                            return m['offset']
                        event=brentq(residual,a,b,xtol=T['event_xtol_meV'],maxiter=T['scalar_max_iterations']);m=measure(event)
                        row['event']={'D_meV':float(event),'measurement_index':cache[float(event)],'offset':m['offset'],'t':m['t'],'flat':[r['f'] for r in m['roots'][:2]],'node':m['roots'][2]['f']}
                        row['pass']=bool(m['pass'] and abs(m['offset'])<=T['event_offset_tolerance'] and a<=event<=b)
                        row['reason']='sampled_event_candidate_pass' if row['pass'] else 'event_residual_or_bracket_rejected'
                except Exception:
                    row['errors'].append(traceback.format_exc());row['reason']='exception_retained'
                row['solver_eigensolves']=sum(r['eigensolves'] for m in row['measurements'] for r in m['roots'])
                row['native_spectrum_evaluations']=len(row.get('supplied_coordinate_checks',[]))+sum(len(m['native']) for m in row['measurements'])
                save();print('STATE',state['id'],engine,N,'dim',row.get('dimension'),'pass',row['pass'],'reason',row['reason'],'event',row['event']['D_meV'] if row['event'] else None,'seconds',round(out['elapsed_seconds'],1),flush=True)
    out['status']='SAMPLED_TWO_ENGINE_N4_N6_CANDIDATES_PASS' if all(r['pass'] for r in out['rows']) else 'PARTIAL_CANDIDATE_RESULTS_RETAINED'
    save();print('STATUS',out['status'],flush=True)

if __name__=='__main__':main()
