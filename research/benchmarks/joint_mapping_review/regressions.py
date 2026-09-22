"""Reproduce review findings against unchanged partner code in temporary files."""
import contextlib
import inspect
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from inputs import ROOT, originals, binding

originals()
import sweep
import trace

checks=[]
def add(name,ok,evidence):
    assert ok,name;checks.append({'name':name,'finding_reproduced':bool(ok),'evidence':evidence})

def baseplan(N=4,grid=24):return {'N':N,'grid':grid,'axes':{'eps':[.007],'phi':[15.],'theta':[1.],'D':[38.],'P':[1.]}}

with tempfile.TemporaryDirectory(prefix='joint_mapping_regression_') as td:
    td=Path(td)
    with contextlib.redirect_stdout(io.StringIO()):
        p=td/'plan.json';out=td/'resume.jsonl';calls=[]
        def work(item):
            calls.append(item);k,x,N,n=item
            return {'key':k,'x':x,'N':N,'grid':n,'status':'ok'}
        p.write_text(json.dumps(baseplan()))
        with patch.object(sweep,'work',work):
            sweep.main(str(p),str(out));p.write_text(json.dumps(baseplan(6,48)));sweep.main(str(p),str(out))
        rows=[json.loads(l) for l in out.read_text().splitlines()]
        add('resume_ignores_N_and_grid',len(calls)==1 and rows[0]['N']==4,{'requested_second_N':6,'requested_second_grid':48,'worker_calls':len(calls),'retained_rows':rows})

        out=td/'errors.jsonl';calls=[];p.write_text(json.dumps(baseplan()))
        def error(item):calls.append(item);return {'key':item[0],'status':'error','error':'synthetic transient failure'}
        with patch.object(sweep,'work',error):sweep.main(str(p),str(out));sweep.main(str(p),str(out))
        add('error_rows_are_not_retried',len(calls)==1,{'worker_calls':len(calls),'retained_output':out.read_text()})

        out=td/'truncated.jsonl';out.write_text('{"key":"interrupted"');calls=[]
        with patch.object(sweep,'work',work):sweep.main(str(p),str(out))
        valid=[]
        for line in out.read_text().splitlines():
            try:valid.append(json.loads(line))
            except json.JSONDecodeError:pass
        add('append_after_truncated_tail_loses_new_record',len(calls)==1 and not valid,{'worker_calls':len(calls),'parseable_records':len(valid),'retained_output':out.read_text()})

    seeds={'flat':[[0.,0.],[1.,0.]],'node':[.5,0.],'gap':'upper'}
    x={'eps':.007,'phi':15.,'theta':1.,'D':0.,'P':1.}
    def fake(fn,t=.5,log=None):
        def f(xx,ss,N=4):
            if log is not None:log.append({'D':xx['D'],'N':N,'solves':3})
            return {'offset':float(fn(xx['D'])),'t':t,'sep':1.,'flat':ss['flat'],'node':ss['node'],'seeds':ss,'solves':3}
        return f
    with patch.object(trace.atlas,'measure',fake(lambda D:D-1,t=2.)):
        result=trace.solve_event(x,seeds,'D',[0.,2.])
    add('outside_segment_accepted_as_event',result is not None and result[1]['t']==2.,{'event_value':result[0],'t':result[1]['t'],'offset':result[1]['offset']})

    calls=[]
    with patch.object(trace.atlas,'measure',fake(lambda D:D**3-2*D+2,log=calls)):
        result=trace.solve_event(x,seeds,'D',[-3.,0.])
    add('secant_leaves_valid_sign_bracket',any(r['D']>0 or r['D'] < -3 for r in calls),{'initial_bracket':[-3.,0.],'endpoint_offsets':[-19.,2.],'evaluations':calls,'event_returned':result is not None})

    with patch.object(trace.atlas,'measure',fake(lambda D:1e-5*(D**2-1))):
        result=trace.solve_event(x,seeds,'D',[0.,2.],tol=1e-7,maxit=1)
    add('event_tolerance_relaxed_on_budget_exhaustion',result is not None and abs(result[1]['offset'])>1e-7,{'requested_tolerance':1e-7,'maxit':1,'accepted_offset':result[1]['offset']})

    s=td/'seed.json';s.write_text(json.dumps([{'x':x,'N':6,'gap':'upper','seeds':seeds}]))
    out=td/'trace.json';calls=[]
    with contextlib.redirect_stdout(io.StringIO()),patch.object(trace.atlas,'measure',fake(lambda D:D-.2,log=calls)):
        trace.main(str(s),str(out),'phi',1.,0,'D')
    saved=json.loads(out.read_text())
    add('seed_cutoff_ignored_by_default',saved['N']==4 and all(r['N']==4 for r in calls),{'seed_N':6,'default_argument':inspect.signature(trace.main).parameters['N'].default,'output_N':saved['N'],'evaluation_count':len(calls)})

    calls=[]
    with patch.object(trace.atlas,'measure',fake(lambda D:D-.2,log=calls)):
        result=trace.solve_event(x,seeds,'D',[-1.,1.])
    reported=result[1]['solves'];total=sum(r['solves'] for r in calls)
    add('point_cost_omits_prior_event_evaluations',reported<total,{'measure_calls':len(calls),'returned_solves':reported,'total_fake_solves':total,'bracketing_cost_not_included':True})

result={'status':'EIGHT_CONSEQUENTIAL_PARTNER_TOOL_FINDINGS_REPRODUCED','source_hashes':binding(['regressions.py']),'findings':checks,'all_findings_reproduced':all(c['finding_reproduced'] for c in checks)}
(ROOT/'REGRESSIONS.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
for c in checks:print(c['name'],c['finding_reproduced'])
