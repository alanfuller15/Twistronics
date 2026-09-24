"""Static retained-evidence verification and destructive-copy controls."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
from fractions import Fraction
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import verify,sha,begin


def need(condition, name):
    if not condition:
        raise ValueError(name)


def main():
    out=HERE/'RUN'
    integrity=verify(out)
    spec=json.loads((HERE/'SPEC.json').read_text())
    summary=json.loads((out/'RESULTS.json').read_text())
    need(summary['status']=='PASS_EXPECTED_BEHAVIORS' and len(summary['jobs'])==len(spec['jobs']), 'summary')
    for source in (out/'SOURCE').rglob('*'):
        if source.is_file():
            need(sha(source)==sha(HERE.parent/source.relative_to(out/'SOURCE')), 'source')
    for path,expected in spec['dependencies'].items():
        need(sha(HERE.parent/path)==expected, 'dependency')
    need(sha(out/'S0J_CURVED.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0J_CURVED.md'), 'derivation')
    env=json.loads((out/'ENVIRONMENT.json').read_text())
    need(env['wheel']['sha256']==spec['backend']['wheel_sha256'] and env['native_artifacts'], 'environment')
    for j,row in zip(spec['jobs'],summary['jobs']):
        r=json.loads((out/(j['id']+'.json')).read_text())
        need(r['job']==j and (r['status'],r['reason'])==(j['expected_status'],j['expected_reason']), j['id'])
        need(r['physical_evaluations']==0, 'scope')
        need(r['resources']==row['resources'] and r['resources']['wall_seconds']>0 and r['resources']['peak_rss_kib']>0, 'resources')
        if 'expected_q' in j:
            need(r['q']==j['expected_q'], 'integer oracle')
            def endpoint(side):
                value=r['q_interval'][side]
                return Fraction(int(value['mantissa']))*Fraction(2)**value['exponent']
            lo,hi=endpoint('lower'),endpoint('upper')
            need(lo<=r['q']<=hi and hi-lo<=Fraction(1,4), 'contained narrow integer')
        if j['id'] in ('independent_positive','independent_negative'):
            need(r['negative_absolute_real_part_observed'], 'full circle exercised')
    for mode,qs in [('same_class',(1,1)),('different_class',(1,-1))]:
        r=json.loads((out/(mode+'.json')).read_text())
        need(tuple(r['individual'][x]['q'] for x in ('a','b'))==qs, 'individual persistence')
    import ast
    tree=ast.parse((HERE/'sewing.py').read_text())
    imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    need(imports==['flint'] and not any(isinstance(n,ast.Import) for n in ast.walk(tree)), 'ambient module import boundary')
    controls=['intact']
    for name,path in [('result','same_class.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0j_001/sewing.py'),('marker','COMPLETE.json')]:
        with tempfile.TemporaryDirectory() as td:
            copy=Path(td)/'run';shutil.copytree(out,copy)
            f=copy/path
            if name=='marker':
                f.unlink()
            else:
                with f.open('a') as stream: stream.write('\nTAMPERED\n')
            try: verify(copy)
            except (ValueError,FileNotFoundError): controls.append(name+'_refused')
            else: raise ValueError('mutation accepted')
    try: begin(out)
    except FileExistsError: controls.append('overwrite_refused')
    else: raise ValueError('overwrite accepted')
    print(json.dumps({'status':'PASS_STATIC_AND_PROTOCOL','jobs':len(spec['jobs']),'record_files':integrity['files'],'controls':controls}))


if __name__=='__main__': main()
