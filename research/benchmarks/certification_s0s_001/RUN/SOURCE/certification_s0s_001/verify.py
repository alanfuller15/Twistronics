"""Rational ledger checks; Arb-produced input boxes remain separately trusted."""
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

def absmax(e): return max(abs(end(e,'lower')),abs(end(e)))
def absmin(e):
    lo,hi=end(e,'lower'),end(e)
    return min(abs(lo),abs(hi)) if lo>0 or hi<0 else Q(0)

def main():
    out=HERE/'RUN';integrity=verify(out)
    r=json.loads((out/'RESULTS.json').read_text());h=Q(1,1024)
    spec=json.loads((HERE/'SPEC.json').read_text())
    need(r['status']=='PASS_TAYLOR_NONCOMMUTING_TRANSPORT' and r['physical_evaluations']==0,'summary')
    need(r['panels']==512 and r['precision']==128 and r['step_size']=='1/1024','budget')
    need(r['source_domain']=='[0,1/16]' and r['target_domain']=='[0,1/8]','domain')
    need([c['id'] for c in r['cases']]==spec['inventory'],'case inventory')
    for c in r['cases']:
        L=24 if c['id']=='constant' else 120;B=3 if c['id']=='constant' else 6
        need(c['lipschitz']==L,'derivative bound')
        need([s['step'] for s in c['steps']]==list(range(128)),'step inventory')
        need([s['cell'] for s in c['seams']]==list(range(64)),'seam inventory')
        previous=Q(0)
        for s in c['steps']:
            a,n,d,g,v,z,b=(end(s[k]) for k in ('start_error','centre_norm','generator_radius','generator_debit','variation_debit','rounding','end_error'))
            need(min(a,n,d,g,v,z,b)>=0 and a==previous,'continuity')
            need(g>=n*d*h and v>=n*L*h*h/4 and b>=a+g+v+z,'ledger')
            need(end(s['orthogonality_bound'])>=2*b+b*b and end(s['range_error_bound'])>=b,'derived bounds')
            u=s['tube_u'];e=absmax(u)-h
            need(e>=0 and -e<=end(u,'lower')<=0 and end(u)>=h,'tube')
            need(end(s['tube_extra'])>=n*(d+L*(h/2+e))*e,'extension')
            previous=b
        need(end(c['final_error'])==previous,'final error')
        for k,s in enumerate(c['seams']):
            lo=end(s['parameter'],'lower');hi=end(s['parameter'])
            need(lo<=k*h and hi>=(k+1)*h,'cell coverage')
            u=c['steps'][k]['tube_u'];ul=c['steps'][2*k]['tube_u'];ur=c['steps'][2*k+1]['tube_u']
            need(end(u,'lower')<=lo-k*h and end(u)>=hi-k*h,'source tube')
            need(end(ul,'lower')<=2*lo-2*k*h and end(ur)>=2*hi-(2*k+1)*h,'target tube')
            need(end(s['sigma_lower'],'lower')>=Q(19,20) and end(s['determinant'],'lower')>0,'seam gates')
            squared=sum(absmax(e)**2 for row in s['dM'] for e in row)
            need(end(s['polar_derivative_bound'])**2>=Q(400,361)*squared,'amplification')
        need([v['panels'] for v in c['calibration']]==[256,512],'quadrature inventory')
        for v in c['calibration']:
            N=v['panels'];pi=end(r['pi'])
            need(end(v['projector_debit'])>=pi*pi/(N*N),'projector remainder')
            need(end(v['derivative_debit'])>=Q(13*B,6)*pi*pi/(N*N),'derivative remainder')
        if c['id']=='two_axis':
            need(any(absmin(e)>0 for row in c['commutator'] for e in row),'noncommutation')
            need(any(absmin(e)>0 for row in c['order_difference'] for e in row),'order separation')
            need(any(absmin(e)>previous for row in c['frozen_difference'] for e in row),'frozen refusal')
    for path in (out/'SOURCE').rglob('*'):
        if path.is_file(): need(sha(path)==sha(HERE.parent/path.relative_to(out/'SOURCE')),'source binding')
    need(sha(out/'S0S_TAYLOR_NONCOMMUTING.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0S_TAYLOR_NONCOMMUTING.md'),'note binding')
    controls=['intact']
    for name,path in [('result','RESULTS.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0s_001/check.py'),('marker','COMPLETE.json')]:
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
    print(json.dumps(dict(status='PASS_ENDPOINTS_AND_PROTOCOL',cases=2,steps=256,seams=128,files=integrity['files'],controls=controls)))

if __name__=='__main__': main()
