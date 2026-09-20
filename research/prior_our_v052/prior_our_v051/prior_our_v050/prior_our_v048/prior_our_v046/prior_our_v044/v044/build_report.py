"""Reconcile immutable steps, located events and the prior oriented frames."""
import json
from pathlib import Path
from dataclasses import asdict
import numpy as np
from checkpoints import digest,load_steps,save_json
from replay import frozen_protocol
from routes import schedule
from measure import require

ROOT=Path(__file__).resolve().parent

def build():
    protocol=frozen_protocol();grid=schedule();table=[];cases={}
    for engine in ['bm_lab','ref_lab']:
        for N in [4,6]:
            folder=ROOT/'results'/f'early_{engine}_N{N}'
            x=json.loads((folder/'summary.json').read_text());rows,_=load_steps(folder,protocol)
            require(x['status']=='ACCEPT' and len(rows)==len(grid) and rows==x['states'],'incomplete or inconsistent primary record')
            require(all(r['status']=='ACCEPT' and r['state']==asdict(g['state']) for r,g in zip(rows,grid)),'accepted schedule mismatch')
            anchor=ROOT/'anchors'/f'v043_start_{engine}_N{N}.json'
            require(digest(anchor.with_suffix('.npz'))==json.loads(anchor.read_text())['frames_sha256'],'anchor frame digest mismatch')
            event_checks=[]
            for e in x['events']:
                near=min(rows[:21],key=lambda r:abs(r['state']['B']-e['B']))
                distances={k:float(np.linalg.norm(np.array(e['nodes'][k]['f'])-near['nodes'][k]['f'])) for k in e['nodes']}
                require(max(distances.values())<.04,'event root jumps from nearest continuation state')
                require(e['singular_path_rejected'] and e['external_gap']<1e-5,'unverified singular event')
                event_checks.append(dict(shift=e['shift'],nearest_state=near['step'],node_distances=distances))
            fine=[t for r in rows for t in r['temporal_transport']]
            coarse=[t for r in rows if r['parameter_mesh_check'] for t in r['parameter_mesh_check']['transport']]
            spatial=[t for r in rows for t in r['spatial_transport']]
            charges={side:sorted({t[side]['charge'] for r in rows for t in r['temporal_trials']}) for side in ['a','b']}
            changes=[dict(step=r['step'],B=r['state']['B'],T=r['state']['T'],label=r['label']) for i,r in enumerate(rows) if i and r['label']!=rows[i-1]['label']]
            row=dict(engine=engine,N=N,geometry=x['geometry'],states=len(rows),center_crossing=x['events'][0]['B'],shifted_crossing=x['events'][1]['B'],
                     events=x['events'],event_checks=event_checks,labels=sorted({r['label'] for r in rows}),label_changes=changes,
                     temporal_charges=charges,final_label=rows[-1]['label'],final_U1_offset=rows[-1]['adjacent_geometry']['U1']['offset'],
                     min_unlink_U1_offset=min(r['adjacent_geometry']['U1']['offset'] for r in rows if r['leg']==3),
                     min_parameter_overlap=min(t['min_overlap'] for t in fine+coarse),min_spatial_overlap=min(t['min_overlap'] for t in spatial),
                     min_resolved_spatial_external_gap=min(t['min_external_gap'] for t in spatial),
                     max_node_gap=max(n['gap'] for r in rows for n in r['nodes'].values()),
                     max_eigen_residual=max(r['diagnostics']['max_eigen_residual'] for r in rows),
                     anchor_join=rows[-1]['anchor_join'],loop_fallbacks=[dict(step=r['step'],attempts=r['rejected_loop_stages']) for r in rows if r['rejected_loop_stages']],
                     seconds=x['seconds'])
            require(len(changes)==1 and all(len(v)==1 for v in charges.values()),'unreconciled label/charge changes')
            table.append(row);cases[(engine,N)]=rows
    control=json.loads((ROOT/'results/exact_control.json').read_text());require(control['status']=='ACCEPT','exact control incomplete')
    geometry=json.loads((ROOT/'provenance/geometry_verification.json').read_text());require(geometry['status']=='PASS','geometry checks incomplete')
    historical=json.loads((ROOT/'provenance/historical_braid_roots.json').read_text());sensitivity=[]
    for r in table:
        old=next(x for x in historical['records'] if x['N']==r['N'] and x['engine']==('original' if r['engine']=='bm_lab' else 'partner'))
        previous=next(e['B'] for e in old['crossings'] if e['shift']==0.)
        sensitivity.append(dict(engine=r['engine'],N=r['N'],old_kinetic=old['kinetic'],old_B=previous,new_B=r['center_crossing'],difference=r['center_crossing']-previous))
    comparisons=[]
    for N in [4,6]:
        a,b=[cases[(e,N)] for e in ['bm_lab','ref_lab']]
        node_errors=[float(np.linalg.norm(np.array(x['nodes'][k]['f'])-y['nodes'][k]['f'])) for x,y in zip(a,b) for k in x['nodes']]
        ea,eb=[next(r for r in table if r['engine']==e and r['N']==N) for e in ['bm_lab','ref_lab']]
        comparisons.append(dict(N=N,max_tracked_node_difference=max(node_errors),labels_agree=all(x['label']==y['label'] for x,y in zip(a,b)),
                                center_root_ref_minus_bm=eb['center_crossing']-ea['center_crossing']))
    result=dict(status='ACCEPT',version='v044',protocol_sha256=protocol,primary_states=sum(r['states'] for r in table),cases=table,
                comparisons=comparisons,exact_control=control,geometry_verification=geometry,
                cutoff_witness=json.loads((ROOT/'provenance/cutoff_boundary_witness.json').read_text()),historical_comparison=sensitivity,
                tests=dict(supplied='29 passed in 39.31s',adopted_guards='10 passed in 39.03s',optional_cutoff_patch='8 passed'))
    require('29 passed' in (ROOT/'provenance/supplied_tests.txt').read_text() and '10 passed' in (ROOT/'provenance/adopted_guard_tests.txt').read_text(),'test evidence missing')
    require('8 passed' in (ROOT/'provenance/cutoff_patch_tests.txt').read_text(),'cutoff patch tests incomplete')
    save_json(ROOT/'SUMMARY.json',result)
    lines=['# v044 — Braid 1 joined to the accepted connections','',
      'The earlier route now reaches our accepted v043 starting frames in both engines at N=4 and N=6. All 148 primary sampled states pass. Braid 1 changes the spatial flat-pair label SAME to OPPOSITE at a located upper-node crossing. Deepening B and then changing T retains OPPOSITE and joins the previously measured route to the first annihilation. Individual charges carried in parameter space remain constant.','',
      '| Engine | Geometry | N | Center-path crossing B | Shifted-path crossing B (delta f1=0.012) | Final U1 offset | Endpoint root mismatch |',
      '|---|---|---:|---:|---:|---:|---:|']
    for r in table:lines.append(f"| {r['engine']} | {r['geometry']} | {r['N']} | {r['center_crossing']:.10f} | {r['shifted_crossing']:.10f} | {r['final_U1_offset']:.7f} | {r['anchor_join']['max_distance']:.3g} |")
    lines+=['',
      'The critical B depends on the declared spatial comparison path; the shifted-path control is not a separate physical transition. At both located crossings the selected two-band frame rejects the singular path. Quoted digits identify finite-cutoff roots, not physical precision.','',
      'The center-path crossing also changes with the declared kinetic/gauge prescription. The historical v037 original/no-tensor value is about -0.28594 and its legacy (I-E)R^T reference value about -0.28795. These accepted historical values are retained with their model tags; they are not silently relabeled lab_nn_full. Exact differences are recorded in SUMMARY.json. Neither comparison reverses the checked endpoint SAME/OPPOSITE labels.','',
      '## Route and gate','',
      'Fixed theta=1.05 degrees, eps=0.003, A=0.2, phi=0, w0/w1=0.8, kinetic=lab_nn_full. Start B=-0.25, T=0. Follow B to -0.30 in 20 intervals, deepen B to -0.40 in eight, then T to -0.40 in eight. Coordinates remain unwrapped. The flat and upper pairs are tracked throughout; the lower pair is tracked through the B legs only. Its later annihilation is not inferred from a failed search and is not claimed measured here.','',
      'The gate retains the v043 loop mesh/radius checks, spatial orientation checks with both exterior-gap minima refined, fine/coarse parameter orientation checks, eigenpair and reality checks, distinct-root and jump guards, and immutable JSON/frame commits. Endpoint joins compare roots and two-plane overlaps and record the per-node orientation needed to match the earlier frame initialization. A different absolute charge sign from an arbitrary starting frame is not a label change.','',
      f"Smallest resolved spatial exterior gap at a sampled state: {min(r['min_resolved_spatial_external_gap'] for r in table):.6g} meV. Minimum spatial overlap: {min(r['min_spatial_overlap'] for r in table):.8f}; minimum parameter overlap: {min(r['min_parameter_overlap'] for r in table):.8f}. Maximum tracked-node gap residual: {max(r['max_node_gap'] for r in table):.3g} meV.",'',
      '## Partner update and matched geometry','',
      'The incoming partner v043 contains the adopted v042 guard patch verbatim. All 29 supplied tests and ten stronger guard regressions pass. Twenty-four complete operator comparisons show exact-geometry agreement to about 1.4e-12 meV and bitwise preservation of the historical linear matrices at the checked states. See SOURCE_REVIEW.md for scope, API wording and minor record corrections.','',
      'One structural qualification remains: cutoff padding is 1e-6 in BM and 1e-9 in TBG. At N=4, eps=0.003 and phi=15.843560625 degrees, the same exact reciprocal geometry gives dimensions 196 and 188 because two indices lie between those margins. The claim that only the estimators differ is therefore too broad. The optional fixes/ patch adds an explicit common cutoff_tol while preserving both historical defaults; eight tests pass. It is not used in these primary replays. This counterexample does not invalidate the reported agreements at the checked campaign states.','',
      'The primary continuations keep BM linear and TBG exact to join their existing chains without silently changing geometry. Separate BM exact controls locate the same center and shifted crossing roots as TBG exact:', '',
      '| N | Path shift | BM exact B | TBG exact B | Difference |',
      '|---:|---:|---:|---:|---:|']
    for e in control['events']:lines.append(f"| {e['N']} | {e['shift']} | {e['B']:.10f} | {e['ref_B']:.10f} | {e['difference']:.3g} |")
    lines+=['','These controls cover roots and singular-path rejection; they are not a third full-path replay. Both Hamiltonian engines use our common measurement harness here. Agreement of matched operators does not constitute a fresh comparison of the two legacy topological estimators.','',
      '## What the combined record supports','',
      'Our v044 early route joins our v043 pre-annihilation connection, which joins the v042 first-annihilation window. The accepted post-transfer state joins our v043 later connection into the v042 braid-2 window. Endpoint frame orientations are explicitly reconciled. This is a connected set of sampled windows from braid 1 through braid 2 under each recorded geometry choice.','',
      'Remaining work: the cleanup and later collision windows after braid 2; any claim about the lower-pair unlinking collision itself; the earlier preparation from the original v023 baseline; a named strain law for w0 and w1; N>6 endpoint convergence and physical-bilayer validation. The two v043 contributions remain separate in the package. No historical linear-geometry result is relabeled exact.','',
      'Finite parameter/momentum sampling, finite cutoff and common conceptual/harness assumptions remain limits. This is not an interval proof, an exhaustive node inventory or a completed full campaign. Source hashes, records, frames, event controls, tests and the exact review cutoff accompany the result.']
    (ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n');return result

if __name__=='__main__':
    r=build();print(json.dumps(dict(status=r['status'],states=r['primary_states'],cases=len(r['cases'])),indent=2))
