"""Validate the controlled helper-only comparison, without numerical execution."""
from pathlib import Path
from evidence import read,require,sha,safe,finite,write
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]

def compare(a,b,plan,protocol):
    for variant,r in [('defective',a),('repaired',b)]:
        finite(r)
        require(r['status']=='COMPLETE' and r['variant']==variant and r['impact_plan_sha256']==protocol,'impact identity/status mismatch')
        require(r['kinetic']=='none' and r['N']==4,'impact model changed')
        require([c['recipe'] for c in r['cases']]==[x['name'] for x in plan['recipes']],'impact recipe list mismatch')
        for c,p in zip(r['cases'],plan['recipes']):
            require(c['state']==p['state'] and c['status']=='RECIPE_COMPLETED','recipe state or execution mismatch')
            require(len(c['refine_calls'])==2,'missing refinement call')
            m=c['measurement'];require(len(m['nodes'])==len(m['values'])==len(m['windings'])==2,'incomplete measurement')
            qs=[round(w) for w in m['windings']]
            require(all(abs(q)==1 and abs(w-q)<.05 for w,q in zip(m['windings'],qs)),'unresolved historical winding')
            require(m['label']==('SAME' if qs[0]*qs[1]>0 else 'OPPOSITE'),'impact label contradicts winding')
            for j,call in enumerate(c['refine_calls']):
                require(call['seed']==p['seeds'][j] and len(call['attempts']) in [1,2],'refinement sequence mismatch')
                require(call['returned_coordinate']==m['nodes'][j] and call['returned_value']==m['values'][j] and call['reported_metadata']==m['metadata'][j],'refinement log differs from measurement')
                require(call['returned_value']==call['recomputed_value'] and 0<=call['returned_value']<1e-6,'returned value not supported by recomputation')
                require(call['final_optimizer_success']==call['attempts'][-1]['success'],'final optimizer diagnostic mismatch')
                require(call['reported_metadata']['success'] is True,'historical success assertion could not pass')
                if variant=='repaired':
                    info=call['reported_metadata'];last=call['attempts'][-1]
                    require(info['optimizer_success']==last['success'] and info['status']==last['status'] and info['message']==last['message'],'repaired metadata is stale')
                    require(len(info['attempts'])==len(call['attempts']) and not info['rejection_reasons'],'repaired attempt history missing/rejected')
    rows=[]
    for x,y in zip(a['cases'],b['cases']):
        require(x['Hstat_sha256']==y['Hstat_sha256'] and x['model_dimension']==y['model_dimension'],'comparison changed the Hamiltonian')
        ma,mb=x['measurement'],y['measurement']
        rows.append(dict(recipe=x['recipe'],old_label=ma['label'],new_label=mb['label'],label_changed=ma['label']!=mb['label'],
          max_coordinate_change=max(abs(v-w) for p,q in zip(ma['nodes'],mb['nodes']) for v,w in zip(p,q)),
          max_value_change=max(abs(v-w) for v,w in zip(ma['values'],mb['values'])),
          max_winding_change=max(abs(v-w) for v,w in zip(ma['windings'],mb['windings']))))
    return dict(schema=1,status='CONTROLLED_COMPARISON_COMPLETE',impact_plan_sha256=protocol,cases=rows,
      label_changes=sum(r['label_changed'] for r in rows),
      calls_by_variant={r['variant']:sum(len(c['refine_calls']) for c in r['cases']) for r in [a,b]},
      second_attempt_calls_by_variant={r['variant']:sum(len(z['attempts'])==2 for c in r['cases'] for z in c['refine_calls']) for r in [a,b]},
      scope=plan['scope'],limits=['The original historical runtime was not reproduced.','The five recipes use the retained v041 engine, N4 and kinetic=none; this is separate from the modern lab_nn_full campaign.','The historical recipe assertion is exercised, but its winding gate does not provide all modern isolation/refinement guarantees.','Absence of a second attempt in this probe cannot exclude its use in other historical runs.','Zero changes here do not establish that every recorded historical conclusion was unaffected.'])

def build():
    plan=read(ROOT/'IMPACT_PLAN.json');protocol=sha(ROOT/'IMPACT_PLAN.json')
    require(sha(ROOT/'legacy_impact.py')==plan['runner_sha256'],'impact runner changed')
    for name,h in plan['inputs'].items():require(sha(safe(REPO,name))==h,'impact input changed')
    a=ROOT/'results/legacy_defective.json';b=ROOT/'results/legacy_repaired.json'
    result=compare(read(a),read(b),plan,protocol)
    result['record_sha256']={p.name:sha(p) for p in [a,b]}
    return result

if __name__=='__main__':
    r=build();write(ROOT/'IMPACT.json',r);print({k:r[k] for k in ['status','label_changes','calls_by_variant','second_attempt_calls_by_variant']})
