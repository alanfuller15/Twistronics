"""Verify retained provenance, matrix margins, charged widths and protocol refusals."""
import json
from fractions import Fraction
from pathlib import Path
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import verify,sha,begin

def need(ok,message):
    if not ok: raise ValueError(message)

def endpoint(e,side):
    x=e[side]
    return Fraction(int(x['mantissa']))*Fraction(2)**x['exponent']

def main():
    out=HERE/'RUN'; integrity=verify(out)
    spec=json.loads((HERE/'SPEC.json').read_text())
    summary=json.loads((out/'RESULTS.json').read_text())
    need(summary['status']=='PASS_EXPECTED_BEHAVIORS','summary')
    need(len(spec['jobs'])==len(summary['jobs'])==10,'inventory')
    need(len({j['id'] for j in spec['jobs']})==10,'duplicate job')
    for f in (out/'SOURCE').rglob('*'):
        if f.is_file(): need(sha(f)==sha(HERE.parent/f.relative_to(out/'SOURCE')),'source')
    for path,digest in spec['dependencies'].items(): need(sha(HERE.parent/path)==digest,'dependency')
    need(sha(out/'S0M_MATRIX.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0M_MATRIX.md'),'note')
    env=json.loads((out/'ENVIRONMENT.json').read_text())
    need(env['wheel']['sha256']==spec['backend']['wheel_sha256'] and env['native_artifacts'],'environment')
    records={}
    for job,row in zip(spec['jobs'],summary['jobs']):
        r=json.loads((out/(job['id']+'.json')).read_text());records[job['id']]=r
        need(r['job']==job and row['id']==job['id'] and row['passed'],'job binding')
        need((r['status'],r['reason'])==(job['expected_status'],job['expected_reason']),'outcome')
        need(r['physical_evaluations']==0 and r['resources']==row['resources'],'record')
        if 'expected_q' in job:
            need(r['q']==job['expected_q'] and r['perturbed_samples'],'perturbed integer')
            lo,hi=endpoint(r['q_interval'],'lower'),endpoint(r['q_interval'],'upper')
            need(lo<=r['q']<=hi and Fraction(15,100)<hi-lo<Fraction(17,100),'charged containment')
            need(Fraction(7,100)<(hi+lo)/2-r['q']<Fraction(9,100),'actual phase shift')
            need(endpoint(r['repair_angle_error'],'lower')>0,'repair term')
        if job['id'].startswith('pair_'):
            need(r['relative']['cells_per_edge']==4096,'fixed cell budget')
            need(r['individual']['a']['q']==job['winding'] and r['individual']['b']['q']==job['other_winding'],'individuals')
            if r['status']=='CERTIFIED':
                need(r['relative']['reason']=='CENTERED_MATRIX_Q_SCREEN','matrix screen')
                need(endpoint(r['relative']['max_distance_F_bound'],'upper')<1,'uniform screen')
                need(all(endpoint(e,'lower')>0 for e in r['relative']['cell_debits_F']),'variation charged')
    near=records['pair_matrix_1']['relative']
    need(endpoint(near['max_distance_F_bound'],'lower')>Fraction(99,100),'near threshold')
    for name in ('pair_matrix_2','pair_matrix_3'):
        need(endpoint(records[name]['relative']['distance_F_bound'],'upper')>1,'screen refusal')
    r=records['repair_width_refuse']
    need(endpoint(r['q_interval'],'upper')-endpoint(r['q_interval'],'lower')>Fraction(1,4),'width refusal')
    controls=['intact']
    for name,path in [('result','perturbed_positive.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0m_001/combined.py'),('marker','COMPLETE.json')]:
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
    print(json.dumps(dict(status='PASS_STATIC_AND_PROTOCOL',jobs=10,record_files=integrity['files'],controls=controls)))

if __name__=='__main__': main()
