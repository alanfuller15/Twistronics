"""Static retained-record checks; no numerical rerun."""
import json
from fractions import Fraction
from pathlib import Path
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import verify,sha,begin

def need(test,message):
    if not test: raise ValueError(message)

def endpoint(e,side):
    v=e[side];return Fraction(int(v['mantissa']))*Fraction(2)**v['exponent']

def main():
    out=HERE/'RUN';integrity=verify(out)
    spec=json.loads((HERE/'SPEC.json').read_text())
    summary=json.loads((out/'RESULTS.json').read_text())
    need(summary['status']=='PASS_EXPECTED_BEHAVIORS' and len(summary['jobs'])==len(spec['jobs']),'summary')
    for f in (out/'SOURCE').rglob('*'):
        if f.is_file(): need(sha(f)==sha(HERE.parent/f.relative_to(out/'SOURCE')),'source')
    for path,digest in spec['dependencies'].items(): need(sha(HERE.parent/path)==digest,'dependency')
    need(sha(out/'S0L_STRESS.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0L_STRESS.md'),'note')
    env=json.loads((out/'ENVIRONMENT.json').read_text())
    need(env['wheel']['sha256']==spec['backend']['wheel_sha256'] and env['native_artifacts'],'environment')
    for job,row in zip(spec['jobs'],summary['jobs']):
        r=json.loads((out/(job['id']+'.json')).read_text())
        need(r['job']==job and (r['status'],r['reason'])==(job['expected_status'],job['expected_reason']),'outcome')
        need(row['passed'] and r['resources']==row['resources'] and r['physical_evaluations']==0,'record')
        if 'expected_q' in job:
            need(r['q']==job['expected_q'],'oracle')
            lo,hi=endpoint(r['q_interval'],'lower'),endpoint(r['q_interval'],'upper')
            need(lo<=r['q']<=hi and hi-lo<=Fraction(1,4),'integer containment')
            need(r['corner']['delta_excludes_zero'],'nonzero repair')
            need(endpoint(r['uniform_seam_smin_lower'],'lower')>=Fraction(19,20),'singular gate')
            for d in r['deficits']:
                need(endpoint(d['origin_deletion'],'lower')>0 and endpoint(d['origin_off_target_squared'],'lower')>0,'both deficits')
    for mode,qs in [('pair_equal',(1,1)),('pair_unequal',(1,-1))]:
        r=json.loads((out/(mode+'.json')).read_text())
        need(tuple(r['individual'][x]['q'] for x in ('a','b'))==qs,'pair records')
    need(len(spec['jobs'])==15 and len({j['id'] for j in spec['jobs']})==15,'fixed inventory')
    for name in ('width_positive','width_negative'):
        r=json.loads((out/(name+'.json')).read_text())
        width=endpoint(r['q_interval'],'upper')-endpoint(r['q_interval'],'lower')
        need(Fraction(12,100)<width<Fraction(14,100),'nontrivial propagated width')
    for name in ('pair_defect','pair_near_pass','pair_near_refuse'):
        r=json.loads((out/(name+'.json')).read_text())
        need(all(r['individual'][x]['q']==1 for x in ('a','b')),'same-class individual integers')
    near=json.loads((out/'pair_near_pass.json').read_text())['relative']
    need(Fraction(96,100)<endpoint(near['max_distance_F_bound'],'upper')<1,'near-threshold passing bound')
    refused=json.loads((out/'pair_near_refuse.json').read_text())['relative']
    need(refused['failed_edge']==2 and endpoint(refused['distance_F_bound'],'upper')>1,'near-threshold refusal')
    controls=['intact']
    for name,path in [('result','positive.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0l_001/combined.py'),('marker','COMPLETE.json')]:
        with tempfile.TemporaryDirectory() as td:
            copy=Path(td)/'run';shutil.copytree(out,copy);f=copy/path
            if name=='marker': f.unlink()
            else:
                with f.open('a') as stream: stream.write('\nTAMPERED\n')
            try: verify(copy)
            except (ValueError,FileNotFoundError): controls.append(name+'_refused')
            else: raise ValueError('mutation accepted')
    try: begin(out)
    except FileExistsError: controls.append('overwrite_refused')
    else: raise ValueError('overwrite accepted')
    print(json.dumps(dict(status='PASS_STATIC_AND_PROTOCOL',jobs=len(spec['jobs']),record_files=integrity['files'],controls=controls)))

if __name__=='__main__':main()
