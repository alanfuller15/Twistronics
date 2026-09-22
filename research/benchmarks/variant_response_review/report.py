"""Reconcile the retained response, raw spectral ledger and bounded probes."""
from pathlib import Path
import collections,gzip,hashlib,json,xml.etree.ElementTree as ET,zipfile
import numpy as np
ROOT=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((ROOT/n).read_text())
def rows(mode):
    with gzip.open(ROOT/f'{mode}_EVALUATIONS.jsonl.gz','rt') as f:return [json.loads(line) for line in f]
def main():
    manifest=read('INPUT_MANIFEST.json');assert H(ROOT/'partner_v074p.zip')==manifest['archive_sha256']
    with zipfile.ZipFile(ROOT/'partner_v074p.zip') as z:
        for n,r in manifest['files'].items():assert hashlib.sha256(z.read(n)).hexdigest()==r['sha256']
        supplied={n:json.loads(z.read(n)) for n in ['CHIRAL_CONTROL.json','VALLEY_MIRROR.json']}
    probes=read('PROBES.json');assert probes['plan_sha256']==H(ROOT/'PLAN.json')
    tests=ET.parse(ROOT/'SUPPLIED_TESTS.xml').getroot();assert len(list(tests.iter('testcase')))==8 and not list(tests.iter('failure')) and not list(tests.iter('error'))
    mr=probes['matrix_rows'];assert len(mr)==18 and all(r['pass'] for r in mr)
    for r in mr:assert r['spectrum_error_meV']==float(np.max(np.abs(np.array(r['native_bands_meV'])-r['fast_bands_meV'])))
    sr=probes['sparse_smoke'];assert len(sr)==6 and all(r['status']=='RETURNED' and r['matrix_error_meV']<1e-9 and r['spectrum_error_meV']<1e-8 for r in sr)
    executions=read('EXECUTIONS.json');assert len(executions)==4 and all(r['exit_code']==0 and not r['timed_out'] for r in executions)
    replay={n:read('REPLAY_'+n) for n in supplied};chiral=replay['CHIRAL_CONTROL.json'];valley=replay['VALLEY_MIRROR.json']
    crows=rows('CHIRAL');vrows=rows('VALLEY');all_models={'CHIRAL':read('CHIRAL_MODELS.json'),'VALLEY':read('VALLEY_MODELS.json')}
    for mode,rr in [('CHIRAL',crows),('VALLEY',vrows)]:
        run=read(mode+'_RUN.json');assert run['status']=='COMPLETED'
        assert dict(collections.Counter(r['kind'] for r in rr))==run['counts']
        assert all(r['sequence']==i+1 for i,r in enumerate(rr))
        for n,sha in run['source_sha256'].items():assert sha==manifest['files'][n]['sha256']
        for m in all_models[mode]:
            assert m['dimension']==4*len(m['ordered_indices'])
            assert hashlib.sha256(json.dumps(m['ordered_indices'],separators=(',',':')).encode()).hexdigest()==m['indices_json_sha256']
    scan=[];cm={m['model_id']:m for m in all_models['CHIRAL']}
    for row in chiral['bandwidth_scan']:
        matching=[m for m in cm.values() if m['parameters']['N']==row['N'] and round(m['parameters']['theta_deg'],4)==row['theta_deg']]
        records=[x for x in crows if x['kind']=='fast_bands' and x['model_id'] in {m['model_id'] for m in matching}]
        assert len(records)==100 and len({tuple(x['f']) for x in records})==100
        expected_grid={(a/10,b/10) for a in range(10) for b in range(10)}
        assert all(any(np.max(np.abs(np.array(x['f'])-g))<1e-14 for g in expected_grid) for x in records)
        bw=max(x['eigenvalues_meV'][1] for x in records)-min(x['eigenvalues_meV'][0] for x in records)
        assert abs(bw-row['bandwidth_meV'])<1e-12
        scan.append({'N':row['N'],'theta_deg':row['theta_deg'],'alpha':row['alpha'],'bandwidth_meV':bw,'records':len(records),'reconstruction_error_meV':abs(bw-row['bandwidth_meV'])})
    assert len(scan)==16
    # External gap from each four-band Euler spectrum, independently reduced from the retained ledger.
    gaps={}
    for mode,rr in [('CHIRAL',crows),('VALLEY',vrows)]:
        for mid in sorted({x['state']['model_id'] for x in rr if x['kind']=='eigh' and x['context']['function']=='euler_wilson'}):
            ev=[x['eigenvalues_meV'] for x in rr if x['kind']=='eigh' and x['context']['function']=='euler_wilson' and x['state']['model_id']==mid]
            assert all(len(w)==4 for w in ev)
            gaps[mode+':'+str(mid)]={'model_id':mid,'rows':len(ev),'min_external_gap_meV':min(min(w[1]-w[0],w[3]-w[2]) for w in ev)}
    chgap=next(v for k,v in gaps.items() if k.startswith('CHIRAL:'));assert abs(chgap['min_external_gap_meV']-chiral['euler']['min_external_gap_meV'])<1e-12
    # Supplied versus replayed numerical leaves (orientation signs remain only recorded values).
    comparisons=[]
    def compare(a,b,path):
        if isinstance(a,dict) and isinstance(b,dict):
            assert set(a)==set(b),(path,'keys differ')
            for k in a:compare(a[k],b[k],path+'/'+k)
        elif isinstance(a,list) and isinstance(b,list):
            assert len(a)==len(b),(path,'length differs')
            for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
        elif isinstance(a,(float,int)) and isinstance(b,(float,int)):
            comparisons.append({'path':path,'supplied':a,'replayed':b,'abs_difference':abs(a-b)})
        else:assert a==b,(path,a,b)
    for n in supplied:compare(supplied[n],replay[n],n)
    controls=probes['controls'];assert controls['native_mass_reality']['rejected'] and controls['degenerate_band_rejected'] and controls['out_of_range_rejected']
    assert controls['synthetic_zero_overlap']['returned']['min_overlap_singular_value']==0
    assert controls['synthetic_inertia']['returned_negative_count']!=controls['synthetic_inertia']['true_negative_count']
    assert abs(controls['instrumented_loop_geometry']['runs'][1]['base_to_first_loop_distance']-.024)<1e-14
    status={'V01':'CORRECTED_IN_BOUNDED_MATRIX_DERIVATIVE_FRAME_AND_SPARSE_VALLEY_CHECKS','V02':'PRODUCER_REPRODUCES_LABELS_BUT_LOOP_GEOMETRY_NOT_FULLY_MIRRORED','V03':'DIAGNOSTICS_ADDED_ACCEPTANCE_GATES_STILL_MISSING','V04':'REALITY_AND_SAMPLED_DEGENERACY_REJECTION_CORRECTED','V05':'INTEGER_BAND_SELECTION_AND_RANGE_REJECTION_CORRECTED','V06':'SIGNED_CLAIM_WITHDRAWN_REFERENCE_NOTE_NEEDS_PRECISION','V07':'FRESH_SCAN_PRODUCER_REPRODUCED_NO_REFINEMENT_CERTIFICATE'}
    summary={'status':'SUBSTANTIAL_VARIANT_CORRECTIONS_TOPOLOGY_AND_SPARSE_INTEGRATION_WITHHELD','finding_status':status,'supplied_tests_passed':8,'matrix_rows':18,'sparse_valley_samples':6,
      'max_matrix_error_meV':max(r['matrix_error_meV'] for r in mr),'max_spectrum_error_meV':max(r['spectrum_error_meV'] for r in mr),'max_derivative_error_meV':max(max(r['derivative_errors_meV']) for r in mr),'max_frame_projector_error':max(r['frame_projector_error'] for r in mr),'max_sparse_spectrum_error_meV':max(r['spectrum_error_meV'] for r in sr),
      'scan':scan,'scan_raw_spectra':sum(r['records'] for r in scan),'scan_max_reconstruction_error_meV':max(r['reconstruction_error_meV'] for r in scan),'euler_gap_reconstruction':gaps,
      'replay_comparison':{'numeric_leaves':len(comparisons),'max_abs_numeric_difference':max(x['abs_difference'] for x in comparisons),'differences_above_1e-8':[x for x in comparisons if x['abs_difference']>1e-8]},
      'replayed_chiral_diagnostics':chiral['euler'],'replayed_valley_labels':{B:{k:v['label'] for k,v in rec.items() if isinstance(v,dict) and 'label' in v} for B,rec in valley.items() if B.startswith('braid_')},
      'input_sha256':{n:H(ROOT/n) for n in ['partner_v074p.zip','PLAN.json','PROBES.json','CHIRAL_EVALUATIONS.jsonl.gz','VALLEY_EVALUATIONS.jsonl.gz','REPLAY_CHIRAL_CONTROL.json','REPLAY_VALLEY_MIRROR.json']},
      'limits':['Finite sampled engine checks only.','Diagnostic overlap/gap values are not enforced acceptance gates or continuous bounds.','The synthetic inertia counterexample tests the kernel, not an accepted native sparse window.','Raw ledger retains spectral values and matrix-state coordinates, not all eigenvectors.','Producer wrappers share the supplied computations; this is reproduction and reconciliation, not independent physical validation.']}
    (ROOT/'REPLAY_COMPARISON.json').write_text(json.dumps(comparisons,indent=2)+'\n');(ROOT/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
