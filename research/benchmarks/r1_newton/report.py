"""Reconstruct saved acceptance decisions and independently reevaluate final roots."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'PLAN.json').read_text());V=P['validation']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    data=json.loads((ROOT/'RESULTS.json').read_text());control=json.loads((ROOT/'CONTROLS.json').read_text())
    assert data['status']!='RUNNING' and not data['errors'];assert data['plan_sha256']==control['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT.parent/n)==h for n,h in data['source_hashes'].items())
    assert control['all_controls_pass'] and all(sha(ROOT/n)==h for n,h in control['source_hashes'].items())
    sys.path.insert(0,str(ROOT.parent/'r1_holonomy'));from measure import Family
    families={e:Family(e) for e in P['engines']}
    parent={e:json.loads((ROOT.parent/'r1_holonomy'/(e.upper()+'.json')).read_text())['tracks']['16']['stations'] for e in P['engines']}
    errors={k:0. for k in ['stored_gap','stored_exterior_gap','stored_jacobian_singular_values','returned_gap','returned_position','step_equation','step_position','reevaluated_spectrum_meV','reevaluated_jacobian_singular_values','case_distance']}
    histories=0;trials=0;max_step=0.;final_records=[]
    for group in ['primary','forced_fallback','stress']:
        for row in data[group]:
            r=row['variant']['result'];cfg=r['config'];history=r['history'];box=np.array(r['box']);family=families[row['engine']]
            assert r['eigensolves']==len(history);histories+=len(history)
            for h in history:
                f=np.array(h['f']);w=np.array(h['w']);assert np.isfinite(w).all() and np.isfinite(f).all() and np.all(np.diff(w)>=0)
                assert np.all(f>=box[0]) and np.all(f<=box[1]);sv=np.linalg.svd(h['jacobian'],compute_uv=False)
                errors['stored_gap']=max(errors['stored_gap'],abs(h['gap_meV']-(w[2]-w[1])))
                errors['stored_exterior_gap']=max(errors['stored_exterior_gap'],abs(h['exterior_gap_meV']-min(w[1]-w[0],w[3]-w[2])))
                errors['stored_jacobian_singular_values']=max(errors['stored_jacobian_singular_values'],float(np.max(np.abs(sv-h['jacobian_singular_values']))))
                if h['guard_failure'] is None:
                    assert h['exterior_gap_meV']>=cfg['exterior_gap_min_meV'] and h['anchor_smin']>=cfg['anchor_smin_min'] and h['orthogonality_error']<=cfg['orthogonality_tolerance']
            returned=history[r['returned_evaluation']] if r['returned_evaluation'] is not None else None
            if returned:
                errors['returned_gap']=max(errors['returned_gap'],abs(r['gap_meV']-returned['gap_meV']))
                errors['returned_position']=max(errors['returned_position'],float(np.max(np.abs(np.array(r['f'])-returned['f']))))
                assert returned['guard_failure'] is None
                w,F=eigh(family.H([*r['f'],r['D_meV']]),subset_by_index=(r['lo']-1,r['lo']+2));Fp=F[:,1:3]
                errors['reevaluated_spectrum_meV']=max(errors['reevaluated_spectrum_meV'],float(np.max(np.abs(w-returned['w']))))
                aj=[Fp.T@family.A[a]@Fp for a in [0,1]];J=np.array([[(a[0,0]-a[1,1])/2 for a in aj],[a[0,1] for a in aj]])
                sv=np.linalg.svd(J,compute_uv=False);errors['reevaluated_jacobian_singular_values']=max(errors['reevaluated_jacobian_singular_values'],float(np.max(np.abs(sv-returned['jacobian_singular_values']))))
                final_records.append({'engine':row['engine'],'group':group,'D_meV':r['D_meV'],'node_or_case':row.get('node',row.get('case')),'accepted':r['accepted'],'fresh_gap_meV':float(w[2]-w[1]),'fresh_jacobian_singular_values':sv.tolist()})
                if r['accepted']:
                    assert r['reason']=='converged' and r['gap_meV']<=cfg['acceptance_gap_meV'] and sv[-1]>=cfg['jacobian_smin_min'] and sv[0]/sv[-1]<=cfg['jacobian_condition_max']
                    if r['method']=='newton':assert r['gap_meV']<=cfg['newton_stop_gap_meV']
                    else:assert r['fallback_optimizer']['success'] and r['fallback_attempted']
            for step in r['steps']:
                trials+=1;a=history[step['from_evaluation']];J=np.array(a['jacobian']);delta=np.array(step['raw_step']);alpha=step['scale']
                equation=J@delta-np.array([a['gap_meV']/2,0.]);errors['step_equation']=max(errors['step_equation'],float(np.max(np.abs(equation))))
                target=np.clip(np.array(a['f'])+alpha*delta,*box);errors['step_position']=max(errors['step_position'],float(np.max(np.abs(target-step['target']))))
                length=float(np.linalg.norm(target-a['f']));max_step=max(max_step,length);assert length<=cfg['trust_radius']+1e-14
                if step['accepted']:
                    b=history[step['trial_evaluation']];assert b['guard_failure'] is None and np.array_equal(b['f'],step['target'])
                    assert b['gap_meV']<=cfg['newton_stop_gap_meV'] or b['gap_meV']<a['gap_meV']*(1-cfg['armijo']*alpha)
            if group=='primary':
                j=row['station'];k=['p','q','upper'].index(row['node']);retained=np.array(parent[row['engine']][j]['roots'][k]['f']);assert row['D_meV']==parent[row['engine']][j]['D_meV']
                expected=retained+[.002,-.001] if row['seed_mode']=='offset' else np.array(parent[row['engine']][j-1]['roots'][k]['f']) if j else retained+[-.002,.001]
                assert np.array_equal(expected,row['seed']) and np.array_equal(expected,r['seed']) and np.array_equal(retained,row['retained_root'])
                actual=float(np.linalg.norm(np.array(r['f'])-row['reference']['result']['f']));errors['case_distance']=max(errors['case_distance'],abs(actual-row['root_distance']))
                ok=r['accepted'] and row['reference']['result']['accepted'] and actual<V['root_distance_max'] and np.linalg.norm(np.array(r['f'])-retained)<V['root_distance_max'] and row['native']['gap_meV']<V['native_gap_max_meV'] and row['native']['spectrum_error_meV']<V['native_spectrum_max_meV']
                assert bool(ok)==row['pass']
            if group=='forced_fallback':assert r['fallback_attempted'] and r['method']=='bounded_least_squares' and r['config']['newton_iterations']==0
    expected={(e,j,n,m) for e in P['engines'] for j in range(17) for n in ['p','q','upper'] for m in ['offset','carried']}
    actual=[(r['engine'],r['station'],r['node'],r['seed_mode']) for r in data['primary']];assert len(actual)==len(set(actual)) and set(actual)==expected
    assert max(errors.values())<V['reconciliation_error'],errors
    performance=[]
    for e in P['engines']:
        rr=[r for r in data['primary'] if r['engine']==e]
        ratios=[r['reference']['seconds']/r['variant']['seconds'] for r in rr]
        performance.append({'engine':e,'cases':len(rr),'reference_total_eigensolves':sum(r['reference']['eigensolves'] for r in rr),'variant_total_eigensolves':sum(r['variant']['result']['eigensolves'] for r in rr),
          'reference_median_eigensolves':float(np.median([r['reference']['eigensolves'] for r in rr])),'variant_median_eigensolves':float(np.median([r['variant']['result']['eigensolves'] for r in rr])),
          'reference_total_seconds':sum(r['reference']['seconds'] for r in rr),'variant_total_seconds':sum(r['variant']['seconds'] for r in rr),'median_per_case_speedup':float(np.median(ratios)),
          'primary_fallbacks':sum(r['variant']['result']['fallback_attempted'] for r in rr)})
    allrows=data['primary']+data['forced_fallback'];stress=[{'engine':r['engine'],'case':r['case'],'D_meV':r['D_meV'],'accepted':r['variant']['result']['accepted'],'method':r['variant']['result']['method'],'reason':r['variant']['result']['reason'],'gap_meV':r['variant']['result']['gap_meV'],'matches_expected_behavior':r['matches_expected_behavior']} for r in data['stress']]
    ok=all(r['pass'] for r in allrows) and all(r['matches_expected_behavior'] for r in data['stress'])
    summary={'status':'RECONCILED_GUARDED_NEWTON_VARIANT_PASS' if ok else 'UNRESOLVED_COMPARISONS_RETAINED','all_checks_pass':ok,'primary_cases':len(data['primary']),'forced_fallback_cases':len(data['forced_fallback']),'analytic_controls':len(control['controls']),'stress_cases':stress,
      'performance':performance,'maximum_root_difference':max(r['root_distance'] for r in data['primary']),'maximum_retained_root_difference':max(r['retained_root_distance'] for r in data['primary']),
      'maximum_native_gap_meV':max(r['native']['gap_meV'] for r in allrows),'maximum_native_spectrum_error_meV':max(r['native']['spectrum_error_meV'] for r in allrows),'recorded_evaluations':histories,'newton_trials':trials,'maximum_newton_step':max_step,'reconstruction_errors':errors,'final_reevaluations':final_records,
      'scope':P['scope'],'source_hashes':{n:sha(ROOT/n) for n in ['PLAN.json','solver.py','run.py','report.py','RESULTS.json','CONTROLS.json','controls.py','partner_fast_engine.py','partner_engine_study.zip']}}
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ['source_hashes','final_reevaluations']},indent=2))
    return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
