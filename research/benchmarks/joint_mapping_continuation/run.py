"""Frozen two-engine local event-branch continuation; failed cells are retained."""
import hashlib,json,platform,time,traceback
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq
from deformation import ROOT,PLAN,CFG,model,make_family
from coupled import center_data,certificate,containment

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    dest=ROOT/'RESULTS.json'
    if dest.exists():raise FileExistsError('refusing overwrite of retained continuation results')
    controls=json.loads((ROOT/'CONTROLS.json').read_text());assert controls['all_controls_pass']
    assert all(sha(ROOT/n)==h for n,h in controls['source_hashes'].items())
    parent_path=ROOT.parent/'joint_mapping_guarded/RESULTS.json';parent=json.loads(parent_path.read_text())
    assert parent['status']=='SAMPLED_COMMON_BASIS_CHECKS_COMPLETED'
    parent_rows=[next(r for r in parent['rows'] if r['station']==i and r['mode']=='union' and r['engine']=='bm') for i in (0,1)]
    ss=PLAN['strain_interval'];seedpoints=[]
    for r in parent_rows:
        e=r['result']['event'];seedpoints.append(dict(D=e['D_meV'],f=np.array([*e['seeds']['flat'],e['seeds']['node']])))
    sources=model.sources()
    for n in ['PLAN.json','deformation.py','coupled.py','controls.py','CONTROLS.json','run.py']:
        sources['joint_mapping_continuation/'+n]=sha(ROOT/n)
    for n in ['BASIS.json','RESULTS.json','SUMMARY.json']:
        sources['joint_mapping_guarded/'+n]=sha(ROOT.parent/'joint_mapping_guarded'/n)
    out=dict(status='RUNNING',source_hashes=sources,centers={},campaigns=[],errors=[],
             runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,blas_threads=1),scope=PLAN['scope'])
    frames={};cache={};family_cache={};start=time.perf_counter()
    def save():
        out['seconds']=time.perf_counter()-start
        dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
        np.savez_compressed(ROOT/'FRAMES.npz',**frames)
    save()
    for engine in PLAN['engines']:
        engine_count=0
        def get_center(s):
            nonlocal engine_count
            cachekey=(engine,float(s).hex())
            if cachekey in cache:return cache[cachekey]
            key=engine+'_'+str(engine_count);engine_count+=1;cache[cachekey]=key
            row=dict(engine=engine,s=float(s),pass_check=False,locator=None,native=[],raw=None)
            out['centers'][key]=row
            if engine_count>PLAN['max_unique_centers_per_engine']:
                row['reason']='center_budget_exhausted';return key
            t=(s-ss[0])/(ss[1]-ss[0]);D=(1-t)*seedpoints[0]['D']+t*seedpoints[1]['D']
            f=(1-t)*seedpoints[0]['f']+t*seedpoints[1]['f'];seeds=dict(flat=f[:2].tolist(),node=f[2].tolist(),gap='upper')
            a=D-PLAN['locator']['D_bracket_halfwidth_meV'];b=D+PLAN['locator']['D_bracket_halfwidth_meV']
            loc=dict(bracket=[a,b],seed=seeds,measurements=[],event=None,cost=0);row['locator']=loc
            try:
                family=make_family(engine,s,D);family_cache[key]=family
                measures={}
                def measure(d):
                    d=float(d)
                    if d not in measures:
                        m=model.measure(dict(family.x,D=d),seeds,family.cfg,family)
                        measures[d]=m;loc['measurements'].append(dict(D=d,result=m));loc['cost']+=m['cost']
                    return measures[d]
                def residual(d):
                    m=measure(d)
                    if not m['ok'] or not CFG['segment_margin']<m['t']<1-CFG['segment_margin']:
                        raise ValueError('locator_measurement_rejected')
                    return m['offset']
                left,right=residual(a),residual(b)
                if left*right>=0:raise ValueError('no_locator_sign_bracket')
                d=float(brentq(residual,a,b,xtol=PLAN['locator']['D_xtol_meV'],maxiter=PLAN['locator']['max_iterations']))
                final=measure(d)
                if abs(final['offset'])>PLAN['locator']['event_offset_tolerance']:raise ValueError('locator_residual_rejected')
                roots=[r['f'] for r in final['roots']];loc['event']=dict(D=d,offset=final['offset'],roots=roots)
                raw,F=center_data([family]*3,s,d,roots)
                row['raw']=raw
                for k in range(3):
                    frames[key+'_'+str(k)]=F[k]
                    native=family.native_check(d,np.array(roots[k]),raw['pairs'][k]['lo']);row['native'].append(native)
                row['pass_check']=bool(all(n['ok'] for n in row['native']) and all(p['inertia_correct'] for p in raw['pairs']))
                row['reason']='center_accepted' if row['pass_check'] else 'native_or_inertia_check'
            except Exception:
                row.update(reason='center_exception',error=traceback.format_exc())
            if engine_count%8==0:print('CENTER',engine,engine_count,'seconds',round(time.perf_counter()-start,1),flush=True)
            return key
        def bound(key,h):
            row=out['centers'][key]
            if not row['pass_check']:return dict(pass_check=False,reason=row['reason'])
            raw=row['raw'];family=family_cache[key]
            rem=[family.remainder_bounds(raw['y'][3*k:3*k+2],raw['velocity'][3*k:3*k+3],h) for k in range(3)]
            return certificate(raw,h,rem)
        for initial in PLAN['initial_intervals']:
            campaign=dict(engine=engine,initial_intervals=initial,attempts=[],leaf_ids=[],points={},joins=[])
            out['campaigns'].append(campaign)
            def visit(a,b,depth,parent_id=None):
                key=get_center((a+b)/2);cert=bound(key,(b-a)/2);idx=len(campaign['attempts'])
                rec=dict(id=idx,a=float(a),b=float(b),depth=depth,parent=parent_id,center=key,certificate=cert,children=[])
                campaign['attempts'].append(rec)
                if cert['pass_check'] or depth>=PLAN['max_bisection_depth']:
                    campaign['leaf_ids'].append(idx)
                else:
                    mid=(a+b)/2
                    for l,r in [(a,mid),(mid,b)]:rec['children'].append(visit(l,r,depth+1,idx))
                return idx
            grid=np.linspace(*ss,initial+1)
            for a,b in zip(grid[:-1],grid[1:]):visit(float(a),float(b),0);save()
            for idx in campaign['leaf_ids']:
                leaf=campaign['attempts'][idx]
                if not leaf['certificate']['pass_check']:continue
                for s in [leaf['a'],leaf['b']]:
                    key=get_center(s)
                    if key not in campaign['points']:campaign['points'][key]=bound(key,0)
                    point=out['centers'][key];pc=campaign['points'][key]
                    join=containment(point['raw'],pc,out['centers'][leaf['center']]['raw'],leaf['certificate'],s) if point['pass_check'] else dict(pass_check=False,reason=point['reason'])
                    campaign['joins'].append(dict(s=s,point=key,leaf=idx,check=join))
            campaign['pass_check']=bool(all(campaign['attempts'][i]['certificate']['pass_check'] for i in campaign['leaf_ids']) and
                                        all(j['check']['pass_check'] for j in campaign['joins']))
            save();print('CAMPAIGN',engine,initial,'leaves',len(campaign['leaf_ids']),'pass',campaign['pass_check'],'seconds',round(out['seconds'],1),flush=True)
        family_cache.clear()
    out['status']='CONDITIONAL_FIXED_BASIS_EVENT_BRANCH_PASS' if all(c['pass_check'] for c in out['campaigns']) else 'UNRESOLVED_CELLS_OR_JOINS_RETAINED'
    save();print('STATUS',out['status'],flush=True)

if __name__=='__main__':main()
