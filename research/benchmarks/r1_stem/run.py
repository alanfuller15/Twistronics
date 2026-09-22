"""Retain every subdivision and isolate one tracked-node crossing per stem."""
import json
import platform
import time
import traceback
import numpy as np
import scipy
from scipy.linalg import eigh
from crossing import ROOT, PLAN, T, CFG, sha, load, Family, model, solve, center_data, certificate, identity, stem, geometry, interval_newton

def main():
    dest=ROOT/'RESULTS.json'
    if dest.exists() or (ROOT/'FRAMES.npz').exists():raise SystemExit('Refusing overwrite of retained crossing evidence')
    controls=json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and controls['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in controls['source_hashes'].items())
    cont,cases,sources=load()
    sources.update({str((ROOT/n).relative_to(ROOT.parent)):sha(ROOT/n) for n in ['PLAN.json','crossing.py','controls.py','CONTROLS.json','run.py']})
    out={'status':'RUNNING','plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':sources,'centers':{},'cases':[],'errors':[],
         'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'blas_threads':1}}
    frames={};start=time.perf_counter()
    def save():
        np.savez_compressed(ROOT/'FRAMES.npz',**frames)
        out['frames_sha256']=sha(ROOT/'FRAMES.npz')
        dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    save()
    try:
        for engine in PLAN['engines']:
            family=Family(engine)
            def fresh(D,parent):
                key=f'{engine}_{D:.14f}'
                if key in out['centers']:return key,out['centers'][key]
                old=cont['centers'][parent['center']]['raw']
                seed=np.array(old['y'][:2])+(D-old['D_meV'])*np.array(old['velocity'][:2])
                result=solve(family,D,298,seed,box=[np.maximum(seed-.02,0),np.minimum(seed+.02,1)])
                rec={'engine':engine,'D_meV':D,'root':result,'pass':False};out['centers'][key]=rec
                if not result['accepted']:return key,rec
                raw,F=center_data(family,D,298,result['f']);frames[key]=F
                native=model(engine,8,D).H(family.k(np.array(result['f'])))
                error=float(np.max(abs(family.U.conj().T@native@family.U-family.H([*result['f'],D]))))
                nw=eigh(native,eigvals_only=True,subset_by_index=(297,300))
                se=float(max(abs(nw-raw['w4'])))
                rec.update(raw=raw,native={'matrix_error_meV':error,'w4':nw.tolist(),'spectrum_error_meV':se})
                rec['pass']=bool(error<=CFG['matrix_tolerance_meV'] and se<=CFG['native_spectrum_tolerance_meV'] and nw[2]-nw[1]<=CFG['native_spectrum_tolerance_meV'] and raw['inertia_correct'])
                return key,rec

            for case in [c for c in cases if c['engine']==engine]:
                name=f"{engine}_{case['mesh']}_{case['radius']:g}"
                result={'name':name,'engine':engine,'mesh':case['mesh'],'radius':case['radius'],'attempts':[],'leaf_ids':[],'points':[],'event_steps':[],'pass':False}
                out['cases'].append(result)
                window=PLAN['event_window_meV'];path=case['paths']['upper']
                def parent_at(a,b):return next(p for p in path if p['a']<=a and b<=p['b'])
                def visit(a,b,parent,depth=0,pid=None):
                    old=cont['centers'][parent['center']]['raw']
                    if depth==0:
                        key=parent['center'];raw=old;cert=parent['certificate'];link={'pass':True,'reused_parent':True};origin='inherited'
                    else:
                        key,rec=fresh((a+b)/2,parent);origin='new'
                        raw=rec.get('raw');cert=certificate(raw,(b-a)/2) if rec['pass'] else {'pass':False}
                        link=identity(raw,cert,old,parent['certificate'],a,b) if raw is not None else {'pass':False}
                    ends,vel=stem(case,a,b)
                    g=geometry(raw,cert,ends,vel,a,b) if raw is not None and cert['pass'] and link['pass'] else {'pass':False}
                    inside=a>=window[0] and b<=window[1]
                    ok=bool(g['pass'] and (g['slope_bounds'][1]<-T['strict_slope_margin'] and g['along_bounds'][0]>T['segment_interior_margin'] and g['along_bounds'][1]<1-T['segment_interior_margin'] if inside else g['side_bounds'][0]>T['strict_side_margin'] or g['side_bounds'][1]<-T['strict_side_margin']))
                    i=len(result['attempts']);r={'id':i,'parent':pid,'a':a,'b':b,'depth':depth,'inherited_tube':parent['id'],'center':key,'origin':origin,'certificate':cert,'identity':link,'geometry':g,'region':'event_window' if inside else 'outside','pass':ok,'children':[]}
                    result['attempts'].append(r)
                    if ok or depth>=PLAN['maximum_depth']:result['leaf_ids'].append(i)
                    else:
                        m=(a+b)/2;r['children']=[visit(a,m,parent,depth+1,i),visit(m,b,parent,depth+1,i)]
                    return i
                cuts=sorted(set([38.,39.,*window]+[g['D_meV'] for g in case['geometry']]+[v for p in path for v in [p['a'],p['b']]]))
                for a,b in zip(cuts[:-1],cuts[1:]):visit(a,b,parent_at(a,b))
                leaves=[result['attempts'][i] for i in result['leaf_ids']]
                result['unresolved_leaves']=sum(not r['pass'] for r in leaves)
                def point(D):
                    parent=parent_at(D,D);key,rec=fresh(D,parent)
                    cert=certificate(rec['raw'],0) if rec['pass'] else {'pass':False}
                    link=identity(rec.get('raw'),cert,cont['centers'][parent['center']]['raw'],parent['certificate'],D,D) if rec['pass'] else {'pass':False}
                    ends,vel=stem(case,D,D)
                    g=geometry(rec['raw'],cert,ends,vel,D,D) if rec['pass'] and cert['pass'] and link['pass'] else {'pass':False}
                    p={'D_meV':D,'center':key,'inherited_tube':parent['id'],'certificate':cert,'identity':link,'geometry':g,'pass':bool(g['pass'])}
                    result['points'].append(p);return p
                left,right=[point(D) for D in window]
                event_leaves=[r for r in leaves if r['region']=='event_window']
                slope=[min(r['geometry']['slope_bounds'][0] for r in event_leaves if r['geometry']['pass']),max(r['geometry']['slope_bounds'][1] for r in event_leaves if r['geometry']['pass'])]
                result['event_slope_bounds']=slope
                existence=left['pass'] and right['pass'] and left['geometry']['side_bounds'][0]>T['strict_side_margin'] and right['geometry']['side_bounds'][1]<-T['strict_side_margin']
                result['one_transverse_crossing']=bool(existence and result['unresolved_leaves']==0)
                interval=list(window)
                if result['one_transverse_crossing']:
                    for k in range(PLAN['maximum_event_steps']):
                        if interval[1]-interval[0]<=PLAN['target_event_width_meV']:break
                        mid=sum(interval)/2;p=point(mid)
                        step=interval_newton(*interval,mid,p['geometry']['side_bounds'],slope) if p['pass'] else {'pass':False}
                        result['event_steps'].append({'before':interval.copy(),'point_index':len(result['points'])-1,**step})
                        if not step['pass']:break
                        oldwidth=interval[1]-interval[0];interval=step['interval']
                        if interval[1]-interval[0]>=oldwidth:break
                result['event_interval_meV']=interval;result['event_width_meV']=interval[1]-interval[0]
                result['pass']=bool(result['one_transverse_crossing'] and result['event_width_meV']<=PLAN['target_event_width_meV'] and all(p['pass'] for p in result['points']) and all(s['pass'] for s in result['event_steps']))
                save();print(name,'attempts',len(result['attempts']),'leaves',len(leaves),'unresolved',result['unresolved_leaves'],'event',interval,'pass',result['pass'],'seconds',round(time.perf_counter()-start,1),flush=True)
        out['status']='CONDITIONAL_UNIQUE_TRACKED_NODE_STEM_CROSSING_PASS' if all(c['pass'] for c in out['cases']) else 'UNRESOLVED_STEM_CROSSING_RETAINED'
    except Exception:
        out['errors'].append(traceback.format_exc());out['status']='UNRESOLVED_STEM_CROSSING_RETAINED';print(out['errors'][-1],flush=True)
    save();print('STATUS',out['status'],'new centers',len(out['centers']),flush=True)
    return 0 if out['status']=='CONDITIONAL_UNIQUE_TRACKED_NODE_STEM_CROSSING_PASS' else 1

if __name__=='__main__':raise SystemExit(main())
