"""Guarded projected Newton variant on the existing affine real Hamiltonian.

Inspired by the supplied partner fast_engine.newton_node. The local projected
Jacobian freezes the current pair frame; it is NOT the derivative of the
anchor-aligned residual used by the independent bounded fallback.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parent
PLAN=json.loads((ROOT/'PLAN.json').read_text());DEFAULT=PLAN['solver']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
class GuardFailure(RuntimeError):pass

def coefficient_guard(family,cfg):
    for A in [family.h0,*family.A]:
        if A.shape!=(family.dim,family.dim) or not np.isfinite(A).all():raise GuardFailure('nonfinite_or_invalid_coefficients')
        if np.max(np.abs(np.imag(A)))>cfg['matrix_tolerance_meV']:raise GuardFailure('nonreal_coefficients')
        if np.max(np.abs(A-A.conj().T))>cfg['matrix_tolerance_meV']:raise GuardFailure('nonsymmetric_coefficients')

class Evaluator:
    def __init__(self,family,D,lo,seed,box,cfg):
        self.family,self.D,self.lo,self.cfg=family,float(D),int(lo),cfg
        self.box=np.array(box,float);self.anchor=None;self.history=[];self.calls=0
        coefficient_guard(family,cfg)
        if not np.isfinite(D) or not np.isfinite(seed).all() or np.shape(seed)!=(2,):raise GuardFailure('nonfinite_or_invalid_input')
        if not (1<=lo<=family.dim-3) or lo!=int(lo):raise GuardFailure('invalid_band_index')
        if self.box.shape!=(2,2) or not np.isfinite(self.box).all() or np.any(self.box[0]>=self.box[1]):raise GuardFailure('invalid_box')
        if np.any(seed<self.box[0]) or np.any(seed>self.box[1]):raise GuardFailure('seed_outside_box')
    def evaluate(self,f,phase):
        f=np.asarray(f,float)
        if f.shape!=(2,) or not np.isfinite(f).all():raise GuardFailure('nonfinite_trial')
        if np.any(f<self.box[0]) or np.any(f>self.box[1]):raise GuardFailure('trial_outside_box')
        h=self.family.H([*f,self.D]);self.calls+=1
        w,V=eigh(np.real(h),subset_by_index=(self.lo-1,self.lo+2),check_finite=True)
        F=V[:,1:3]
        if not np.isfinite(w).all() or not np.isfinite(F).all():raise GuardFailure('nonfinite_eigensolution')
        orth=float(np.max(np.abs(F.T@F-np.eye(2))))
        if self.anchor is None:self.anchor=F.copy()
        overlap=float(np.linalg.svd(F.T@self.anchor,compute_uv=False).min())
        projected=[F.T@self.family.A[a].real@F for a in range(2)]
        J=np.array([[(a[0,0]-a[1,1])/2 for a in projected],[a[0,1] for a in projected]])
        sv=np.linalg.svd(J,compute_uv=False);condition=float(sv[0]/sv[1]) if sv[1]>0 else None
        data={'f':f.tolist(),'w':w.tolist(),'gap_meV':float(w[2]-w[1]),'exterior_gap_meV':float(min(w[1]-w[0],w[3]-w[2])),
              'anchor_smin':overlap,'orthogonality_error':orth,'jacobian':J.tolist(),'jacobian_singular_values':sv.tolist(),'jacobian_condition':condition,'phase':phase,'guard_failure':None}
        idx=len(self.history);self.history.append(data)
        reason=('frame_orthogonality' if orth>self.cfg['orthogonality_tolerance'] else 'pair_not_isolated' if data['exterior_gap_meV']<self.cfg['exterior_gap_min_meV'] else 'anchor_overlap' if overlap<self.cfg['anchor_smin_min'] else None)
        if reason:data['guard_failure']=reason;raise GuardFailure(reason)
        return {'record':data,'F':F,'index':idx}

def rank_ok(data,cfg):
    r=data['record'];s=r['jacobian_singular_values'];c=r['jacobian_condition']
    return bool(s[-1]>=cfg['jacobian_smin_min'] and c is not None and c<=cfg['jacobian_condition_max'])
def acceptable(data,cfg):return data['record']['gap_meV']<=cfg['acceptance_gap_meV'] and rank_ok(data,cfg)

def solve(family,D,lo,seed,*,box=None,config=None,fallback=True):
    cfg=dict(DEFAULT,**(config or {}));seed=np.asarray(seed,float)
    if box is None:
        box=np.array([np.maximum(seed-cfg['local_box_radius'],0.),np.minimum(seed+cfg['local_box_radius'],1.)])
    result={'variant':'guarded_projected_newton_v1','D_meV':float(D) if np.isfinite(D) else None,'lo':int(lo),'seed':seed.tolist() if np.isfinite(seed).all() else None,
            'box':np.asarray(box).tolist() if np.isfinite(box).all() else None,'accepted':False,'method':None,'reason':None,'newton_reason':None,'fallback_attempted':False,'fallback_optimizer':None,
            'f':None,'gap_meV':None,'returned_evaluation':None,'eigensolves':0,'history':[],'steps':[],'config':cfg}
    ev=None;current=None
    def finish(reason,method,accepted=False):
        result.update(reason=reason,method=method,accepted=bool(accepted),eigensolves=ev.calls if ev else 0,history=ev.history if ev else [])
        if current is not None:
            result.update(f=current['record']['f'],gap_meV=current['record']['gap_meV'],returned_evaluation=current['index'])
        return result
    try:
        ev=Evaluator(family,D,lo,seed,box,cfg);current=ev.evaluate(seed,'initial')
    except (GuardFailure,ValueError,np.linalg.LinAlgError) as e:return finish(str(e),'rejected_input_or_initial_pair')
    reason='iteration_budget'
    for iteration in range(cfg['newton_iterations']):
        if not rank_ok(current,cfg):reason='ill_conditioned_jacobian';break
        g=current['record']['gap_meV']
        if g<=cfg['newton_stop_gap_meV']:return finish('converged','newton',True)
        J=np.array(current['record']['jacobian'])
        try:step=np.linalg.solve(J,np.array([g/2,0.]))
        except np.linalg.LinAlgError:reason='singular_jacobian';break
        if not np.isfinite(step).all():reason='nonfinite_step';break
        f=np.array(current['record']['f']);length=float(np.linalg.norm(step))
        if length==0:reason='zero_step';break
        scale=min(1.,cfg['trust_radius']/length)
        for a in range(2):
            if step[a]>0:scale=min(scale,(ev.box[1,a]-f[a])/step[a])
            elif step[a]<0:scale=min(scale,(ev.box[0,a]-f[a])/step[a])
        if scale<=0:reason='blocked_at_box';break
        accepted_step=False
        for bt in range(cfg['backtracking_steps']):
            alpha=scale*2.**(-bt);target=np.clip(f+alpha*step,ev.box[0],ev.box[1])
            sr={'iteration':iteration,'from_evaluation':current['index'],'raw_step':step.tolist(),'scale':float(alpha),'target':target.tolist(),'accepted':False,'trial_evaluation':None,'failure':None}
            try:
                trial=ev.evaluate(target,'newton_trial');sr['trial_evaluation']=trial['index']
                ng=trial['record']['gap_meV']
                if ng<=cfg['newton_stop_gap_meV'] or ng<g*(1-cfg['armijo']*alpha):
                    current=trial;accepted_step=True;sr['accepted']=True
            except (GuardFailure,ValueError,np.linalg.LinAlgError) as e:sr['failure']=str(e)
            result['steps'].append(sr)
            if accepted_step:break
        if not accepted_step:reason='line_search_failed';break
    if cfg['newton_iterations']>0 and current['record']['gap_meV']<=cfg['newton_stop_gap_meV'] and rank_ok(current,cfg):
        return finish('converged','newton',True)
    result['newton_reason']=reason
    # The returned position is always current's evaluated position, including
    # exhaustion immediately after an accepted trial. No stale gap is returned.
    if not fallback:return finish(reason,'newton')
    result['fallback_attempted']=True;start=np.array(current['record']['f'])
    def residual(f):
        d=ev.evaluate(f,'fallback');F=d['F'];w=np.array(d['record']['w'])[1:3]
        u,_,vt=np.linalg.svd(F.T@ev.anchor);q=u@vt;h=q.T@np.diag(w-w.mean())@q
        return np.array([h[0,0]-h[1,1],2*h[0,1]])
    try:
        opt=least_squares(residual,start,bounds=(ev.box[0],ev.box[1]),xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=cfg['fallback_max_nfev'])
        result['fallback_optimizer']={'success':bool(opt.success),'status':int(opt.status),'nfev':int(opt.nfev),'message':str(opt.message)}
        current=ev.evaluate(opt.x,'fallback_final');ok=bool(opt.success and acceptable(current,cfg))
        why='converged' if ok else 'final_jacobian_rejected' if not rank_ok(current,cfg) else 'final_gap_or_optimizer_rejected'
        return finish(why,'bounded_least_squares',ok)
    except (GuardFailure,ValueError,np.linalg.LinAlgError) as e:return finish('fallback_guard: '+str(e),'bounded_least_squares')
