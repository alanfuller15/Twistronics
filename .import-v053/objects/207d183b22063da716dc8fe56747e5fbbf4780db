# TWISTRONICS LOG — v041 — v040 disposition; one declared model in both engines

**Scope.** Response to the team's v040 reconciled package. (a) Its path replays of braid 2 and the first annihilation in the `tbg_ref` full variant are adopted. (b) Its three corrections to v039 are accepted. (c) Its ranked action 2, "declare the model and implement it in both engines", is done: the convention in `STRAIN_NOTE.md` is now `kinetic='lab_nn_full'` in both `bm_strain` and `tbg_ref`, and the two engines agree to \(10^{-6}\) in node position for every kinetic option. (d) The source-review items on the estimator are closed. New/changed: `bm_strain.py` (kinetic option), `tbg_ref.py` (explicit kinetic, `lab_nn_full`, `None` sentinel, per-node overlap log, radius bound, bounded seam-seeded `gap_min`), `test_tbg_ref.py` (+5), `cross_kinetic.py`.

---

## 1. Adopted from v040

- **Braid 2 path replay**, `tbg_ref` `kinetic='full'`: eleven parameter states, two upper and four upper-next nodes tracked; the spatial comparison flips SAME→OPPOSITE at the center-segment crossing, ratio \(0.990534\) (\(N=4\)) / \(0.990762\) (\(N=6\)); carried charges unchanged; singular comparison rejected. Same structure as v037 for braid 1.
- **First annihilation** (flat pair, \(B_\tau\)): two distinct approaching roots of opposite charge, derivative-refined rank-one zero, nonzero fold curvature; root \(B_\tau^\ast=-0.71355\) (\(N=4\)) / \(-0.71348\) (\(N=6\)). Post-transfer upper pair SAME at both cutoffs.
- **Endpoint** and the earlier gapped candidate (ratio 1.04): identical per-band \(w_1\) at both cutoffs; no Euler class assigned to the non-orientable flat pair.

These are one-engine results with the team's harness; that limit is theirs and is kept here.

## 2. Corrections to v039, accepted

| v039 statement | v040 finding | corrected statement |
|---|---|---|
| §4: "both engines carry the same kinetic option" | `bm_strain` had none | false at the time; now true (§3) |
| §5: close-pair under-count "merge tolerance vs separation" | dedup threshold 0.01 < separation 0.019, so the inequality was false; the instrumented search proposes only **one** seed | the global grid never generates a second candidate: a coverage failure, not a merge or cone rejection. Two local seeds are required for any pair closer than the grid spacing; no universal 0.05 threshold is claimed |
| §1: annihilation shift "0.01" | roots \(-0.7135\) (full) vs \(-0.7120\) (original-model root) | shift \(\approx0.0016\), and it mixes the reciprocal-geometry and kinetic changes; coarse 0.01 brackets could not support the earlier number |
| §1 / §6: endpoint lower gap 23.18 / 23.19 meV | boundary seeds find 23.03669 meV at (0.99218, 0.29298) | **23.037 meV (\(N=4\))**, a second edge-minimum search correction of the same kind as v035 §2 |
| §2: "frame overlap 0.991" | `last_smin` was overwritten by the second loop | 0.991 was the second node's value only; both are now logged and the minimum is reported |

## 3. The declared model, in both engines

Lab strain \(\mathbf E_l=\mp\mathbf E/2\), layer rotation \(R_l=R(\theta_l)\), bond deformation \(F=(\mathbf I+\mathbf E_l)R_l\):

$$ h_l(\mathbf p)=\hbar v_0\,\Big[R_l^{\rm T}\big(\mathbf I+(1-\beta)\mathbf E_l\big)\,(\mathbf p-\mathbf K_l-\mathbf A_l)\Big]\cdot\boldsymbol\sigma,\qquad \mathbf A_l=R_l\,\mathbf a\!\left(R_l^{\rm T}\mathbf E_lR_l\right),\quad \mathbf a(\mathbf E)=\tfrac{\sqrt3\beta}{2a}\,(E_{xx}-E_{yy},\,-2E_{xy}), $$

i.e. the Oliva-Leyva–Naumis tensor and gauge in the layer's crystal frame, rotated to the lab (team `STRAIN_NOTE.md`; their 36-check monolayer audit: cone-metric error \(9\times10^{-6}\) vs \(7\times10^{-5}\) for the v039 order). This is `kinetic='lab_nn_full'`. `'full'` (v039 order) and `'none'` (campaign) are retained and named; `tbg_ref` no longer has a default and raises unless the option is given.

Cross-engine check, \(N=4\), 0.3 %, \(\phi=0\):

| kinetic | nodes (both engines, max diff) | remote gap `bm_strain` / `tbg_ref` (meV) | charges |
|---|---|---|---|
| none | \(8.5\times10^{-7}\) | 5.4578 / 5.4580 | same |
| full | \(8.5\times10^{-7}\) | 4.9663 / 4.9665 | same |
| **lab_nn_full** | \(8.5\times10^{-7}\) | **4.9707 / 4.9709** | same |

`lab_nn_full` − `full`: 0.004 meV, node shift \(7\times10^{-4}\): the O(\(\epsilon\theta\)) rotation terms, as predicted. Both engines now implement the same declared model to the precision of the plane-wave truncation; this closes the "one-engine" limit for anything run from here on, but not retroactively for v040's path replays.

Still unmodelled in both: strain dependence of \(w_0,w_1\), lattice relaxation. Still open: whether the joint small-angle expansion should drop the \(\epsilon\theta\) terms deliberately; the difference is below every other uncertainty in the project.

## 4. Source-review items closed

| item | change |
|---|---|
| `node_charge` returned 0 as a sentinel | returns `None`; `relative_charge` classifies, never arithmetic on the sentinel |
| `last_smin` overwritten | `smin_log` per loop; `relative_charge` reports the minimum over both |
| radius bound bypassable | \(r=\min(r_{\rm req},0.01,0.3\,{\rm sep})\) for any request; coincident seeds raise |
| `gap_min` unbounded, no seam seeds | bounded Nelder–Mead in \([0,1]^2\) from each grid candidate plus its edge/seam images and both edge projections |
| `tbg_ref` default `kinetic` selected `geom_wrong` | no default; explicit or `ValueError` |
| no loop-mesh/radius agreement gate in `node_charge` | not added here; the team harness has it, and the gate that *is* here (overlap ≥ 0.9, integer within 0.05) is the minimum, not full coverage |

Tests: 27 (17 regression, 10 cross-implementation), including one per kinetic option for cross-engine agreement, one that `tbg_ref` refuses an unspecified kinetic, and one that an invalid loop yields `None`, never 0.

## 5. Next
- Rerun the v040 path replays with `lab_nn_full` in **both** engines (now possible).
- Connecting legs (v027–v028 cleanup, v030–v031 transfer) under the declared model with two-seed continuation.
- A named strain law for \(w_0,w_1\) before any magnitude is called physical; \(N>6\) on the endpoint gaps.

## 6. Self-corrections this entry
- Four v039 statements corrected (§2); the "merge tolerance" explanation was wrong in its arithmetic, not only incomplete.
- The v039 estimator's 0-sentinel and overwritten diagnostic were exactly the kind of defect v034 §1 was meant to rule out; the gate covered the label but not the diagnostic record. Fixed.
