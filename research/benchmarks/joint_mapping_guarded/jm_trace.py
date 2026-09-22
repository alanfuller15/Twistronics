"""Bounded geometric event candidates; sampled tracing, never an identity proof."""
from pathlib import Path
import json
import time
import sys
import numpy as np
import jm_model as model

def resolve_config(seed, supplied=None, allow_basis_reseed=False):
    supplied = dict(supplied or {})
    if 'N' not in seed: raise ValueError('seed cutoff metadata required')
    if 'N' in supplied and supplied['N'] != seed['N']:
        raise ValueError('seed/request cutoff mismatch')
    supplied['N']=seed['N']; c=model.config(supplied)
    x=model.state(seed['x']); tag=seed.get('model',{})
    if seed.get('gap') != seed.get('seeds',{}).get('gap') or seed.get('gap') not in ('upper','lower'):
        raise ValueError('inconsistent seed gap metadata')
    expected=dict(kinetic='lab_nn_full',geometry='exact',cutoff_tol=c['cutoff_tol'],
                  w1_meV=110*x['P'],w0_meV=88*x['P'],D_convention=model.MODEL['D_convention'])
    if tag != expected: raise ValueError('seed model metadata missing or mismatched')
    radial_c=dict(c,indices=None)
    native=model.build(x,radial_c)[0]
    idx=native.idx if c['engine']=='bm' else native.mn
    # The prior review used json.dumps rather than this module's canonical encoding.
    import hashlib
    radial_hash=hashlib.sha256(json.dumps(idx).encode()).hexdigest()
    requested=model.digest(c['indices'] if c['indices'] is not None else [list(p) for p in idx])
    recorded=seed.get('basis_sha256')
    if recorded not in (radial_hash, requested): raise ValueError('unrecognized seed basis')
    same_indices=c['indices'] is None or c['indices']==[list(p) for p in idx]
    if not same_indices and recorded!=requested and not allow_basis_reseed:
        raise ValueError('basis conversion requires explicit reseed declaration')
    return c,dict(source_basis_hash=recorded,target_basis_hash=requested,
                  basis_reseed=bool(not same_indices and recorded!=requested))

def solve_event(x, seeds, cfg, bracket, *, tol=1e-9, xtol=1e-9, maxit=40, measure_fn=None):
    """Safeguarded bisection with full measurements and unchanged acceptance gates.

    No bracket expansion. Seed boxes are frozen throughout each scalar solve.
    The returned cost includes rejected evaluations and endpoint bracketing.
    """
    x=model.state(x); c=model.config(cfg); a,b=map(float,bracket)
    if not np.isfinite([a,b,tol,xtol]).all() or a>=b or tol<=0 or xtol<=0 or maxit<0 or int(maxit)!=maxit:
        raise ValueError('invalid event bounds or budget')
    result=dict(status='failed',reason=None,bracket=[a,b],tolerance=tol,xtol=xtol,
                maxit=maxit,measurements=[],event=None,cost=0,cost_complete=True)
    start=time.perf_counter()
    family=model.Family(x,c) if measure_fn is None else None
    def finish(reason,event=None):
        result.update(status='candidate' if event is not None else 'failed',reason=reason,event=event,
                      seconds=time.perf_counter()-start)
        return result
    def evaluate(D):
        try:
            m=(measure_fn or (lambda xx,ss,cc:model.measure(xx,ss,cc,family)))(dict(x,D=D),seeds,c)
        except Exception as e:
            m=dict(ok=False,reason='measurement_exception',error=repr(e),cost=0,cost_complete=False)
        result['measurements'].append(dict(D_meV=D,measurement=m))
        result['cost']+=m.get('cost',0)
        result['cost_complete'] &= m.get('cost_complete',True)
        valid=(m.get('ok') and np.isfinite([m.get('offset',np.nan),m.get('t',np.nan),m.get('sep',np.nan)]).all()
               and c['segment_margin']<m['t']<1-c['segment_margin'] and m['sep']>c['separation_min'])
        return m if valid else None
    def event(D,m):
        return dict(D_meV=D,measurement_index=len(result['measurements'])-1,
                    offset=m['offset'],t=m['t'],seeds=m.get('seeds'))
    left=evaluate(a)
    if left is None:return finish('left_endpoint_rejected')
    right=evaluate(b)
    if right is None:return finish('right_endpoint_rejected')
    # Retain endpoint-root candidates, including their correct measurement index.
    if abs(left['offset'])<=tol:
        e=event(a,left);e['measurement_index']=0;return finish('endpoint_candidate',e)
    if abs(right['offset'])<=tol:return finish('endpoint_candidate',event(b,right))
    if left['offset']*right['offset']>=0:return finish('no_sign_bracket')
    for _ in range(maxit):
        mid=(a+b)/2
        if mid==a or mid==b:return finish('floating_point_stagnation')
        m=evaluate(mid)
        if m is None:return finish('interior_evaluation_rejected')
        if abs(m['offset'])<=tol:return finish('sampled_event_candidate',event(mid,m))
        if b-a<=xtol:return finish('width_reached_residual_failed')
        if left['offset']*m['offset']<0:b,right=mid,m
        else:a,left=mid,m
    return finish('iteration_budget_exhausted')

def run(seed, plan, out_path, measure_fn=None):
    """Each station declares an absolute D bracket. Persist every stopping reason."""
    allowed={'config','allow_basis_reseed','stations','tol','xtol','maxit'}
    if set(plan)-allowed or not plan.get('stations'):raise ValueError('invalid trace plan')
    dest=Path(out_path)
    if dest.exists():raise FileExistsError('refusing overwrite of trace evidence')
    out=dict(status='running',source_hashes=model.sources(),plan=plan,input_seed=seed,
             stations=[],stop_reason=None,cost=0,cost_complete=True)
    start=time.perf_counter()
    def save():
        out['seconds']=time.perf_counter()-start
        tmp=dest.with_name(dest.name+'.tmp')
        with open(tmp,'w') as f:
            json.dump(out,f,indent=2,allow_nan=False);f.write('\n');f.flush();__import__('os').fsync(f.fileno())
        tmp.replace(dest)
    # Reserve output so a second invocation cannot overwrite it.
    with open(dest,'x') as f: f.write('{}\n')
    try:
        cfg,conversion=resolve_config(seed,plan.get('config'),plan.get('allow_basis_reseed',False))
        out.update(config=cfg,model=model.MODEL,conversion=conversion)
        seeds=seed['seeds']; previous_basis=None
        for station in plan['stations']:
            x=model.state(dict(seed['x'],**station.get('knobs',{})))
            family=model.Family(x,cfg)
            basis=model.digest(family.indices)
            item=dict(x=x,basis=basis,dimension=family.dim,result=None)
            out['stations'].append(item)
            if previous_basis is not None and basis!=previous_basis:
                out.update(status='stopped',stop_reason='basis_changed_between_stations');save();return out
            previous_basis=basis
            r=solve_event(x,seeds,cfg,station['D_bracket'],tol=plan.get('tol',1e-9),
                          xtol=plan.get('xtol',1e-9),maxit=plan.get('maxit',40),measure_fn=measure_fn)
            item['result']=r;out['cost']+=r['cost'];out['cost_complete'] &= r['cost_complete']
            if r['status']!='candidate':
                out.update(status='stopped',stop_reason=r['reason']);save();return out
            seeds=r['event']['seeds'];save()
        out.update(status='sampled_trace_completed',stop_reason='declared_stations_completed')
    except Exception as e:
        out.update(status='stopped',stop_reason='exception',error=repr(e),cost_complete=False)
    save();return out

if __name__=='__main__':
    seeds=json.loads(Path(sys.argv[1]).read_text()); seed=seeds[0] if isinstance(seeds,list) else seeds
    out=run(seed,json.loads(Path(sys.argv[2]).read_text()),sys.argv[3])
    print(out['status'],out['stop_reason'],out['cost'])
