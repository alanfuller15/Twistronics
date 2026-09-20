"""Reconcile completed measurements; no conclusions from incomplete files."""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent

def load(name):return json.loads((ROOT/'results'/name).read_text())
def accepted(name):
    r=load(name)
    if r.get('status')!='ACCEPT':raise ValueError('Unaccepted measurement: '+name)
    return r
def minimum(r,key):return min(t['minimum']['gap'] for t in r['gaps'][key])
def labels(r):
    result={}
    for band,rows in r['cycles'].items():
        result[band]=[]
        for axis in [0,1]:
            signs={t['sign'] for q in rows if q['axis']==axis for t in q['trials']}
            if len(signs)!=1:raise ValueError('Unresolved cycle label')
            result[band].append(0 if next(iter(signs))>0 else 1)
    return result

def build():
    old=json.loads((ROOT/'provenance/v040_summary.json').read_text())
    summary=dict(status='ACCEPT',kinetic='lab_nn_full',engines={},cross_engine={},model_sensitivity={})
    records={}
    for engine in ['bm_lab','ref_lab']:
        summary['engines'][engine]={}
        for N in [4,6]:
            r={key:accepted(f'{key}_{engine}_N{N}.json') for key in ['second','first_ann','bridge','endpoint','post_transfer']}
            records[engine,N]=r;b=r['second'];a=r['first_ann']
            if not b['event']['singular_path_rejected'] or a['nondegeneracy']['status']!='PASS':raise ValueError('missing event guard')
            bridge_labels=labels(r['bridge']);end_labels=labels(r['endpoint'])
            if bridge_labels!=end_labels:raise ValueError('candidate and endpoint labels differ; report requires revision')
            if bridge_labels!=old['cutoffs'][str(N)]['w1']:raise ValueError('band labels changed from v040; report requires revision')
            if r['post_transfer']['pair']['label']!=old['cutoffs'][str(N)]['post_transfer_label']:raise ValueError('post-transfer label changed; report requires revision')
            summary['engines'][engine][N]=dict(braid_crossing=b['event']['ratio'],annihilation=a['event']['parameter'],
                braid_labels=[b['states'][0]['label'],b['states'][-1]['label']],
                annihilation_pair_labels=[q['measurement']['label'] for q in a['charges']],
                post_transfer_label=r['post_transfer']['pair']['label'],
                bridge_gaps={k:minimum(r['bridge'],k) for k in r['bridge']['gaps']},
                endpoint_gaps={k:minimum(r['endpoint'],k) for k in r['endpoint']['gaps']},w1=bridge_labels)
    for N in [4,6]:
        aa=summary['engines']['bm_lab'][N];bb=summary['engines']['ref_lab'][N]
        for key in ['braid_labels','annihilation_pair_labels','post_transfer_label','w1']:
            if aa[key]!=bb[key]:raise ValueError('cross-engine label difference: '+key)
        a=records['bm_lab',N]['second'];b=records['ref_lab',N]['second']
        distances=[]
        for x,y in zip(a['states'],b['states']):
            if x['ratio']!=y['ratio']:raise ValueError('different braid parameter grids')
            for name in x['nodes']:
                distances.append(float(np.linalg.norm(np.array(x['nodes'][name]['f'])-y['nodes'][name]['f'])))
        summary['cross_engine'][N]=dict(braid_crossing_difference=bb['braid_crossing']-aa['braid_crossing'],
            annihilation_difference=bb['annihilation']-aa['annihilation'],
            max_tracked_braid_node_difference=max(distances),
            max_gapped_checkpoint_difference=max(abs(aa[s][k]-bb[s][k]) for s in ['bridge_gaps','endpoint_gaps'] for k in aa[s]),
            labels_agree=True)
        prior=old['cutoffs'][str(N)]
        summary['model_sensitivity'][N]=dict(engine='tbg_ref',comparison='lab_nn_full minus v040 full, same cutoff',
            braid_crossing_change=bb['braid_crossing']-prior['braid_crossing'],
            annihilation_change=bb['annihilation']-prior['annihilation'],
            bridge_gap_changes={k:bb['bridge_gaps'][k]-prior['bridge_gaps'][k] for k in bb['bridge_gaps']},
            endpoint_gap_changes={k:bb['endpoint_gaps'][k]-prior['endpoint_gaps'][k] for k in bb['endpoint_gaps']})
    f4=summary['engines']['ref_lab'][4];f6=summary['engines']['ref_lab'][6]
    summary['reference_annihilation_cutoff_shift']=f6['annihilation']-f4['annihilation']
    summary['prior_full_annihilation_cutoff_shift']=old['cutoffs']['6']['annihilation']-old['cutoffs']['4']['annihilation']
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines=['# v042 — The lab-frame replay in both engines','',
      '**Both engines pass the v040 replay protocol with `kinetic=lab_nn_full` at',
      'N=4 and N=6. No checked topological label changes.** This closes the',
      'one-engine limitation for the second-braid and first-annihilation windows,',
      'the post-transfer checkpoint, and the two gapped checkpoints measured here.',
      'It does not close the untraced connecting legs or certify the whole campaign.','',
      'The engine files are unchanged from the v041 upload. The Hamiltonians share',
      'the declared first-order kinetic/gauge prescription, while retaining their',
      'different reciprocal-geometry approximations. A separate helper patch is',
      'provided for review; it is not used to generate these measurements.','',
      '## Decisive events','',
      '| Engine | N | Braid-2 crossing ratio | First-annihilation T |',
      '|---|---:|---:|---:|']
    for engine in ['bm_lab','ref_lab']:
        for N in [4,6]:
            r=summary['engines'][engine][N];lines.append(f"| {engine} | {N} | {r['braid_crossing']:.9f} | {r['annihilation']:.9f} |")
    lines += ['', 'Braid 2 tracks the two upper nodes and four upper-next nodes through eleven',
      'ratio states from 0.99 to 1.00, with parameter-step halving. Its spatial',
      'comparison changes SAME to OPPOSITE as an upper-next node crosses the',
      'center-to-center segment. Each temporally carried charge remains unchanged.',
      'The singular comparison at the located crossing is rejected. Two loop',
      'meshes, a halved loop radius, and transport refinement agree.','',
      'The first-annihilation window tracks two distinct flat roots through nine',
      'states from T=-0.70 toward their meeting. Charges are OPPOSITE before the',
      'event. The collision solves a zero with a rank-one spatial Jacobian, passes',
      'derivative-step refinement and nonzero fold curvature/parameter-slope',
      'checks, and has a positive refined gap on the open side. The post-transfer',
      'upper pair at T=-0.74 is SAME in all four engine/cutoff runs. Failed node',
      'searches are never used as evidence that a pair disappeared.','',
      'The quoted digits locate finite-cutoff numerical roots. They do not imply',
      'physical critical parameters accurate to nine decimal places.','',
      '## Agreement and what remains different','',
      '| N | Braid-root difference (ref minus BM) | Annihilation-root difference | Max tracked braid-node difference | Max checkpoint gap difference, meV |',
      '|---:|---:|---:|---:|---:|']
    for N,q in summary['cross_engine'].items():
        lines.append(f"| {N} | {q['braid_crossing_difference']:+.3e} | {q['annihilation_difference']:+.3e} | {q['max_tracked_braid_node_difference']:.3e} | {q['max_gapped_checkpoint_difference']:.3e} |")
    lines += ['', 'BM retains `(I-E)R` reciprocal geometry; TBG uses `(I+E)^(-T)R`.',
      'The remaining agreement error is therefore not solely plane-wave cutoff',
      'error. Sixteen assembly checks cover baseline, annihilation, braid and',
      'endpoint parameters at both cutoffs and two momentum points, including',
      'an unwrapped point. After matching only q/G on disposable diagnostic',
      'objects, the maximum matrix difference is about 1.6e-12 meV. Without',
      'that replacement the sampled central-band differences reach 5.6e-4 meV.',
      'The primary replays keep the original geometry in each engine.','',
      '## Gapped checkpoints','',
      'Earlier candidate: A=-0.35, B=-0.40, T=-1.8, phi=80 degrees, ratio=1.04.',
      'Recorded endpoint: A=-0.30, same B/T/phi, ratio=1.10.',
      'Both use theta=1.05 degrees and total heterostrain 0.003.','',
      '| State | Engine | N | Lower | Flat | Upper | Upper-next | Below-lower |',
      '|---|---|---:|---:|---:|---:|---:|---:|']
    for state,key in [('Earlier candidate','bridge_gaps'),('Endpoint','endpoint_gaps')]:
        for engine in ['bm_lab','ref_lab']:
            for N in [4,6]:
                g=summary['engines'][engine][N][key]
                lines.append(f'| {state} | {engine} | {N} | '+' | '.join(f'{g[k]:.6f}' for k in ['lower','flat','upper','next','outer_lower'])+' |')
    lines += ['', 'All gaps are meV. Bounded multistart minimization uses grids 18x18 and',
      '24x24, explicit edge/corner seeds, and opposite-seam seeds. Agreement',
      'between searches is a numerical check, not a rigorous continuum lower bound.','',
      '| Band/group | w1 along k1 | w1 along k2 |',
      '|---|---:|---:|',
      '| Lower remote | 0 | 0 |',
      '| Lower flat | 1 | 0 |',
      '| Upper flat | 0 | 0 |',
      '| Upper remote | 0 | 0 |',
      '| Flat pair | 1 | 0 |','',
      'This table holds at both checkpoints in both engines and cutoffs. Each',
      'cycle passes meshes 64/128, offsets 0 and 0.5, both directions, external',
      'isolation, and sewing norm/overlap gates. The earlier candidate is therefore',
      'still a supported endpoint candidate. Its connecting cleanup route under',
      'this declared model remains to be traced. No Euler class is assigned to the',
      'non-orientable flat pair.','',
      '## Convention sensitivity is observable-specific','',
      'For TBG, comparing the new lab-frame result to v040 full at fixed cutoff:','',
      '| N | Braid crossing change | Annihilation T change | Endpoint flat-gap change, meV |',
      '|---:|---:|---:|---:|']
    for N,q in summary['model_sensitivity'].items():
        lines.append(f"| {N} | {q['braid_crossing_change']:+.3e} | {q['annihilation_change']:+.3e} | {q['endpoint_gap_changes']['flat']:+.6f} |")
    lines += ['',f"The lab-frame annihilation root shifts by about 1.6e-4 relative to full,",
      f"while its new N4-to-N6 shift is {summary['reference_annihilation_cutoff_shift']:+.3e}",
      f"(the prior full shift was {summary['prior_full_annihilation_cutoff_shift']:+.3e}).",
      'The frame-convention effect is consequently larger than this cutoff',
      'comparison for that event. The baseline 0.004 meV remote-gap sensitivity',
      'should not be generalized to “below every other uncertainty.” None of',
      'these measured shifts changes the checked labels.','',
      'The v041 adoption table also contains a transcription error: the previous',
      'original-model annihilation roots were -0.71514090/-0.71505612, not',
      '-0.7120. Its accepted approximately +0.0016 change to v040 full remains',
      'correct. This correction concerns the historical comparison, not the new',
      'lab-frame roots above.','',
      '## Follow-through and next actions','',
      '1. Adopt these two-engine lab-frame results for the explicitly tested',
      '   windows and checkpoints. Preserve model, geometry, path lift and cutoff',
      '   beside each number; do not rename older results retroactively.',
      '2. Trace the earlier connecting legs with two distinct seeds and basis-aware',
      '   overlap transport as phi changes the reciprocal basis. Then rerun the',
      '   remaining cleanup/collision legs under the same declared convention.',
      '3. Apply/review the small public-helper patch: optimizer failure must raise,',
      '   never return positive infinity as a gap; radii must be positive and',
      '   finite. Expanded boundary/inward seeds recover an edge minimum still',
      '   missed by two agreeing grids in the uploaded helper. Ten regression',
      '   cases accompany the patch. Primary measurements',
      '   already use a separate gate and are unaffected by the patch.',
      '4. State the strain law for w0 and w1 and relaxation assumptions before',
      '   treating magnitudes as physical; then extend endpoint gap convergence',
      '   beyond N6. Numerical cutoff refinement cannot resolve model uncertainty.','',
      'Five historical reference drivers also require explicit kinetic options',
      'after the intentional API change. SOURCE_REVIEW.md lists this and the',
      'remaining helper limitations, with the exact review cutoff.','',
      '## Evidence and limits','',
      'Twenty primary jobs pass: five tasks for each engine/cutoff combination.',
      'The supplied 27 tests pass; seven new integration checks and ten optional',
      'helper-patch checks pass. Source/input hashes, fixed protocol, preflight',
      'seeds, environment, and raw checkpointed measurements are included. Two',
      'primary numerical processes were used, with one BLAS thread each.','',
      'The report gate found one incomplete saved N4 TBG endpoint record despite',
      'a completion line in the run log. The cause was not established. The',
      'incomplete snapshot is preserved, that one job was rerun under the same',
      'source hashes and tolerances, and the report uses the complete replacement.',
      'No acceptance condition was relaxed.','',
      'The measurements are sampled path continuations and finite momentum',
      'searches, not proofs over a continuum. Both Hamiltonians share the same',
      'conceptual prescription and measurement harness/libraries; their agreement',
      'guards implementation differences, not a shared conceptual error. No',
      'end-to-end campaign, N>6 convergence, complete quaternion algebra, or',
      'physical strained-bilayer validation is claimed.','']
    text='\n'.join(lines);(ROOT/'REPORT.md').write_text(text);(ROOT/'TWISTRONICS_LOG_v042.md').write_text(text)
    team=f'''TEAM SHARE — v042

The one-engine limitation is closed for the v040 windows and checkpoints.
With kinetic='lab_nn_full', BOTH uploaded engines pass the second-braid and
first-annihilation gates at N4 and N6. Spatial SAME→OPPOSITE, unchanged
carried charges, rejected singular comparison, and the fold diagnostics all
reproduce. The post-transfer U pair remains SAME. The ratio-1.04 candidate
and recorded endpoint keep identical measured per-band w1.

TBG braid-2 crossing: {f4['braid_crossing']:.8f} / {f6['braid_crossing']:.8f}.
TBG first-annihilation T: {f4['annihilation']:.8f} / {f6['annihilation']:.8f}.
BM values and full cross-engine differences are in the report.

Two qualifications: BM still linearizes reciprocal geometry while TBG uses
the exact inverse; matching only that geometry makes their matrices agree
to roundoff. Also, the ~1.6e-4 frame-convention shift in the annihilation root
exceeds its ~{abs(summary['reference_annihilation_cutoff_shift']):.1e} N4-to-N6 shift. Sensitivity must be quoted per
observable; no checked label changes. The v041 table's old root -0.7120 is
a transcription error: the earlier original roots were -0.71514090/-0.71505612.

Residual helper defects are fixed in a separate tested patch: gap_min can
return +infinity if all minimizers fail. The patch raises on failed/nonfinite
or seed-worsening refinement and rejects invalid radii. Expanded boundary
seeds also recover the known N4 edge minimum, which the uploaded revised
helper still misses by ~0.013 meV despite two-grid agreement. The scientific replay
uses the unmodified uploaded Hamiltonians and its existing external gate.

Next: basis-aware connecting legs, remaining cleanup under the declared
model, then named tunneling strain dependence and N>6 endpoint convergence.
This remains declared-model numerical evidence, not physical-bilayer validation.

Package: raw results for all 20 accepted jobs, 27 supplied tests plus 17 new
checks, source review, helper patch, and preserved prior records in one ZIP.
'''
    (ROOT/'TEAM_SHARE_v042.md').write_text(team)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':build()
