# Our v051 — extra flat-pair preparation events

[self-tested] Both extra flat-pair events pass the new local-domain gate in both engines at N4/N6. The birth and annihilation windows join at A=0.2, B=0. The original flat pair remains separately resolved outside the local rectangle. These results close two preparation events, not the whole preparation route.

| event | engine / geometry | N | fold parameter | near-open local gap (meV) |
|---|---|---:|---:|---:|
| annihilation B | bm_lab / linear | 4 | -0.0339767312 | 0.05190182 |
| annihilation B | bm_lab / linear | 6 | -0.0339521522 | 0.05189507 |
| annihilation B | ref_lab / exact | 4 | -0.0339759867 | 0.05190235 |
| annihilation B | ref_lab / exact | 6 | -0.0339514088 | 0.05189559 |
| birth A | bm_lab / linear | 4 | 0.1763069111 | 0.06532289 |
| birth A | bm_lab / linear | 6 | 0.1763243698 | 0.06532112 |
| birth A | ref_lab / exact | 4 | 0.1763071916 | 0.06532331 |
| birth A | ref_lab / exact | 6 | 0.1763246497 | 0.06532154 |

Across the accepted windows, the smallest located boundary gap is 0.87034599 meV, the smallest local open-side gap is 0.05189507 meV, and the nearest original root is 0.13654035 fractional-coordinate units outside the rectangle. The largest original-root residual is 1.19e-12 meV. Shared-state root joins are at most 0. There were 0 charge-station mesh fallbacks.

## What was measured

Eight accepted windows contain 72 root-state records, 16 mesh/radius charge measurements (all OPPOSITE), 96 boundary/original-pair station evaluations and 16 local open-side station evaluations. Each window has nine distinct two-root states, rank-one fold refinement, curvature/parameter-slope checks, two charge stations, and two bounded local open-side searches. The common A=0.2,B=0 point is measured in both windows for each engine/cutoff: counts include four repeated common-state records and charge measurements. They are not independent additional parameter coverage.

The local rectangle is f1=[0.42,0.63], f2=[0.52,0.63]. Boundaries use 24/48 edge grids and bounded minima; local interiors use closed 17/25 grids with bounded gradient refinements and explicit corner/fold seeds. Original-root controls at all 12 stations per window prevent a local opening being promoted to a global flat gap. Charge is checked at the first and last root state, not all 72 records. No parameter-carried absolute orientation is claimed.

Both engines explicitly use lab_nn_full and constant w0,w1. BM retains linear reciprocal geometry with cutoff_tol=1e−6; TBG uses exact reciprocal geometry with cutoff_tol=1e−9. Their source bytes are unchanged from v050. The two engines share the new measurement harness. Pilot locations were exploratory; source and protocol hashes were frozen before the accepted N4/N6 measurements. Both N4 engines passed before either N6 worker started.

## What changed in the gate

Using the old full-chart positive-flat-gap requirement would be invalid here: the original flat nodes remain on the open side of each extra-pair event. The new gate requires a bounded local minimum, a positive sampled/refined boundary, roots away from the boundary, and explicit original roots outside it. It is a separate, named local-event claim. The older global-gap gates and earlier accepted records are unchanged.

Twenty-four tests pass: ten local-domain synthetic/failure tests, nine publication-record acceptance/mutation tests and five inherited ledger tests. The Hamiltonians were not changed, so the 31 supplied regression tests from v050 were not repeated; that prior result is retained as historical evidence, not counted as a new test run. The new gate rejects boundary/interior zeros, optimizers escaping the domain, nonfinite values, missing records, changed scope, wrong domains and original roots entering the local rectangle.

## Limits and next work

Boundary positivity and open-side minima are finite numerical searches, not analytic interval certificates. Narrow unseeded minima or events between parameter samples cannot be ruled out. These are local fold windows and sampled root continuations, not a complete global node inventory, a full preparation frame replay or an Euler-class calculation. No established campaign topology label was revised; the new extra-pair charges are opposite at the measured stations.

Next: follow both lower-gap roots backward to locate their preparation birth, then complete the original-flat-pair preparation continuation with the frame/root join into v044, and measure the separate lower unlink collision. N4/N6 differences are sampled cutoff shifts, not infinite-cutoff error bounds. Physical-bilayer validation remains outside the campaign. Recipient consumption is [unconfirmed].
