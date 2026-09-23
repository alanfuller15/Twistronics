"""Test semantic verification separately from raw hash-integrity checks.

Every mutation is explicitly recorded and made in a fresh copy. Most mutations
refresh the run's own manifest, as a new producer would. This is not an attempt
to evade the trusted archive hash, and these rows are never physics evidence.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from review_inputs import ROOT,extract,pack

ENV=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def read(p):return json.loads(p.read_text())
def write(p,obj):p.write_text(json.dumps(obj,indent=1)+'\n')
def lines(p):return [json.loads(x) for x in p.read_text().splitlines()]
def putlines(p,rows):p.write_text(''.join(json.dumps(x)+'\n' for x in rows))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def mutate(d,mode):
    rows=lines(d/'ROWS.jsonl');diag=lines(d/'DIAGNOSTICS.jsonl');summary=read(d/'SUMMARY.json')
    note=''; refresh=True
    if mode=='intact':return 'No mutation',False
    if mode=='missing_geometry':(d/'GEOMETRY.json').unlink();return 'Remove required geometry; retain original manifest',False
    if mode=='unrefreshed_angle':
        next(x for x in diag if x['kind']=='angle')['step_rad']+=.01;putlines(d/'DIAGNOSTICS.jsonl',diag)
        return 'Alter one angle increment without refreshing manifest',False
    if mode=='empty_rows':putlines(d/'ROWS.jsonl',[]);note='Remove every row; leave COMPLETE/eight accepted summary'
    elif mode=='duplicate_row':rows[-1]=rows[0];putlines(d/'ROWS.jsonl',rows);note='Replace last row with first; one expected case absent and another duplicated'
    elif mode=='wrong_label':rows[0]['label']='OPPOSITE';putlines(d/'ROWS.jsonl',rows);note='Flip first SAME label while retaining same-sign winding pair'
    elif mode=='wrong_source':summary['source_sha256']['guarded_topology.py']='0'*64;write(d/'SUMMARY.json',summary);note='Wrong guarded source hash in summary'
    elif mode=='wrong_model':
        models=read(d/'MODELS.json');models[rows[0]['model_ref']]['defaults']['eps']=.02;write(d/'MODELS.json',models);note='Change row model strain from .003 to .02; retain plan and numerical records'
    elif mode=='wrong_basis':
        b=read(d/'BASIS.json');b['ordered_indices'][0]=[999,999];write(d/'BASIS.json',b);note='Replace first basis vector; retain declared ordered-basis hash'
    elif mode=='zero_overlap':
        x=next(x for x in diag if x['kind']=='link');x['singular_values']=[0.,0.];x['min_overlap']=0.;putlines(d/'DIAGNOSTICS.jsonl',diag);note='Set a transport link overlap to zero, below policy .5'
    elif mode=='wrong_frame_role':
        row=rows[0];g=read(d/'GEOMETRY.json')[row['geometry_ref']][row['geometry_side']]
        next(x for x in diag if x['case']==row['case_id'] and x['kind']=='frame' and x['where']=='transport:1')['f']=g['nodes'][0]
        putlines(d/'DIAGNOSTICS.jsonl',diag);note='Move transport:1 frame to a node coordinate that belongs to geometry but is not transport:1'
    elif mode=='missing_link_frames':
        new=[]
        for row in rows:
            selected=diag[row['diagnostics']['first_line']:row['diagnostics']['first_line']+row['diagnostics']['count']]
            selected=[x for x in selected if x['kind']=='angle' or (x['kind']=='frame' and x['where'].startswith('node:'))]
            row['diagnostics']['first_line']=len(new);row['diagnostics']['count']=len(selected);new.extend(selected)
        putlines(d/'DIAGNOSTICS.jsonl',new);putlines(d/'ROWS.jsonl',rows);note='Keep only node frames and angle increments; remove all links and other frames and update slice offsets/counts'
    elif mode=='empty_manifest':write(d/'MANIFEST.json',{});return 'Replace run manifest with empty mapping while keeping files present',False
    else:raise ValueError(mode)
    if refresh:write(d/'MANIFEST.json',{p.name:sha(p) for p in sorted(d.iterdir()) if p.is_file() and p.name!='MANIFEST.json'})
    return note,refresh

def run():
    results=[]
    with tempfile.TemporaryDirectory(prefix='v078-probes-') as tmp:
        tmp=Path(tmp);payload=tmp/'retained';payload.mkdir()
        for mode in ['intact','missing_geometry','unrefreshed_angle','empty_rows','duplicate_row','wrong_label','wrong_source','wrong_model','wrong_basis','zero_overlap','wrong_frame_role','missing_link_frames','empty_manifest']:
            work=extract(tmp/mode);note,refresh=mutate(work/'RUN',mode)
            (work/'VERIFY_RUN.json').unlink(missing_ok=True)
            t=time.perf_counter();p=subprocess.run([sys.executable,'verify_migration.py','RUN'],cwd=work,env=ENV,capture_output=True,timeout=30)
            destination=payload/mode;destination.mkdir()
            (destination/'stdout.log').write_bytes(p.stdout+p.stderr)
            result=read(work/'VERIFY_RUN.json') if (work/'VERIFY_RUN.json').exists() else None
            write(destination/'verification.json',result)
            # Store changed evidence bytes, not thirteen redundant full runs.
            with __import__('zipfile').ZipFile(ROOT/'partner_v078p.zip') as z:
                mutations=[]
                for name in ['SUMMARY.json','ROWS.jsonl','DIAGNOSTICS.jsonl','MODELS.json','GEOMETRY.json','BASIS.json','MANIFEST.json']:
                    source=work/'RUN'/name
                    if not source.exists():mutations.append(dict(file=name,removed=True))
                    elif source.read_bytes()!=z.read('RUN/'+name):
                        (destination/name).write_bytes(source.read_bytes());mutations.append(dict(file=name,sha256=sha(source)))
            record=dict(case=mode,mutation=note,manifest_refreshed=refresh,returncode=p.returncode,checks=len(result['checks']) if result else None,failed=result['failed'] if result else None,wall_seconds=time.perf_counter()-t,mutations=mutations)
            write(destination/'control.json',record);results.append(record)
        consumers=[]
        for mode in ['late_geometry','wrong_gate_status','duplicate_case']:
            work=extract(tmp/('consumer_'+mode),True)
            p=subprocess.run([sys.executable,ROOT/'consumer_control_worker.py',work,mode],cwd=work,env=ENV,capture_output=True,timeout=60)
            destination=payload/('consumer_'+mode);destination.mkdir();(destination/'stdout.log').write_bytes(p.stdout+p.stderr)
            out=work/'OUT'
            files=[p.name for p in out.iterdir()] if out.exists() else []
            for f in files:(destination/f).write_bytes((out/f).read_bytes())
            rows=lines(out/'ROWS.jsonl') if (out/'ROWS.jsonl').exists() else []
            summary=read(out/'SUMMARY.json') if (out/'SUMMARY.json').exists() else None
            write(destination/'PLAN_MIGRATION.json',read(work/'PLAN_MIGRATION.json'))
            record=dict(case=mode,returncode=p.returncode,rows=len(rows),unique_case_ids=len({x['case_id'] for x in rows}),run_status=summary['run_status'] if summary else None,files=sorted(files),gate_statuses=sorted({x.get('gate_status','') for x in rows}),scope='synthetic stubs; not physics')
            write(destination/'control.json',record);consumers.append(record)
        pack(ROOT/'CONTRACT_PROBES_EVIDENCE.zip',[(p,p.relative_to(payload).as_posix()) for p in payload.rglob('*') if p.is_file()])
    write(ROOT/'CONTRACT_PROBES.json',dict(verifier=results,consumer=consumers))
    for x in results:print(x['case'],'exit',x['returncode'],'failed',x['failed'])
    for x in consumers:print('consumer',x['case'],'exit',x['returncode'],'rows',x['rows'],'unique',x['unique_case_ids'],'status',x['run_status'],'files',x['files'])

if __name__=='__main__':run()
