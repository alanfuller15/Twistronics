"""Assemble conclusions only after all specified jobs and guards finish."""
import json,hashlib,itertools
from pathlib import Path
import numpy as np
from checkpoints import digest,load_steps,save_json
from replay import frozen_protocol
ROOT=Path(__file__).resolve().parent

def read(path):return json.loads((ROOT/path).read_text())
def main():
    protocol=frozen_protocol();clean=[];folds=[]
    for engine,N in itertools.product(['bm_lab','ref_lab'],[4,6]):
        folder=f'results/cleanup_{engine}_N{N}';s=read(folder+'/summary.json')
        rows,_=load_steps(ROOT/folder,protocol)
        assert s['status']=='ACCEPT' and len(rows)==17 and s['states']==rows
        assert s['matches_expected'] and s['labels']==['OPPOSITE']
        assert all(len(v)==1 for v in s['temporal_charges'].values())
        clean.append(s)
        f=read(f'results/upper_ann_{engine}_N{N}_refined.json')
        assert f['status']=='ACCEPT' and f['protocol_sha256']==protocol
        assert f['cleanup_join']['max_distance']<1e-6
        assert f['nondegeneracy']['status']=='PASS' and len(f['states'])==9
        assert all(p['measurement']['label']=='OPPOSITE' for p in f['charges'])
        assert all(t['minimum']['gap']>1e-5 for c in f['gapped_checks'] for t in c['trials'])
        folds.append(f)
    endpoints=[read(f'results/endpoint_local_N{N}.json') for N in [6,8]]
    sensitivity=read('results/sensitivity.json');default=read('provenance/default_probe.json')
    assert all(x['status']=='ACCEPT' for x in endpoints) and sensitivity['status']=='ACCEPT' and len(sensitivity['rows'])==7
    assert default['status']=='PASS'
    probe=read('PROBE_PLAN.json')
    assert all(digest(ROOT/name)==h for name,h in probe['source_sha256'].items())
    # The three probe result records bind their executing source bytes.
    for x,name in [(endpoints[0],'endpoint_probe.py'),(endpoints[1],'endpoint_probe.py'),(sensitivity,'sensitivity_probe.py'),(default,'default_probe.py')]:
        assert x['source_sha256']==digest(ROOT/name)
    rows=[r for c in clean for r in c['states']]
    minparam=min(t['min_overlap'] for r in rows for t in r['temporal_transport'])
    minspatial=min(t['min_overlap'] for r in rows for t in r['spatial_transport'])
    minpathgap=min(t['min_external_gap'] for r in rows for t in r['spatial_transport'])
    maxjump=max(v for r in rows for v in r['node_jumps'])
    loopfallbacks=sum(len(r['rejected_loop_stages']) for r in rows)
    charges=[c for f in folds for c in f['charges']]
    foldfallbacks=sum(len(c['measurement']['rejected_stages']) for c in charges)
    maxres=max(r['diagnostics']['max_eigen_residual'] for r in rows)
    baseline=[r for r in sensitivity['rows'] if r['kind']=='baseline'];g0=baseline[0]['remote_gap']
    sensrows=[dict(kappa=r['state']['w_kappa'],remote_gap=r['remote_gap'],percent_change=100*(r['remote_gap']/g0-1),label=r['pair']['label']) for r in baseline]
    ep=[]
    for name in ['lower','flat','upper','next']:
        a,b=[r['gaps'][name]['minimum'] for r in endpoints]
        ep.append(dict(gap=name,N6=a['gap'],N8=b['gap'],difference=b['gap']-a['gap'],minimizer_shift=float(np.linalg.norm(np.array(b['f'])-a['f'])),N8_f=b['f']))
    mean_radius=read('provenance/mean_radius_probe.json')
    assert mean_radius['status']=='PASS' and mean_radius['source_sha256']==digest(ROOT/'mean_radius_probe.py')
    summary=dict(verification_tier='self-tested',delivery_status='unconfirmed',status='ACCEPT',version='v046',primary_protocol_sha256=protocol,cleanup_states=len(rows),root_continuation_states=sum(len(f['states']) for f in folds),upper_fold_windows=len(folds),cleanup_labels=['OPPOSITE'],cleanup_loop_fallbacks=loopfallbacks,fold_loop_fallbacks=foldfallbacks,min_parameter_overlap=minparam,min_spatial_overlap=minspatial,min_sampled_path_gap=minpathgap,max_node_jump=maxjump,max_cleanup_eigen_residual=maxres,endpoint_local_gaps=ep,sensitivity=sensrows,full_matrix_points=len(default['rows']),supplied_tests=30,new_guard_patch_tests=9,
      folds=[dict(engine=f['engine'],N=f['N'],ratio=f['event']['parameter'],node=f['event']['f'],cleanup_join=f['cleanup_join']['max_distance'],just_open_gap=f['gapped_checks'][0]['trials'][-1]['minimum']['gap'],far_open_gap=f['gapped_checks'][1]['trials'][-1]['minimum']['gap']) for f in folds])
    save_json(ROOT/'SUMMARY.json',summary)
    lines=['# Twistronics v046 — measured continuation and v045 reconciliation','',
    'Numerical evidence: `[self-tested]`. Recipient consumption: `[unconfirmed]`. Sources and raw records are included; this is not external physical validation.','',
    'All 68 scheduled cleanup states pass the full pair gate in both engines at N4/N6. The upper pair remains OPPOSITE and joins four accepted upper-annihilation windows. The supplied 30 tests and nine new adapter/optional-patch assertions pass. The v045 gap and sensitivity results are separately checked with explicit limits below.','',
    '## What was measured','',
    'The cleanup starts at the accepted end of braid 2: (A,B,T,phi,ratio)=(0,-0.4,-0.8,80,1). Its four legs are T→−1.2, A→−0.2, T→−1.8, A→−0.35, each in four intervals. Common endpoints are stored once: 17 states per engine/cutoff. Each state has two-seed refinement, separate roots, exterior-gap checks, comparison-path mesh refinement, loop-mesh/radius agreement and fine/coarse parameter transport. The initial roots match the v042 braid endpoint; the final roots match the fresh upper-collision seeds. Historical absolute frame signs were not saved at the braid endpoint, so that join reinitializes orientation and asserts root identity/relative charge only.','',
    'The upper-collision window uses nine root-continuation states, charge checks at its start and near the collision, a rank-one spatial Jacobian, derivative-step halving, nonzero null curvature and transverse parameter slope. Positive open-side minima are checked just beyond the collision and at ratio 1.1, using explicit chart boundaries. No failed root solve is interpreted as a node death. Interior root-continuation states do not each have a separate loop measurement.','',
    '| Engine | N | Upper-annihilation ratio | Gap at ratio root+0.001 (meV) | Gap at ratio 1.1 (meV) |','|---|---:|---:|---:|---:|']
    for r in summary['folds']:lines.append(f"| {r['engine']} | {r['N']} | {r['ratio']:.10f} | {r['just_open_gap']:.8f} | {r['far_open_gap']:.8f} |")
    lines += ['',f"Maximum cleanup-to-fold root mismatch is {max(r['cleanup_join'] for r in summary['folds']):.3g}. The smallest sampled cleanup comparison-path exterior gap is {minpathgap:.8f} meV; minimum spatial overlap is {minspatial:.8f}, and minimum parameter overlap is {minparam:.8f}. Maximum root step is {maxjump:.6f} in fractional coordinates. Maximum relative eigen residual in cleanup is {maxres:.3g}. Cleanup loop refinements used {loopfallbacks} fallback stages; fold charge measurements used {foldfallbacks}. Rejected refinement stages, if any, remain in the raw records.",'',
    'Both engines explicitly use lab_nn_full. BM retains linear reciprocal geometry and 1e-6 cutoff padding; TBG retains exact inverse deformation and 1e-9 padding. Thus their tiny numerical differences are not attributed solely to independent estimators. The replay uses a common charge/transport harness. The input engines are unchanged; BM average mode has kappa=0. At sixteen full-matrix points, the checks found that default and average±5 reproduce the prior exact-geometry BM matrices bit for bit.','',
    '## v045 endpoint check','',
    'Each previously located minimum was freshly refined from its seed and two diagonal offsets of size 0.002 at N6 and N8. Optimizer success, non-worsening, projected gradient below 1e-4, positive local curvature and agreement across three starts are recorded. This is local multistart confirmation, not a global N8 search or an infinite-cutoff error estimate.','',
    '| Gap | N6 (meV) | N8 (meV) | N8−N6 (meV) |','|---|---:|---:|---:|']
    for r in ep:lines.append(f"| {r['gap']} | {r['N6']:.10f} | {r['N8']:.10f} | {r['difference']:+.10f} |")
    lines += ['',f"Largest absolute shift among these four tracked local minima: {max(abs(r['difference']) for r in ep):.6g} meV. No N8 path labels or global topological invariant were remeasured.",'',
    '## v045 tunneling scenario check','',
    'Exact-geometry BM at N4 was checked at three baseline configurations and four braid endpoints. Both exterior gaps receive bounded 18/24-grid multistart searches at baseline; pair labels use comparison-path and loop refinements. Average±5 need no separate eigensolver runs because their full Hamiltonians are identical to average0 at the checked points and cancellation follows directly from the implemented opposite strains.','',
    '| Mode | kappa | Baseline remote gap (meV) | Change | Pair label |','|---|---:|---:|---:|---|']
    for r in sensrows:lines.append(f"| {'average' if r['kappa']==0 else 'layer1'} | {r['kappa']:+g} | {r['remote_gap']:.8f} | {r['percent_change']:+.5f}% | {r['label']} |")
    lines += ['','| kappa (layer1) | B | Gated pair label |','|---:|---:|---|']
    for r in sensitivity['rows']:
        if r['kind']=='braid_endpoint':lines.append(f"| {r['state']['w_kappa']:+g} | {r['state']['B']:+.2f} | {r['pair']['label']} |")
    lines += ['','These are sampled scenario results, not a calibrated worst-case physical bound. The same directional factor multiplies w0 and w1, so their ratio is not independently varied by this strain option. The average-mode cancellation is built into the ansatz; it does not validate the general physical claim in the v045 headline. The source review provides primary literature and a concrete finite-twist qualification: the proposed mean of rotated valley radii has an O(epsilon theta) term. That calculation tests the geometric argument, not a microscopic hopping law.','',
    '## Sequence status and limits','',
    '| Segment | Current status |','|---|---|',
    '| Early braid/deepening/unlinking parameter legs | v044: 148 accepted sampled states; separate lower unlink collision not resolved there. |',
    '| Connections around the first annihilation | Our v043: 160 accepted states; v042 provides the first-annihilation fold and braid-2 window. |',
    '| Post-braid-2 cleanup and upper collision | This batch: 68 fully gated cleanup states, four fold windows with 36 root-continuation states. |',
    '| Later flat-pair birth, final annihilation and joins to gapped checkpoints | Next declared-model replay; historical results are retained as historical. |',
    '| Earlier v023 preparation / lower unlink collision itself | Do not imply complete coverage from neighboring legs. |',
    '| N>6 path replay / global N8 search / microscopic bilayer validation | Not performed. |','',
    'See SOURCE_REVIEW.md for the layered review, graded findings and ranked actions. The optional finite-coefficient patch has nine targeted passing assertions and preserves valid matrices. It is not used to generate the primary results. The v044 cutoff-tolerance patch remains separate and unadopted by the incoming toolkit. The new raw NaN witness establishes an input defect, not corruption of a recorded conclusion. PROTOCOL_ERRATA.md corrects the half-radius mesh metadata in the frozen plan: executed trials used the finer 512/2048 counts recorded in the source and results.','',
    'Finite searches can miss other nodes or extrema. Loop/mesh agreement and nondegenerate-fold diagnostics strengthen these local conclusions without establishing mathematical completeness. No claim is made that all original audit defects affected, or did not affect, every historical conclusion.']
    (ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
