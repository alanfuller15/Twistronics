# TWISTRONICS LOG — v039 — Later checkpoints with the full kinetic tensor

**Scope.** v038 §6 item 1: the v029, v031 and v033 checkpoints in the second engine (`tbg_ref`) with the Oliva-Leyva–Naumis kinetic tensor \(v_0(\mathbf I+(1-\beta)\mathbf E_l)\). **All labels reproduce.** One estimator defect was found and gated on the way. New files: `ref_later.py`, `ref_v029_local.py`; `tbg_ref.py` gains the \(\tau_z\sigma_z\) knob, generic gap helpers, a line-bundle sign holonomy, and a projection gate in the fixed-frame charge estimator. \(N=4\) throughout; the \(N=6\) pass is queued.

---

## 1. Results (second engine, `kinetic='full'`)

| checkpoint | state | measured | logged (first engine, `kinetic='none'`) |
|---|---|---|---|
| v029 pre-annihilation | \((0,-0.40,-0.70,65^\circ)\) | flat pair (0.6464, 0.8378), (0.6273, 0.8340), sep 0.0194, charges \((+1,-1)\) **OPPOSITE** | OPPOSITE, sep 0.0216 |
| v029 annihilation | \(B_\tau\) sweep | pair present at −0.71 (sep 0.0097, opposite), gone at −0.72; **\(B_\tau^\ast\in(-0.71,-0.72)\)** | \((-0.70,-0.72)\) |
| v029 post-transfer | \(B_\tau=-0.74\) | **0** flat nodes (min flat gap 0.164 meV); U pair (0.590, 0.691), (0.521, 0.964) charges \((-1,-1)\) **SAME**; lower gap 15.2 meV | 0 nodes, 0.159 meV; SAME |
| v031 before braid 2 | \(w_0/w_1=0.99\), \((0,-0.40,-0.80,80^\circ)\) | U pair \((+1,+1)\) **SAME** | SAME |
| v031 after braid 2 | \(w_0/w_1=1.00\) | U pair \((+1,-1)\) **OPPOSITE** | OPPOSITE |
| v033 endpoint | \((-0.30,-0.40,-1.8,80^\circ,1.10)\) | gaps: below-lower 33.61, lower-flat\(_1\) 23.18, flat 2.863, flat\(_2\)-upper 3.34, upper-next 10.82 meV; **0 flat nodes** | 34.04, 22.54, 2.87, 3.15, 10.73; 0 nodes |
| v033 per-band \(w_1\) | same | lower \((+,+)\); **flat\(_1\) \((-,+)\)**; flat\(_2\) \((+,+)\); upper \((+,+)\) | identical |

Every topological label of the campaign is now reproduced by the second implementation with the correct kinetic term. Magnitudes shift at the level v038 §4 predicted (up to ~0.6 meV on the endpoint gaps, 0.01 in \(B_\tau^\ast\)); node positions shift by \(\lesssim3\times10^{-3}\).

## 2. Estimator defect found and gated

The fixed-frame effective-\(2\times2\) winding (v036 §1) returned 0 for one node of the v029 pair at separations 0.01–0.04, while the partner gave ±1 and \(|d|\) stayed bounded away from zero. Cause: the frame point sat *between* the two nodes, and the projection of the true two-band subspace along the loop onto the fixed frame became degenerate (smallest singular value of \(F^{\rm T}F_k\) well below 1), so the projected \(d\)-vector no longer represented the node. The old code rounded that 0 to a charge.

Fix, in `node_charge`: the smallest singular value of the frame overlap along the loop is recorded and must exceed 0.9, and the raw winding must be within 0.05 of an integer, else the estimator returns INDETERMINATE (never a charge). `relative_charge` now takes the frame point on the side of each node *away* from its partner, with loop radius \(\le0.3\times\) separation. With that, the v029 pair reads OPPOSITE at every separation down to 0.0097, and the baseline re-check gives SAME with overlap 0.993.

This is the second time in this project that a "charge = 0" reading would have been silently mislabelled by an unguarded estimator (v034 §4 was the first). The rule is now universal across both engines: a winding is a charge only if the estimator's own validity diagnostic passes.

## 3. Status of the kinetic caveat

With `kinetic='full'` implemented and all checkpoints re-verified, the magnitude caveat in v038 §4 can be made concrete: for the states above, gap magnitudes under the full tensor differ from the logged values by −0.5 to +0.6 meV (largest: flat\(_2\)–upper at the endpoint, 3.15 → 3.34), node positions by \(\le3\times10^{-3}\), and the v029 annihilation amplitude by 0.01. Interlayer-tunnelling strain dependence remains unmodelled in both engines (v038 §5).

## 4. Next
- \(N=6\) pass of this entry's table in `tbg_ref` (queued; ~5× runtime).
- Extend the v037 gated path replay to braid 2 and the annihilation, in both engines, now that both carry the same kinetic option.
- Port the projection gate of §2 into the first engine's `nodewind`/`braid` estimators (they use transported frames and are not subject to the same failure, but the diagnostic is cheap and should be logged everywhere).

## 5. Self-corrections this entry
- The v036 estimator lacked a validity diagnostic; found by a failure on a close pair, not by design. Gated (§2).
- First reading of the v029 pre-annihilation state reported "1 flat node" from the global search (merge tolerance 0.01 > separation 0.019 after the cone check displaced one refine); resolved by a local search, which is now the standard for any pair closer than 0.05.

---

## 6. Addendum — \(N=6\) pass (second engine, `kinetic='full'`)

| checkpoint | \(N=6\) result | \(N=4\) (§1) |
|---|---|---|
| v029 pre-annihilation | pair (0.6464, 0.8377), (0.6274, 0.8339), sep 0.0193, node gaps \(10^{-11}\); charges \((+1,-1)\) **OPPOSITE**, frame overlap 0.991 | OPPOSITE, sep 0.0194 |
| v029 post-transfer | 0 flat nodes (min 0.164 meV); U pair (0.590, 0.691), (0.521, 0.963) charges \((+1,+1)\) **SAME**; lower gap 15.26 | SAME |
| v031 before / after braid 2 | \((-1,-1)\) SAME / \((-1,+1)\) **OPPOSITE** | SAME / OPPOSITE |
| v033 endpoint gaps (meV) | below-lower 33.36, lower-flat\(_1\) 23.19, flat 2.770, flat\(_2\)-upper 3.39, upper-next 10.86; 0 flat nodes | 33.61, 23.18, 2.863, 3.34, 10.82 |
| v033 per-band \(w_1\) | flat\(_1\) \((-,+)\), flat\(_2\) \((+,+)\) | identical |

All labels cutoff-stable. Largest \(N=4\to6\) magnitude change: below-lower gap 0.25 meV, flat gap 0.09 meV, consistent with v035 §4. The global node search at \(N=6\) again returned "1 flat node" for the pre-annihilation state (merge tolerance vs 0.019 separation); the local two-seed search is authoritative, as in §5.
