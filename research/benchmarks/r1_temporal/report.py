"""Independent checks of saved bounds, carried frames and quaternion images."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'PLAN.json').read_text());T=P['thresholds']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def su2(q):
    w,x,y,z=q;return np.array([[w-1j*z,-y-1j*x],[y-1j*x,w+1j*z]])
def cat(*parts):return np.concatenate([parts[0],*[p[1:] for p in parts[1:]]])

def main():
    controls=json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and len(controls['rows'])==8
    assert controls['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in controls['sources'].items())
    assert controls['parent_controls_sha256']==sha(ROOT.parent/'r1_three_band'/'CONTROLS.json')
    axis=json.loads((ROOT/'TEMPORAL_AXIS_CONTROLS.json').read_text())
    assert axis['all_controls_pass'] and len(axis['rows'])==2 and axis['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in axis['sources'].items())
    errors={'bounds':0.,'coordinates':0.,'frame_lift':0.,'unit_quaternion':0.,'carried_frame':0.,'shared_base_frames':0.,'SU2_conjugation':0.,'cover_volume_relative':0.,'frame_step_angle':0.}
    results={};counts={'transported_station_loops':0,'temporal_edges':0,'base_edges':0,'endpoint_comparisons':0,'volume_leaves':0,'guarded_edge_leaves':0}
    minima={'volume_exterior_gap_meV':float('inf'),'volume_chart_smin':1.,'spatial_gap_meV':float('inf'),'temporal_gap_meV':float('inf')}
    grid_comparisons=[]
    for engine in ['bm','ref']:
        d=json.loads((ROOT/(engine.upper()+'.json')).read_text());z=np.load(ROOT/(engine.upper()+'.npz'))
        assert d['status']=='GUARDED_TEMPORAL_GRID_AND_CONJUGATION_PASS_NOT_FULL_BRAID',d['errors']
        assert d['plan_sha256']==sha(ROOT/'PLAN.json') and d['arrays_sha256']==sha(ROOT/(engine.upper()+'.npz'))
        assert all(sha(ROOT.parent/n)==h for n,h in d['sources'].items())
        def verify_edges(report,key,category,expected_pass=True):
            v,w,Q=z[key+'_v'],z[key+'_w'],z[key+'_Q'];assert all(np.isfinite(x).all() for x in [v,w,Q])
            assert np.min(z[key+'_smin'])>=T['chart_smin']
            edges=report['edges'] if 'edges' in report else [report];index=0
            for e in edges:
                leaves=e['leaves'];a,b=np.array(e['start']),np.array(e['end'])
                assert leaves[0]['a']==0 and leaves[-1]['b']==1
                for j,l in enumerate(leaves):
                    if j:assert leaves[j-1]['b']==l['a']
                    delta=e['norm_meV']*(l['b']-l['a'])
                    low=min(*np.diff(w[index]),*np.diff(w[index+1]))-delta-T['floating_allowance']
                    errors['bounds']=max(errors['bounds'],abs(low-l['gap_lower_meV']),abs(delta-l['variation_meV']))
                    errors['coordinates']=max(errors['coordinates'],float(np.max(np.abs(v[index]-(a+l['a']*(b-a))))),float(np.max(np.abs(v[index+1]-(a+l['b']*(b-a))))))
                    if expected_pass:
                        assert l['pass'] and low>T['gap_margin_meV']
                        cfg=next(c for c in P['mesh_levels'] if c['name']==('coarse' if key.startswith('coarse') else 'fine'))
                        assert delta/low<=cfg['variation_over_lower_max']+1e-12
                        signs=np.where(np.diag(Q[index].T@Q[index+1])>=0,1.,-1.)
                        step=Q[index].T@(Q[index+1]*signs);assert np.linalg.det(step)>0
                        angle=float(Rotation.from_matrix(step).magnitude())
                        assert angle<=cfg['maximum_frame_step_radians']+1e-12
                        errors['frame_step_angle']=max(errors['frame_step_angle'],abs(angle-l['frame_step_radians']))
                        minima[category]=min(minima[category],low);counts['guarded_edge_leaves']+=1
                    index+=1
            assert index==len(v)-1
            assert bool(report['pass'])==expected_pass
        def verify_lift(raw,base,path):
            assert len(raw)==len(path)
            current=base.copy();first=base.copy()
            errors['unit_quaternion']=max(errors['unit_quaternion'],float(np.max(np.abs(np.linalg.norm(path,axis=1)-1))))
            for U,q in zip(raw,path):
                U=U*np.where(np.diag(current.T@U)>=0,1.,-1.)
                assert np.linalg.det(current.T@U)>0
                R=Rotation.from_quat(np.r_[-q[1:],q[0]]).as_matrix()
                errors['frame_lift']=max(errors['frame_lift'],float(np.max(np.abs(R-first.T@U))))
                current=U
        for vol in d['volumes']:
            assert vol['pass'];bounds=np.array(vol['bounds']);total=0.
            for c in vol['cells']:
                a,b=np.array(c['a']),np.array(c['b']);assert np.all(a>=bounds[0]-1e-12) and np.all(b<=bounds[1]+1e-12)
                delta=float(((b-a)/2)@vol['norms_meV']);low=c['gap_meV']-2*delta-T['floating_allowance']
                s2=c['smin']**2-np.sqrt(3)*delta/low-T['floating_allowance']
                assert c['pass'] and low>T['gap_margin_meV'] and s2>T['chart_smin']**2
                errors['bounds']=max(errors['bounds'],abs(low-c['gap_lower_meV']),abs(s2-c['smin_squared_lower']))
                total+=float(np.prod(b-a));counts['volume_leaves']+=1
                minima['volume_exterior_gap_meV']=min(minima['volume_exterior_gap_meV'],low);minima['volume_chart_smin']=min(minima['volume_chart_smin'],float(np.sqrt(s2)))
            exact=float(np.prod(bounds[1]-bounds[0]));errors['cover_volume_relative']=max(errors['cover_volume_relative'],abs(total/exact-1))
        previous={}
        for b in d['base_transports']:
            name=b['mesh'];j=b['station'];key=f'{name}_base_{j}';raw=z[key+'_Q']
            if j==0:
                cur=raw[0].copy()
                if np.linalg.det(cur)<0:cur[:,0]*=-1
            else:
                verify_edges(b['edge'],key,'temporal_gap_meV');counts['base_edges']+=1;cur=previous[name]
            for U in raw:
                U=U*np.where(np.diag(cur.T@U)>=0,1.,-1.);assert np.linalg.det(cur.T@U)>0;cur=U
            errors['carried_frame']=max(errors['carried_frame'],float(np.max(np.abs(cur-z[key+'_carried']))));previous[name]=cur
        for j in range(9):
            R=z[f'coarse_base_{j}_carried'].T@z[f'fine_base_{2*j}_carried']
            errors['shared_base_frames']=max(errors['shared_base_frames'],float(np.max(np.abs(R-np.eye(3)))))
        for s in d['stations']:
            key=s['key'];assert s['diagnostics_pass'] and s['charge']['valid']
            verify_edges(s['paths']['stem'],key+'_stem','spatial_gap_meV');verify_edges(s['paths']['circle'],key+'_circle','spatial_gap_meV')
            stem,circle=z[key+'_stem_Q'],z[key+'_circle_Q'];raw=cat(stem,circle,stem[::-1]);path=z[key+'_T_quaternion_path']
            base=z[f'{s["mesh"]}_base_{s["station"]}_carried'];verify_lift(raw,base,path)
            assert np.max(np.abs(path[-1]-s['charge']['quaternion']))<T['cross_check_error'];counts['transported_station_loops']+=1
        for e in d['temporal_edges']:
            verify_edges(e['edge'],e['key'],'temporal_gap_meV');counts['temporal_edges']+=1
        for c in d['endpoint_comparisons']:
            assert c['pass'];key=c['key'];s=next(s for s in d['stations'] if s['key']==key)
            verify_edges(c['nominal_stem'],key+'_nominal_stem','spatial_gap_meV')
            t,n,circle=z[key+'_stem_Q'],z[key+'_nominal_stem_Q'],z[key+'_circle_Q']
            S=cat(n,circle,n[::-1]);C=cat(t,n[::-1]);CSC=cat(C,S,C[::-1]);base=z[f'{s["mesh"]}_base_{s["station"]}_carried']
            for name,raw in [('S',S),('C',C),('CSC_inverse',CSC)]:verify_lift(raw,base,z[key+'_'+name+'_quaternion_path'])
            qT=z[key+'_T_quaternion_path'][-1];qS=z[key+'_S_quaternion_path'][-1];qC=z[key+'_C_quaternion_path'][-1]
            err=float(np.max(np.abs(su2(qC)@su2(qS)@su2(qC).conj().T-su2(qT))))
            errors['SU2_conjugation']=max(errors['SU2_conjugation'],err);counts['endpoint_comparisons']+=1
        cross=d['crossing_control'];assert cross['required_rejection_pass'] and cross['accepted_charge'] is None
        verify_edges(cross['nominal_stem'],'crossing_control','spatial_gap_meV',False)
        for coarse in [s for s in d['stations'] if s['mesh']=='coarse']:
            fine=next(s for s in d['stations'] if s['mesh']=='fine' and s['D_meV']==coarse['D_meV'] and s['radius']==coarse['radius'])
            error=float(np.max(np.abs(np.array(coarse['charge']['quaternion'])-fine['charge']['quaternion'])))
            grid_comparisons.append({'engine':engine,'D_meV':coarse['D_meV'],'radius':coarse['radius'],'error':error,'pass':error<T['cross_check_error']})
        for s in [s for s in d['stations'] if s['radius']==.003]:
            other=next(t for t in d['stations'] if t['mesh']==s['mesh'] and t['D_meV']==s['D_meV'] and t['radius']==.0015)
            assert np.max(np.abs(np.array(s['charge']['quaternion'])-other['charge']['quaternion']))<T['cross_check_error']
        results[engine]=d
    assert all(c['pass'] for c in grid_comparisons) and max(errors.values())<T['cross_check_error'],errors
    comparisons=[]
    for a,b in zip(results['bm']['stations'],results['ref']['stations']):
        assert a['key']==b['key'];classes=[x['charge']['conjugacy_class'] for x in [a,b]]
        comparisons.append({'key':a['key'],'classes':classes,'pass':len(set(classes))==1})
    assert all(c['pass'] for c in comparisons)
    out={'status':'RECONCILED_TEMPORAL_GRID_AND_CONJUGATION_NOT_FULL_BRAID','all_numerical_checks_pass':True,
         'new_analytic_controls':10,'core_analytic_controls':8,'supplementary_D_axis_controls':2,'reused_parent_analytic_controls':18,'counts':counts,'minimum_conditional_estimates':minima,
         'reconstruction_errors':errors,'grid_comparisons':grid_comparisons,'engine_class_comparisons':comparisons,
         'crossing_D_meV':{n:d['crossing_control']['D_meV'] for n,d in results.items()},
         'all_hypotheses_match':all(d['all_hypotheses_match'] for d in results.values()),
         'sequences':{n:d['charge_sequences'] for n,d in results.items()},
         'scope':P['scope'],'source_hashes':{n:sha(ROOT/n) for n in ['PLAN.json','BM.json','REF.json','BM.npz','REF.npz','CONTROLS.json','TEMPORAL_AXIS_CONTROLS.json','report.py']}}
    (ROOT/'SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['grid_comparisons','engine_class_comparisons','sequences','source_hashes','scope']},indent=2))

if __name__=='__main__':main()
