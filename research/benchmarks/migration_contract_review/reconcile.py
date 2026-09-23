"""Compare original/replayed evidence and exercise the stricter record checker."""
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile
from review_inputs import ROOT,extract
from check_records import check_records

def load(p):return json.loads(Path(p).read_text())
def compare(a,b,skip=()):
    result=dict(numeric_leaves=0,numeric_exact=0,max_abs_difference=0.,differences=[])
    def walk(a,b,path):
        if isinstance(a,dict) and isinstance(b,dict):
            ka,kb=set(a)-set(skip),set(b)-set(skip)
            if ka!=kb:result['differences'].append(dict(path=path,reason='keys'))
            for k in sorted(ka&kb):walk(a[k],b[k],path+'/'+k)
        elif isinstance(a,list) and isinstance(b,list):
            if len(a)!=len(b):result['differences'].append(dict(path=path,reason='length'))
            for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+'/'+str(i))
        elif isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):
            delta=abs(a-b);result['numeric_leaves']+=1;result['numeric_exact']+=int(a==b);result['max_abs_difference']=max(result['max_abs_difference'],delta)
            if delta>1e-10:result['differences'].append(dict(path=path,a=a,b=b))
        elif a!=b:result['differences'].append(dict(path=path,a=a,b=b))
    walk(a,b,'');result['passed']=not result['differences'];return result

def json_or_lines(b,name):
    return [json.loads(x) for x in b.decode().splitlines()] if name.endswith('.jsonl') else json.loads(b)

def run():
    comparisons={}
    with zipfile.ZipFile(ROOT/'partner_v078p.zip') as a,zipfile.ZipFile(ROOT/'POSITIVE_EVIDENCE.zip') as b:
        for name in ['SUMMARY.json','ROWS.jsonl','DIAGNOSTICS.jsonl','MODELS.json','GEOMETRY.json','BASIS.json']:
            comparisons[name]=compare(json_or_lines(a.read('RUN/'+name),name),json_or_lines(b.read('REPLAY/'+name),name),['seconds_measurement_only'])
    with zipfile.ZipFile(ROOT/'partner_v078p.zip') as a,zipfile.ZipFile(ROOT/'SUPPLIED_CONTROLS_EVIDENCE.zip') as b:
        comparisons['METAMORPHIC.json']=compare(json.loads(a.read('METAMORPHIC.json')),json.loads(b.read('METAMORPHIC.json')))
        old=json.loads(a.read('FAILURE_CONTROLS.json'))['controls'];new=json.loads(b.read('FAILURE_CONTROLS.json'))['controls']
        comparisons['SUPPLIED_CONTROL_OUTCOMES']=compare(old,new,['produced'])
        controls=new
    regressions=[]
    with tempfile.TemporaryDirectory(prefix='v078-reconcile-') as tmp:
        tmp=Path(tmp);source=extract(tmp/'source');original=source/'RUN'
        with zipfile.ZipFile(ROOT/'POSITIVE_EVIDENCE.zip') as z:z.extractall(tmp/'replay')
        replay=check_records(tmp/'replay'/'REPLAY',source)
        (ROOT/'REPLAY_RECORD_CHECK.json').write_text(json.dumps(replay,indent=2)+'\n')
        with zipfile.ZipFile(ROOT/'CONTRACT_PROBES_EVIDENCE.zip') as z:z.extractall(tmp/'probes')
        for d in sorted((tmp/'probes').iterdir()):
            record=load(d/'control.json')
            if d.name.startswith('consumer_'):
                # Incomplete synthetic outputs are refused as accepted evidence.
                result=check_records(d,source);expected=False
            else:
                target=tmp/('check_'+d.name);target.mkdir()
                for p in original.iterdir():
                    if p.is_file():(target/p.name).write_bytes(p.read_bytes())
                for mutation in record['mutations']:
                    p=target/mutation['file']
                    if mutation.get('removed'):p.unlink()
                    else:p.write_bytes((d/mutation['file']).read_bytes())
                result=check_records(target,source);expected=d.name=='intact'
            regressions.append(dict(case=d.name,expected_acceptance=expected,actual_acceptance=result['accepted'],passed=result['accepted']==expected,checks=result['checks'],error_count=len(result['errors']),first_errors=result['errors'][:8]))
    (ROOT/'CHECKER_REGRESSIONS.json').write_text(json.dumps(regressions,indent=2)+'\n')
    summary=dict(comparisons=comparisons,positive_record_acceptance=replay['accepted'],positive_checks=replay['checks'],case_metrics=replay['metrics'],supplied_controls=controls,checker_regressions=len(regressions),checker_regressions_passing=sum(x['passed'] for x in regressions),record_checker_sha256=hashlib.sha256((ROOT/'check_records.py').read_bytes()).hexdigest(),scope='Record consistency and finite sampled replay; synthetic mutations do not describe observed physics.')
    (ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['case_metrics','supplied_controls']},indent=2))
    if not replay['accepted'] or not all(x['passed'] for x in regressions) or not all(x['passed'] for x in comparisons.values()):raise SystemExit(1)

if __name__=='__main__':run()
