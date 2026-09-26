"""Exact rational verification of the retained restart ledger and integrity."""
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

def end(e,side='upper'):
    return Q(int(e[side]['mantissa']))*Q(2)**e[side]['exponent']

def absmax(e):
    return max(abs(end(e,'lower')),abs(end(e)))

def main():
    out=HERE/'RUN';integrity=verify(out)
    r=json.loads((out/'RESULTS.json').read_text());h=Q(1,1024)
    need(r['status']=='PASS_RESTARTED_TRANSPORT' and r['physical_evaluations']==0,'summary')
    need(r['panels']==2048 and r['precision']==128 and r['step_size']=='1/1024','budget')
    need(r['source_domain']=='[0,1/16]' and r['target_domain']=='[0,1/8]','domain')
    need([s['step'] for s in r['steps']]==list(range(128)),'steps')
    need([s['cell'] for s in r['seams']]==list(range(64)),'seams')
    previous=Q(0)
    for s in r['steps']:
        a,c,d,g,v,z,b=(end(s[n]) for n in ('start_error','centre_norm','generator_radius','generator_debit','variation_debit','rounding','end_error'))
        need(min(a,c,d,g,v,z,b)>=0 and a==previous,'error continuity')
        need(g>=c*d*h and v>=c*48*h*h/4,'local debit')
        need(b>=a+g+v+z,'accumulation')
        need(end(s['orthogonality_bound'])>=2*b+b*b and end(s['range_error_bound'])>=b,'derived errors')
        u=s['tube_u'];e=absmax(u)-h
        need(e>=0 and end(u,'lower')<=0 and end(u)>=h,'tube coverage')
        need(end(u,'lower')>=-e,'negative extension')
        need(end(s['tube_extra'])>=c*(d+48*(h/2+e))*e,'extension debit')
        previous=b
    for k,s in enumerate(r['seams']):
        lo=end(s['parameter'],'lower');hi=end(s['parameter'])
        need(lo<=k*h and hi>=(k+1)*h,'cell coverage')
        u=r['steps'][k]['tube_u']
        need(end(u,'lower')<=lo-k*h and end(u)>=hi-k*h,'source tube')
        ul=r['steps'][2*k]['tube_u'];ur=r['steps'][2*k+1]['tube_u']
        need(end(ul,'lower')<=2*lo-2*k*h and end(ur)>=2*hi-(2*k+1)*h,'target tubes')
        need(end(s['sigma_lower'],'lower')>=Q(19,20),'seam gate')
        need(len(s['dM'])==2 and all(len(row)==2 for row in s['dM']),'shape')
        need(all(end(e,'lower')<=end(e) for row in s['dM'] for e in row),'endpoints')
        squared=sum(absmax(e)**2 for row in s['dM'] for e in row)
        need(end(s['polar_derivative_bound'])**2>=Q(400,361)*squared,'polar amplification')
    need(end(r['final_frame_error'])==previous<end(r['single_origin_remainder'],'lower'),'comparison')
    need(end(r['geometric_refusal_column_upper'])<Q(19,20),'geometric refusal')
    need(r['controls']==['non_skew_refused','geometric_seam_refused'],'controls')
    for path in (out/'SOURCE').rglob('*'):
        if path.is_file(): need(sha(path)==sha(HERE.parent/path.relative_to(out/'SOURCE')),'source binding')
    need(sha(out/'S0R_RESTARTED_TRANSPORT.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0R_RESTARTED_TRANSPORT.md'),'note binding')
    controls=['intact']
    for name,path in [('result','RESULTS.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0r_001/check.py'),('marker','COMPLETE.json')]:
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
    print(json.dumps(dict(status='PASS_ENDPOINTS_AND_PROTOCOL',steps=128,seams=64,files=integrity['files'],controls=controls)))

if __name__=='__main__': main()
