# TWISTRONICS LOG — v035 — Corrections from the independent replay

**Scope.** Disposition of the "remediation and decisive replay" report of 20 September 2026: an independent replay engine, a frozen acceptance plan (SHA-256 recorded before the runs), and 16 pair-charge, 56 cycle-sign, 10 gap and 2 Euler comparisons at \(N=4\) and \(N=6\). This entry records what changes in the log as a result. The v023–v034 text is left as written; corrections are appended here, per the log's rule.

---

## 1. Labels: none change

Every topological label in v023–v033 that the campaign's conclusions rest on was reproduced under the replay's gate at both cutoffs: baseline same-charge pair and \(|e_2|=1\); both braid flips (v026, v031); the pre-annihilation opposite pair (v029); the same-charge transferred U pair (v029); the opposite flat pair before the final annihilation (v032); and the endpoint sign holonomies giving \(w_1(\text{flat}_1)=(1,0)\) with all other bands trivial (v033). The \(N=6\) second-braid checkpoint, unfinished in v031, now returns OPPOSITE. Smallest transport overlap singular value 0.966; largest deviation of the old raw winding estimator from unit magnitude 0.020; frame-holonomy correction changed no label.

## 2. One number corrected

v033 §2 logged the endpoint lower-remote / flat\(_1\) gap as **22.7 meV** at \(N=4\). The replay found that the original `refine` returned a wrapped coordinate together with an objective value evaluated at the *unwrapped* point (audit F08); at the wrapped coordinate the objective is 22.54 meV, and re-refinement in the actual cell gives

$$ \Delta_{\rm lower|flat_1}(N=4) = 22.537986\ \text{meV},\qquad \Delta_{\rm lower|flat_1}(N=6) = 22.691985\ \text{meV}. $$

Reproduced here with the v034-patched `refine`, which now re-refines across the wrap and reports the shift: the minimum sits at \(f=(0.992,\ 0.294)\), i.e. on the \(f_1=1\) edge, with `wrap_shift` \(3.7\times10^{-3}\) at \(N=4\) and \(6\times10^{-7}\) at \(N=6\). This is the one place in the endpoint inventory where a minimum lies on a BZ edge, which is why it is the one number the defect touched. The gap stays open; the "fully gapped" label survives. **v033 §2, lower gap: 22.7 → 22.54 meV (N=4).**

## 3. One prerequisite added

The endpoint's band-by-band reading (v033 §3) treated the lower remote band as isolated, but only its gap to flat\(_1\) had been inventoried. The replay searched the gap below it explicitly:

$$ \Delta_{\rm below\text{-}lower\,|\,lower}(N=4)=34.041131\ \text{meV},\qquad (N=6)=33.794046\ \text{meV}, $$

positive at both cutoffs (reproduced here to six decimals). The lower remote band is a legitimately isolated line bundle, and its trivial \(w_1\) in v033 §3 stands.

## 4. Cutoff note on the endpoint gaps

The replay's \(N=6\) values differ from \(N=4\) by up to 0.09 meV (flat gap 2.869 → 2.777 meV). All signs and labels are cutoff-stable; the magnitudes at the endpoint are not claimed to be converged beyond ~0.1 meV. Consistent with v023 §3, where the baseline was converged to 0.05 meV only from \(N\ge5\).

## 5. What the replay does and does not establish

- It reran the decisive checkpoints, not the continuous descent trajectories or braid paths between them. The endpoints and flips are reproduced; the causal story connecting them (v027–v031) is supported by the recorded intermediate measurements but was not re-traced.
- It is a second engine on the same model, with tests authored during remediation: [self-tested] tier, not external verification. An implementation with independently chosen conventions (Koshino-style basis, different strain parametrisation) reproducing v023 §3 and one braid flip remains the outstanding check, as v034 §6 said.
- Finite sampling cannot exclude unsampled narrow nodes; the positive-gap labels are numerical, on 24/36 grids with refinement.

## 6. Status of the toolkit

The replay's guards supersede the v034 gate where they are stricter (Hermiticity and eigen-residual checks, transport singular-value floor 0.1, mesh/radius agreement for windings, sewing-norm checks for cycles, rejection of Euler class for non-orientable frames, `ast.literal_eval` for seeds, `logaddexp` softplus, `-O`-safe runtime checks). The scanner-side fixes (docstring-parsed doctest detection, raw-string secret handling, path-sorted ties, physical line counts) go to the AUDIT plugin's own record. The documented replay commands are the acceptance entry points from here on.

## 7. Self-corrections this entry
- v034 §2 stated F08 had "no historical effect" for the flat-pair descents. That was true for the descents but not for the endpoint gap inventory, where one minimum lies on an edge. Corrected in §2.
- v034 §3 reported the v033 endpoint gaps only by label; the replay supplied the magnitudes and one of them was wrong. The general lesson is recorded: any minimum found within a few \(10^{-3}\) of a BZ edge must be re-refined in the canonical cell before its value is quoted.
