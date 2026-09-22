"""Reconcile supplied records, fresh native event spectra and cutoff comparisons."""
import json
import hashlib
import numpy as np
from scipy.linalg import eigh
from inputs import ROOT, PLAN, originals, sha
folder=originals()
from bm_strain import BM
from tbg_ref import TBG

def check_source(data):
    assert all(sha(ROOT/n)==h for n,h in data['source_hashes'].items())

d=json.loads((ROOT/'CANDIDATES.json').read_text());reg=json.loads((ROOT/'REGRESSIONS.json').read_text());grid=json.loads((ROOT/'GRID_REPLAY.json').read_text())
for data in [d,reg,grid]:check_source(data)
assert reg['all_findings_reproduced'] and grid['known_crossing_node_missed']
T=PLAN['thresholds'];comparisons=[];max_matrix=0.;max_spectrum=0.;max_gap=0.;max_original_gap=0.;max_final_offset=0.;max_native_recheck=0.
for row in d['rows']:
    state=d['states'][row['state_id']];x=state['x'];N=row['N'];e=row['engine']
    assert row['pass'] and not row['errors'];event=row['event'];a,b=row['event_bracket_meV']
    assert [a,b]==[x['D']-.1,x['D']+.1] and a<=event['D_meV']<=b
    assert all(a<=v<=b for v in row['scalar_calls'])
    lo=row['dimension']//2-1
    assert row['basis_sha256']==hashlib.sha256(json.dumps(row['basis_indices']).encode()).hexdigest()
    endpoints=[next(m for m in row['measurements'] if m['D_meV']==v) for v in [a,b]]
    assert endpoints[0]['offset']*endpoints[1]['offset']<0
    for native in row['supplied_coordinate_checks']:
        assert native['numerical_model_check_pass']
        if N==4:max_original_gap=max(max_original_gap,native['gap_meV'])
    for m in row['measurements']:
        assert m['pass'] and m['image_shifts']==row['seed_image_shifts']
        assert T['segment_interior_margin']<m['t']<1-T['segment_interior_margin']
        assert len(m['roots'])==len(m['native'])==3
        for root,native,seed in zip(m['roots'],m['native'],[*state['flat'],state['node']]):
            assert root['accepted'] and native['numerical_model_check_pass'] and native['gap_meV']<=T['native_gap_tolerance_meV']
            assert np.all(abs(np.array(root['f'])-seed)<=T['coordinate_seed_radius'])
            assert root['f']==root['history'][root['returned_evaluation']]['f']
            max_matrix=max(max_matrix,native['matrix_error_meV']);max_spectrum=max(max_spectrum,native['spectrum_error_meV']);max_gap=max(max_gap,native['gap_meV'])
    assert row['solver_eigensolves']==sum(r['eigensolves'] for m in row['measurements'] for r in m['roots'])
    m=row['measurements'][event['measurement_index']];assert m['D_meV']==event['D_meV']
    F=np.array([r['f'] for r in m['roots']]);delta=F[1]-F[0];delta-=np.floor(delta+.5);rel=F[2]-F[0];rel-=np.floor(rel+.5)
    L=np.linalg.norm(delta);t=float(rel@delta/(L*L));offset=float((delta[0]*rel[1]-delta[1]*rel[0])/L)
    assert abs(offset-m['offset'])<1e-12 and abs(t-m['t'])<1e-12 and abs(offset)<T['event_offset_tolerance'];max_final_offset=max(max_final_offset,abs(offset))
    # Fresh native complex spectra at every final event, separate from the real affine evaluator.
    kw=dict(N=N,eps=x['eps'],w1=110*x['P'],Dfield=event['D_meV'],kinetic='lab_nn_full',cutoff_tol=1e-6)
    native=BM(theta_deg=x['theta'],phi_deg=x['phi'],ratio=.8,geometry='exact',**kw) if e=='bm' else TBG(theta=x['theta'],phi=x['phi'],w0=88*x['P'],**kw)
    assert native.dim==row['dimension']
    for j,f in enumerate(F):
        idx=lo+int(j==2);k=native.frac_to_k(f) if e=='bm' else native.k(f)
        w=eigh(native.H(k),eigvals_only=True,subset_by_index=(idx-1,idx+2))
        err=float(max(abs(w-m['native'][j]['w4'])));max_native_recheck=max(max_native_recheck,err)
        assert err<1e-9 and w[2]-w[1]<T['native_gap_tolerance_meV']

for state in d['states']:
    row={'state_id':state['id'],'x':state['x'],'input_rows':state['input_rows'],'cutoffs':{}}
    for N in [4,6]:
        bm,ref=[next(r for r in d['rows'] if r['state_id']==state['id'] and r['N']==N and r['engine']==e) for e in ['bm','ref']]
        assert bm['basis_indices']==ref['basis_indices']
        ferr=float(np.max(abs(np.array([*bm['event']['flat'],bm['event']['node']])-np.array([*ref['event']['flat'],ref['event']['node']]))));derr=abs(bm['event']['D_meV']-ref['event']['D_meV'])
        assert ferr<T['cross_engine_coordinate_tolerance'] and derr<T['cross_engine_event_tolerance_meV']
        row['cutoffs'][str(N)]={'BM_D_meV':bm['event']['D_meV'],'REF_D_meV':ref['event']['D_meV'],'cross_engine_D_error_meV':derr,'cross_engine_coordinate_error':ferr,'dimension':bm['dimension'],'nG':bm['dimension']//4,'basis_sha256':bm['basis_sha256']}
    row['N6_minus_N4_D_meV']=row['cutoffs']['6']['BM_D_meV']-row['cutoffs']['4']['BM_D_meV'];comparisons.append(row)

transitions=[]
for source in ['trace_phi_A.json','trace_eps_A.json']:
    ids=[s['id'] for s in d['states'] if any(r[0]==source for r in s['input_rows'])]
    for N in [4,6]:
        for left,right in zip(ids[:-1],ids[1:]):
            a,b=[next(r for r in d['rows'] if r['state_id']==i and r['N']==N and r['engine']=='bm') for i in [left,right]]
            sa={tuple(p) for p in a['basis_indices']};sb={tuple(p) for p in b['basis_indices']}
            transitions.append({'source':source,'N':N,'states':[left,right],'changed':sa!=sb,'added':sorted(sb-sa),'removed':sorted(sa-sb),'dimensions':[a['dimension'],b['dimension']]})

# Reusable candidate records contain the checked N6 locations, not an acceptance claim.
seeds=[]
for state in d['states']:
    row=next(r for r in d['rows'] if r['state_id']==state['id'] and r['N']==6 and r['engine']=='bm')
    seeds.append({'status':'SAMPLED_CANDIDATE_ONLY','x':dict(state['x'],D=row['event']['D_meV']),'N':6,'gap':'upper',
                  'model':row['model'],'basis_sha256':row['basis_sha256'],'seeds':{'flat':row['event']['flat'],'node':row['event']['node'],'gap':'upper'},
                  'input_rows':state['input_rows'],'evidence_source':'CANDIDATES.json','evidence_sha256':sha(ROOT/'CANDIDATES.json')})
(ROOT/'N6_CANDIDATE_SEEDS.json').write_text(json.dumps(seeds,indent=2,allow_nan=False)+'\n')
names=['PLAN.json','INPUT_MANIFEST.json','partner_joint_mapping.zip','inputs.py','regressions.py','REGRESSIONS.json','check_candidates.py','CANDIDATES.json','replay_grid.py','GRID_REPLAY.json','report.py','N6_CANDIDATE_SEEDS.json']
summary={'status':'PARTNER_CANDIDATES_REPRODUCED_TOOLING_FIXES_REQUIRED','all_candidate_checks_pass':True,'reproduced_tooling_findings':len(reg['findings']),
         'distinct_supplied_states':6,'engine_cutoff_state_rows':len(d['rows']),'comparisons':comparisons,'basis_transitions':transitions,
         'maximum_cutoff_D_shift_meV':max(abs(c['N6_minus_N4_D_meV']) for c in comparisons),
         'maximum_engine_D_difference_meV':max(c['cutoffs'][str(N)]['cross_engine_D_error_meV'] for c in comparisons for N in [4,6]),
         'maximum_engine_coordinate_difference':max(c['cutoffs'][str(N)]['cross_engine_coordinate_error'] for c in comparisons for N in [4,6]),
         'maximum_matrix_error_meV':max_matrix,'maximum_spectrum_error_meV':max_spectrum,'maximum_refined_native_gap_meV':max_gap,
         'maximum_supplied_N4_native_gap_meV':max_original_gap,'maximum_event_offset':max_final_offset,'maximum_final_native_recheck_error_meV':max_native_recheck,
         'solver_eigensolves':sum(r['solver_eigensolves'] for r in d['rows']),'native_spectrum_evaluations':sum(r['native_spectrum_evaluations'] for r in d['rows']),
         'new_native_final_spectra_in_report':72,'known_grid_blind_spot_reproduced':grid['known_crossing_node_missed'],
         'candidate_wall_seconds':d['elapsed_seconds'],'source_hashes':{n:sha(ROOT/n) for n in names},'scope':PLAN['scope']}
(ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print(summary['status']);print('ROWS',len(d['rows']),'FINDINGS',len(reg['findings']),'MAX CUTOFF SHIFT',summary['maximum_cutoff_D_shift_meV']);print('BASIS CHANGES',[t for t in transitions if t['changed']])
