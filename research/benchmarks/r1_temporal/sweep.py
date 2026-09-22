"""Carried base frames and moving contour grids; no moving-face certificate."""
import argparse,json,time,traceback,platform
import numpy as np
import scipy
from scipy.linalg import eigh
from scipy.optimize import brentq
from transport import ROOT,PLAN,T,Family,Chart3,geometry,volume,route,join,align,charge,station_paths,array_points,edge,sha,multiply,inverse

def crossing_control(family,chart,stations,cfg):
    evaluations=[]
    def interp(D):
        j=max(0,min(len(stations)-2,int(np.searchsorted([s['D_meV'] for s in stations],D)-1)))
        a,b=stations[j:j+2];t=(D-a['D_meV'])/(b['D_meV']-a['D_meV'])
        return [(1-t)*np.array(x['f'])+t*np.array(y['f']) for x,y in zip(a['roots'],b['roots'])]
    def residual(D):
        p,q,seed=interp(D);r=family.solver(D).root(seed,'upper');assert r['accepted']
        e=(q-p)/np.linalg.norm(q-p);normal=np.array([-e[1],e[0]])
        offset=float((np.array(r['f'])-p)@normal)
        evaluations.append({'D_meV':float(D),'upper':r,'offset':offset})
        return offset
    D=float(brentq(residual,38.0625,38.125,xtol=1e-11));residual(D);root=evaluations[-1]['upper']
    p,q,_=interp(D);e=(q-p)/np.linalg.norm(q-p)
    vertices=[np.r_[p+.55*(q-p),D],np.r_[root['f'],D],np.r_[q-.003*e,D]]
    er,points=route(chart,vertices,cfg)
    passed=root['gap_meV']<T['root_gap_meV'] and abs(evaluations[-1]['offset'])<T['crossing_offset'] and not er['pass']
    return {'D_meV':D,'evaluations':evaluations,'nominal_stem':er,'accepted_charge':None,'required_rejection_pass':bool(passed)},points

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=PLAN['engines'],required=True);args=ap.parse_args()
    dest=ROOT/(args.engine.upper()+'.json');npz=dest.with_suffix('.npz')
    if dest.exists() or npz.exists():raise SystemExit('Refusing overwrite')
    control=json.loads((ROOT/'CONTROLS.json').read_text())
    assert control['all_controls_pass'] and control['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in control['sources'].items())
    parentpath=ROOT.parent/'r1_holonomy'/(args.engine.upper()+'.json');parent=json.loads(parentpath.read_text())
    priorpath=ROOT.parent/'r1_three_band'/(args.engine.upper()+'.json');prior=json.loads(priorpath.read_text())
    sources={ROOT/n for n in ['transport.py','sweep.py','controls.py','CONTROLS.json','survey.py','SURVEY.json']}
    sources.update([parentpath,priorpath]);sources.update(ROOT.parent/n for n in prior['source_hashes'])
    out={'status':'RUNNING','engine':args.engine,'N':8,'plan_sha256':sha(ROOT/'PLAN.json'),
         'sources':{str(p.relative_to(ROOT.parent)):sha(p) for p in sorted(sources)},
         'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
         'volumes':[],'base_transports':[],'stations':[],'temporal_edges':[],'endpoint_comparisons':[],'errors':[]}
    arrays={}
    def save():
        dest.write_text(json.dumps(out,indent=2)+'\n')
        if arrays:np.savez_compressed(npz,**arrays)
    save()
    try:
        family=Family(args.engine);fine=parent['tracks']['16']['stations'];allvertices=[]
        for s in fine:
            for r in PLAN['radii']:
                g=geometry(s,r,128);allvertices.extend([g['base'],g['kink'],*g['ring']])
        bounds=np.array([np.min(allvertices,axis=0),np.max(allvertices,axis=0)]);bounds[0,:2]-=1e-8;bounds[1,:2]+=1e-8
        reference=bounds.mean(axis=0);chart=Chart3(family,reference);arrays['reference_frame']=chart.B
        out.update(reference=reference.tolist(),bounds=bounds.tolist(),dimension=family.dim,affine_checks=family.checks)
        wn=eigh(family.models[38.5].H(family.k(reference[:2])),eigvals_only=True,subset_by_index=(family.lo-1,family.lo+3))
        native_error=float(np.max(np.abs(wn-chart.data(reference)['w'])));assert native_error<1e-8
        out['reference_native_spectrum_error_meV']=native_error
        carried={}
        for cfg in PLAN['mesh_levels']:
            name=cfg['name'];stations=parent['tracks'][str(cfg['track_intervals'])]['stations']
            start=time.time();vol=volume(chart,bounds,cfg['volume_grid']);vol.update(mesh=name,seconds=time.time()-start);out['volumes'].append(vol);save()
            print('VOLUME',args.engine,name,'pass',vol['pass'],'cells',len(vol['cells']),'gap',vol['minimum_gap_lower_meV'],'chart',vol['minimum_smin_lower'],flush=True)
            previous=None;previous_g={};seed=None
            for j,s in enumerate(stations):
                D=s['D_meV'];gbase=geometry(s,.003,cfg['polygon_edges']);base=gbase['base']
                if previous is None:
                    points=[chart.data(base)];seed=align(points)[0];ber={'pass':True,'initial':True,'vertices':[base.tolist()]}
                else:
                    ber,points=edge(chart,previous,base,cfg);seed=align(points,seed)[-1]
                carried[(name,j)]=seed.copy();arrays[f'{name}_base_{j}_carried']=seed
                array_points(arrays,f'{name}_base_{j}',points)
                out['base_transports'].append({'mesh':name,'station':j,'D_meV':D,'edge':ber});previous=base
                for radius in PLAN['radii']:
                    start=time.time();key=f'{name}_D{D}_r{radius}';g=geometry(s,radius,cfg['polygon_edges'])
                    pr,stem,circle=station_paths(chart,g,cfg);tp=join(stem,circle,list(reversed(stem)))
                    tq,tpath=charge(tp,seed)
                    valid=vol['pass'] and ber['pass'] and pr['pass'] and tq['valid']
                    tq['accepted_label']=tq['nearest_label'] if valid else None
                    out['stations'].append({'key':key,'mesh':name,'station':j,'D_meV':D,'radius':radius,'geometry':{k:v.tolist() for k,v in g.items()},
                                            'paths':pr,'charge':tq,'diagnostics_pass':bool(valid),'seconds':time.time()-start})
                    array_points(arrays,key+'_stem',stem);array_points(arrays,key+'_circle',circle);arrays[key+'_T_quaternion_path']=tpath
                    if radius in previous_g:
                        old=previous_g[radius];stride=cfg['polygon_edges']//cfg['temporal_circle_vertices']
                        left=[old['base'],old['kink'],*old['ring'][:-1:stride]];right=[g['base'],g['kink'],*g['ring'][:-1:stride]]
                        for col,(a,b) in enumerate(zip(left,right)):
                            er,ep=edge(chart,a,b,cfg);ekey=key+f'_temporal_{col}';array_points(arrays,ekey,ep)
                            out['temporal_edges'].append({'key':ekey,'mesh':name,'radius':radius,'station':j,'column':col,'edge':er})
                    previous_g[radius]=g
                    if j in [0,len(stations)-1]:
                        sr,sp=route(chart,[g['base'],g['ring'][0]],cfg,cfg['stem_subintervals'])
                        nominal=join(sp,circle,list(reversed(sp)));comparison=join(stem,list(reversed(sp)))
                        sq,sqpath=charge(nominal,seed);cq,cqpath=charge(comparison,seed)
                        direct=join(comparison,nominal,list(reversed(comparison)));dq,dqpath=charge(direct,seed)
                        predicted=multiply(multiply(cq['quaternion'],sq['quaternion']),inverse(cq['quaternion']))
                        product_error=float(np.max(np.abs(predicted-dq['quaternion'])));target_error=float(np.max(np.abs(np.array(dq['quaternion'])-tq['quaternion'])))
                        ok=valid and sr['pass'] and sq['valid'] and cq['valid'] and dq['valid'] and max(product_error,target_error)<T['cross_check_error']
                        out['endpoint_comparisons'].append({'key':key,'D_meV':D,'mesh':name,'radius':radius,'nominal_stem':sr,
                                                            'S':sq,'C':cq,'direct_CSC_inverse':dq,'product_error':product_error,'transported_charge_error':target_error,'pass':bool(ok)})
                        array_points(arrays,key+'_nominal_stem',sp)
                        for qname,path in [('S',sqpath),('C',cqpath),('CSC_inverse',dqpath)]:arrays[key+'_'+qname+'_quaternion_path']=path
                    save()
                    print('STATION',args.engine,name,D,radius,'T',tq['accepted_label'],'pass',valid,'temporal_pass',all(x['edge']['pass'] for x in out['temporal_edges']),'seconds',round(time.time()-start,1),flush=True)
        compare=[]
        for j in range(9):
            R=carried[('coarse',j)].T@carried[('fine',2*j)]
            compare.append({'D_meV':38+j/8,'matrix':R.tolist(),'max_identity_error':float(np.max(np.abs(R-np.eye(3)))),'pass':float(np.min(np.diag(R)))>=T['base_frame_overlap']})
        out['base_grid_comparisons']=compare
        out['charge_sequences']=[]
        for cfg in PLAN['mesh_levels']:
            for r in PLAN['radii']:
                rows=[s for s in out['stations'] if s['mesh']==cfg['name'] and s['radius']==r]
                labels=[s['charge']['accepted_label'] for s in rows]
                out['charge_sequences'].append({'mesh':cfg['name'],'radius':r,'labels':labels,'constant':None not in labels and len(set(labels))==1})
        out['crossing_control'],cp=crossing_control(family,chart,fine,PLAN['mesh_levels'][-1]);array_points(arrays,'crossing_control',cp)
        endpoints=out['endpoint_comparisons'];hypotheses=[]
        for cfg in PLAN['mesh_levels']:
            for r in PLAN['radii']:
                a,b=[x for x in endpoints if x['mesh']==cfg['name'] and x['radius']==r]
                flip=float(np.max(np.abs(np.array(a['S']['quaternion'])+b['S']['quaternion'])))
                hypotheses.append({'mesh':cfg['name'],'radius':r,'S_sign_flip_error':flip,'C_start':a['C']['conjugacy_class'],'C_end':b['C']['conjugacy_class'],
                                   'matches':flip<T['cross_check_error'] and a['C']['conjugacy_class']=='+1' and b['C']['conjugacy_class']=='+-i'})
        out['hypotheses']=hypotheses
        ok=(len(out['stations'])==52 and all(x['pass'] for x in out['volumes']) and all(x['edge']['pass'] for x in out['base_transports']+out['temporal_edges']) and
            all(x['diagnostics_pass'] for x in out['stations']) and all(x['pass'] for x in endpoints+compare) and out['crossing_control']['required_rejection_pass'])
        out['all_hypotheses_match']=all(h['matches'] for h in hypotheses) and all(s['constant'] for s in out['charge_sequences'])
        out['status']='GUARDED_TEMPORAL_GRID_AND_CONJUGATION_PASS_NOT_FULL_BRAID' if ok else 'UNRESOLVED_CHECKS_RETAINED'
    except Exception:
        out['status']='UNRESOLVED_CHECKS_RETAINED';out['errors'].append(traceback.format_exc());print(out['errors'][-1],flush=True)
    save();out['arrays_sha256']=sha(npz) if npz.exists() else None
    dest.write_text(json.dumps(out,indent=2)+'\n');print('STATUS',out['status'],flush=True)
    return 0 if out['status'].startswith('GUARDED_TEMPORAL_GRID_AND_CONJUGATION_PASS') else 1

if __name__=='__main__':raise SystemExit(main())
