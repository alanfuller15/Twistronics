"""Two engines, two D slices, two radii, two mesh levels; retain all evidence."""
import argparse,json,traceback,platform,time
import numpy as np
import scipy
from scipy.linalg import eigh
from frame import ROOT,P,T,Family,Chart,rectangle,loop,words,sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=P['engines'],required=True);args=ap.parse_args()
    dest=ROOT/(args.engine.upper()+'.json');npz=dest.with_suffix('.npz')
    if dest.exists() or npz.exists():raise SystemExit('Refusing to overwrite evidence')
    control=json.loads((ROOT/'CONTROLS.json').read_text())
    assert control['all_controls_pass'] and control['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in control['source_hashes'].items())
    parentpath=ROOT.parent/'r1_holonomy'/(args.engine.upper()+'.json');parent=json.loads(parentpath.read_text())
    sources={ROOT/n for n in ['frame.py','sweep.py','controls.py','CONTROLS.json','FEASIBILITY.json']}
    sources.add(parentpath)
    sources.update(ROOT.parent/n for n in parent['source_hashes'])
    out={'status':'RUNNING','engine':args.engine,'N':P['N'],'plan_sha256':sha(ROOT/'PLAN.json'),
         'source_hashes':{str(n.relative_to(ROOT.parent)):sha(n) for n in sorted(sources)},
         'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
         'regions':[],'cases':[],'errors':[],'native_checks':[]}
    arrays={}
    def save():
        dest.write_text(json.dumps(out,indent=2)+'\n')
        if arrays:np.savez_compressed(npz,**arrays)
    save()
    try:
        fam=Family(args.engine);out['dimension']=fam.dim;out['affine_checks']=fam.checks
        assert fam.lo==P['bands_zero_based'][0]
        stations=parent['tracks']['16']['stations']
        for station in [stations[0],stations[-1]]:
            D=station['D_meV'];q=np.array(station['roots'][1]['f']);u=np.array(station['roots'][2]['f'])
            base=(q+u)/2+[0,.012];chart=Chart(fam,D,base)
            arrays[f'D{int(D)}_anchor']=chart.B
            bounds=np.array([np.minimum(np.minimum(q-.003,u-.003),base),np.maximum(np.maximum(q+.003,u+.003),base)])
            wn=eigh(fam.models[D].H(fam.k(base)),eigvals_only=True,subset_by_index=(fam.lo-1,fam.lo+3))
            wa=np.array(chart.data(base)['w']);err=float(np.max(np.abs(wn-wa)))
            out['native_checks'].append({'D_meV':D,'base_f':base.tolist(),'native_eigenvalues_meV':wn.tolist(),'affine_eigenvalues_meV':wa.tolist(),'error_meV':err,'pass':err<T['native_spectrum_meV']})
            for cfg in P['mesh_levels']:
                region=rectangle(chart,bounds,cfg['region_cells_per_axis'])
                region.update(D_meV=D,mesh=cfg['name']);out['regions'].append(region);save()
                print('REGION',args.engine,D,cfg['name'],'pass',region['pass'],'gap',region['minimum_exterior_lower_meV'],'chart',region['minimum_chart_smin_lower'],flush=True)
                for radius in P['radii']:
                    start=time.time();key=f'D{int(D)}_{cfg["name"]}_r{radius}'
                    A,a,pa=loop(chart,q,radius,cfg);B,b,pb=loop(chart,u,radius,cfg)
                    wr,paths=words(a,b)
                    valid=region['pass'] and A['diagnostics_pass'] and B['diagnostics_pass'] and all(x['valid'] for x in wr.values())
                    for name,w in wr.items():w['accepted_label']=w['nearest_label'] if valid else None
                    hypotheses=all(wr[name]['conjugacy_class']==P['hypotheses'][name+'_class'] for name in ['A','B','AB','BA']) and wr['commutator']['nearest_label']==P['hypotheses']['commutator']
                    out['cases'].append({'key':key,'D_meV':D,'mesh':cfg['name'],'radius':radius,'base_f':base.tolist(),
                                         'flat_q_root':station['roots'][1],'upper_root':station['roots'][2],
                                         'A':A,'B':B,'words':wr,'diagnostics_pass':bool(valid),'hypotheses_match':bool(hypotheses),
                                         'seconds':time.time()-start})
                    for name,samples in [('A',a),('B',b)]:
                        arrays[key+'_'+name+'_f']=np.array([s['f'] for s in samples])
                        arrays[key+'_'+name+'_Q']=np.array([s['Q'] for s in samples])
                        arrays[key+'_'+name+'_w']=np.array([s['w'] for s in samples])
                        arrays[key+'_'+name+'_smin']=np.array([s['smin'] for s in samples])
                    for name,path in paths.items():arrays[key+'_'+name+'_quaternion_path']=path
                    save()
                    print('CASE',args.engine,key,'pass',valid,'labels',{k:v['accepted_label'] for k,v in wr.items()},'points',len(a)+len(b),'seconds',round(time.time()-start,1),flush=True)
        comparisons=[]
        for D in P['D_meV']:
            cases=[c for c in out['cases'] if c['D_meV']==D]
            for name in ['A','B','AB','BA','commutator']:
                classes=[c['words'][name]['conjugacy_class'] for c in cases]
                comparisons.append({'D_meV':D,'word':name,'classes':classes,'pass':len(set(classes))==1})
        out['radius_mesh_comparisons']=comparisons
        ok=len(out['cases'])==8 and all(c['diagnostics_pass'] for c in out['cases']) and all(c['pass'] for c in comparisons+out['native_checks'])
        out['status']='LOCAL_THREE_BAND_DIAGNOSTICS_PASS_NOT_FULL_BRAID' if ok else 'UNRESOLVED_CHECKS_RETAINED'
        out['all_hypotheses_match']=all(c['hypotheses_match'] for c in out['cases'])
    except Exception:
        out['status']='UNRESOLVED_CHECKS_RETAINED';out['errors'].append(traceback.format_exc());print(out['errors'][-1],flush=True)
    if npz.exists():out['arrays_sha256']=sha(npz)
    dest.write_text(json.dumps(out,indent=2)+'\n')
    print('STATUS',out['status'],flush=True)
    return 0 if out['status'].startswith('LOCAL_THREE_BAND_DIAGNOSTICS_PASS') else 1

if __name__=='__main__':raise SystemExit(main())
