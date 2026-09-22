"""Both independently coded Hamiltonians, identical frozen face-cover diagnostic."""
import argparse,json,time,traceback,platform
import numpy as np
import scipy
from surface import ROOT,PLAN,T,COLUMNS,STATES,Family,Spectrum,operator_norms,face_geometry,cover,summaries,sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--engine',choices=PLAN['engines'],required=True);args=ap.parse_args();engine=args.engine
    dest=ROOT/(engine.upper()+'.json')
    if dest.exists():raise SystemExit('Refusing overwrite')
    controls=json.loads((ROOT/'CONTROLS.json').read_text());assert controls['all_controls_pass'] and controls['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in controls['source_hashes'].items())
    parentpath=ROOT.parent/'r1_temporal'/(engine.upper()+'.json');parent=json.loads(parentpath.read_text())
    assert parent['status']=='GUARDED_TEMPORAL_GRID_AND_CONJUGATION_PASS_NOT_FULL_BRAID'
    assert all(sha(ROOT.parent/n)==h for n,h in parent['sources'].items())
    assert sha(parentpath.with_suffix('.npz'))==parent['arrays_sha256']
    tracks_path=ROOT.parent/'r1_holonomy'/(engine.upper()+'.json');tracks=json.loads(tracks_path.read_text())
    paths=[ROOT/n for n in ['PLAN.json','surface.py','sweep.py','controls.py','CONTROLS.json']]+[parentpath,tracks_path,ROOT.parent/'r1_temporal'/'SUMMARY.json']
    out={'status':'RUNNING','engine':engine,'N':8,'plan_sha256':sha(ROOT/'PLAN.json'),'source_hashes':{str(p.relative_to(ROOT.parent)):sha(p) for p in paths},
         'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'columns':COLUMNS,'states':STATES,'cases':[],'errors':[]}
    def save():dest.write_text(json.dumps(out,indent=2)+'\n')
    save()
    try:
        family=Family(engine);spec=Spectrum(family);norms=operator_norms(family);bounds=np.array(parent['bounds'])
        out.update(dimension=family.dim,affine_checks=family.checks,operator_norms_meV=norms.tolist(),parent_bounds=bounds.tolist(),
                   parent_volume_checks=[{k:v[k] for k in ['mesh','pass','minimum_gap_lower_meV','minimum_smin_lower']} for v in parent['volumes']])
        assert all(v['pass'] for v in parent['volumes'])
        for cfg in PLAN['mesh_levels']:
            for radius in PLAN['radii']:
                name=f"{engine.upper()}_{cfg['name']}_r{radius}".replace('.','p');npz=ROOT/(name+'.npz')
                if npz.exists():raise RuntimeError('Refusing overwrite '+str(npz))
                started=time.time();patches=[];records=[];offsets=[0];faces=[]
                for j,k,c in face_geometry(tracks['tracks'][str(cfg['track_intervals'])]['stations'],radius,cfg['polygon_edges']):
                    if np.any(c<bounds[0]-1e-14) or np.any(c>bounds[1]+1e-14):raise RuntimeError('Face outside prior chart box')
                    rows=cover(c,spec,norms);s=summaries(rows);patches.append(c);records.append(rows);offsets.append(offsets[-1]+len(rows));faces.append(dict(interval=j,edge=k,**s))
                    if k==cfg['polygon_edges']+1:
                        print(engine,cfg['name'],radius,'D interval',j+1,'evaluations',offsets[-1],'leaves',sum(x['leaves'] for x in faces),'unresolved',sum(x['unresolved_leaves'] for x in faces),'seconds',round(time.time()-started,1),flush=True)
                np.savez_compressed(npz,corners=np.array(patches),rows=np.concatenate(records),offsets=np.array(offsets,dtype=np.int64),operator_norms=norms)
                case={'name':name,'mesh':cfg['name'],'radius':radius,'arrays_file':npz.name,'arrays_sha256':sha(npz),'faces':faces,'seconds':time.time()-started,
                      'pass':all(f['pass'] for f in faces),'minimum_lower_meV':min(f['minimum_lower_meV'] for f in faces),'evaluations':sum(f['evaluations'] for f in faces),'leaves':sum(f['leaves'] for f in faces),'unresolved_leaves':sum(f['unresolved_leaves'] for f in faces)}
                out['cases'].append(case);save();print('CASE',engine,name,case['pass'],case['minimum_lower_meV'],flush=True)
        out['status']='FULL_DECLARED_SURFACE_ISOLATION_PASS_CONDITIONAL' if len(out['cases'])==4 and all(c['pass'] for c in out['cases']) else 'UNRESOLVED_FACES_RETAINED'
    except Exception:
        out['status']='UNRESOLVED_FACES_RETAINED';out['errors'].append(traceback.format_exc());print(out['errors'][-1],flush=True)
    save();print('STATUS',out['status'],flush=True)
    return 0 if out['status']=='FULL_DECLARED_SURFACE_ISOLATION_PASS_CONDITIONAL' else 1
if __name__=='__main__':raise SystemExit(main())
