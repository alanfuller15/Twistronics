# TWISTRONICS LOG — v043 — v042 disposition; one model, one geometry, two engines

**Scope.** Response to the team's v042 lab-frame replay. Adopted: both engines pass the braid-2 and first-annihilation path gates with `kinetic='lab_nn_full'` at \(N=4\) and \(N=6\); post-transfer U pair SAME; endpoint and ratio-1.04 candidate with identical per-band \(w_1\). Corrected here: a transcription error in v041 §2 and an overgeneralised sensitivity remark in v041 §3. Closed: the last structural difference between the engines (linearised vs exact reciprocal geometry) and the residual helper defects. Changed: `bm_strain.py` (`geometry` option), `tbg_ref.py` (team guard patch applied verbatim), `test_tbg_ref.py` (+2 → 29 tests), `cross_exact.py`.

---

## 1. Adopted from v042 (both engines, declared model)

| event | `bm_lab` \(N=4\) / \(N=6\) | `ref_lab` \(N=4\) / \(N=6\) | ref − bm |
|---|---|---|---|
| braid-2 center-segment crossing, \(w_0/w_1\) | 0.990538737 / 0.990766131 | 0.990541398 / 0.990768791 | \(+2.7\times10^{-6}\) |
| first annihilation, \(B_\tau^\ast\) | −0.713373536 / −0.713301013 | −0.713386736 / −0.713314259 | \(-1.3\times10^{-5}\) |

Same structure as v037/v040: spatial SAME→OPPOSITE at the crossing, carried charges unchanged, singular comparison rejected, fold diagnostics at the annihilation. Endpoint gaps agree between engines to \(3.2\times10^{-4}\) meV; per-band \(w_1\) identical: lower remote (0,0), **flat\(_1\) (1,0)**, flat\(_2\) (0,0), upper remote (0,0). The one-engine limit of v040 is closed for these windows and checkpoints. Not closed: the connecting legs (v042 `NEXT_LEGS.md` lists them), \(N>6\), tunnelling strain law.

## 2. Corrections to v041

- **§2, annihilation-shift row: transcription error.** The earlier original-model roots were \(-0.71514090\) (\(N=4\)) / \(-0.71505612\) (\(N=6\)), not "\(-0.7120\)". The accepted \(\approx+0.0016\) shift to `full` stands; the number I typed beside it was wrong.
- **§3, "the difference sits below every other uncertainty in the project": withdrawn.** Convention sensitivity is observable-specific. For `tbg_ref` at fixed cutoff, `lab_nn_full` − `full`: braid-2 crossing \(+7\times10^{-6}\); annihilation root \(+1.63\times10^{-4}\); endpoint flat gap \(+0.0072\) meV. The annihilation-root shift exceeds its own \(N=4\to6\) shift (\(7.2\times10^{-5}\)). The 0.004 meV baseline remote-gap figure was one observable, not a bound. Every sensitivity is now quoted next to its observable.

## 3. The last engine difference, closed

v042 found that after matching only the \(q_j/G\) geometry the two Hamiltonians agree to \(1.6\times10^{-12}\) meV, i.e. the remaining \(\sim5\times10^{-4}\) meV disagreement was `bm_strain`'s linearised strain geometry \((\mathbf I-\mathbf E_l)R\) against `tbg_ref`'s exact \((\mathbf I+\mathbf E_l)^{-T}R\). `bm_strain` now takes `geometry='linear'` (campaign, default, so no historical run changes meaning) or `'exact'`. Check at \(N=4\), \(\phi=65^\circ\), `lab_nn_full`, six central bands at two momenta (one unwrapped):

| geometry | max \(|E_{\rm bm}-E_{\rm ref}|\) (meV) | \(|G_1|\) bm / ref (Å\(^{-1}\)) |
|---|---|---|
| linear | \(2.9\times10^{-4}\), \(5.0\times10^{-4}\) | 0.0549547481 / 0.0549548703 |
| **exact** | **\(1.9\times10^{-13}\), \(7.1\times10^{-13}\)** | 0.0549548703 / 0.0549548703 |

With `geometry='exact'` and `kinetic='lab_nn_full'` the two engines are the same declared model to roundoff. That is the intended end state of the cross-implementation programme begun in v036: the engines were independent enough to find three convention errors (v036 sign, v038 tensor, v040 rotation order) and one geometry approximation, and now agree because every one has been resolved to a declared choice. Their independence as *estimators* (Wilson-line vs plaquette Euler class, transported-frame vs fixed-frame charge) is unchanged.

## 4. Helper defects, closed

Team patch applied verbatim to `tbg_ref.py` (no Hamiltonian, eigensolver or mesh lines changed, verified by diff): nonfinite/nonpositive radii and nonfinite/coincident seeds rejected; failed, nonfinite or seed-worsening gap refinements raise; `gap_min` never returns \(+\infty\); both boundary faces, corners, edge centres and inward seeds included. The patched helper recovers the \(N=4\) endpoint edge minimum that the v041 helper overestimated by 0.013 meV despite two-grid agreement, which is the third edge-minimum lesson (v035, v040, here): grid agreement is not completeness.

Tests: 29. New: exact geometry gives roundoff agreement and linear gives the reported residual; `gap_min` returns a finite positive value.

## 5. Next (from v042 `NEXT_LEGS.md`, adopted as written)
Connecting legs 1–9 from the successful v028–v031 route under the declared model with basis-aware continuation and two-seed tracking; then the fixed-\(\phi\) cleanup windows; then a named tunnelling strain law and \(N>6\) endpoint convergence. Old results keep their original kinetic/geometry labels.

## 6. Self-corrections this entry
- v041 transcription error (§2), caught by the team against their own records.
- The "below every other uncertainty" remark was the kind of generalisation the log is supposed to refuse; withdrawn with the per-observable numbers that replace it.
