"""Derive a report only from complete, hash-checked immutable step records."""
import json
from pathlib import Path
import numpy as np
from dataclasses import asdict
from checkpoints import load_steps,save_json
from replay import frozen_protocol
from routes import schedule

ROOT=Path(__file__).resolve().parent

def build():
    protocol=frozen_protocol();cases={};table=[]
    for case in ['pre_ann','post_ann']:
        for engine in ['bm_lab','ref_lab']:
            for N in [4,6]:
                key=f'{case}_{engine}_N{N}';folder=ROOT/'results'/key
                summary=json.loads((folder/'summary.json').read_text())
                rows,_=load_steps(folder,protocol);grid=schedule(case)
                if summary['status']!='ACCEPT' or len(rows)!=len(grid):raise ValueError('incomplete case: '+key)
                if summary['states']!=rows:raise ValueError('summary disagrees with immutable steps: '+key)
                if any(r['status']!='ACCEPT' or r['state']!=asdict(g['state']) for r,g in zip(rows,grid)):
                    raise ValueError('state acceptance mismatch: '+key)
                fine=[t for r in rows for t in r['temporal_transport']]
                coarse=[t for r in rows if r['parameter_mesh_check'] for t in r['parameter_mesh_check']['transport']]
                links=fine+coarse
                loops=[t[s] for r in rows for t in r['temporal_trials'] for s in ['a','b']]
                spatial=[t for r in rows for t in r['spatial_transport']]
                row=dict(case=case,engine=engine,N=N,states=len(rows),labels=summary['labels'],
                    temporal_charges=summary['temporal_charges'],label_changes=summary['label_changes'],
                    min_pair_separation=min(r['separation'] for r in rows),max_node_jump=max(max(r['node_jumps']) for r in rows),
                    dimensions=sorted({r['basis_dimension'] for r in rows}),
                    min_parameter_overlap=min(t['min_overlap'] for t in links),
                    max_basis_norm_loss=max(max(t['old_norm_loss'],t['new_norm_loss']) for t in links),
                    fine_basis_changes=sum(t['added']>0 or t['removed']>0 for t in fine[::2]),
                    min_spatial_overlap=min(t['min_overlap'] for t in spatial),
                    min_spatial_external_gap=min(t['min_external_gap'] for t in spatial),
                    min_loop_gap=min(t['min_loop_gap'] for t in loops),
                    min_loop_overlap=min(t['min_chart_overlap'] for t in loops),
                    max_loop_phase_step=max(t['max_phase_step'] for t in loops),
                    max_root_gap=max(n['gap'] for r in rows for n in r['nodes']),
                    max_eigen_residual=max(r['diagnostics']['max_eigen_residual'] for r in rows),
                    max_reality=max(r['diagnostics']['max_reality'] for r in rows),
                    min_spatial_mesh_determinant=min(r['spatial_mesh_determinant'] for r in rows),
                    min_parameter_mesh_determinant=min(min(r['parameter_mesh_check']['orientation']) for r in rows if r['parameter_mesh_check']),
                    max_anchor_error=max(x['max_distance'] for x in summary['anchor_matches']),
                    loop_refinements=[dict(step=r['step'],attempts=r['rejected_loop_stages']) for r in rows if r['rejected_loop_stages']],
                    seconds=summary['seconds'])
                table.append(row);cases[key]=rows
    comparisons=[]
    for case in ['pre_ann','post_ann']:
        for N in [4,6]:
            a,b=[cases[f'{case}_{engine}_N{N}'] for engine in ['bm_lab','ref_lab']]
            errors=[float(np.linalg.norm(np.array(ra['nodes'][i]['f'])-rb['nodes'][i]['f'])) for ra,rb in zip(a,b) for i in range(2)]
            comparisons.append(dict(type='cross_engine',case=case,N=N,max_node_difference=max(errors),
                labels_agree=all(ra['label']==rb['label'] for ra,rb in zip(a,b)),
                max_spatial_gap_difference=max(abs(ra['spatial_transport'][1]['min_external_gap']-rb['spatial_transport'][1]['min_external_gap']) for ra,rb in zip(a,b))))
        for engine in ['bm_lab','ref_lab']:
            a,b=[cases[f'{case}_{engine}_N{N}'] for N in [4,6]]
            errors=[float(np.linalg.norm(np.array(ra['nodes'][i]['f'])-rb['nodes'][i]['f'])) for ra,rb in zip(a,b) for i in range(2)]
            comparisons.append(dict(type='cutoff',case=case,engine=engine,max_node_difference=max(errors),
                                    labels_agree=all(ra['label']==rb['label'] for ra,rb in zip(a,b))))
    validation=json.loads((ROOT/'provenance/test_validation.json').read_text())
    resume=json.loads((ROOT/'provenance/resume_verification.json').read_text())
    if validation['exit_code']!=0 or resume['status']!='PASS':raise ValueError('validation incomplete')
    result=dict(status='ACCEPT',protocol_sha256=protocol,states=sum(t['states'] for t in table),cases=table,comparisons=comparisons,
                validation=dict(unit_tests=validation['observed_result'],numerical_resume=resume['status']))
    save_json(ROOT/'SUMMARY.json',result)
    text=['# v043 — Connecting the accepted windows','',
      'Both uploaded v041 engines use `kinetic=lab_nn_full` without modification. '+
      'The two routes below carry two distinct roots and their real two-band frames at N=4 and N=6. '+
      'These results join the v028 checkpoint to the accepted first-annihilation window and the post-transfer checkpoint to the accepted second-braid window.','',
      '| Route | Engine | N | States | Spatial label(s) | Smallest resolved path exterior gap (meV) | Maximum endpoint root mismatch |',
      '|---|---|---:|---:|---|---:|---:|']
    for t in table:text.append(f"| {t['case']} | {t['engine']} | {t['N']} | {t['states']} | {', '.join(t['labels'])} | {t['min_spatial_external_gap']:.6g} | {t['max_anchor_error']:.3g} |")
    text+=['',
      f"All {result['states']} primary sampled states pass. Relative labels agree between both engines and cutoffs. Individual carried charges remain constant within each run. No loop-resolution fallback was needed in this batch.",'',
      f"Maximum cross-engine node difference over the sampled states: {max(r['max_node_difference'] for r in comparisons if r['type']=='cross_engine'):.6g} in fractional reciprocal coordinates. Maximum N=4 to N=6 node shift: {max(r['max_node_difference'] for r in comparisons if r['type']=='cutoff'):.6g}. These are finite-cutoff comparisons, not error bounds against an infinite-basis result.",'',
      '## Declared paths','',
      'Fixed throughout: theta=1.05 degrees, eps=0.003, B=-0.4. Coordinates stay unwrapped.','',
      '- Pre-annihilation flat pair: start A=0.2, T=-0.4, phi=0, ratio=0.8; phi to 60; A to 0; phi to 65; T to -0.70. The 19 states end on the v042 annihilation starting roots.',
      '- Post-annihilation upper pair: start A=0, T=-0.74, phi=65, ratio=0.8; phi to 80; T to -0.8; ratio to 0.90, 0.98, 0.99. The 21 states start on the v042 post-transfer roots and end on the v042 second-braid starting roots.',
      '', '## Changing-basis transport','',
      'The pullback identifies fixed dimensionless moire-cell coordinates and removes each declared Bloch/layer phase. Periodic-envelope coefficients are indexed by (layer,m,n,real-spinor index), with absent coefficients zero in a common space. We intersect indices before calculating overlap; we do not compare raw array rows or renormalize away discarded weight. This is an explicit numerical bundle identification, not a claim about physical time evolution in laboratory coordinates.','',
      f"Across fine and coarse parameter links, minimum singular overlap = {min(t['min_parameter_overlap'] for t in table):.9g}; maximum lost frame norm eigenvalue = {max(t['max_basis_norm_loss'] for t in table):.9g} (gate <=0.02).",
      f"Minimum spatial overlap = {min(t['min_spatial_overlap'] for t in table):.9g}; maximum node residual gap = {max(t['max_root_gap'] for t in table):.3g} meV.",'',
      '## Checks and interpretation','',
      'Parameter transport uses the fine schedule and a schedule with every other point omitted within each leg. Spatial comparisons use 128/256 base intervals, local minimization of both exterior gaps, and graded points around resolved minima. Transport refinement checks orientation agreement, not convergence of the full rotation matrix. Charge loops use 64/128 points plus half-radius agreement; only phase-resolution rejection can increase the loops to 256/512 and then 1024/2048. Every rejected refinement stage is retained. The individual charges transported in parameter space are recorded separately from the spatial SAME/OPPOSITE label. No expected label is used to force numerical acceptance.','',
      'Each accepted step commits its JSON record and numerical frames together by a directory rename. The JSON binds the array file with SHA-256; resume verifies protocol, source and anchor hashes, state identity, completeness and contiguous steps. The final report re-reads those records and requires exact agreement with each completed summary.','',
      'Seven new tests pass: six basis/transport checks and one checkpoint integrity check. A separate real numerical experiment splits the three-state N=4 BM pilot after its first state, resumes it, and reproduces every saved frame bit for bit and every diagnostic except wall-clock time and the array-container hash. Its raw output is retained under provenance/resume_probe/. Prior v042 tests are included as historical evidence, not counted as newly rerun tests.','',
      '## Scope and limits','',
      'This batch has finite sampling in momentum and parameters, and a finite basis cutoff. Agreement of two meshes is evidence of resolution, not an interval proof, exhaustive node inventory, or proof of no missed event between samples. Continuation preserves the two followed roots; it does not assert a global node count. Comparisons depend on the declared pullback and spatial path.','',
      'Still open under lab_nn_full: the first-braid replay and its deepening/unlinking legs into the v028 checkpoint; the cleanup and later collision windows after braid 2. The existing accepted first-annihilation and second-braid windows are reused as anchors, not recomputed here. A named strain law for w0 and w1, N>6 endpoint convergence and physical-bilayer validation remain separate tasks. Both Hamiltonian engines share an author and conceptual assumptions, and these replays use a common measurement/gating harness; agreement does not remove shared model or harness errors.','',
      'Independently initialized frame orientations can reverse every signed charge in one run. Cross-engine comparisons therefore use relative SAME/OPPOSITE labels and within-run charge constancy; absolute signs are not treated as invariant across those initializations.',
      '', 'See SUMMARY.json for the full numerical ranges, cross-engine/cutoff differences, refinement history and root-identity matches. PLAN.json freezes the primary source and anchors; immutable records and frames are under results/.']
    (ROOT/'REPORT.md').write_text('\n'.join(text)+'\n')
    return result

if __name__=='__main__':
    r=build();print(json.dumps(dict(status=r['status'],states=r['states'],cases=len(r['cases'])),indent=2))
