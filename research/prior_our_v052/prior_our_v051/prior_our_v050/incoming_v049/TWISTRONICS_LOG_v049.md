# TWISTRONICS LOG — v049 — Anchors for the last two windows; the O(εθ) term checked

**Scope.** (a) Anchors for the team's `NEXT_SEQUENCE` items 1–2, the later flat-pair birth and the final annihilation, under the declared model in both engines, with both events bracketed by the fold law. (b) An independent computation of the finite-twist mean-radius term the team used to qualify v045. New: `anchors_final.py`, `final_local.py`, `epstheta_check.py`, `anchors_final_N4.json`; `ledger.py` reads the new anchors.

`lab_nn_full`, bm exact, \(N=4\), \(\phi=80^\circ\), \(B_{\rm sym}=-0.40\), \(B_\tau=-1.8\).

---

## 1. Flat-pair birth window (\(A=-0.35\), \(w_0/w_1:1.10\to1.05\))

| \(w_0/w_1\) | roots (bm; ref within \(10^{-11}\)) | separation | label |
|---|---|---|---|
| 1.10 | (0.68048, 0.96618), (0.68196, 0.87264) | 0.0936 | OPPOSITE |
| 1.08 | (0.68135, 0.94509), (0.67919, 0.88473) | 0.0604 | OPPOSITE |
| 1.060 | (0.68001, 0.92294), (0.67692, 0.89809) | 0.02504 | (local search) |
| 1.058 | (0.67962, 0.92033), (0.67682, 0.89985) | 0.02068 | |
| 1.056 | (0.67911, 0.91741), (0.67679, 0.90193) | 0.01565 | |
| 1.054 | one root found at (0.67839, 0.91364); partner unresolved | | |
| 1.052 | none; box minimum 0.116 meV | | |

Fold law: \(\text{sep}^2\) is linear in the parameter, slope 0.0955 per unit ratio, giving **birth at \(w_0/w_1\approx1.0534\)** near (0.678, 0.913). The single root at 1.054 is the pair below the local search's resolution, not a lone node.

## 2. Final annihilation window (\(w_0/w_1=1.10\), \(A:-0.35\to-0.31\))

| \(A\) | roots | separation | label |
|---|---|---|---|
| −0.35 | (0.68048, 0.96618), (0.68196, 0.87264) | 0.0936 | OPPOSITE |
| −0.33 | (0.67868, 0.94493), (0.67969, 0.89533) | 0.0496 | OPPOSITE |
| −0.320 | (0.67779, 0.93003), (0.67824, 0.91068) | 0.01935 | OPPOSITE |
| −0.318 | (0.67784, 0.91741), (0.67770, 0.92338) | 0.00598 | (local search) |
| −0.316 | none; box minimum 0.305 meV | | |

Fold law: slope 0.169 per unit \(A\), **annihilation at \(A^\ast\approx-0.3178\)** near (0.678, 0.920). Under `kinetic='none'` (v033) the pair was gone by \(-0.30\) with no finer bracket; this is the first location of the event.

Both windows: the tracker-collapse signature (two refiners on one root with zero gap) appeared at 1.06 and at −0.31 in the coarse pass and was resolved by the local search in each case, as the v039 §5 rule requires. Engines agree on every root to \(\le1.3\times10^{-11}\) where both find the pair. These are fixed-parameter anchors; the team's fold checks (rank-one zero, curvature, transverse slope, open-side minima) are theirs to run.

## 3. The finite-twist mean-radius term, computed

Team v046 qualified v045: the mean over layers of the rotated valley radius carries an \(O(\epsilon\theta)\) term that the implemented `average` projection (same unrotated direction for both layers) cancels exactly. Computed directly with the exact geometry \((\mathbf I+\mathbf E_l)^{-T}R(\theta_l)\mathbf K_j\), \(\epsilon=0.3\%\), \(\theta=1.05^\circ\), \(\phi=0\):

| | \(j=0\) | \(j=1\) | \(j=2\) |
|---|---|---|---|
| relative mean-radius shift | \(2.2\times10^{-6}\) | \(-1.29\times10^{-5}\) | \(1.47\times10^{-5}\) |
| implemented `average` | 0 | 0 | 0 |
| at \(\theta=0\) (pure \(O(\epsilon^2)\)) | \(2.2\times10^{-6}\) | \(8.9\times10^{-7}\) | \(8.9\times10^{-7}\) |

Doubling \(\theta\) doubles the \(j=1,2\) terms; doubling \(\epsilon\) doubles them; \(j=0\) (the \(K\) along the strain axis, symmetric under \(\pm\theta/2\)) has no first-order term. **Confirmed:** the term is \(O(\epsilon\theta)\), of relative size \(1.5\times10^{-5}\) here, and the v045 cancellation is an artefact of projecting on the unrotated direction. At \(\kappa=5\) it would move \(w_j\) by \(\sim7\times10^{-5}\), far below anything measured, but the v048 wording ("under a declared joint small-angle approximation") is the correct one and stands.

## 4. Status
Path-replayed under the declared model, both engines: braid 1 → deepening → un-linking → v028 → first annihilation → post-transfer → braid 2 → cleanup → upper collision. Anchored, awaiting replay: flat birth (§1), final annihilation (§2), preparation (v047). Scope limits: the lower un-link collision; physical-bilayer validation.

## 5. Self-corrections this entry
- None to the physics. `ledger.py` now takes the new anchor file; `LEDGER.md` regenerated.
