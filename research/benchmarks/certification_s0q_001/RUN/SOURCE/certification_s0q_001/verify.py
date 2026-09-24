"""Verify retained endpoint implications, source binding and artifact refusals."""
from fractions import Fraction as Q
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

def end(e,side):
    return Q(int(e[side]['mantissa']))*Q(2)**e[side]['exponent']

def absmax(e):
    return max(abs(end(e,'lower')),abs(end(e,'upper')))

def main():
    out=HERE/'RUN'
    integrity=verify(out)
    spec=json.loads((HERE/'SPEC.json').read_text())
    r=json.loads((out/'RESULTS.json').read_text())
    need(r['status']=='PASS_RESOLVENT_KATO_SEAM' and r['checks']==9 and r['physical_evaluations']==0,'summary')
    need(r['panels']==1024 and r['precision']==128,'budget')
    rows=r['records']
    need([v['id'] for v in rows]==spec['inventory'],'inventory')
    for k,v in enumerate(rows[:4]):
        need(v['status']=='CERTIFIED' and v['oracle_points']==3,'cell')
        need(end(v['parameter'],'lower')<=Q(k,512) and end(v['parameter'],'upper')>=Q(k+1,512),'coverage')
        need(end(v['sigma_lower'],'lower')>=Q(19,20),'singular gate')
        for key,shape in [('P',(3,3)),('dP',(3,3)),('F',(3,2)),('dF',(3,2)),('M',(2,2)),('dM',(2,2)),('dU',(2,2))]:
            need(len(v[key])==shape[0] and all(len(row)==shape[1] for row in v[key]),'matrix shape')
            need(all(end(e,'lower')<=end(e,'upper') for row in v[key] for e in row),'endpoints')
        # Check rounded amplification against independently reconstructed squared norm.
        amp=end(v['polar_derivative_bound'],'upper')
        squared=sum(absmax(e)**2 for row in v['dM'] for e in row)
        need(amp>0 and amp**2>=Q(400,361)*squared,'amplification')
        tmax=absmax(v['parameter'])
        for name,t in [('source_remainder',tmax),('target_remainder',2*tmax)]:
            need(end(v[name],'upper')**2>=Q(3528)*t**4,'Taylor remainder')
    expected=['CONTOUR_SEPARATION_REQUIRED','SEAM_SINGULAR_GATE','POSITIVE_DETERMINANT_REQUIRED']
    need([v['reason'] for v in rows[4:7]]==expected and all(v['status']=='INCONCLUSIVE' for v in rows[4:7]),'refusals')
    need(all(v['status']=='MUTATION_REFUSED' for v in rows[7:]),'mutation controls')
    for path in (out/'SOURCE').rglob('*'):
        if path.is_file(): need(sha(path)==sha(HERE.parent/path.relative_to(out/'SOURCE')),'source binding')
    need(sha(out/'S0Q_RESOLVENT_KATO.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0Q_RESOLVENT_KATO.md'),'note binding')
    controls=['intact']
    for name,path in [('result','RESULTS.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0q_001/check.py'),('marker','COMPLETE.json')]:
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
    print(json.dumps(dict(status='PASS_ENDPOINTS_AND_PROTOCOL',checks=9,files=integrity['files'],controls=controls)))

if __name__=='__main__': main()
