# v042 — The lab-frame replay in both engines

**Both engines pass the v040 replay protocol with `kinetic=lab_nn_full` at
N=4 and N=6. No checked topological label changes.** This closes the
one-engine limitation for the second-braid and first-annihilation windows,
the post-transfer checkpoint, and the two gapped checkpoints measured here.
It does not close the untraced connecting legs or certify the whole campaign.

The engine files are unchanged from the v041 upload. The Hamiltonians share
the declared first-order kinetic/gauge prescription, while retaining their
different reciprocal-geometry approximations. A separate helper patch is
provided for review; it is not used to generate these measurements.

## Decisive events

| Engine | N | Braid-2 crossing ratio | First-annihilation T |
|---|---:|---:|---:|
| bm_lab | 4 | 0.990538737 | -0.713373536 |
| bm_lab | 6 | 0.990766131 | -0.713301013 |
| ref_lab | 4 | 0.990541398 | -0.713386736 |
| ref_lab | 6 | 0.990768791 | -0.713314259 |

Braid 2 tracks the two upper nodes and four upper-next nodes through eleven
ratio states from 0.99 to 1.00, with parameter-step halving. Its spatial
comparison changes SAME to OPPOSITE as an upper-next node crosses the
center-to-center segment. Each temporally carried charge remains unchanged.
The singular comparison at the located crossing is rejected. Two loop
meshes, a halved loop radius, and transport refinement agree.

The first-annihilation window tracks two distinct flat roots through nine
states from T=-0.70 toward their meeting. Charges are OPPOSITE before the
event. The collision solves a zero with a rank-one spatial Jacobian, passes
derivative-step refinement and nonzero fold curvature/parameter-slope
checks, and has a positive refined gap on the open side. The post-transfer
upper pair at T=-0.74 is SAME in all four engine/cutoff runs. Failed node
searches are never used as evidence that a pair disappeared.

The quoted digits locate finite-cutoff numerical roots. They do not imply
physical critical parameters accurate to nine decimal places.

## Agreement and what remains different

| N | Braid-root difference (ref minus BM) | Annihilation-root difference | Max tracked braid-node difference | Max checkpoint gap difference, meV |
|---:|---:|---:|---:|---:|
| 4 | +2.661e-06 | -1.320e-05 | 3.449e-05 | 3.242e-04 |
| 6 | +2.660e-06 | -1.325e-05 | 3.734e-05 | 3.236e-04 |

BM retains `(I-E)R` reciprocal geometry; TBG uses `(I+E)^(-T)R`.
The remaining agreement error is therefore not solely plane-wave cutoff
error. Sixteen assembly checks cover baseline, annihilation, braid and
endpoint parameters at both cutoffs and two momentum points, including
an unwrapped point. After matching only q/G on disposable diagnostic
objects, the maximum matrix difference is about 1.6e-12 meV. Without
that replacement the sampled central-band differences reach 5.6e-4 meV.
The primary replays keep the original geometry in each engine.

## Gapped checkpoints

Earlier candidate: A=-0.35, B=-0.40, T=-1.8, phi=80 degrees, ratio=1.04.
Recorded endpoint: A=-0.30, same B/T/phi, ratio=1.10.
Both use theta=1.05 degrees and total heterostrain 0.003.

| State | Engine | N | Lower | Flat | Upper | Upper-next | Below-lower |
|---|---|---:|---:|---:|---:|---:|---:|
| Earlier candidate | bm_lab | 4 | 30.800373 | 1.408419 | 1.065298 | 7.870500 | 31.205803 |
| Earlier candidate | bm_lab | 6 | 30.943055 | 1.324462 | 1.124590 | 7.902231 | 30.988921 |
| Earlier candidate | ref_lab | 4 | 30.800159 | 1.408551 | 1.064974 | 7.870545 | 31.205954 |
| Earlier candidate | ref_lab | 6 | 30.942839 | 1.324600 | 1.124266 | 7.902276 | 30.989073 |
| Endpoint | bm_lab | 4 | 23.029393 | 2.869727 | 3.335681 | 10.821556 | 33.611062 |
| Endpoint | bm_lab | 6 | 23.181552 | 2.776527 | 3.392819 | 10.856038 | 33.364255 |
| Endpoint | ref_lab | 4 | 23.029191 | 2.869924 | 3.335359 | 10.821606 | 33.611207 |
| Endpoint | ref_lab | 6 | 23.181348 | 2.776726 | 3.392498 | 10.856087 | 33.364402 |

All gaps are meV. Bounded multistart minimization uses grids 18x18 and
24x24, explicit edge/corner seeds, and opposite-seam seeds. Agreement
between searches is a numerical check, not a rigorous continuum lower bound.

| Band/group | w1 along k1 | w1 along k2 |
|---|---:|---:|
| Lower remote | 0 | 0 |
| Lower flat | 1 | 0 |
| Upper flat | 0 | 0 |
| Upper remote | 0 | 0 |
| Flat pair | 1 | 0 |

This table holds at both checkpoints in both engines and cutoffs. Each
cycle passes meshes 64/128, offsets 0 and 0.5, both directions, external
isolation, and sewing norm/overlap gates. The earlier candidate is therefore
still a supported endpoint candidate. Its connecting cleanup route under
this declared model remains to be traced. No Euler class is assigned to the
non-orientable flat pair.

## Convention sensitivity is observable-specific

For TBG, comparing the new lab-frame result to v040 full at fixed cutoff:

| N | Braid crossing change | Annihilation T change | Endpoint flat-gap change, meV |
|---:|---:|---:|---:|
| 4 | +7.177e-06 | +1.629e-04 | +0.007184 |
| 6 | +7.207e-06 | +1.634e-04 | +0.007184 |

The lab-frame annihilation root shifts by about 1.6e-4 relative to full,
while its new N4-to-N6 shift is +7.248e-05
(the prior full shift was +7.201e-05).
The frame-convention effect is consequently larger than this cutoff
comparison for that event. The baseline 0.004 meV remote-gap sensitivity
should not be generalized to “below every other uncertainty.” None of
these measured shifts changes the checked labels.

The v041 adoption table also contains a transcription error: the previous
original-model annihilation roots were -0.71514090/-0.71505612, not
-0.7120. Its accepted approximately +0.0016 change to v040 full remains
correct. This correction concerns the historical comparison, not the new
lab-frame roots above.

## Follow-through and next actions

1. Adopt these two-engine lab-frame results for the explicitly tested
   windows and checkpoints. Preserve model, geometry, path lift and cutoff
   beside each number; do not rename older results retroactively.
2. Trace the earlier connecting legs with two distinct seeds and basis-aware
   overlap transport as phi changes the reciprocal basis. Then rerun the
   remaining cleanup/collision legs under the same declared convention.
3. Apply/review the small public-helper patch: optimizer failure must raise,
   never return positive infinity as a gap; radii must be positive and
   finite. Expanded boundary/inward seeds recover an edge minimum still
   missed by two agreeing grids in the uploaded helper. Ten regression
   cases accompany the patch. Primary measurements
   already use a separate gate and are unaffected by the patch.
4. State the strain law for w0 and w1 and relaxation assumptions before
   treating magnitudes as physical; then extend endpoint gap convergence
   beyond N6. Numerical cutoff refinement cannot resolve model uncertainty.

Five historical reference drivers also require explicit kinetic options
after the intentional API change. SOURCE_REVIEW.md lists this and the
remaining helper limitations, with the exact review cutoff.

## Evidence and limits

Twenty primary jobs pass: five tasks for each engine/cutoff combination.
The supplied 27 tests pass; seven new integration checks and ten optional
helper-patch checks pass. Source/input hashes, fixed protocol, preflight
seeds, environment, and raw checkpointed measurements are included. Two
primary numerical processes were used, with one BLAS thread each.

The report gate found one incomplete saved N4 TBG endpoint record despite
a completion line in the run log. The cause was not established. The
incomplete snapshot is preserved, that one job was rerun under the same
source hashes and tolerances, and the report uses the complete replacement.
No acceptance condition was relaxed.

The measurements are sampled path continuations and finite momentum
searches, not proofs over a continuum. Both Hamiltonians share the same
conceptual prescription and measurement harness/libraries; their agreement
guards implementation differences, not a shared conceptual error. No
end-to-end campaign, N>6 convergence, complete quaternion algebra, or
physical strained-bilayer validation is claimed.
