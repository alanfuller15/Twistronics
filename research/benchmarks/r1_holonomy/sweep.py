"""N8 two-grid continuation and four closed-contour diagnostics per grid."""
import json,argparse,traceback,platform,time
import numpy as np
import scipy
from measure import ROOT,P,Family,sha,continue_nodes,static_vertices,ribbon_vertices,closed_loop

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--engine',choices=P['engines'],required=True)
    ap.add_argument('--output')
    args=ap.parse_args()
    dest=ROOT/(args.output or (args.engine.upper()+'.json'))
    framepath=dest.with_suffix('.npz')
    if dest.exists() or framepath.exists():raise SystemExit('Refusing overwrite')
    parentpath=ROOT.parent/'r1_sequence'/(args.engine.upper()+'.json')
    parent=json.loads(parentpath.read_text())
    controls=json.loads((ROOT/'CONTROLS.json').read_text())
    if not controls['all_controls_pass']:raise RuntimeError('Analytic controls did not pass')
    if controls['plan_sha256'] != sha(ROOT/'PLAN.json'):raise RuntimeError('Control plan changed')
    for name,digest in controls['source_hashes'].items():
        if sha(ROOT/name) != digest:raise RuntimeError('Control source changed: '+name)
    sources=[ROOT/'measure.py',ROOT/'sweep.py',ROOT/'controls.py',ROOT/'CONTROLS.json',parentpath]
    sources += [ROOT.parent/name for name in parent['source_hashes']]
    result={'status':'RUNNING','N':P['N'],'engine':args.engine,'plan_sha256':sha(ROOT/'PLAN.json'),
            'source_hashes':{str(p.relative_to(ROOT.parent)):sha(p) for p in sources},
            'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'tracks':{},'loops':[],'errors':[]}
    arrays={}
    def save():
        dest.write_text(json.dumps(result,indent=2)+'\n')
        if arrays:np.savez_compressed(framepath,**arrays)
    save()
    try:
        family=Family(args.engine)
        result.update(dimension=family.dim,affine_checks=family.checks)
        aligned={}
        for intervals in P['continuation_intervals']:
            name=str(intervals)
            result['tracks'][name]={'intervals':intervals,'stations':[]}
            def progress(rows):
                result['tracks'][name]['stations']=rows
                save()
            track,frames=continue_nodes(family,parent,intervals,progress)
            result['tracks'][name]=track;aligned[intervals]=frames
            for (j,n),F in frames.items():arrays[f'track_{intervals}_station_{j}_flat_{n}']=F
            save()
            print('TRACK',args.engine,intervals,'stations',len(track['stations']),'smin',track['minimum_temporal_step_smin'],flush=True)
        comparisons=[]
        coarse=result['tracks']['8']['stations'];fine=result['tracks']['16']['stations']
        for j,(a,b) in enumerate(zip(coarse,fine[::2])):
            differences=[float(np.linalg.norm(np.array(x['f'])-y['f'])) for x,y in zip(a['roots'],b['roots'])]
            determinants=[float(np.linalg.det(aligned[8][(j,n)].T@aligned[16][(2*j,n)])) for n in [0,1]]
            comparisons.append({'D_meV':a['D_meV'],'root_coordinate_differences':differences,'temporal_frame_determinants':determinants,
                                'pass':max(differences)<P['shared_root_match_tolerance'] and min(determinants)>P['coarse_fine_orientation_det']})
        result['continuation_comparisons']=comparisons
        result['endpoint_joins']=[]
        for D,j in [(38.,0),(39.,16)]:
            old=next(s for s in parent['matched_path_stations'] if s['D_meV']==D)
            diffs=[float(np.linalg.norm(np.array(r['f'])-s['f'])) for r,s in zip(fine[j]['roots'][:2],old['roots'])]
            result['endpoint_joins'].append({'D_meV':D,'flat_root_differences':diffs,'pass':max(diffs)<P['shared_root_match_tolerance']})
        save()
        for cfg in P['mesh_levels']:
            track=result['tracks'][str(cfg['continuation_intervals'])]
            paths={f'static_D{int(s["D_meV"])}':static_vertices(s,P['path_radius']) for s in parent['matched_path_stations']}
            paths['center_ribbon']=ribbon_vertices(track,np.array([0.,0.]))
            paths['shifted_ribbon']=ribbon_vertices(track,np.array([P['path_radius'],0.]))
            for name,vertices in paths.items():
                start=time.time()
                row=closed_loop(family,vertices,cfg)
                row.update(name=name,seconds=time.time()-start,hypothesis_sign=P['hypotheses'][name],
                           hypothesis_matches=row['accepted_sign']==P['hypotheses'][name])
                result['loops'].append(row)
                for j,v in enumerate(vertices):arrays[f'{cfg["name"]}_{name}_vertex_{j}']=family.data(v)[0]
                save()
                print('LOOP',args.engine,cfg['name'],name,'sign',row['accepted_sign'],'pass',row['diagnostics_pass'],
                      'points',row['sample_points'],'smin',row['minimum_step_smin'],'seconds',round(row['seconds'],1),flush=True)
        result['maximum_frame_orthogonality_error']=family.maximum_frame_orthogonality_error
        result['mesh_comparisons']=[{'name':name,'signs':[r['accepted_sign'] for r in result['loops'] if r['name']==name],
                                    'signs_agree':len({r['accepted_sign'] for r in result['loops'] if r['name']==name})==1}
                                   for name in P['hypotheses']]
        passed=(all(t['temporal_conditioning_pass'] for t in result['tracks'].values()) and
                all(c['pass'] for c in comparisons+result['endpoint_joins']) and
                len(result['loops'])==8 and all(r['diagnostics_pass'] for r in result['loops']) and
                all(c['signs_agree'] for c in result['mesh_comparisons']))
        result['all_hypotheses_match']=all(r['hypothesis_matches'] for r in result['loops'])
        result['status']='CLOSED_CONTOUR_DIAGNOSTICS_PASS_NOT_FULL_BRAID' if passed else 'UNRESOLVED_CHECKS_RETAINED'
    except Exception:
        result['status']='UNRESOLVED_CHECKS_RETAINED'
        result['errors'].append(traceback.format_exc())
        print(result['errors'][-1],flush=True)
    if framepath.exists():result['frames_sha256']=sha(framepath)
    # Save JSON only: rewriting NPZ after hashing would invalidate its byte hash.
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print('STATUS',result['status'],flush=True)
    return 0 if result['status'].startswith('CLOSED_CONTOUR_DIAGNOSTICS_PASS') else 1

if __name__=='__main__':raise SystemExit(main())
