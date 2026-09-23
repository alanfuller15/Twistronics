"""Reconcile retained migration results with raw reviewer records, no eigensolves."""
import collections
import gzip
import hashlib
import json
import math
from pathlib import Path
import zipfile
import numpy as np

ROOT = Path(__file__).resolve().parent
def load(name): return json.loads((ROOT/name).read_text())

def compare(a, b, skip_seconds=False):
    out = dict(numeric_leaves=0, numeric_exact=0, max_abs_difference=0., differences=[])
    def walk(a,b,p):
        if isinstance(a,dict) and isinstance(b,dict):
            ka,kb=set(a),set(b)
            if skip_seconds: ka.discard('seconds'); kb.discard('seconds')
            if ka!=kb: out['differences'].append(dict(path=p,keys_a=sorted(ka),keys_b=sorted(kb)))
            for k in sorted(ka&kb): walk(a[k],b[k],p+'/'+k)
        elif isinstance(a,list) and isinstance(b,list):
            if len(a)!=len(b): out['differences'].append(dict(path=p,len_a=len(a),len_b=len(b)))
            for i,(aa,bb) in enumerate(zip(a,b)): walk(aa,bb,p+'/'+str(i))
        elif isinstance(a,(float,int)) and not isinstance(a,bool) and isinstance(b,(float,int)) and not isinstance(b,bool):
            out['numeric_leaves']+=1
            delta=abs(a-b);out['max_abs_difference']=max(out['max_abs_difference'],delta)
            if a==b: out['numeric_exact']+=1
            if not math.isfinite(delta) or delta>1e-10: out['differences'].append(dict(path=p,a=a,b=b))
        elif a!=b: out['differences'].append(dict(path=p,a=a,b=b))
    walk(a,b,'')
    out['within_declared_tolerance']=not out['differences']
    return out

def run():
    with zipfile.ZipFile(ROOT/'partner_v077p.zip') as z:
        original = json.loads(z.read('MIGRATION_RESULTS.json'))
        original_mr = json.loads(z.read('METAMORPHIC.json'))
        original_negative = json.loads(z.read('NEGATIVE_CONTROLS.json'))
        binding={k:hashlib.sha256(z.read(k)).hexdigest()==v for k,v in original['source_sha256'].items()}
    replay,clean=load('REPLAY_MIGRATION_RESULTS.json'),load('CLEAN_MIGRATION_RESULTS.json')
    calls,models,discovery=load('MIGRATION_GEOMETRY.json'),load('MIGRATION_MODELS.json'),load('MIGRATION_DISCOVERY.json')
    by_call=collections.defaultdict(list)
    with gzip.open(ROOT/'MIGRATION_LEDGER.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);by_call[r['call_id']].append(r)
    checks=[]
    def check(name,ok,**details): checks.append(dict(name=name,passed=bool(ok),**details))
    check('all supplied source hashes match attachment',all(binding.values()),bindings=binding)
    expected={(b,v,r,n,t) for b in [-.25,-.3] for v in [1,-1] for r,n,t in [(.012,96,300),(.008,192,600)]}
    actual={(r['B'],r['valley'],r['radius'],r['intervals'],r['transport_intervals']) for r in replay['rows']}
    check('exact expected case inventory',len(replay['rows'])==8 and actual==expected)
    check('retained call count',len(calls)==len(replay['rows'])==8)
    rows=[]
    for call,row in zip(calls,replay['rows']):
        cid=call['call_id']; m=models[call['model_id']]; g=call['geometry']; ledger=by_call[cid]
        p=call['policy']; frames=[x for x in ledger if x['kind']=='frame']; links=[x for x in ledger if x['kind']=='link']; angles=[x for x in ledger if x['kind']=='angle']
        coordinate_ok=True
        for frame in frames:
            parts=frame['where'].split(':')
            if parts[0]=='node': coordinate=g['nodes'][int(parts[1])]
            elif parts[0]=='transport': coordinate=g['transport'][int(parts[1])]
            else: coordinate=g['loops'][int(parts[1])][int(parts[3])]
            coordinate_ok &= coordinate==frame['f']
        root_gaps=[]; loop_gaps=[]; exts=[]
        for frame in frames:
            w=frame['energies_meV']; j=frame['lo']-frame['first_band']; gap=w[j+1]-w[j]
            if frame['where'].startswith('node:'): root_gaps.append(gap)
            elif frame['where'].startswith('loop:'): loop_gaps.append(gap)
            lower=w[j]-w[j-1] if frame['lower_external_gap_meV'] is not None else None
            upper=w[j+2]-w[j+1] if frame['upper_external_gap_meV'] is not None else None
            ext=min(v for v in [lower,upper] if v is not None)
            check(f'call {cid} frame {frame["where"]} gaps reconcile',lower==frame['lower_external_gap_meV'] and upper==frame['upper_external_gap_meV'] and ext==frame['external_gap_meV'])
            exts.append(ext)
        winds=[sum(x['step_rad'] for x in angles if x['where']==f'loop:{i}')/math.pi for i in range(2)]
        min_link=min(min(x['singular_values']) for x in links)
        max_step=max(abs(x['step_rad']) for x in angles)
        check(f'call {cid} coordinates exact',coordinate_ok and g['transport'][0]==g['loops'][0][0] and g['transport'][-1]==g['loops'][1][0])
        check(f'call {cid} summary reconciles',root_gaps==row['node_gaps_meV'] and winds==row['windings'] and len(ledger)==row['ledger_rows'] and len(ledger)==call['ledger_rows'])
        check(f'call {cid} model and basis identity',m['constructor']['valley']==row['valley'] and m['harmonics'][0]['amp']==row['B'] and m['index_sha256']==replay['index_set']['sha256'] and m['nG']==49 and m['constructor']['index_set']==m['ordered_index_set'])
        passed=all(x<=p['root_gap_meV'] for x in root_gaps) and min(exts)>=p['external_gap_meV'] and min(loop_gaps)>=p['internal_gap_meV'] and min_link>=p['overlap_min'] and max_step<=p['phase_step_max_rad'] and all(abs(abs(x)-1)<=p['unit_winding_tol'] for x in winds) and max(x['reality_meV'] for x in frames)<=p['reality_meV'] and max(x['hermiticity_meV'] for x in frames)<=p['hermiticity_meV']
        check(f'call {cid} sampled scalar gates reconcile',passed)
        label='SAME' if winds[0]*winds[1]>0 else 'OPPOSITE'
        check(f'call {cid} expected classification',label==row['label']==('SAME' if row['B']==-.25 else 'OPPOSITE') and row['status']=='PASSED_SAMPLED_GATES')
        rows.append(dict(call_id=cid,B=row['B'],valley=row['valley'],radius=row['radius'],intervals=row['intervals'],transport_intervals=row['transport_intervals'],label=label,windings=winds,max_node_gap_meV=max(root_gaps),min_external_gap_meV=min(exts),min_loop_internal_gap_meV=min(loop_gaps),min_link_overlap=min_link,max_phase_increment_rad=max_step,ledger_counts=dict(collections.Counter(x['kind'] for x in ledger))))
    for i in range(0,len(calls),2):
        a,b=calls[i]['geometry'],calls[i+1]['geometry']
        check(f'calls {i}/{i+1} exact coordinate mirror',all(np.array_equal(np.asarray(a[k]),-np.asarray(b[k])) for k in ['nodes','loops','transport']))
    comparisons=dict(supplied_vs_replay=compare(original,replay,True), replay_vs_clean=compare(replay,clean,True),metamorphic=compare(original_mr,load('METAMORPHIC_METAMORPHIC.json')),negative_controls=compare(original_negative,load('NEGATIVE_NEGATIVE_CONTROLS.json')))
    for n,c in comparisons.items(): check(n,c['within_declared_tolerance'])
    controls={r['name']:dict(returncode=r['returncode'],generated=r['generated']) for r in load('EXECUTIONS.json') if r['name'].startswith('CONTROL_')}
    controls['CONTROL_REJECTED']['statuses']=[x['status'] for x in load('CONTROL_REJECTED_MIGRATION_RESULTS.json')['rows']]
    controls['CONTROL_NO_PAIR']['statuses']=[x['status'] for x in load('CONTROL_NO_PAIR_MIGRATION_RESULTS.json')['rows']]
    controls['CONTROL_METAMORPHIC']['false_relations']=[x['relation'] for x in load('CONTROL_METAMORPHIC_METAMORPHIC.json') if not x['holds']]
    failed=[x for x in checks if not x['passed']]
    (ROOT/'RECONCILIATION_CHECKS.json.gz').write_bytes(gzip.compress((json.dumps(checks,indent=1)+'\n').encode(),mtime=0))
    summary=dict(scope='Reviewer replay and contract findings; supplied sources unchanged. All numerical checks are finite, sampled checks.',comparisons=comparisons,source_bindings=binding,checks=len(checks),failed_checks=failed,rows=rows,ledger_rows=sum(len(x) for x in by_call.values()),ledger_counts=dict(collections.Counter(r['kind'] for rs in by_call.values() for r in rs)),model_records=len(models),discovery_searches=len(discovery['searches']),refinement_records=len(discovery['refinements']),refinement_failures=sum(not x.get('last_refine',{}).get('success',False) for x in discovery['refinements']),synthetic_release_controls=controls)
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['rows','synthetic_release_controls']},indent=2))
    if failed: raise SystemExit(1)

if __name__=='__main__': run()
