"""Receipt-bound replay and numerical comparison. No eigensolver calls."""
import json,sys
from fractions import Fraction
from pathlib import Path
import numpy as np
import run as R
root=Path(sys.argv[1]);commit=sys.argv[2];R.bindings(commit)
expected=['refine0','refine1','refine2','refine3','dynamics16','dynamics32']
if (root/'cutoff').exists():expected.append('cutoff')
results={}
for name in expected:
    p=root/name;receipt=json.loads((p/'RECEIPT.json').read_text())
    assert receipt['implementation_commit']==commit and receipt['termination']=='NORMAL_EXIT' and receipt['exit_code']==0 and receipt['process_group_empty']
    assert set(x.name for x in p.iterdir())==set(receipt['files'])|{'RECEIPT.json'}
    for file,info in receipt['files'].items():assert R.digest(p/file)==info['sha256'] and (p/file).stat().st_size==info['bytes']
    result=json.loads((p/'RESULTS.json').read_text());assert result['implementation_commit']==commit and result['spec_sha256']==R.digest(R.HERE/'SPEC.json');results[name]=result
    provenance=json.loads((p/'RUNTIME.json').read_text());assert provenance['loaded_extension_bound_to_wheel'] and provenance['mapped_native_libraries_bound_to_wheel'] and provenance['loaded_object_inventory']=='glibc dl_iterate_phdr' and not provenance['proc_maps_checked']
old=R.ROOT/'research/benchmarks/certification_s1b_quadrant_a_002';sys.path.insert(0,str(old))
v=R.load(old/'verify.py','tf_final_verify');strict=R.load(R.ROOT/'research/benchmarks/parallel_domain_006/parallel.py','tf_strict')
accepted,parents,children=R.initial();new=[];unresolved=[];factorizations=0
for slot in range(4):
    rows=[json.loads(x) for x in (root/f'refine{slot}'/'CELLS.ndjson').read_text().splitlines()]
    assert [tuple(r['cell']) for r in rows]==children[slot::4]
    factors=0
    for row in rows:
        e=row['evidence'];cell=tuple(row['cell']);a,b=strict.strict_evidence(e,e['status'],{'algorithm':{'precision_bits':128,'recomputation_decimal_digits':10}},cell,v);factors+=a+b
        (new if e['status']=='CERTIFIED_RECOMPUTED_FIXED_CELL_WINDOWS' else unresolved).append(cell)
    assert factors==results[f'refine{slot}']['factorizations'] and factors<=960;factorizations+=factors
R.partition_check(accepted+new+unresolved)
area=sum(Fraction(1,4**d) for d,x,y in accepted+new)
R.write(root/'PARTITION.json',{'accepted':sorted(accepted+new),'unresolved':sorted(unresolved),'frontier':[]})
refinement={'status':'INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE' if unresolved else 'FULL_FINITE_CUTOFF_CELL_ISOLATION_PENDING_REVIEW','accepted_area':str(area),'accepted_percent':float(area*100),'accepted_cells':len(accepted+new),'newly_accepted_children':len(new),'unresolved_depth11':len(unresolved),'factorizations':factorizations,'attempts':len(children),'independent_review':'PENDING'}
# Recalculate paired point gaps from the complete retained spectra.
spec=json.loads((R.HERE/'SPEC.json').read_text())
cutoff={'status':'BLOCKED_PENDING_INDEPENDENT_PRE_EXECUTION_REVIEW','physical_calls':0}
if 'cutoff' in results:
    rows=json.loads((root/'cutoff/SPECTRA.json').read_text());assert len(rows)==128
    spec=json.loads((R.HERE/'SPEC.json').read_text());points=spec['cutoff']['points'];case=json.loads((R.ROOT/'docs/certification-readiness/CASE.json').read_text());paired={}
    for key in ['a','b']:
        group=[r for r in rows if r['cutoff']==key];assert [r['point'] for r in group]==points
        lo,hi=case['cutoffs'][key]['selected_bands_zero_based'];dim=case['cutoffs'][key]['dimension']
        for r in group:
            e=np.array(r['eigenvalues_meV']);assert len(e)==dim and np.isfinite(e).all() and np.all(np.diff(e)>=0)
            assert r['upper_gap_meV']==e[hi+1]-e[hi] and r['lower_gap_meV']==e[lo]-e[lo-1]
        paired[key]=group
    ratios=[b['upper_gap_meV']/a['upper_gap_meV'] for a,b in zip(paired['a'],paired['b'])]
    cutoff={**results['cutoff'],'pointwise_gap_ratio_b_over_a_range':[min(ratios),max(ratios)]}
dynamics={}
a,b=results['dynamics16'],results['dynamics32'];assert a['times_fs']==b['times_fs']
for tag in a['packets']:
    aa=np.fromfile(root/'dynamics16'/a['packets'][tag]['density_file'],dtype='<f4').reshape(-1,64,64)
    bb=np.fromfile(root/'dynamics32'/b['packets'][tag]['density_file'],dtype='<f4').reshape(-1,64,64)
    assert np.isfinite(aa).all() and np.isfinite(bb).all() and aa.min()>=0 and bb.min()>=0
    l1=np.sum(np.abs(aa.astype(float)-bb.astype(float)),axis=(1,2))*b['pixel_area_nm_squared']
    maximum=float(l1.max());meets=maximum<=spec['dynamics']['grid_L1_tolerance']
    dynamics[tag]={'max_common_window_density_L1':maximum,'tolerance':spec['dynamics']['grid_L1_tolerance'],'meets_tolerance':meets,'fine_max_norm_error':b['packets'][tag]['max_norm_error'],'fine_max_boundary_probability':b['packets'][tag]['maximum_boundary_probability'],'site_promotion':'PENDING_INDEPENDENT_REVIEW' if meets else 'BLOCKED_GRID_COMPARISON'}
R.write(root/'SUMMARY.json',{'implementation_commit':commit,'refinement':refinement,'cutoff':cutoff,'dynamics':dynamics,'independent_review':'PENDING','coverage_claim_ceiling':'finite-cutoff-a local isolation only; no topology, seams, cutoff convergence, or experimental claim'})
print((root/'SUMMARY.json').read_text())
