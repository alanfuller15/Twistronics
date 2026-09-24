"""Exact endpoint checks and independent artifact integrity controls."""
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
    out=HERE/'RUN';integrity=verify(out);r=json.loads((out/'RESULTS.json').read_text())
    rows=r['records'];expected={'edge1_single_term_refused','uncertain_refused','singular_refused','reflection_refused'}|{f'cell_{n}_8' for n in (1,3,5,7)}
    need(r['status']=='PASS_CELL_DERIVATIVE_CONTROLS' and r['physical_evaluations']==0,'summary')
    need(len(rows)==r['checks']==8 and {v['id'] for v in rows}==expected and all(v['passed'] for v in rows),'inventory')
    for v in rows:
        if v['id']=='edge1_single_term_refused':
            need(end(v['mutant_F'],'lower')>end(v['allowance'],'upper')>0,'mutation margin')
        elif v['id'].startswith('cell_'):
            need(end(v['determinant'],'lower')>0 and end(v['s'],'lower')>0,'domain')
            upper=2*end(v['dM_F_bound'],'upper')/end(v['s'],'lower')
            need(end(v['amplification_F_bound'],'upper')>=upper,'amplification upper rounding')
            need(len(v['dU'])==2 and all(len(row)==2 for row in v['dU']),'matrix shape')
            need({x['offset'] for x in v['point_checks']}=={-1,0,1},'point inventory')
            need(all(end(x['oracle_residual_F'],'upper')<Fraction(1,10**28) for x in v['point_checks']),'oracle residual')
        else: need(v['reason']=='POSITIVE_DETERMINANT_REQUIRED','refusal')
    for path in (out/'SOURCE').rglob('*'):
        if path.is_file(): need(sha(path)==sha(HERE.parent/path.relative_to(out/'SOURCE')),'source binding')
    need(sha(out/'S0P_CELL_DERIVATIVES.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0P_CELL_DERIVATIVES.md'),'note binding')
    controls=['intact']
    for name,path in [('result','RESULTS.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0p_001/check.py'),('marker','COMPLETE.json')]:
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
    print(json.dumps(dict(status='PASS_CELL_RECORDS_AND_PROTOCOL',checks=8,files=integrity['files'],controls=controls)))
if __name__=='__main__': main()
