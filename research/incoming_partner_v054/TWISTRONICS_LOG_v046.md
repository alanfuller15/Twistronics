# TWISTRONICS LOG — v046 — Braid 1 joined; the campaign is connected from braid 1 to braid 2

**Scope.** Disposition of the team's v044 reconciled package (their braid-1 batch; numbered v044 on their side, filed here as the team's v044 beside my v044 anchors entry). Adopted in full. Their record corrections to my v043 share are accepted. Their cutoff-padding witness is accepted and the optional patch applied to both engines. Two of their listed open items were already closed in v045 (tunnelling law, \(N>6\)), which their batch predates. New: `cutoff_tol` in both engines, docstring correction in `tbg_ref`, one test (31 total).

---

## 1. Adopted: braid 1, deepening, un-linking, in both engines

Route: \(A=0.2,\ \phi=0,\ w_0/w_1=0.8,\ B_\tau=0\); \(B_{\rm sym}:-0.25\to-0.30\) (20 steps), \(\to-0.40\) (8), then \(B_\tau:0\to-0.40\) (8). 148 primary states, all gated, both engines, \(N=4,6\). Spatial flat-pair label SAME→OPPOSITE at the located upper-node crossing, OPPOSITE through both connecting legs, joining their v043 pre-annihilation starting frames with root mismatch \(<3\times10^{-15}\) and the relative frame orientation recorded rather than assumed. Smallest resolved exterior gap 0.0155 meV; minimum spatial overlap 0.986.

| engine / geometry | \(N=4\) center-path \(B^\ast\) | \(N=6\) | shifted path (\(\Delta f_1=0.012\)) |
|---|---|---|---|
| bm_lab / linear | −0.2901737962 | −0.2901702643 | −0.2799795363 / −0.2799791809 |
| ref_lab / exact | −0.2901753967 | −0.2901718633 | −0.2799809816 / −0.2799806247 |
| bm exact (control) | −0.2901753967 | −0.2901718633 | agrees with ref to \(<4\times10^{-15}\) |

These are `lab_nn_full` values. The historical \(-0.28594\) (`none`) and \(-0.28795\) (legacy \((\mathbf I-\mathbf E)R^{\rm T}\)) stay under their model tags. The crossing is path-dependent (the 0.012-shifted path gives \(-0.27998\)), and the v044 anchors' \(B=-0.30\) row is correctly on the far side of it.

## 2. Coverage under one declared model, two engines — updated

| leg | status |
|---|---|
| baseline \(e_2=\pm1\), same-charge pair | fixed-parameter (v041) |
| **braid 1** | **path replayed** (team v044) |
| **deepening \(B\to-0.40\); un-linking \(B_\tau\to-0.40\)** | **path replayed** (team v044); the lower-pair annihilation itself is tracked through the \(B\) legs only and is not claimed measured |
| v028 → first annihilation | path replayed (team v043) |
| first annihilation | path replayed (v042) |
| post-transfer → braid 2 | path replayed (team v043) |
| braid 2 | path replayed (v042) |
| cleanup after braid 2 → endpoint | **open** (next team batch) |
| endpoint, per-band \(w_1\) | fixed-parameter (v042); cutoff-converged at \(N=6\) (v045) |
| tunnelling strain law | closed: first-order heterostrain modulation vanishes; worst case ±7 %, no label (v045) |

One caveat of the team's, kept: the BM chain runs `geometry='linear'` and the TBG chain `'exact'`, each continuing its own history; BM-exact controls reproduce the TBG-exact roots to \(10^{-15}\), so the two chains are the same model up to a difference already measured (v043 §3), but they are not literally one geometry along the paths. And the preparation from the original v023 baseline (the \(A:0\to0.2\) leg that creates the U pair) has not been path-replayed by anyone.

## 3. Record corrections to my v043 share, accepted

- The bundle had 20 numbered logs, not 21.
- The BM \(N=6\) annihilation root rounds to \(-0.71330\); \(-0.71331\) is TBG's. I transposed them in the short note; the v043 table was right.
- `geometry` is a `bm_strain` option only; `tbg_ref` is fixed exact. The share implied both.
- `tbg_ref`'s docstring still described the v036 \((\mathbf I-\mathbf E)\) kinetic term; corrected to describe the four named branches and the mandatory selection.

## 4. Cutoff padding: the witness accepted, "only the estimators differ" narrowed

The engines' cutoff paddings differed (BM \(10^{-6}\), TBG \(10^{-9}\) Å\(^{-1}\)). At \(N=4\), \(\epsilon=0.3\%\), \(\phi=15.843560625^\circ\), exact geometry, reciprocal indices \((\mp4,\pm3)\) exceed the nominal cutoff by \(\approx5\times10^{-7}\) and fall between the two paddings: dimensions 196 vs 188 for the same nominal model. No campaign state sits there, but v043 §3's "differ only in their topological estimators" was too broad and is narrowed to: *identical for matched \((\text{kinetic},\text{geometry},N,\text{cutoff\_tol})\), else a truncation difference.* The team's patch is applied: `cutoff_tol` is an explicit constructor argument in both engines, historical defaults preserved bit for bit, negative or non-finite values rejected. Test added: the witness reproduces (196/188), and with either common tolerance the bases and central bands match to \(10^{-10}\) meV. Any matched-model comparison names all four.

## 5. Next
- Team: the cleanup and later collision windows after braid 2 to the endpoint; then, if wanted, the \(A:0\to0.2\) preparation leg from the v023 baseline, which would make the record connected from the isolated \(e_2=\pm1\) state to the fully gapped \(w_1=(1,0)\) state.
- Toolkit: nothing named open. When the last leg lands, the closing entry should be a single table of every leg with its model tag, cutoffs, and the smallest gate margin along it.

## 6. Self-corrections this entry
- Three transcription-level errors in a two-paragraph share (§3). The pattern is the same as v041's: short notes written from memory of a table. Rule adopted: every number in a share is pasted from the entry, never retyped.
- v043 §3's scope claim about estimator-only differences (§4).
