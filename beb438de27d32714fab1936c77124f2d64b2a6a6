"""Frozen controlled replays. No historical driver top-level bodies execute."""
import argparse,ast,hashlib,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize
from evidence import read,sha,require,safe,write
from test_evidence import runtime_identity
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]

def plain(x):
    if isinstance(x,np.ndarray):return plain(x.tolist())
    if isinstance(x,np.generic):return plain(x.item())
    if isinstance(x,dict):return {k:plain(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [plain(v) for v in x]
    if isinstance(x,float) and not np.isfinite(x):return {'nonfinite':str(x)}
    return x

def definitions(path,names,ns):
    tr=ast.parse(path.read_text());chosen=[n for n in tr.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
    require({n.name for n in chosen}==set(names),'missing reviewed definitions')
    exec(compile(ast.Module(body=chosen,type_ignores=[]),str(path),'exec'),ns)

def engine(plan,variant):
    ns={'__name__':'controlled_old_bm'};path=safe(REPO,plan['paths']['engine'])
    exec(compile(path.read_text(),str(path),'exec'),ns)
    if variant=='repaired':
        tree=ast.parse(safe(REPO,plan['paths']['repaired']).read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='BM')
        fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='refine')
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'repaired_refine_only','exec'),ns);ns['BM'].refine=ns['refine']
    definitions(safe(REPO,plan['paths']['knobs']),['add_harmonic'],ns)
    calls=[];attempts=[];stage=['initializing'];original=ns['BM'].refine
    def observed_minimize(fun,x0,*args,**kwargs):
        z=minimize(fun,x0,*args,**kwargs)
        attempts.append(dict(seed=plain(x0),x=plain(z.x),value=plain(float(z.fun)),success=bool(z.success),status=int(z.status),message=str(z.message),nfev=int(z.nfev)))
        return z
    ns['minimize']=observed_minimize
    def observed_refine(self,seed,func,*args,**kwargs):
        start=len(attempts);row=dict(stage=stage[0],seed=plain(seed),return_result=bool(kwargs.get('return_result',False)))
        try:
            result=original(self,seed,func,*args,**kwargs)
            row.update(status='RETURNED',coordinate=plain(result[0]),returned_value=plain(float(result[1])),recomputed_value=plain(float(func(result[0]))))
            return result
        except Exception as ex:
            row.update(status='RAISED',error=type(ex).__name()+': '+str(ex));raise
        finally:
            row.update(attempts=attempts[start:],metadata=plain(getattr(self,'last_refine',None)));calls.append(row)
    ns['BM'].refine=observed_refine
    return ns,calls,stage

def attempt(fn):
    try:return dict(status='COMPLETED',value=plain(fn()))
    except Exception as ex:return dict(status='REJECTED',error=type(ex).__name()+': '+str(ex))

def numerical_variant(plan,N,variant):
    ns,calls,stage=engine(plan,variant);m=ns['BM'](N=N,eps=.003,phi_deg=0,kinetic='none')
    r=dict(variant=variant,baseline_model_sha256=hashlib.sha256(m.Hstat.tobytes()).hexdigest(),baseline_dimension=m.dim)
    stage[0]='baseline_nodes';r['baseline_nodes']=attempt(lambda:m.find_nodes(ngrid=15,nkeep=6))
    stage[0]='baseline_remote';r['baseline_remote']=attempt(lambda:m.min_remote(ngrid=15,nkeep=4))
    stage[0]='baseline_bandwidth';r['baseline_bandwidth']=attempt(lambda:m.flat_bandwidth(12))
    m=ns['BM'](N=N,ratio=1.1,eps=.003,phi_deg=80,A_scalar=-.30,kinetic='none')
    ns['add_harmonic'](m,-.4,mat=ns['sz'],use_sin=True);ns['add_harmonic'](m,-1.8,mat=ns['sz'],use_sin=True,layer_sign=-1)
    r['endpoint_model_sha256']=hashlib.sha256(m.Hstat.tobytes()).hexdigest();r['endpoint_dimension']=m.dim
    def lower_search():
        # Exact lowergap_check recipe: both grids and every selected minimum.
        g=lambda f:(lambda w:w[2]-w[1])(m.bands_near_zero(m.frac_to_k(f),3))
        candidates=[];grid_records=[]
        for ng in [24,36]:
            fs,vals=m.grid(ng,g);seeds=m.local_minima(fs,vals,8)
            grid_records.append(dict(grid=ng,minimum=float(vals.min()),seeds=plain(seeds)))
            for value,a,b in seeds:
                f,val,info=m.refine(np.array([a,b]),g,return_result=True)
                candidates.append(dict(grid=ng,seed=[float(a),float(b)],coordinate=plain(f),value=float(val),recomputed_value=float(g(f)),metadata=plain(info),call_index=len(calls)-1))
        require(bool(candidates),'no endpoint candidates')
        best=min(candidates,key=lambda x:x['value'])
        return dict(best=best,grids=grid_records,candidates=candidates)
    stage[0]='endpoint_lower';r['endpoint_lower']=attempt(lower_search);r['refine_calls']=calls
    return r

def euler_probe(plan,N):
    ns,calls,stage=engine(plan,'defective');m=ns['BM'](N=N,eps=.003,phi_deg=0,kinetic='none')
    definitions(safe(REPO,plan['paths']['euler']),['shift_matrix','real_frame','euler'],ns)
    def raw():
        phases,dets,closure,wind=ns['euler'](m,24,40)
        return dict(mesh=[24,40],phases=plain(phases),determinants=plain(dets),closure=float(closure),winding=float(wind))
    result=dict(raw=attempt(raw),gated=[])
    gate={'np':np,'eigh':eigh};p=safe(REPO,plan['paths']['gate']);tree=ast.parse(p.read_text())
    policy=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POLICY' for t in n.targets))
    gate['POLICY']={x.arg:ast.literal_eval(x.value) for x in policy.keywords}
    definitions(p,['GateError','require','finite','checked_qr','orient','integer_charge','real_hamiltonian','spectrum','selected_frame','Measurement','euler_measurement'],gate)
    S1=ns['shift_matrix'](m,(-1,0));S2=ns['shift_matrix'](m,(0,-1))
    for nf1,nf2 in plan['euler_meshes']:
        def measured():
            me=gate['Measurement'](m)
            value=gate['euler_measurement'](me,m.dim//2-1,nf1,nf2,S1,S2)
            return dict(mesh=[nf1,nf2],measurement=value,metrics=me.metrics,points=len(me.cache))
        result['gated'].append(attempt(measured))
    result['refine_calls']=calls
    return result

def run(N):
    require(__debug__,'normal Python mode required for controlled legacy assertions')
    plan=read(ROOT/'NUMERICAL_PLAN.json');out=ROOT/'results'/f'probe_N{N}.json'
    require(N in plan['cutoffs'] and not out.exists(),'invalid cutoff or output already exists')
    for name,h in plan['runner_sha256'].items():require(sha(safe(ROOT,name))==h,'frozen runner changed')
    for name,h in plan['inputs'].items():require(sha(safe(REPO,name))==h,'frozen input changed')
    r=dict(schema=1,status='RUNNING',N=N,kinetic='none',plan_sha256=sha(ROOT/'NUMERICAL_PLAN.json'),started_utc=datetime.now(timezone.utc).isoformat(),runtime_before=runtime_identity(),variants=[])
    write(out,plain(r));start=time.time()
    for variant in ['defective','repaired']:
        r['variants'].append(numerical_variant(plan,N,variant));write(out,plain(r));print('N',N,variant,'complete',flush=True)
    r['euler']=euler_probe(plan,N);r.update(status='COMPLETE',seconds=time.time()-start,runtime_after=runtime_identity(),finished_utc=datetime.now(timezone.utc).isoformat())
    write(out,plain(r));print('N',N,'Euler complete; seconds',r['seconds'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--N',type=int,required=True);run(p.parse_args().N)
