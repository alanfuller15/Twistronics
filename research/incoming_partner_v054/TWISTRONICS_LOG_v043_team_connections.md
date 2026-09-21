# v043 — Connecting the accepted windows

Both uploaded v041 engines use `kinetic=lab_nn_full` without modification. The two routes below carry two distinct roots and their real two-band frames at N=4 and N=6. These results join the v028 checkpoint to the accepted first-annihilation window and the post-transfer checkpoint to the accepted second-braid window.

| Route | Engine | N | States | Spatial label(s) | Smallest resolved path exterior gap (meV) | Maximum endpoint root mismatch |
|---|---|---:|---:|---|---:|---:|
| pre_ann | bm_lab | 4 | 19 | OPPOSITE | 1.58841 | 3.02e-14 |
| pre_ann | bm_lab | 6 | 19 | OPPOSITE | 1.54267 | 3.07e-14 |
| pre_ann | ref_lab | 4 | 19 | OPPOSITE | 1.58838 | 4.39e-14 |
| pre_ann | ref_lab | 6 | 19 | OPPOSITE | 1.54264 | 2.87e-14 |
| post_ann | bm_lab | 4 | 21 | SAME | 0.0531269 | 5.08e-15 |
| post_ann | bm_lab | 6 | 21 | SAME | 0.0754708 | 6.56e-15 |
| post_ann | ref_lab | 4 | 21 | SAME | 0.0533893 | 1.34e-15 |
| post_ann | ref_lab | 6 | 21 | SAME | 0.0757326 | 1.04e-14 |

All 160 primary sampled states pass. Relative labels agree between both engines and cutoffs. Individual carried charges remain constant within each run. No loop-resolution fallback was needed in this batch.

Maximum cross-engine node difference over the sampled states: 5.02929e-06 in fractional reciprocal coordinates. Maximum N=4 to N=6 node shift: 0.00036118. These are finite-cutoff comparisons, not error bounds against an infinite-basis result.

## Declared paths

Fixed throughout: theta=1.05 degrees, eps=0.003, B=-0.4. Coordinates stay unwrapped.

- Pre-annihilation flat pair: start A=0.2, T=-0.4, phi=0, ratio=0.8; phi to 60; A to 0; phi to 65; T to -0.70. The 19 states end on the v042 annihilation starting roots.
- Post-annihilation upper pair: start A=0, T=-0.74, phi=65, ratio=0.8; phi to 80; T to -0.8; ratio to 0.90, 0.98, 0.99. The 21 states start on the v042 post-transfer roots and end on the v042 second-braid starting roots.

## Changing-basis transport

The pullback identifies fixed dimensionless moire-cell coordinates and removes each declared Bloch/layer phase. Periodic-envelope coefficients are indexed by (layer,m,n,real-spinor index), with absent coefficients zero in a common space. We intersect indices before calculating overlap; we do not compare raw array rows or renormalize away discarded weight. This is an explicit numerical bundle identification, not a claim about physical time evolution in laboratory coordinates.

Across fine and coarse parameter links, minimum singular overlap = 0.898280433; maximum lost frame norm eigenvalue = 0.000529594167 (gate <=0.02).
Minimum spatial overlap = 0.985533923; maximum node residual gap = 1.62e-12 meV.

## Checks and interpretation

Parameter transport uses the fine schedule and a schedule with every other point omitted within each leg. Spatial comparisons use 128/256 base intervals, local minimization of both exterior gaps, and graded points around resolved minima. Transport refinement checks orientation agreement, not convergence of the full rotation matrix. Charge loops use 64/128 points plus half-radius agreement; only phase-resolution rejection can increase the loops to 256/512 and then 1024/2048. Every rejected refinement stage is retained. The individual charges transported in parameter space are recorded separately from the spatial SAME/OPPOSITE label. No expected label is used to force numerical acceptance.

Each accepted step commits its JSON record and numerical frames together by a directory rename. The JSON binds the array file with SHA-256; resume verifies protocol, source and anchor hashes, state identity, completeness and contiguous steps. The final report re-reads those records and requires exact agreement with each completed summary.

Seven new tests pass: six basis/transport checks and one checkpoint integrity check. A separate real numerical experiment splits the three-state N=4 BM pilot after its first state, resumes it, and reproduces every saved frame bit for bit and every diagnostic except wall-clock time and the array-container hash. Its raw output is retained under provenance/resume_probe/. Prior v042 tests are included as historical evidence, not counted as newly rerun tests.

## Scope and limits

This batch has finite sampling in momentum and parameters, and a finite basis cutoff. Agreement of two meshes is evidence of resolution, not an interval proof, exhaustive node inventory, or proof of no missed event between samples. Continuation preserves the two followed roots; it does not assert a global node count. Comparisons depend on the declared pullback and spatial path.

Still open under lab_nn_full: the first-braid replay and its deepening/unlinking legs into the v028 checkpoint; the cleanup and later collision windows after braid 2. The existing accepted first-annihilation and second-braid windows are reused as anchors, not recomputed here. A named strain law for w0 and w1, N>6 endpoint convergence and physical-bilayer validation remain separate tasks. Both Hamiltonian engines share an author and conceptual assumptions, and these replays use a common measurement/gating harness; agreement does not remove shared model or harness errors.

Independently initialized frame orientations can reverse every signed charge in one run. Cross-engine comparisons therefore use relative SAME/OPPOSITE labels and within-run charge constancy; absolute signs are not treated as invariant across those initializations.

See SUMMARY.json for the full numerical ranges, cross-engine/cutoff differences, refinement history and root-identity matches. PLAN.json freezes the primary source and anchors; immutable records and frames are under results/.
