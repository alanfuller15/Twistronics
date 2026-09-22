"""Reconcile saved work, brackets, basis membership and native final spectra."""
from pathlib import Path
import hashlib
import json
import numpy as np
import jm_model as m

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    root=m.ROOT;r=json.loads((root/'RESULTS.json').read_text());plan=json.loads((root/'PLAN.json').read_text())
    for name,h in r['source_hashes'].items():assert sha(root.parent/name)==h,name
    controls=json.loads((root/'CONTROLS.json').read_text());assert all(c['pass_check'] for c in controls['checks'])
    assert len(r['rows'])==30
    n=plan['numerics'];basis=json.loads((root/'BASIS.json').read_text())
    validation=[];fresh=[];cost=0;lookup={}
    def verify_result(result, cfg, seed, bracket):
        assert result['bracket']==bracket
        assert result['tolerance']==n['event_offset_tol'] and result['xtol']==n['D_xtol_meV']
        assert result['maxit']==n['max_bisections']
        assert result['cost']==sum(a['measurement']['cost'] for a in result['measurements'])
        assert result['cost_complete']
        for item in result['measurements']:
            assert bracket[0]<=item['D_meV']<=bracket[1]
            meas=item['measurement']
            assert meas['cost']==sum(v['eigensolves'] for v in meas['roots'])+sum(v['eigensolves'] for v in meas['native'])
            for rr in meas['roots']:
                bounds=np.array(rr['box'])
                assert rr['config']==cfg['solver']
                for h in rr['history']:
                    assert np.all(np.array(h['f'])>=bounds[0]) and np.all(np.array(h['f'])<=bounds[1])
                if rr['accepted']:
                    last=rr['history'][rr['returned_evaluation']]
                    assert rr['f']==last['f'] and rr['gap_meV']==last['gap_meV']
        if result['status']!='candidate':return None
        e=result['event'];final=result['measurements'][e['measurement_index']]
        assert e['D_meV']==final['D_meV'] and abs(e['offset'])<=n['event_offset_tol']
        meas=final['measurement'];assert meas['ok'] and len(meas['roots'])==3
        fs=np.array([v['f'] for v in meas['roots']]);t,offset,sep=m.segment_geometry(*fs)
        assert abs(t-e['t'])<1e-12 and abs(offset-e['offset'])<1e-12
        assert cfg['segment_margin']<t<1-cfg['segment_margin'] and sep>cfg['separation_min']
        assert m.image_shifts(fs)==m.image_shifts([*seed['flat'],seed['node']])
        for f,s,rr in zip(fs,[*seed['flat'],seed['node']],meas['roots']):
            expected=[np.maximum(np.array(s)-cfg['root_radius'],0),np.minimum(np.array(s)+cfg['root_radius'],1)]
            assert np.max(abs(np.array(rr['box'])-expected))<1e-15
        family=m.Family(meas['x'],cfg)
        assert meas['dimension']==family.dim and meas['basis']==m.digest(family.indices)
        los=[family.dim//2-1,family.dim//2-1,family.dim//2]
        for f,lo,stored in zip(fs,los,meas['native']):
            check=family.native_check(e['D_meV'],f,lo);assert check['ok']
            check['saved_spectrum_error_meV']=float(np.max(abs(np.array(check['w4'])-stored['w4'])))
            assert check['saved_spectrum_error_meV']<1e-9
            fresh.append(check)
        return dict(D=e['D_meV'],roots=fs.tolist(),dimension=family.dim,basis=m.digest(family.indices),
                    gap_max=max(v['gap_meV'] for v in meas['native']),offset=offset)
    for row in r['rows']:
        s=r['stations'][row['station']];expected_indices=None if row['mode']=='radial' else basis[row['mode']]
        assert row['config']['indices']==expected_indices and row['config']['N']==6
        assert row['config']['engine']==row['engine']
        x=verify_result(row['result'],row['config'],s['seed']['seeds'],s['D_bracket'])
        cost+=row['result']['cost'];validation.append(dict(station=row['station'],mode=row['mode'],engine=row['engine'],passed=x is not None))
        if x is not None:lookup[row['station'],row['mode'],row['engine']]=x
    trace_checks=[]
    for engine,info in r['traces'].items():
        assert sha(root/info['file'])==info['sha256']
        tr=json.loads((root/info['file']).read_text());assert tr['source_hashes']==m.sources()
        seed=tr['input_seed']['seeds'];trace_cost=0;hashes=[]
        for i,station in enumerate(tr['stations']):
            if station['result'] is None:continue
            x=verify_result(station['result'],tr['config'],seed,tr['plan']['stations'][i]['D_bracket'])
            trace_cost+=station['result']['cost']
            if x is not None:
                independent=lookup[i,'union',engine]
                delta=abs(x['D']-independent['D'])
                assert delta<1e-5
                trace_checks.append(dict(engine=engine,station=i,independent_D_difference_meV=delta,passed=True))
                hashes.append(x['basis']);seed=station['result']['event']['seeds']
        assert trace_cost==tr['cost'] and len(set(hashes))<=1
        cost+=trace_cost
    comparisons=[];engine_delta=[];coordinate_delta=[]
    for i,s in enumerate(r['stations']):
        if not all((i,b,e) in lookup for b in n['basis_modes'] for e in n['engines']):continue
        for mode in n['basis_modes']:
            a,b=lookup[i,mode,'bm'],lookup[i,mode,'ref']
            engine_delta.append(abs(a['D']-b['D']));coordinate_delta.append(float(np.max(abs(np.array(a['roots'])-b['roots']))))
        radial,union,inter=[lookup[i,mode,'bm'] for mode in n['basis_modes']]
        comparisons.append(dict(eps=s['seed']['x']['eps'],radial_dimension=radial['dimension'],
            radial_D_meV=radial['D'],union_D_meV=union['D'],intersection_D_meV=inter['D'],
            union_minus_radial_meV=union['D']-radial['D'],intersection_minus_radial_meV=inter['D']-radial['D'],
            union_minus_intersection_meV=union['D']-inter['D']))
    assert max(engine_delta,default=0)<1e-5 and max(coordinate_delta,default=0)<1e-7
    native_max=max(v['gap_meV'] for v in fresh)
    all_pass=(len(lookup)==30 and len(trace_checks)==10 and r['status']=='SAMPLED_COMMON_BASIS_CHECKS_COMPLETED')
    out=dict(status='GUARDED_TOOLS_AND_SAMPLED_BASIS_COMPARISON_PASS' if all_pass else 'PARTIAL_RESULTS_RETAINED',
             all_checks_pass=all_pass,controls=len(controls['checks']),event_rows=len(validation),trace_stations=len(trace_checks),
             validation=validation,trace_checks=trace_checks,comparisons=comparisons,total_recorded_eigensolves=cost,
             fresh_native_final_checks=len(fresh),fresh_report_eigensolves=2*len(fresh),
             max_engine_D_difference_meV=max(engine_delta,default=None),max_engine_coordinate_difference=max(coordinate_delta,default=None),
             max_native_gap_meV=native_max,max_native_matrix_error_meV=max(v['matrix_error_meV'] for v in fresh),
             max_saved_spectrum_recheck_error_meV=max(v['saved_spectrum_error_meV'] for v in fresh),
             max_abs_union_minus_intersection_meV=max(abs(c['union_minus_intersection_meV']) for c in comparisons),
             fresh_checks=fresh,source_hashes=dict(r['source_hashes']),scope=plan['scope'])
    for name in ('RESULTS.json','TRACE_BM.json','TRACE_REF.json','report.py'):
        out['source_hashes']['joint_mapping_guarded/'+name]=sha(root/name)
    (root/'SUMMARY.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(out['status'],flush=True)
    for key in ('controls','event_rows','trace_stations','total_recorded_eigensolves','fresh_native_final_checks',
                'max_engine_D_difference_meV','max_native_gap_meV','max_abs_union_minus_intersection_meV'):
        print(key,out[key],flush=True)
    for c in comparisons:print(c,flush=True)

if __name__=='__main__':main()
