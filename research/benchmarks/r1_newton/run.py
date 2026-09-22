"""Frozen sampled comparison, forced fallback and separately reported stress."""
import sys,json,time,platform,traceback
import numpy as np
import scipy
from scipy.linalg import eigh
from solver import ROOT,PLAN,DEFAULT,solve,sha
sys.path.insert(0,str(ROOT.parent/'r1_holonomy'))
from measure import Family
from track import model
V=PLAN['validation']
def baseline(family,D,seed,gap):
    old=family.solver(D);original=old.eig;calls=[0]
    def counted(f,vectors=False):calls[0]+=1;return original(f,vectors)
    old.eig=counted;t=time.perf_counter();r=old.root(seed,gap);seconds=time.perf_counter()-t
    return {'result':r,'eigensolves':calls[0],'seconds':seconds}
def timed_variant(family,D,lo,seed,**kw):
    t=time.perf_counter();r=solve(family,D,lo,seed,**kw);return {'result':r,'seconds':time.perf_counter()-t}
def native_check(m,family,D,lo,r):
    if r['f'] is None:return None
    f=np.array(r['f']);w=eigh(m.H(family.k(f)),eigvals_only=True,subset_by_index=(lo-1,lo+2));saved=np.array(r['history'][r['returned_evaluation']]['w'])
    return {'w':w.tolist(),'gap_meV':float(w[2]-w[1]),'spectrum_error_meV':float(np.max(np.abs(w-saved)))}
def main():
    dest=ROOT/'RESULTS.json'
    if dest.exists():raise SystemExit('Refusing overwrite')
    ctl=json.loads((ROOT/'CONTROLS.json').read_text());assert ctl['all_controls_pass'] and ctl['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in ctl['source_hashes'].items())
    sources=[ROOT/n for n in ['solver.py','run.py','controls.py','CONTROLS.json','partner_fast_engine.py','partner_engine_study.zip']]
    parent=json.loads((ROOT.parent/'r1_surface'/'SUMMARY.json').read_text());assert parent['all_surface_checks_pass']
    assert all(sha(ROOT.parent/'r1_surface'/n)==h for n,h in parent['source_hashes'].items())
    sources += [ROOT.parent/'r1_surface'/'SUMMARY.json']
    for engine in PLAN['engines']:
        for name in ['r1_holonomy','r1_n8']:
            p=ROOT.parent/name/(engine.upper()+'.json');d=json.loads(p.read_text());assert all(sha(ROOT.parent/n)==h for n,h in d['source_hashes'].items());sources.append(p)
            sources.extend(ROOT.parent/n for n in d['source_hashes'])
    out={'status':'RUNNING','plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{str(p.relative_to(ROOT.parent)):sha(p) for p in sorted(set(sources))},
         'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'blas_threads':1},'families':[],'primary':[],'forced_fallback':[],'stress':[],'errors':[]}
    def save():dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    save()
    try:
        for engine in PLAN['engines']:
            family=Family(engine);stations=json.loads((ROOT.parent/'r1_holonomy'/(engine.upper()+'.json')).read_text())['tracks']['16']['stations']
            fr={'engine':engine,'dimension':family.dim,'affine_checks':family.checks,'station_native_checks':[]};out['families'].append(fr)
            started=time.perf_counter()
            for j,s in enumerate(stations):
                D=s['D_meV'];m=model(engine,8,D);f=np.array([.71,.62]);direct=family.U.conj().T@m.H(family.k(f))@family.U
                error=float(np.max(np.abs(direct-family.H([*f,D]))));fr['station_native_checks'].append({'D_meV':D,'matrix_error_meV':error});assert error<V['matrix_error_max_meV']
                for k,name in enumerate(['p','q','upper']):
                    gap='upper' if name=='upper' else 'flat';lo=family.lo+(name=='upper');retained=np.array(s['roots'][k]['f'])
                    for mode in ['offset','carried']:
                        seed=retained+[.002,-.001] if mode=='offset' else np.array(stations[j-1]['roots'][k]['f']) if j else retained+[-.002,.001]
                        if len(out['primary'])%2:
                            new=timed_variant(family,D,lo,seed);old=baseline(family,D,seed,gap);order=['newton','reference']
                        else:
                            old=baseline(family,D,seed,gap);new=timed_variant(family,D,lo,seed);order=['reference','newton']
                        r=new['result'];native=native_check(m,family,D,lo,r)
                        distance=float(np.linalg.norm(np.array(r['f'])-old['result']['f'])) if r['f'] is not None else None
                        retained_distance=float(np.linalg.norm(np.array(r['f'])-retained)) if r['f'] is not None else None
                        ok=bool(r['accepted'] and old['result']['accepted'] and old['result']['gap_meV']<V['native_gap_max_meV'] and distance<V['root_distance_max'] and retained_distance<V['root_distance_max'] and native['gap_meV']<V['native_gap_max_meV'] and native['spectrum_error_meV']<V['native_spectrum_max_meV'])
                        out['primary'].append({'engine':engine,'station':j,'D_meV':D,'node':name,'seed_mode':mode,'seed':seed.tolist(),'retained_root':retained.tolist(),'order':order,'reference':old,'variant':new,'native':native,'root_distance':distance,'retained_root_distance':retained_distance,'pass':ok})
                save();print('STATION',engine,D,'cases',len(out['primary']),'pass',all(r['pass'] for r in out['primary']),'seconds',round(time.perf_counter()-started,1),flush=True)
            for k,name in enumerate(['p','q','upper']):
                seed=np.array(stations[0]['roots'][k]['f'])+[.002,-.001];lo=family.lo+(name=='upper');new=timed_variant(family,38.,lo,seed,config={'newton_iterations':0});r=new['result'];native=native_check(family.models[38.],family,38.,lo,r)
                distance=float(np.linalg.norm(np.array(r['f'])-stations[0]['roots'][k]['f'])) if r['f'] is not None else None
                ok=bool(r['accepted'] and r['fallback_attempted'] and r['method']=='bounded_least_squares' and distance<V['root_distance_max'] and native['gap_meV']<V['native_gap_max_meV'] and native['spectrum_error_meV']<V['native_spectrum_max_meV'])
                out['forced_fallback'].append({'engine':engine,'node':name,'variant':new,'native':native,'root_distance':distance,'pass':ok})
            merger=json.loads((ROOT.parent/'r1_n8'/(engine.upper()+'.json')).read_text());before=min(merger['sweeps']['forward'],key=lambda r:abs(r['D_meV']-40.38));assert abs(before['D_meV']-40.38)<1e-12 and len(before['roots'])==2
            stress=[(40.38,'pre_fold_'+str(i),np.array(r['f'])+[1e-4,-1e-4],np.array(r['f'])) for i,r in enumerate(before['roots'])]
            stress.append((40.40,'post_fold_search',np.array(merger['folds'][0]['f']),None))
            for D,name,seed,expected in stress:
                m=model(engine,8,D);native_matrix=family.U.conj().T@m.H(family.k(seed))@family.U;error=float(np.max(np.abs(native_matrix-family.H([*seed,D]))));assert error<V['matrix_error_max_meV']
                new=timed_variant(family,D,family.lo+1,seed,box=[[.765,.585],[.793,.632]]);r=new['result'];native=native_check(m,family,D,family.lo+1,r)
                distance=float(np.linalg.norm(np.array(r['f'])-expected)) if expected is not None and r['f'] is not None else None
                ok=bool((r['accepted'] and distance<V['root_distance_max']) if expected is not None else not r['accepted'])
                if r['accepted']:ok=ok and native['gap_meV']<V['native_gap_max_meV'] and native['spectrum_error_meV']<V['native_spectrum_max_meV']
                out['stress'].append({'engine':engine,'D_meV':D,'case':name,'affine_native_error_meV':error,'expected_root':expected.tolist() if expected is not None else None,'root_distance':distance,'variant':new,'native':native,'matches_expected_behavior':bool(ok),'scope':'Sampled solver behavior; a rejected search is not root absence.'})
                print('STRESS',engine,name,'accepted',r['accepted'],'method',r['method'],'reason',r['reason'],'gap',r['gap_meV'],flush=True)
            save()
        ok=len(out['primary'])==204 and all(r['pass'] for r in out['primary']) and len(out['forced_fallback'])==6 and all(r['pass'] for r in out['forced_fallback'])
        out['status']='SAMPLED_SOLVER_EQUIVALENCE_PASS' if ok else 'UNRESOLVED_COMPARISONS_RETAINED'
    except Exception:
        out['status']='UNRESOLVED_COMPARISONS_RETAINED';out['errors'].append(traceback.format_exc());print(out['errors'][-1],flush=True)
    save();print('STATUS',out['status'],flush=True)
    return 0 if out['status']=='SAMPLED_SOLVER_EQUIVALENCE_PASS' else 1
if __name__=='__main__':raise SystemExit(main())
