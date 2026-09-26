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
    need(r['status']=='PASS_SIGNED_ENDPOINT_DEFECT' and r['physical_evaluations']==0,'summary')
    need(r['panels']==512 and r['precision']==128 and r['step_size']=='1/1024','budget')
    need(r['source_domain']=='[0,1/16]' and r['target_domain']=='[0,1/8]','domain')
    need([c['id'] for c in r['cases']]==spec['inventory'],'case inventory')
    for c in r['cases']:
        expected={'constant':dict(k=3,k1=24,k2=438),'two_axis':dict(k=6,k1=120,k2=4656)}[c['id']]
        B=expected['k'];L=expected['k1'];L2=expected['k2']
        need(c['bounds']==expected,'derivative bounds')
        need([s['step'] for s in c['steps']]==list(range(128)),'step inventory')
        need([s['cell'] for s in c['seams']]==list(range(64)),'seam inventory')
        previous=Q(0);legacy_previous=Q(0)
        for s in c['steps']:
            a,la,n,d,g,kb,an,k1,k2,sv,tv,z,b,lb=(end(s[k]) for k in ('start_error','legacy_start_error','centre_norm','generator_radius','generator_debit','generator_norm_bound','frozen_generator_norm','generator_derivative_bound','generator_second_derivative_bound','endpoint_variation_debit','tube_variation_debit','rounding','end_error','legacy_end_error'))
            need(min(a,la,n,d,g,kb,an,k1,k2,sv,tv,z,b,lb)>=0 and a==previous and la==legacy_previous,'continuity')
            need(kb>=B and k1>=L and k2>=L2,'declared bounds')
            need(g>=n*d*h,'generator debit')
            need(sv>=n*(k2*h**3/Q(24)+k1*(kb+an)*h**3/Q(12)),'signed endpoint debit')
            need(tv>=n*k1*h*h/Q(4),'tube variation debit')
            need(b>=a+g+sv+z and lb>=la+g+tv+z,'ledger')
            need(end(s['orthogonality_bound'])>=2*b+b*b and end(s['range_error_bound'])>=b,'derived bounds')
            u=s['tube_u'];e=absmax(u)-h
            need(e>=0 and -e<=end(u,'lower')<=0 and end(u)>=h,'tube')
            need(end(s['tube_extra'])>=n*(d+k1*(h/2+e))*e,'extension')
            previous=b;legacy_previous=lb
        need(end(c['final_error'])==previous and end(c['legacy_final_error'])==legacy_previous,'final error')
        claimed=end(c['improvement'],'lower')
        need(previous<legacy_previous and Q(0)<claimed<=legacy_previous-previous,'signed improvement')
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
    contract=r['gap_to_derivative_contract']
    need(contract['status']=='DECLARED_UNEXECUTED','gap contract state')
    need(contract['required_inputs']==['cluster_interval','complement_interval','spectral_gap_lower','H_derivative_bounds','contour_or_sylvester_choice'],'gap inputs')
    need(contract['required_outputs']==['P_derivative_bounds','K_derivative_bounds','valid_parameter_domain'],'gap outputs')
    need(contract['refusals']==['missing_theorem','missing_gap','unbound_derivative_input','domain_mismatch'],'gap refusals')
    for path in (out/'SOURCE').rglob('*'):
        if path.is_file(): need(sha(path)==sha(HERE.parent/path.relative_to(out/'SOURCE')),'source binding')
    need(sha(out/'S0T_SIGNED_ENDPOINT.md')==sha(HERE.parents[2]/'docs/certification-readiness/S0T_SIGNED_ENDPOINT.md'),'note binding')
    controls=['intact']
    for name,path in [('result','RESULTS.json'),('environment','ENVIRONMENT.json'),('source','SOURCE/certification_s0t_001/check.py'),('marker','COMPLETE.json')]:
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
    print(json.dumps(dict(status='PASS_SIGNED_ENDPOINTS_AND_PROTOCOL',cases=2,steps=256,seams=128,files=integrity['files'],controls=controls)))

if __name__=='__main__': main()
