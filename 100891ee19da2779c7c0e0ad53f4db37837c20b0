"""Controlled historical recipe comparison, not a new scientific acceptance gate.

Only BM.refine changes. Retained v041/v042 Hamiltonian uses kinetic='none'.
Read-reviewed function definitions are extracted without running old script bodies.
"""
import argparse,ast,hashlib,json,time
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.linalg import eigh
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def plain(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [plain(v) for v in x]
    return x
def save(path,r):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(plain(r),indent=2,allow_nan=False)+'\n');tmp.replace(path)
def definitions(path,names,namespace):
    tree=ast.parse(path.read_text());selected=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
    if {n.name for n in selected}!=set(names):raise ValueError('missing reviewed definition')
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace)

def run(variant):
    if not __debug__:raise ValueError('historical success assertion requires normal Python mode')
    path=ROOT/'results'/f'legacy_{variant}.json'
    if path.exists():raise ValueError('refusing to overwrite impact record')
    plan=json.loads((ROOT/'IMPACT_PLAN.json').read_text())
    for name,h in plan['inputs'].items():
        if sha(REPO/name)!=h:raise ValueError('frozen impact input changed: '+name)
    if sha(ROOT/'legacy_impact.py')!=plan['runner_sha256']:raise ValueError('impact runner changed')
    index=json.loads((ROOT/'SOURCE_INDEX.json').read_text());old=REPO/index['batches']['v042'];partner=REPO/index['partner']
    ns={'__name__':'reviewed_legacy_engine','np':np,'eigh':eigh}
    exec(compile((old/'engines/bm_strain.py').read_text(),str(old/'engines/bm_strain.py'),'exec'),ns)
    definitions(partner/'gate.py',['GateError','real_basis','real_frame_checked','ortho_checked','classify'],ns)
    ns.update(REAL_TOL=1e-9,WIND_TOL=.15,COND_TOL=1e-6,ortho=ns['ortho_checked'])
    definitions(partner/'final_check.py',['frame','winding','transport2'],ns)
    definitions(old/'engines/knobs.py',['add_harmonic'],ns)
    definitions(partner/'gated_rerun.py',['pair'],ns)
    # Append a diagnostic return to the otherwise unchanged historical pair body.
    pair=next(n for n in ast.parse((partner/'gated_rerun.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='pair')
    pair.body.append(ast.parse("return dict(nodes=[a,b], values=[va,vb], metadata=[ia,ib], windings=[wa,wb], label=classify(wa,wb))").body[0])
    tree=ast.fix_missing_locations(ast.Module(body=[pair],type_ignores=[]));exec(compile(tree,'historical_pair_with_diagnostic_return','exec'),ns)
    if variant=='repaired':
        tr=ast.parse((REPO/'research/v055/engines/bm_strain.py').read_text())
        cls=next(n for n in tr.body if isinstance(n,ast.ClassDef) and n.name=='BM')
        fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='refine')
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'v055_refine_only','exec'),ns);ns['BM'].refine=ns['refine']
    attempts=[]
    def observed_minimize(fun,x0,*args,**kwargs):
        result=minimize(fun,x0,*args,**kwargs)
        attempts.append(dict(seed=np.asarray(x0).tolist(),x=result.x.tolist(),value=float(result.fun),success=bool(result.success),status=int(result.status),message=str(result.message),nfev=int(result.nfev)))
        return result
    ns['minimize']=observed_minimize
    original=ns['BM'].refine;calls=[]
    def observed_refine(self,seed,func,*args,**kwargs):
        start=len(attempts);answer=original(self,seed,func,*args,**kwargs)
        trials=attempts[start:];calls.append(dict(seed=np.asarray(seed).tolist(),attempts=trials,returned_coordinate=np.asarray(answer[0]).tolist(),returned_value=float(answer[1]),recomputed_value=float(func(answer[0])),reported_metadata=plain(self.last_refine),final_optimizer_success=trials[-1]['success']))
        return answer
    ns['BM'].refine=observed_refine
    r=dict(status='RUNNING',scope='five historical charge recipes; controlled helper-only impact comparison',variant=variant,kinetic='none',N=4,engine_snapshot='v041 engines retained in v042',impact_plan_sha256=sha(ROOT/'IMPACT_PLAN.json'),cases=[])
    save(path,r);start=time.time()
    for recipe in plan['recipes']:
        p=recipe['state'];m=ns['BM'](N=4,eps=.003,phi_deg=p['phi'],A_scalar=p['A'],ratio=p['ratio'],kinetic='none')
        ns['add_harmonic'](m,p['B'],mat=ns['sz'],use_sin=True)
        ns['add_harmonic'](m,p['T'],mat=ns['sz'],use_sin=True,layer_sign=-1)
        U=ns['real_basis'](m.nG);begin=len(calls)
        row=dict(recipe=recipe['name'],state=p,model_dimension=m.dim,Hstat_sha256=hashlib.sha256(m.Hstat.tobytes()).hexdigest())
        try:
            measured=ns['pair'](m,U,np.array(recipe['seeds'][0]),np.array(recipe['seeds'][1]),m.dim//2+recipe['lo_offset'],recipe['radius'],recipe['name'])
            row.update(status='RECIPE_COMPLETED',measurement=measured)
        except Exception as error:row.update(status='RECIPE_REJECTED',error=type(error).__name()+': '+str(error))
        row['refine_calls']=calls[begin:];r['cases'].append(row);save(path,r)
        print(variant,recipe['name'],row['status'],flush=True)
    r.update(status='COMPLETE',seconds=time.time()-start);save(path,r)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--variant',choices=['defective','repaired'],required=True);run(p.parse_args().variant)
