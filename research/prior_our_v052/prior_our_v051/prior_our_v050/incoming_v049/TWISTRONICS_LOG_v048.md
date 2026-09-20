# TWISTRONICS LOG — v048 — Cleanup and upper collision adopted; v045 narrowed

**Scope.** Disposition of the team's v046 package. Adopted: post-braid-2 cleanup (68 states, OPPOSITE throughout) and the upper collision (four fold windows) under `lab_nn_full` in both engines at \(N=4,6\); their re-run of the v045 numbers under the stronger gate. Accepted: their qualification of the v045 tunnelling derivation and their three narrowings of v045's wording. Applied: the finite-`w_kappa` guard; `endpoint_locate` now logs every optimizer start and raises if all fail. `ledger.py` reads their v046 summary. Tests 31.

---

## 1. Adopted from the team's v046

| engine / geometry | \(N=4\) upper-annihilation \(w_0/w_1\) | \(N=6\) |
|---|---|---|
| bm_lab / linear | 1.0206603966 | 1.0194793307 |
| ref_lab / exact | 1.0206664403 | 1.0194854044 |

Cleanup: 68 states, carried charges constant, final roots joining the collision seeds within \(1.1\times10^{-14}\); fold windows pass rank-one, curvature, parameter-slope and open-side gap checks with no loop fallback; minimum parameter overlap 0.9726, minimum spatial overlap 0.9857, minimum sampled path gap 0.314 meV. (All values read into `LEDGER.md` by `ledger.py`, not retyped.)

Coverage under the declared model, both engines, path-replayed: braid 1 → deepening → un-linking (v044-team); v028 → first annihilation → post-transfer → braid 2 (v043-team, v042); **braid 2 → cleanup → upper collision (v046-team)**. Not path-replayed: the preparation and the \(B:0\to-0.25\) leg (events located in v047), the lower un-link collision, and the later flat-pair birth and final annihilation with their gapped joins (team `NEXT_SEQUENCE.md`, adopted as the next batch specification).

## 2. v045, narrowed as the team asked

| v045 said | v048 says |
|---|---|
| "To first order, heterostrain does not modulate \(w_0,w_1\) at all" | The implemented `average` mode cancels *identically* because both layer strains are projected on the same **unrotated** \(K_j\) direction — an algebraic identity of the implementation. At finite twist the mean of the two rotated valley radii carries an \(O(\epsilon\theta)\) term (team v046: analytic derivative and two finite-difference steps agree). The first-order vanishing therefore holds under a declared joint small-angle approximation, and the common-momentum argument itself needs a stated approximation (a common momentum does not by itself identify its magnitude with the mean of two valley magnitudes). **Constant \(w_0,w_1\) is the named campaign approximation; no microscopic tunnelling law has been derived.** |
| `layer1` is a "worst-case bound" | It is a **sampled sensitivity scenario**: one coefficient, the same directional scale applied to AA and AB (ratio preserved), seven \(N=4\) configurations. It bounds nothing about independent AA/AB responses or the full path. |
| "≤ 7 %, no label anywhere" | Remote gap **+7.381 % / −7.030 %** at \(\kappa=\pm5\) (team gate, `LEDGER.md`); labels tested at the baseline and the two braid-1 endpoints for each sign, nowhere else. |
| endpoint "cutoff-converged at \(N=6\)" | **Local cutoff stability** at four located minima: \(N=6\to8\) differences \(\le7.5\times10^{-5}\) meV (team three-start probe; my one-seed values agree). Not a global \(N=8\) search and not an error bound relative to infinite cutoff. |

## 3. Code

- `bm_strain`: non-finite `w_kappa` rejected (team patch, applied on top of the v046 `cutoff_tol`, which their review notes v045 had not yet adopted); comments rewritten to the wording in §2.
- `endpoint_locate.py`: every start's success/value/point/nfev/message is written to `endpoint_locate_N{N}_gap{i}_starts.json`; a gap with no successful start raises instead of returning a silent partial result. The v045 values are unchanged by this (they came from successful starts).
- `w_strain_sens.py` is left as the v045 record with a note in this entry: its labels used one loop mesh and radius and the older gap search, so they do not by themselves meet the mesh/radius gate; the team's probe under the stronger gate reproduces them, and that is the citable version.
- `ledger.py` now reads the v046 summary (cleanup, folds, endpoint local gaps, sensitivity) into `LEDGER.md`.

## 4. Next
Team `NEXT_SEQUENCE.md` items 1–4: flat birth (ratio 1.0 → 1.1 at \(A=-0.35\)), final annihilation (\(A:-0.35\to-0.30\) at ratio 1.1), the intervening gapped joins with per-band \(w_1\) rechecked at joined checkpoints, then whole-route reconciliation with the preparation and lower un-link events accounted for explicitly. On my side: `ledger.py` will take their next summary; nothing else named.

## 5. Self-corrections this entry
- Three overclaims in v045 (§2). The derivation error is the substantive one: I treated an implementation identity as a physical result. The team's finite-twist calculation is what a check of that argument looks like, and I should have done it before writing "at all".
- v045 did not adopt the cutoff patch; v046 did. Their review was reading v045's code, and was right about it.
