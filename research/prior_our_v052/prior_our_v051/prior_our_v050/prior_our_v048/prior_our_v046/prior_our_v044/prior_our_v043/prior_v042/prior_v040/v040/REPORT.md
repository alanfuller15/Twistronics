# v040 — Gated checks of the uploaded full-kinetic variant

**The reported labels survive the new gated checks at N=4 and N=6.**
The second braid and first flat-pair annihilation now have sampled path
replays in the uploaded `tbg_ref` full variant. The earlier gapped candidate
at ratio 1.04 also retains the measured endpoint band labels. Two numerical
attributions in v039 require correction; none changes these labels.

These runs use one Hamiltonian engine and the separately developed v038
measurement harness. They do not establish full-kinetic path agreement
between both Hamiltonian engines. The uploaded `bm_strain.py` still has no
matching full-kinetic option.

## Paths and checkpoints

| Measurement | N=4 | N=6 |
|---|---:|---:|
| Braid-2 center-segment crossing, ratio | 0.990534221 | 0.990761584 |
| First flat annihilation, T | -0.713549636 | -0.713477622 |
| Shift from previous original-model root | +0.001591262 | +0.001578499 |
| Pre-annihilation pair separation at T=-0.70 | 0.0194155 | 0.0193460 |

Braid 2 tracks the two upper nodes and four upper-next nodes at eleven
parameter states. The spatial comparison flips SAME to OPPOSITE; each
temporally carried individual charge is unchanged. The crossing node lies
on the center-to-center segment and the singular comparison is rejected.
Parameter-step halving, loop mesh/radius checks and spatial transport
refinement agree. Crossing digits describe numerical roots at each cutoff,
not a cutoff-converged physical critical ratio.

The first annihilation has two distinct approaching roots, opposite charges,
a derivative-refined rank-one zero, nonzero fold curvature and parameter
slope, and positive refined gaps on the open side. Failure to find a node
is never used as the event criterion. At T=-0.74 the separately checked
upper pair is SAME at both cutoffs. The old-to-new root shift is about
0.0016, not the 0.01 claimed from overlapping coarse brackets. That
comparison includes both original-versus-exact reciprocal geometry and
the kinetic change; it is not a single-term attribution.

## Earlier endpoint and recorded endpoint

Earlier candidate: A=-0.35, B=-0.4, T=-1.8, phi=80 degrees, ratio=1.04.
Recorded endpoint: A=-0.30, same B/T/phi, ratio=1.10.
Both use theta=1.05 degrees and total heterostrain 0.003.

| State | N | Lower gap | Flat gap | Upper gap | Upper-next gap | Below-lower gap |
|---|---:|---:|---:|---:|---:|---:|
| Earlier candidate | 4 | 30.808192 | 1.401486 | 1.064915 | 7.870238 | 31.206446 |
| Earlier candidate | 6 | 30.950515 | 1.317509 | 1.124172 | 7.901965 | 30.989526 |
| Recorded endpoint | 4 | 23.036691 | 2.862740 | 3.335716 | 10.821175 | 33.611443 |
| Recorded endpoint | 6 | 23.188860 | 2.769542 | 3.392809 | 10.855652 | 33.364588 |

Gaps are meV. Each uses bounded multistart refinement on 18x18 and 24x24
grids with explicit edge/corner and opposite-seam seeds. These are finite
numerical searches, not certified continuum lower bounds.

At both states and cutoffs: lower remote w1=(0,0), lower flat w1=(1,0),
upper flat w1=(0,0), upper remote w1=(0,0), flat pair w1=(1,0). Each
cycle sign passes meshes 64/128, two offsets, both axes, external isolation,
and sewing norm/overlap gates. No Euler class is assigned to the
non-orientable flat pair. The earlier candidate remains a supported
checkpoint under the uploaded full variant; its entire connecting cleanup
route has not been rerun under that variant.

## Corrections with direct evidence

1. **Close-pair under-count: candidate coverage.** The instrumented N4
   24x24 global search creates one local-minimum seed, which passes its cone
   checks. It never proposes the other root. The observed failure occurs
   before deduplication or cone rejection. Two local seeds recover both
   roots and opposite charges. This does not prove a general completeness
   threshold at separation 0.05, or identify the uninstrumented N6 cause.
2. **Endpoint lower-gap search.** The uploaded N4 search returns
   23.17645445 meV; explicit boundary seeds find 23.03669106 meV at
   (0.99217659,0.29298133). Direct evaluation with the same uploaded
   Hamiltonian confirms the lower value. This is a search correction.
3. **Kinetic convention.** `full` uses V R^T and a lab-component gauge.
   The explicitly specified rotated-bond monolayer expansion instead
   gives R^T V and a crystal-to-lab transformed gauge. The independent
   monolayer checks quantify the difference; it is not silently applied
   to any primary replay. See STRAIN_NOTE.md and the separately named
   `lab_nn_full` adapter.

## Ranked next actions

1. Reconcile the two v038 entries and adopt the corrected search attribution
   and gap values. Preserve the original records as provenance.
2. Declare the retained orders in strain and twist, and the interlayer
   tunneling assumptions. Implement that same declared model in both
   engines before claiming full-model cross-implementation agreement.
3. Rerun the connecting cleanup and remaining collision windows under the
   chosen full variant; then tackle the earlier strain-direction and
   transfer legs with basis-aware continuation. Existing old-model paths
   remain evidence for those specifically named models.
4. Retain two-seed continuation, explicit boundary seeds and per-node
   diagnostics. Improve global candidate coverage; lowering a merge
   threshold does not repair the reproduced failure.

## Validation and limits

All 22 supplied tests pass; six new adapter/gate tests pass. The independent
monolayer program passes 36 checks, and nine comparisons quantify the
frame-convention difference. Raw records, fixed protocol/source hashes,
input inventory, environment, and the instrumented search are included.
See SOURCE_REVIEW.md for the findings table and deep-read cutoff.

This is not an end-to-end campaign certification, an N>6 convergence study,
a proof excluding every unsampled node, or a complete physical strain
model. The lab-frame sensitivity adapter is tested but has no campaign
replay in this package. A static flag or a successful regression test is
triage evidence; accepted numerical conclusions require their own guards.
