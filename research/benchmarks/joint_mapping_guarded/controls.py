"""Adversarial controls for the reviewed defects and native basis construction."""
import copy
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import numpy as np
import jm_model as m
import jm_sweep as sweep
import jm_trace as trace

checks=[]
def add(name, ok, evidence):
    checks.append(dict(name=name,pass_check=bool(ok),evidence=evidence))
    if not ok: raise AssertionError(name)

def rejected(fn):
    try: fn()
    except (ValueError,RuntimeError,FileExistsError) as e: return str(e)
    return None

def plan():
    return dict(config=dict(N=4),grid=4,max_attempts=2,
                axes=dict(eps=[.007],phi=[15.],theta=[1.],D=[38.],P=[1.]))

def fake(fn, t=.5, fail_at=None):
    def measure(x,seeds,cfg):
        if fail_at is not None and x['D']==fail_at:
            return dict(ok=False,reason='synthetic_root_loss',cost=5)
        return dict(ok=True,offset=float(fn(x['D'])),t=t,sep=1.,cost=3,seeds=seeds)
    return measure

def main():
    seed=json.loads((m.ROOT.parent/'joint_mapping_review/N6_CANDIDATE_SEEDS.json').read_text())[0]
    x=seed['x'];seeds=seed['seeds'];cfg=m.config(dict(N=6))
    with tempfile.TemporaryDirectory(prefix='joint_mapping_guard_controls_') as tmp:
        tmp=Path(tmp)
        calls=[]
        def worker(item): calls.append(item);return dict(status='ok',result={'cost':7})
        p=plan();path=tmp/'resume.jsonl'
        sweep.run(p,path,worker=worker);before=path.read_bytes()
        changes=[]
        for k,v in [('N',6),('grid',48),('solver',dict(trust_radius=.01))]:
            other=copy.deepcopy(p)
            if k=='grid':other[k]=v
            else:other['config'][k]=v
            changes.append(rejected(lambda:sweep.run(other,path,worker=worker)))
        again=sweep.run(p,path,worker=worker)
        add('resume_rejects_cutoff_grid_and_solver_changes',all(changes) and len(calls)==1 and path.read_bytes()==before,
            dict(rejections=changes,unchanged_resume=again))
        with patch.object(m,'sources',lambda:{'synthetic_source':'changed'}):
            source_error=rejected(lambda:sweep.run(p,path,worker=worker))
        add('source_binding_changes_rejected',source_error is not None,source_error)

        path=tmp/'retry.jsonl';calls=[]
        def transient(item):
            calls.append(item)
            return dict(status='error' if len(calls)==1 else 'ok',result={'synthetic':True})
        a=sweep.run(p,path,worker=transient);b=sweep.run(p,path,worker=transient);c=sweep.run(p,path,worker=transient)
        add('failed_state_retried_then_success_skipped',len(calls)==2 and b['successes']==1 and c['attempted']==0,[a,b,c])
        path=tmp/'exhausted.jsonl';calls=[]
        def fail(item):calls.append(item);return dict(status='error',result={'synthetic':True})
        for _ in range(3):last=sweep.run(p,path,worker=fail)
        add('retry_budget_is_bounded',len(calls)==2 and last['attempted']==0,last)

        path=tmp/'tail.jsonl';sweep.run(p,path,worker=worker)
        good=path.read_bytes();tail=b'{"interrupted":'
        path.write_bytes(good+tail)
        rec=sweep.run(p,path,worker=worker)
        quarantine=Path(rec['recovery']['quarantined'])
        add('partial_tail_quarantined_before_append',path.read_bytes()==good and quarantine.read_bytes()==tail,rec)
        # A failed state after a torn tail must still get a parseable successful retry.
        path=tmp/'tail_retry.jsonl';sweep.run(p,path,worker=fail);path.write_bytes(path.read_bytes()+tail)
        rr=sweep.run(p,path,worker=worker)
        add('retry_after_tail_remains_parseable',len([json.loads(s) for s in path.read_text().splitlines()])==2 and rr['successes']==1,rr)
        path=tmp/'newline.jsonl';sweep.run(p,path,worker=worker);path.write_bytes(path.read_bytes().rstrip(b'\n'))
        rr=sweep.run(p,path,worker=worker)
        add('complete_final_record_gets_newline',path.read_bytes().endswith(b'\n'),rr)
        path=tmp/'interior.jsonl';sweep.run(p,path,worker=worker);path.write_bytes(b'{broken}\n'+path.read_bytes())
        damaged=path.read_bytes();err=rejected(lambda:sweep.run(p,path,worker=worker))
        add('interior_corruption_refuses_mutation',err is not None and damaged==path.read_bytes(),err)
        path=tmp/'tamper.jsonl';sweep.run(p,path,worker=worker)
        row=json.loads(path.read_text());row['status']='error';path.write_text(json.dumps(row)+'\n')
        err=rejected(lambda:sweep.run(p,path,worker=worker))
        add('complete_record_hash_tampering_rejected',err is not None,err)
        path=tmp/'lock.jsonl'
        with sweep.writer_lock(path):err=rejected(lambda:sweep.run(p,path,worker=worker))
        add('second_writer_rejected',err is not None,err)

        result=trace.solve_event(x,seeds,cfg,[0,2],measure_fn=fake(lambda D:D-1,t=2))
        add('supporting_line_outside_segment_rejected',result['status']=='failed' and result['event'] is None,result)
        result=trace.solve_event(x,seeds,cfg,[-3,0],tol=1e-8,measure_fn=fake(lambda D:D**3-2*D+2))
        ds=[v['D_meV'] for v in result['measurements']]
        add('all_scalar_trials_stay_in_bracket',result['status']=='candidate' and min(ds)>=-3 and max(ds)<=0,
            dict(reason=result['reason'],evaluations=ds,offset=result['event']['offset']))
        # Root deliberately differs from midpoint; an exhausted budget must not relax tolerance.
        result=trace.solve_event(x,seeds,cfg,[0,2],tol=1e-7,maxit=1,measure_fn=fake(lambda D:1e-5*(D*D-.25)))
        add('exhaustion_keeps_requested_tolerance',result['status']=='failed' and result['reason']=='iteration_budget_exhausted',result)
        resolved,conversion=trace.resolve_config(seed)
        err=rejected(lambda:trace.resolve_config(seed,dict(N=4)))
        add('seed_cutoff_inherited_and_mismatch_rejected',resolved['N']==6 and err is not None,dict(inherited=resolved['N'],rejection=err))
        altered=copy.deepcopy(seed);altered['model']['kinetic']='none'
        err=rejected(lambda:trace.resolve_config(altered))
        add('seed_model_mismatch_rejected',err is not None,err)
        result=trace.solve_event(x,seeds,cfg,[-1,1],measure_fn=fake(lambda D:D))
        add('total_cost_includes_endpoints',result['cost']==9 and len(result['measurements'])==3,result)
        result=trace.solve_event(x,seeds,cfg,[-1,1],measure_fn=fake(lambda D:D,fail_at=0))
        add('failed_measurement_work_retained',result['status']=='failed' and result['cost']==11,result)
        result=trace.solve_event(x,seeds,cfg,[-1,1],measure_fn=fake(lambda D:D*D+1))
        add('same_sign_no_root_not_accepted',result['reason']=='no_sign_bracket',result)
        tp=dict(stations=[dict(D_bracket=[-1,1])])
        stopped=trace.run(seed,tp,tmp/'stopped.json',measure_fn=fake(lambda D:D,t=2))
        saved=json.loads((tmp/'stopped.json').read_text())
        add('trace_persists_stopping_reason',saved['status']=='stopped' and saved['stop_reason']=='left_endpoint_rejected',
            dict(status=stopped['status'],reason=stopped['stop_reason'],cost=stopped['cost']))
        tp=dict(stations=[dict(D_bracket=[-1,1]),dict(knobs={'eps':.0072},D_bracket=[-1,1])])
        stopped=trace.run(seed,tp,tmp/'basis_stop.json',measure_fn=fake(lambda D:D))
        add('radial_trace_stops_on_basis_change',stopped['stop_reason']=='basis_changed_between_stations',
            dict(reason=stopped['stop_reason'],dimensions=[s['dimension'] for s in stopped['stations']]))

        basis=json.loads((m.ROOT/'BASIS.json').read_text());errors=[]
        for engine in ('bm','ref'):
            for eps,mode in [(.007,'union'),(.0072,'intersection')]:
                xx=dict(x,eps=eps);rad=m.build(xx,m.config(dict(N=6,engine=engine)))[0]
                fixed=m.build(xx,m.config(dict(N=6,engine=engine,indices=basis[mode])))[0]
                k=rad.frac_to_k([.71,.63]) if engine=='bm' else rad.k([.71,.63])
                errors.append(float(np.max(abs(rad.H(k)-fixed.H(k)))))
            xx=dict(x,eps=.0072);small=m.build(xx,m.config(dict(N=6,engine=engine,indices=basis['intersection'])))[0]
            large=m.build(xx,m.config(dict(N=6,engine=engine,indices=basis['union'])))[0]
            positions={tuple(v):i for i,v in enumerate(basis['union'])};ids=[]
            for layer in (0,1):
                for p in basis['intersection']:
                    i=positions[tuple(p)];ids.extend([2*len(basis['union'])*layer+2*i,2*len(basis['union'])*layer+2*i+1])
            k=large.frac_to_k([.71,.63]) if engine=='bm' else large.k([.71,.63])
            errors.append(float(np.max(abs(large.H(k)[np.ix_(ids,ids)]-small.H(k)))))
        add('fixed_basis_rebuild_matches_native_and_submatrix',max(errors)<1e-10,dict(matrix_errors_meV=errors))
        err=rejected(lambda:m.config(dict(indices=[[0,0],[0,0],[1,0]])))
        add('invalid_index_set_rejected',err is not None,err)

        # A real grid control merges the very seed omitted by the original 24-grid survey.
        from inputs import originals
        known=json.loads((originals()/'seeds_legA.json').read_text())[0]
        tracked=dict(flat=known['seeds']['flat'],upper=[known['seeds']['node']])
        found=m.survey(known['x'],dict(N=4),grid=24,tracked=tracked,local_grid=3)
        distance=min(np.linalg.norm(np.array(p)-known['seeds']['node']) for p in found['candidates']['upper'])
        add('grid_plus_tracked_seeds_recovers_known_node',distance<1e-6 and any(a['source']=='tracked' and a['accepted'] for a in found['attempts']),
            dict(distance=float(distance),found_counts={k:len(v) for k,v in found['candidates'].items()},cost=found['cost'],
                 attempt_sources={k:sum(a['source']==k for a in found['attempts']) for k in ('grid','tracked','segment_strip')}))
        tiny=plan();tiny['grid']=2;tiny['keep']=1;tiny['axes']['D']=[38.,38.1]
        smoke=sweep.run(tiny,tmp/'parallel.jsonl',workers=2)
        loaded=[json.loads(l) for l in (tmp/'parallel.jsonl').read_text().splitlines()]
        add('two_process_sweep_and_resume_smoke',smoke['successes']==2 and len(loaded)==2 and sweep.run(tiny,tmp/'parallel.jsonl',workers=2)['attempted']==0,smoke)
    out=dict(status='ALL_GUARDED_RUNNER_CONTROLS_PASS',checks=checks,source_hashes=m.sources(),
             control_sha256=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest())
    (m.ROOT/'CONTROLS.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    for c in checks:print(c['name'],c['pass_check'],flush=True)
    print('TOTAL',len(checks),flush=True)

if __name__=='__main__':main()
