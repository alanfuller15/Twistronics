"""Strict bounded record acceptance for the eight reviewed v078p cases.

This is a reviewer-owned reference checker, not a general topology proof or a
replacement for the consumer. It verifies content relationships and stored
scalar gates against separately bound expectations. It cannot establish that
stored diagnostics came from the claimed computation without trusted execution,
nor reconstruct overlaps without eigenvectors. Incomplete runs are rejected for
acceptance, even when they correctly retain failure evidence.
"""
import collections
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parent
def reject_constant(x):raise ValueError('nonfinite JSON '+x)
def load(p):return json.loads(Path(p).read_text(),parse_constant=reject_constant)
def lines(p):return [json.loads(x,parse_constant=reject_constant) for x in Path(p).read_text().splitlines()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def same(a,b):return np.array_equal(np.asarray(a),np.asarray(b))

def check_records(directory,source):
    d,source=Path(directory),Path(source);errors=[];checks=0;metrics=[]
    def ck(ok,message):
        nonlocal checks
        checks+=1
        if not bool(ok):errors.append(message)
    try:
        E=load(ROOT/'CONTRACT_EXPECTATIONS.json')
        names={'SUMMARY.json','ROWS.jsonl','DIAGNOSTICS.jsonl','MODELS.json','GEOMETRY.json','BASIS.json'}
        ck(all((d/n).is_file() for n in names|{'MANIFEST.json'}),'required files')
        if errors:return dict(accepted=False,checks=checks,errors=errors,metrics=[])
        manifest=load(d/'MANIFEST.json');ck(set(manifest)==names,'manifest exact required-file coverage')
        for n in names:ck(manifest.get(n)==sha(d/n),'file hash '+n)
        S=load(d/'SUMMARY.json');rows=lines(d/'ROWS.jsonl');diags=lines(d/'DIAGNOSTICS.jsonl');models=load(d/'MODELS.json');geoms=load(d/'GEOMETRY.json');basis=load(d/'BASIS.json')
        plan=load(source/'PLAN_MIGRATION.json')
        ck(plan==E['plan'],'plan matches frozen reviewed cases and parameters')
        ck(S['plan_sha256']==sha(source/'PLAN_MIGRATION.json'),'current plan hash')
        ck(S['source_sha256']==E['source_sha256'],'declared source identity')
        for n,h in E['source_sha256'].items():ck(sha(source/n)==h,'actual source identity '+n)
        ck(S['policy']==E['policy'],'summary policy')
        ck(basis==E['basis'],'ordered basis and identity')
        ck(hashlib.sha256(json.dumps(basis['ordered_indices']).encode()).hexdigest()==basis['sha256'],'basis internal hash')
        cases=E['plan']['expected_cases'];ids=[c['case_id'] for c in cases]
        ck(len(ids)==len(set(ids))==8,'unique expected case inventory')
        ck(S['expected_cases']==ids,'summary expected case order')
        ck(collections.Counter(r['case_id'] for r in rows)==collections.Counter(ids),'exact actual case inventory without duplicate/missing rows')
        actual_accepted=[r['case_id'] for r in rows if r['status']=='ACCEPTED']
        ck(S['accepted']==actual_accepted,'accepted summary derived from rows')
        ck(S['run_status']=='COMPLETE' and len(actual_accepted)==len(ids),'complete accepted run')
        for k in ['rejected','blocked','errored','missing_cases','stage_failures']:ck(S[k]==[],'empty '+k+' for accepted run')
        ck(S['rows_file']=='ROWS.jsonl' and S['diagnostics_file']=='DIAGNOSTICS.jsonl' and S['basis_file']=='BASIS.json' and S['models_file']=='MODELS.json' and S['geometry_file']=='GEOMETRY.json','summary file references')
        expected_models={f'discovery_B{b:+.2f}' for b in E['plan']['B_values']}|{'model_'+i for i in ids}
        ck(set(models)==expected_models,'model inventory')
        for mid,m in models.items():
            ck(m['defaults']==E['model_defaults'],'constructor defaults '+mid)
            ck(m['basis']=='BASIS.json' and m['dim']==4*basis['vectors'],'basis binding '+mid)
            ck(m['active_constants']=={'HBARV_meV_angstrom':E['HBARV_meV_angstrom']},'active constant '+mid)
            ck(m['harmonic']==dict(E['harmonic'],amplitude=m['B']),'harmonic binding '+mid)
        expected_geometry={f"geom_B{c['B']:+.2f}_r{c['radius']:.3f}" for c in cases}
        ck(set(geoms)==expected_geometry,'geometry inventory')
        offset=0;case_by_id={c['case_id']:c for c in cases};P=E['policy']
        for r in rows:
            cid=r['case_id']
            if cid not in case_by_id:ck(False,'undeclared row '+cid);continue
            c=case_by_id[cid]
            ck(r['status']=='ACCEPTED' and r['gate_status']=='PASSED_SAMPLED_GATES','accepted gate status '+cid)
            ck(all(r[k]==v for k,v in c.items()),'case parameters '+cid)
            ck(r['model_ref']=='model_'+cid,'row model reference '+cid)
            m=models[r['model_ref']]
            ck(m['B']==c['B'] and m['valley']==c['valley'],'model knob/valley '+cid)
            gid=f"geom_B{c['B']:+.2f}_r{c['radius']:.3f}"
            side='K' if c['valley']==1 else 'Kprime'
            ck(r['geometry_ref']==gid and r['geometry_side']==side,'geometry reference '+cid)
            group=geoms[gid];g=group[side];n,nt=c['loop_intervals'],c['transport_intervals']
            ck(group['coupled_setting']=={k:c[k] for k in ['radius','loop_intervals','transport_intervals']},'geometry setting '+cid)
            ck(g['coordinate_policy']=='unwrapped' and g['periodic_translation']==[0,0] and g['radius']==c['radius'],'coordinate policy '+cid)
            ck(np.asarray(g['nodes']).shape==(2,2) and np.asarray(g['loops']).shape==(2,n+1,2) and np.asarray(g['transport']).shape==(nt+1,2),'geometry dimensions '+cid)
            ck(same(g['transport'][0],g['loops'][0][0]) and same(g['transport'][-1],g['loops'][1][0]) and all(same(x[0],x[-1]) for x in g['loops']),'exact loop/transport endpoints '+cid)
            for key in ['nodes','loops','transport']:ck(same(group['K'][key],-np.asarray(group['Kprime'][key])),'exact mirror '+cid+' '+key)
            ck(r['policy']==P,'row policy '+cid)
            lo=m['dim']//2-1;ck(r['lo']==lo,'absolute pair '+cid)
            address=r['diagnostics'];count=2*nt+8*n+7
            ck(address==dict(file='DIAGNOSTICS.jsonl',first_line=offset,count=count),'contiguous complete diagnostics slice '+cid)
            selected=diags[address['first_line']:address['first_line']+address['count']];offset+=address['count']
            ck(len(selected)==count and all(x['case']==cid and x['model']==cid for x in selected),'diagnostic count and identity '+cid)
            signatures=[('frame','node:0',None),('frame','node:1',None),('frame','transport:0',None)]
            for j in range(1,nt+1):signatures.extend([('frame',f'transport:{j}',None),('link',f'transport:{j}',None)])
            for i in range(2):
                signatures.extend(('frame',f'loop:{i}:point:{j}',None) for j in range(n+1));signatures.append(('link',f'loop:{i}:base',None))
                for j in range(1,n+1):signatures.extend([('link',f'loop:{i}:pair:{j}',None),('link',f'loop:{i}:band:{j}',None),('angle',f'loop:{i}',j)])
            ck([(x['kind'],x['where'],x.get('point')) for x in selected]==signatures,'diagnostic role/order/completeness '+cid)
            gaps=[];exts=[];internal=[];links=[];steps=[[],[]]
            for x in selected:
                if x['kind']=='frame':
                    parts=x['where'].split(':')
                    if parts[0]=='node':f=g['nodes'][int(parts[1])]
                    elif parts[0]=='transport':f=g['transport'][int(parts[1])]
                    else:f=g['loops'][int(parts[1])][int(parts[3])]
                    ck(same(x['f'],f),'exact frame role coordinate '+cid+' '+x['where'])
                    w=x['energies_meV'];ck(x['lo']==lo and x['n']==2 and x['first_band']==lo-1 and len(w)==4,'frame absolute bands '+cid+' '+x['where'])
                    ck(np.isfinite(w).all() and np.all(np.diff(w)>=0),'finite ordered energies '+cid+' '+x['where'])
                    lower,upper=w[1]-w[0],w[3]-w[2];ext=min(lower,upper);gap=w[2]-w[1]
                    ck(x['lower_external_gap_meV']==lower and x['upper_external_gap_meV']==upper and x['external_gap_meV']==ext and x['external_status']=='CHECKED','reconstructed external gaps '+cid+' '+x['where'])
                    ck(ext>=P['external_gap_meV'] and 0<=x['reality_meV']<=P['reality_meV'] and 0<=x['hermiticity_meV']<=P['hermiticity_meV'],'frame scalar gates '+cid+' '+x['where'])
                    exts.append(ext)
                    if parts[0]=='node':gaps.append(gap);ck(gap<=P['root_gap_meV'],'root gate '+cid)
                    elif parts[0]=='loop':internal.append(gap);ck(gap>=P['internal_gap_meV'],'loop splitting gate '+cid)
                elif x['kind']=='link':
                    sv=x['singular_values'];low=min(sv);links.append(low)
                    ck(len(sv)==(1 if ':band:' in x['where'] else 2) and np.isfinite(sv).all() and max(sv)<=1+1e-9 and low==x['min_overlap'] and low>=P['overlap_min'],'link scalar gate '+cid+' '+x['where'])
                    ck(x['sewing'] is False and x['sewing_loss'] is None and abs(abs(x['polar_det'])-1)<1e-9,'link metadata '+cid+' '+x['where'])
                elif x['kind']=='angle':
                    ck(np.isfinite(x['angle_rad']) and abs(x['step_rad'])<=P['phase_step_max_rad'],'angle scalar gate '+cid+' '+str(x['point']))
                    steps[int(x['where'].split(':')[1])].append(x['step_rad'])
            winds=[sum(st)/np.pi for st in steps]
            ck(len(gaps)==2 and same(gaps,r['node_gaps_meV']),'reconstructed node gaps '+cid)
            ck(len(r['windings'])==2 and np.max(np.abs(np.asarray(winds)-r['windings']))<1e-12,'reconstructed winding sums '+cid)
            ck(all(abs(abs(w)-1)<=P['unit_winding_tol'] for w in winds),'unit winding gate '+cid)
            label='SAME' if winds[0]*winds[1]>0 else 'OPPOSITE'
            ck(r['label']==label,'label from winding product '+cid)
            metrics.append(dict(case_id=cid,label=label,windings=winds,max_root_gap_meV=max(gaps),min_external_gap_meV=min(exts),min_loop_gap_meV=min(internal),min_overlap=min(links),max_phase_step_rad=max(abs(v) for st in steps for v in st)))
        ck(offset==len(diags),'no unclaimed diagnostics')
    except (KeyError,ValueError,TypeError,IndexError,OSError) as e:
        errors.append('Malformed or incomplete evidence: '+type(e).__name__+': '+str(e))
    return dict(accepted=not errors,checks=checks,errors=errors,metrics=metrics,scope='Scalar record consistency for the eight fixed cases; no independent eigensolve or physical validation')

if __name__=='__main__':
    result=check_records(sys.argv[1],sys.argv[2])
    if len(sys.argv)>3:Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(accepted=result['accepted'],checks=result['checks'],errors=result['errors'][:12]),indent=2))
    raise SystemExit(0 if result['accepted'] else 1)
