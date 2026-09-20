# v044 — Braid 1 joined to the accepted connections

The earlier route now reaches our accepted v043 starting frames in both engines at N=4 and N=6. All 148 primary sampled states pass. Braid 1 changes the spatial flat-pair label SAME to OPPOSITE at a located upper-node crossing. Deepening B and then changing T retains OPPOSITE and joins the previously measured route to the first annihilation. Individual charges carried in parameter space remain constant.

| Engine | Geometry | N | Center-path crossing B | Shifted-path crossing B (delta f1=0.012) | Final U1 offset | Endpoint root mismatch |
|---|---|---:|---:|---:|---:|---:|
| bm_lab | linear | 4 | -0.2901737962 | -0.2799795363 | 0.0165373 | 1.78e-15 |
| bm_lab | linear | 6 | -0.2901702643 | -0.2799791809 | 0.0160936 | 1.11e-15 |
| ref_lab | exact | 4 | -0.2901753967 | -0.2799809816 | 0.0165369 | 2.98e-15 |
| ref_lab | exact | 6 | -0.2901718633 | -0.2799806247 | 0.0160932 | 2.34e-15 |

The critical B depends on the declared spatial comparison path; the shifted-path control is not a separate physical transition. At both located crossings the selected two-band frame rejects the singular path. Quoted digits identify finite-cutoff roots, not physical precision.

The center-path crossing also changes with the declared kinetic/gauge prescription. The historical v037 original/no-tensor value is about -0.28594 and its legacy (I-E)R^T reference value about -0.28795. These accepted historical values are retained with their model tags; they are not silently relabeled lab_nn_full. Exact differences are recorded in SUMMARY.json. Neither comparison reverses the checked endpoint SAME/OPPOSITE labels.

## Route and gate

Fixed theta=1.05 degrees, eps=0.003, A=0.2, phi=0, w0/w1=0.8, kinetic=lab_nn_full. Start B=-0.25, T=0. Follow B to -0.30 in 20 intervals, deepen B to -0.40 in eight, then T to -0.40 in eight. Coordinates remain unwrapped. The flat and upper pairs are tracked throughout; the lower pair is tracked through the B legs only. Its later annihilation is not inferred from a failed search and is not claimed measured here.

The gate retains the v043 loop mesh/radius checks, spatial orientation checks with both exterior-gap minima refined, fine/coarse parameter orientation checks, eigenpair and reality checks, distinct-root and jump guards, and immutable JSON/frame commits. Endpoint joins compare roots and two-plane overlaps and record the per-node orientation needed to match the earlier frame initialization. A different absolute charge sign from an arbitrary starting frame is not a label change.

Smallest resolved spatial exterior gap at a sampled state: 0.0155431 meV. Minimum spatial overlap: 0.98573792; minimum parameter overlap: 0.99430530. Maximum tracked-node gap residual: 1.51e-12 meV.

## Partner update and matched geometry

The incoming partner v043 contains the adopted v042 guard patch verbatim. All 29 supplied tests and ten stronger guard regressions pass. Twenty-four complete operator comparisons show exact-geometry agreement to about 1.4e-12 meV and bitwise preservation of the historical linear matrices at the checked states. See SOURCE_REVIEW.md for scope, API wording and minor record corrections.

One structural qualification remains: cutoff padding is 1e-6 in BM and 1e-9 in TBG. At N=4, eps=0.003 and phi=15.843560625 degrees, the same exact reciprocal geometry gives dimensions 196 and 188 because two indices lie between those margins. The claim that only the estimators differ is therefore too broad. The optional fixes/ patch adds an explicit common cutoff_tol while preserving both historical defaults; eight tests pass. It is not used in these primary replays. This counterexample does not invalidate the reported agreements at the checked campaign states.

The primary continuations keep BM linear and TBG exact to join their existing chains without silently changing geometry. Separate BM exact controls locate the same center and shifted crossing roots as TBG exact:

| N | Path shift | BM exact B | TBG exact B | Difference |
|---:|---:|---:|---:|---:|
| 4 | 0.0 | -0.2901753967 | -0.2901753967 | 2.94e-15 |
| 4 | 0.012 | -0.2799809816 | -0.2799809816 | 9.44e-16 |
| 6 | 0.0 | -0.2901718633 | -0.2901718633 | 3.89e-15 |
| 6 | 0.012 | -0.2799806247 | -0.2799806247 | -2.44e-15 |

These controls cover roots and singular-path rejection; they are not a third full-path replay. Both Hamiltonian engines use our common measurement harness here. Agreement of matched operators does not constitute a fresh comparison of the two legacy topological estimators.

## What the combined record supports

Our v044 early route joins our v043 pre-annihilation connection, which joins the v042 first-annihilation window. The accepted post-transfer state joins our v043 later connection into the v042 braid-2 window. Endpoint frame orientations are explicitly reconciled. This is a connected set of sampled windows from braid 1 through braid 2 under each recorded geometry choice.

Remaining work: the cleanup and later collision windows after braid 2; any claim about the lower-pair unlinking collision itself; the earlier preparation from the original v023 baseline; a named strain law for w0 and w1; N>6 endpoint convergence and physical-bilayer validation. The two v043 contributions remain separate in the package. No historical linear-geometry result is relabeled exact.

Finite parameter/momentum sampling, finite cutoff and common conceptual/harness assumptions remain limits. This is not an interval proof, an exhaustive node inventory or a completed full campaign. Source hashes, records, frames, event controls, tests and the exact review cutoff accompany the result.
