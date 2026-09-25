"""Independently compare retained interval endpoints and integrity controls."""
from fractions import Fraction
import json
from pathlib import Path
import shutil
import sys
import tempfile
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'certification_s0b_001'))
from runner_io import verify,sha,begin
def need(ok,msg):
    if not ok: raise ValueError(msg)
def end(e,k):
    return Fraction(int(e[k]['mantissa']))*Fraction(2)**e[k]['exponent']
def main():
    out=HERE/'RUN';intact=verify(out)
    r=json.loads((out/'RESULTS.json').read_text());rows=r['records']
    need(r['status']=='PASS_FIXED_DERIVATIVE_CONTROLS' and r['physical_evaluations']==0,'summary')
    expected={f'derivative_{e}_{k}' for e in (1,2) for k in (32,128,224)}|{'polar_1_7','polar_1_2','polar_6_7','polar_reflection_refused','L2_quadratic_remainder_counterexample'}
    need(len(rows)==11 and {v['id'] for v in rows}==expected and all(v['passed'] for v in rows),'inventory')
    mutants=0
    for v in rows:
        if v['id'].startswith('derivative_'):
            for key in ('first_bound','second_bound'):
                need(end(v['error_F'],'upper')<=end(v[key],'lower'),'derivative margin')
            if v['id'].startswith('derivative_2_'):
                need(v['negated_Dp_refused'] and end(v['mutant_error_F'],'lower')>end(v['second_bound'],'upper'),'mutant margin');mutants+=1
        if 'residual_F' in v: need(end(v['residual_F'],'upper')<Fraction(1,10**28),'polar residual')
        if v['id']=='L2_quadratic_remainder_counterexample':
            need(end(v['error'],'lower')==Fraction(1,2**24) and end(v['invalid_bound'],'upper')==Fraction(1,2**36),'counterexample')
    need(len(rows)+mutants==r['checks']==14,'count')
    for path in (out/'SOURCE').rglob('*'):
        if path.is_file(): need(sha(path)==sha(HERE.parent/path.relative_to(out/'SOURCE')),'source identity')
    need(sha(out/'S0O_DERIVATIVES.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0O_DERIVATIVES.md'),'note identity')
    controls=['intact']
    for name,path in [('result','RESULTS.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0n_001/combined.py'),('marker','COMPLETE.json')]:
        with tempfile.TemporaryDirectory() as td:
            copy=Path(td)/'run';shutil.copytree(out,copy);p=copy/path
            if name=='marker': p.unlink()
            else:
                with p.open('a') as stream: stream.write('\nTAMPERED\n')
            try: verify(copy)
            except (ValueError,FileNotFoundError): controls.append(name+'_refused')
            else: raise ValueError('mutation accepted')
    try: begin(out)
    except FileExistsError: controls.append('overwrite_refused')
    else: raise ValueError('overwrite accepted')
    print(json.dumps(dict(status='PASS_RETAINED_AND_PROTOCOL',checks=14,files=intact['files'],controls=controls)))
if __name__=='__main__': main()
