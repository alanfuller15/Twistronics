"""Build the handoff only from completed, accepted measurement records."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def read(name):return json.loads((ROOT/'results'/name).read_text())
def accepted(name):
    r=read(name)
    if r.get('status')!='ACCEPT':raise ValueError('Unaccepted source: '+name)
    return r
def smallest(record,name):return min(t['minimum']['gap'] for t in record['gaps'][name])
def label(record,band):
    return tuple(0 if next(row['trials'][-1]['sign'] for row in record['cycles'][band] if row['axis']==axis)>0 else 1 for axis in [0,1])

def build():
    summary=dict(status='ACCEPT',model='Uploaded tbg_ref, explicit kinetic=full',cutoffs={},limits=['One Hamiltonian engine','Finite numerical sampling, not a continuum proof','Earlier connecting legs and full-variant cleanup untraced','No physical tunneling strain law'])
    prior=json.loads((ROOT/'provenance/previous_numbers.json').read_text())
    for N in [4,6]:
        b=accepted(f'second_v039_full_N{N}.json');a=accepted(f'first_ann_v039_full_N{N}.json')
        mid=accepted(f'bridge_v039_full_N{N}.json');end=accepted(f'endpoint_v039_full_N{N}.json');post=accepted(f'post_transfer_N{N}.json')
        assert b['event']['singular_path_rejected'] and a['nondegeneracy']['status']=='PASS'
        for r in [mid,end]:
            for band,want in [('lower_remote',(0,0)),('flat1',(1,0)),('flat2',(0,0)),('upper_remote',(0,0)),('flat_pair',(1,0))]:
                assert label(r,band)==want
        old=prior[str(N)]['original_first_ann']
        summary['cutoffs'][N]=dict(braid_crossing=b['event']['ratio'],annihilation=a['event']['parameter'],previous_original_annihilation=old,
            annihilation_shift=a['event']['parameter']-old,post_transfer_label=post['pair']['label'],
            pre_annihilation_separation=a['states'][0]['separation'],
            bridge_gaps={k:smallest(mid,k) for k in mid['gaps']},endpoint_gaps={k:smallest(end,k) for k in end['gaps']},
            w1={k:label(mid,k) for k in mid['cycles']})
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    r4,r6=summary['cutoffs'][4],summary['cutoffs'][6]
    lines=['# v040 — Gated checks of the uploaded full-kinetic variant','',
      '**The reported labels survive the new gated checks at N=4 and N=6.**',
      'The second braid and first flat-pair annihilation now have sampled path',
      'replays in the uploaded `tbg_ref` full variant. The earlier gapped candidate',
      'at ratio 1.04 also retains the measured endpoint band labels. Two numerical',
      'attributions in v039 require correction; none changes these labels.','',
      'These runs use one Hamiltonian engine and the separately developed v038',
      'measurement harness. They do not establish full-kinetic path agreement',
      'between both Hamiltonian engines. The uploaded `bm_strain.py` still has no',
      'matching full-kinetic option.','',
      '## Paths and checkpoints','',
      '| Measurement | N=4 | N=6 |','|---|---:|---:|',
      f"| Braid-2 center-segment crossing, ratio | {r4['braid_crossing']:.9f} | {r6['braid_crossing']:.9f} |",
      f"| First flat annihilation, T | {r4['annihilation']:.9f} | {r6['annihilation']:.9f} |",
      f"| Shift from previous original-model root | {r4['annihilation_shift']:+.9f} | {r6['annihilation_shift']:+.9f} |",
      f"| Pre-annihilation pair separation at T=-0.70 | {r4['pre_annihilation_separation']:.7f} | {r6['pre_annihilation_separation']:.7f} |",'',
      'Braid 2 tracks the two upper nodes and four upper-next nodes at eleven',
      'parameter states. The spatial comparison flips SAME to OPPOSITE; each',
      'temporally carried individual charge is unchanged. The crossing node lies',
      'on the center-to-center segment and the singular comparison is rejected.',
      'Parameter-step halving, loop mesh/radius checks and spatial transport',
      'refinement agree. Crossing digits describe numerical roots at each cutoff,',
      'not a cutoff-converged physical critical ratio.','',
      'The first annihilation has two distinct approaching roots, opposite charges,',
      'a derivative-refined rank-one zero, nonzero fold curvature and parameter',
      'slope, and positive refined gaps on the open side. Failure to find a node',
      'is never used as the event criterion. At T=-0.74 the separately checked',
      'upper pair is SAME at both cutoffs. The old-to-new root shift is about',
      '0.0016, not the 0.01 claimed from overlapping coarse brackets. That',
      'comparison includes both original-versus-exact reciprocal geometry and',
      'the kinetic change; it is not a single-term attribution.','',
      '## Earlier endpoint and recorded endpoint','',
      'Earlier candidate: A=-0.35, B=-0.4, T=-1.8, phi=80 degrees, ratio=1.04.',
      'Recorded endpoint: A=-0.30, same B/T/phi, ratio=1.10.',
      'Both use theta=1.05 degrees and total heterostrain 0.003.','',
      '| State | N | Lower gap | Flat gap | Upper gap | Upper-next gap | Below-lower gap |',
      '|---|---:|---:|---:|---:|---:|---:|']
    for name,key in [('Earlier candidate','bridge_gaps'),('Recorded endpoint','endpoint_gaps')]:
        for N,r in [(4,r4),(6,r6)]:
            g=r[key];lines.append(f"| {name} | {N} | "+' | '.join(f'{g[k]:.6f}' for k in ['lower','flat','upper','next','outer_lower'])+' |')
    lines += ['', 'Gaps are meV. Each uses bounded multistart refinement on 18x18 and 24x24',
      'grids with explicit edge/corner and opposite-seam seeds. These are finite',
      'numerical searches, not certified continuum lower bounds.','',
      'At both states and cutoffs: lower remote w1=(0,0), lower flat w1=(1,0),',
      'upper flat w1=(0,0), upper remote w1=(0,0), flat pair w1=(1,0). Each',
      'cycle sign passes meshes 64/128, two offsets, both axes, external isolation,',
      'and sewing norm/overlap gates. No Euler class is assigned to the',
      'non-orientable flat pair. The earlier candidate remains a supported',
      'checkpoint under the uploaded full variant; its entire connecting cleanup',
      'route has not been rerun under that variant.','',
      '## Corrections with direct evidence','',
      '1. **Close-pair under-count: candidate coverage.** The instrumented N4',
      '   24x24 global search creates one local-minimum seed, which passes its cone',
      '   checks. It never proposes the other root. The observed failure occurs',
      '   before deduplication or cone rejection. Two local seeds recover both',
      '   roots and opposite charges. This does not prove a general completeness',
      '   threshold at separation 0.05, or identify the uninstrumented N6 cause.',
      '2. **Endpoint lower-gap search.** The uploaded N4 search returns',
      '   23.17645445 meV; explicit boundary seeds find 23.03669106 meV at',
      '   (0.99217659,0.29298133). Direct evaluation with the same uploaded',
      '   Hamiltonian confirms the lower value. This is a search correction.',
      '3. **Kinetic convention.** `full` uses V R^T and a lab-component gauge.',
      '   The explicitly specified rotated-bond monolayer expansion instead',
      '   gives R^T V and a crystal-to-lab transformed gauge. The independent',
      '   monolayer checks quantify the difference; it is not silently applied',
      '   to any primary replay. See STRAIN_NOTE.md and the separately named',
      '   `lab_nn_full` adapter.','',
      '## Ranked next actions','',
      '1. Reconcile the two v038 entries and adopt the corrected search attribution',
      '   and gap values. Preserve the original records as provenance.',
      '2. Declare the retained orders in strain and twist, and the interlayer',
      '   tunneling assumptions. Implement that same declared model in both',
      '   engines before claiming full-model cross-implementation agreement.',
      '3. Rerun the connecting cleanup and remaining collision windows under the',
      '   chosen full variant; then tackle the earlier strain-direction and',
      '   transfer legs with basis-aware continuation. Existing old-model paths',
      '   remain evidence for those specifically named models.',
      '4. Retain two-seed continuation, explicit boundary seeds and per-node',
      '   diagnostics. Improve global candidate coverage; lowering a merge',
      '   threshold does not repair the reproduced failure.','',
      '## Validation and limits','',
      'All 22 supplied tests pass; six new adapter/gate tests pass. The independent',
      'monolayer program passes 36 checks, and nine comparisons quantify the',
      'frame-convention difference. Raw records, fixed protocol/source hashes,',
      'input inventory, environment, and the instrumented search are included.',
      'See SOURCE_REVIEW.md for the findings table and deep-read cutoff.','',
      'This is not an end-to-end campaign certification, an N>6 convergence study,',
      'a proof excluding every unsampled node, or a complete physical strain',
      'model. The lab-frame sensitivity adapter is tested but has no campaign',
      'replay in this package. A static flag or a successful regression test is',
      'triage evidence; accepted numerical conclusions require their own guards.','']
    (ROOT/'REPORT.md').write_text('\n'.join(lines))
    share=f'''TEAM SHARE — v040 follow-through on the v039 addendum

The N=6 checkpoint labels hold. We have now also passed the second-braid and
first-annihilation path gates in the uploaded tbg_ref kinetic='full' variant,
at N=4 and N=6. The earlier gapped candidate at ratio 1.04 keeps w1=(1,0) on
flat1 and trivial flat2, matching the recorded endpoint.

Two corrections are established by direct reruns. The N4 global node search
misses the close pair because its coarse grid supplies only one candidate
seed; no merge or cone rejection removes the second node. At the endpoint,
boundary seeding lowers the N4 lower-gap estimate from 23.17645 to 23.03669
meV in the same Hamiltonian. Neither correction changes the checked labels.

The located first-annihilation roots are {r4['annihilation']:.8f} (N4) and
{r6['annihilation']:.8f} (N6). The shift from our previous original-model roots
is about 0.0016, not 0.01. Coarse overlapping brackets could not establish
the earlier claimed shift.

Scope: these new paths use one Hamiltonian engine. The uploaded original
engine still lacks a matching full-kinetic option. The tensor rotation order
and gauge frame also need an explicit convention; the separately tested
lab-frame adapter has not been substituted into the replay. Connecting
cleanup/earlier legs and strain-dependent tunneling remain open.

Package: both v038 records preserved separately, untouched v039 input,
new source, raw gated measurements, 22 supplied tests plus six new checks,
and the ranked handoff. No independent physical-bilayer validation is claimed.
'''
    (ROOT/'TEAM_SHARE_v040.md').write_text(share)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':build()
