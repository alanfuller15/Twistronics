"""Reconcile saved arrays and bounds without rerunning a Hamiltonian."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
P=json.loads((ROOT/'PLAN.json').read_text());T=P['thresholds']

def su2(q):
    w,x,y,z=q
    return np.array([[w-1j*z,-y-1j*x],[y-1j*x,w+1j*z]])

def reconcile():
    controls=json.loads((ROOT/'CONTROLS.json').read_text())
    assert controls['all_controls_pass'] and len(controls['controls'])==18
    assert controls['plan_sha256']==sha(ROOT/'PLAN.json')
    assert all(sha(ROOT/n)==h for n,h in controls['source_hashes'].items())
    results={};arrays={};errors={'lift_matrix':0.,'bound_reconstruction':0.,'word_SU2':0.,'sample_coordinates':0.,'quaternion_norm':0.}
    for engine in ['bm','ref']:
        d=json.loads((ROOT/(engine.upper()+'.json')).read_text());z=np.load(ROOT/(engine.upper()+'.npz'))
        assert d['status']=='LOCAL_THREE_BAND_DIAGNOSTICS_PASS_NOT_FULL_BRAID'
        assert d['plan_sha256']==sha(ROOT/'PLAN.json') and d['arrays_sha256']==sha(ROOT/(engine.upper()+'.npz'))
        assert all(sha(ROOT.parent/n)==h for n,h in d['source_hashes'].items())
        assert len(d['cases'])==8 and all(c['diagnostics_pass'] for c in d['cases'])
        for region in d['regions']:
            n=region['n'];bounds=np.array(region['bounds']);width=(bounds[1]-bounds[0])/n
            delta=float(width@np.array(region['coordinate_norms_meV'])/2)
            assert len(region['cells'])==n*n
            for index,c in enumerate(region['cells']):
                pos=bounds[0]+(np.array(divmod(index,n))+.5)*width
                assert np.max(np.abs(pos-c['center']))<1e-12
                lower=c['exterior_gap_meV']-2*delta-T['floating_allowance_meV']
                s2=c['anchor_smin']**2-np.sqrt(3)*delta/lower-T['floating_allowance_meV']
                assert lower>T['gap_margin_meV'] and s2>T['chart_smin']**2
                errors['bound_reconstruction']=max(errors['bound_reconstruction'],abs(lower-c['exterior_lower_meV']),abs(s2-c['chart_smin_squared_lower']))
        for c in d['cases']:
            key=c['key'];raw={}
            for name in ['A','B']:
                Q=z[key+'_'+name+'_Q'];f=z[key+'_'+name+'_f'];w=z[key+'_'+name+'_w'];s=z[key+'_'+name+'_smin']
                assert all(np.isfinite(a).all() for a in [Q,f,w,s]) and s.min()>=T['chart_smin']
                assert np.array_equal(f[0],f[-1]) and len(Q)==c[name]['sample_points']
                index=0
                cfg=next(cfg for cfg in P['mesh_levels'] if cfg['name']==c['mesh'])
                for e in c[name]['edges']:
                    a,b=np.array(e['start']),np.array(e['end']);leaves=e['leaves']
                    assert leaves[0]['a']==0 and leaves[-1]['b']==1
                    for j,l in enumerate(leaves):
                        if j:assert leaves[j-1]['b']==l['a']
                        delta=e['norm_meV']*(l['b']-l['a'])
                        low=min(*np.diff(w[index]),*np.diff(w[index+1]))-delta-T['floating_allowance_meV']
                        errors['bound_reconstruction']=max(errors['bound_reconstruction'],abs(low-l['gap_lower_meV']))
                        errors['sample_coordinates']=max(errors['sample_coordinates'],float(np.max(np.abs(f[index]-(a+l['a']*(b-a))))),float(np.max(np.abs(f[index+1]-(a+l['b']*(b-a))))))
                        assert l['pass'] and low>T['gap_margin_meV'] and delta/low<=cfg['variation_over_lower_max']+1e-12
                        assert l['proper'] and l['frame_step_radians']<=cfg['maximum_frame_step_radians']+1e-12
                        index+=1
                assert index==len(w)-1
                raw[name]=Q
            raw['AB']=np.concatenate([raw['A'],raw['B'][1:]])
            raw['BA']=np.concatenate([raw['B'],raw['A'][1:]])
            raw['commutator']=np.concatenate([raw['A'],raw['B'][1:],raw['A'][-2::-1],raw['B'][-2::-1]])
            matrices={}
            for name,Q in raw.items():
                path=z[key+'_'+name+'_quaternion_path'];assert len(Q)==len(path)
                errors['quaternion_norm']=max(errors['quaternion_norm'],float(np.max(np.abs(np.linalg.norm(path,axis=1)-1))))
                previous=Q[0].copy()
                if np.linalg.det(previous)<0:previous[:,0]*=-1
                first=previous.copy()
                for U,q in zip(Q,path):
                    U=U*np.where(np.diag(previous.T@U)>=0,1.,-1.)
                    # Charge is inverse frame lift; reconstruct its SO(3) image.
                    R=Rotation.from_quat(np.r_[-q[1:],q[0]]).as_matrix()
                    errors['lift_matrix']=max(errors['lift_matrix'],float(np.max(np.abs(R-first.T@U))))
                    previous=U
                assert np.max(np.abs(path[-1]-c['words'][name]['quaternion']))<T['cross_check_error']
                assert np.min(np.linalg.norm(np.r_[np.eye(4),-np.eye(4)]-path[-1],axis=1))<T['quaternion_distance']
                matrices[name]=su2(path[-1])
            A,B=matrices['A'],matrices['B']
            for name,expect in [('AB',A@B),('BA',B@A),('commutator',A@B@A.conj().T@B.conj().T)]:
                errors['word_SU2']=max(errors['word_SU2'],float(np.max(np.abs(matrices[name]-expect))))
        results[engine]=d;arrays[engine]=z
    assert max(errors.values())<T['cross_check_error'],errors
    comparisons=[]
    for a,b in zip(results['bm']['cases'],results['ref']['cases']):
        assert a['key']==b['key']
        for name in a['words']:
            classes=[d['words'][name]['conjugacy_class'] for d in [a,b]]
            comparisons.append({'case':a['key'],'word':name,'classes':classes,'pass':len(set(classes))==1})
    assert all(c['pass'] for c in comparisons)
    cases=[c for d in results.values() for c in d['cases']];regions=[r for d in results.values() for r in d['regions']]
    out={'status':'RECONCILED_LOCAL_FRAME_CHARGES_NOT_FULL_BRAID','all_checks_pass':True,'analytic_controls':18,
         'case_count':len(cases),'primitive_loops':len(cases)*2,'composite_loops':len(cases)*3,
         'engine_comparisons':comparisons,'reconstruction_errors':errors,
         'minimum_region_exterior_lower_meV':min(r['minimum_exterior_lower_meV'] for r in regions),
         'minimum_region_chart_smin_lower':min(r['minimum_chart_smin_lower'] for r in regions),
         'minimum_contour_gap_lower_meV':min(c[n]['minimum_gap_lower_meV'] for c in cases for n in ['A','B']),
         'maximum_lift_cross_check_error':max(max(w['cross_checks'].values()) for c in cases for w in c['words'].values()),
         'maximum_Q8_distance':max(w['distance_to_Q8'] for c in cases for w in c['words'].values()),
         'all_hypotheses_match':all(c['hypotheses_match'] for c in cases),
         'sample_points_including_reused_endpoints':sum(c[n]['sample_points'] for c in cases for n in ['A','B']),
         'source_hashes':{n:sha(ROOT/n) for n in ['PLAN.json','BM.json','REF.json','BM.npz','REF.npz','CONTROLS.json','report.py']},
         'scope':P['scope']}
    (ROOT/'SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['engine_comparisons','source_hashes','scope']},indent=2))
    return out,results,arrays

if __name__=='__main__':reconcile()
