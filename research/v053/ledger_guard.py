"""Fail-closed acceptance checks for the generated coverage ledger."""
import json,math
from pathlib import Path

def finite(value):
    if isinstance(value,float) and not math.isfinite(value):raise ValueError('nonfinite ledger value')
    if isinstance(value,dict):
        for v in value.values():finite(v)
    elif isinstance(value,list):
        for v in value:finite(v)

def accepted(path):
    r=json.loads(Path(path).read_text());finite(r)
    if not isinstance(r,dict) or r.get('status')!='ACCEPT':raise ValueError('source lacks ACCEPT: '+str(path))
    return r

def grid(rows,cases=None):
    wanted={(e,n) for e in ['bm_lab','ref_lab'] for n in [4,6]}
    if cases is None:keys=[(r['engine'],r['N']) for r in rows]
    else:
        wanted={(c,e,n) for c in cases for e,n in wanted};keys=[(r['case'],r['engine'],r['N']) for r in rows]
    if len(set(keys))!=len(keys) or set(keys)!=wanted:raise ValueError('incomplete or duplicate engine/cutoff grid')

def kinetic(plan):
    tags=[plan['kinetic']] if 'kinetic' in plan else []
    engines=plan.get('engines',{})
    if isinstance(engines,dict):
        for p in engines.values():
            if isinstance(p,dict):tags.append(p.get('kinetic'))
            elif 'kinetic' not in plan:tags.append(None)
    if not tags or any(x!='lab_nn_full' for x in tags):raise ValueError('unexpected or absent kinetic tag')
