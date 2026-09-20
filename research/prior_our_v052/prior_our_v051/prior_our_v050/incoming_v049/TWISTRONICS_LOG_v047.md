# TWISTRONICS LOG — v047 — Preparation-leg anchors; a generated ledger

**Scope.** Two toolkit-side items while the team runs the post-braid-2 windows. (a) Anchors for the one leg no one has traced: the preparation from the v023 baseline into the team's v044 start — \(A:0\to0.2\) at \(B_{\rm sym}=B_\tau=0\), then \(B_{\rm sym}:0\to-0.25\) at \(A=0.2\) — under the declared model in both engines, with the three events on it located. (b) `ledger.py`, which builds the closing coverage table mechanically from the recorded JSON summaries, so that no number in the closing entry is retyped (the failure mode of v041 §2 and v046 §3). New: `anchors_prep.py`, `prep_detail.py`, `prep_B.py`, `ledger.py`, `LEDGER.md`, `anchors_prep_N4.json`.

---

## 1. Preparation leg, part 1: \(A:0\to0.2\) (\(B_{\rm sym}=B_\tau=0\), \(\phi=0\), \(w_0/w_1=0.8\), `lab_nn_full`, bm exact, \(N=4\))

| \(A\) | flat pair roots (both engines, diff \(\le9\times10^{-12}\)) | label | min remote gap (meV) | upper nodes |
|---|---|---|---|---|
| 0.00 | (0.759429, 0.606615), (0.581553, 0.726597) | SAME | 4.9709 | — |
| 0.05 | (0.761307, 0.620326), (0.582336, 0.744129) | SAME | 4.0295 | — |
| 0.10 | (0.764231, 0.631225), (0.585495, 0.762458) | SAME | 1.9860 | — |
| 0.14 | (0.767693, 0.638992), (0.588631, 0.777054) | SAME | 0 | (0.684, 0.816), (0.637, 0.844) |
| 0.16 | (0.769758, 0.642818), (0.590076, 0.784412) | SAME | 0 | (0.593, 0.875), (0.728, 0.795) |
| 0.20 | (0.774504, 0.650683), (0.592372, 0.799505) | SAME | 0 | (0.538, 0.913), (0.791, 0.769) |

Events on this leg:
- **U-pair birth**: remote-gap minimum falls linearly 1.4805 (0.110) → 0.9486 (0.120) → 0.6734 (0.125) → 0.3924 (0.130) → 0.1058 (0.135) meV; extrapolated closing \(A^\ast\approx0.137\) at \((0.660,\ 0.830)\). Under `kinetic='none'` (v024) this was ≈0.15.
- **Extra flat-pair birth**: 2 flat nodes at \(A=0.16\); 4 at \(0.18\) (new pair at (0.565, 0.573), (0.509, 0.568)); 4 at \(0.20\). Birth in \((0.16,0.18)\) near \((0.54,0.57)\).

## 2. Preparation leg, part 2: \(B_{\rm sym}:0\to-0.25\) at \(A=0.2\)

| \(B_{\rm sym}\) | flat nodes | closest-pair separation | upper nodes |
|---|---|---|---|
| 0.00 | 4 | 0.1405 | (0.538, 0.913), (0.791, 0.769) |
| −0.02 | 4 | 0.0943 | (0.525, 0.920), (0.788, 0.770) |
| −0.04 | 2 | 0.2712 (the originals) | (0.786, 0.769), (0.511, 0.926) |
| −0.10 | 2 | 0.3051 | (0.781, 0.761), (0.468, 0.949) |
| −0.25 | 2: (0.7459, 0.6123), (0.5172, 0.8278) | 0.3141 | (0.687, 0.720), (0.360, 0.018); a lower-gap node also appears |

- **Extra flat-pair annihilation** in \((-0.02,-0.04)\), i.e. \(B^\ast\approx-0.03\) (v026, `none`: ≈ −0.05).
- The \(B=-0.25\) row is the team's v044 route start; the flat roots agree with the v044 anchors (v044 §2, row 1) to \(2\times10^{-5}\), the residual being this script's bm-linear vs bm-exact geometry — the v044 anchors were computed with `geometry='exact'` too, so the difference is the two different seeds' refinement; either way below the team's join tolerance. The lower-gap node at \(-0.25\) is the pair v026 saw born at ≈ −0.25 under `none`; its birth amplitude under the declared model is between −0.10 and −0.25 and is not resolved here.

With these three events located, the tracer has everything it needs to connect the isolated \(e_2=\pm1\) baseline to the v044 start.

## 3. The ledger

`ledger.py` reads the team's `summary.json` (v042), `SUMMARY.json` (v043, v044) and my `anchors_prep_N4.json`, and writes `LEDGER.md`: per-leg rows with engine, geometry, \(N\), states, labels, crossing roots, minimum overlaps, minimum exterior gaps, and the cross-engine differences, all taken from the records. Its output is in the package; two things it surfaced that I would have got wrong by hand: the v044 cases are 37 states each (148 total, four cases), and the v043 minimum parameter overlap 0.898 belongs to the pre-annihilation route at both cutoffs, not to one run. When the last team batch lands, the closing entry is `LEDGER.md` plus one paragraph.

## 4. Coverage (from `LEDGER.md`)

Path-replayed under `lab_nn_full`, both engines, \(N=4,6\): braid 1 → deepening → un-linking (team v044); v028 → annihilation window and post-transfer → braid-2 window (team v043); braid-2 window and first-annihilation window (v042). Fixed-parameter: baseline, preparation-leg anchors (here), post-transfer, endpoint (cutoff-converged at \(N=6\)). Not yet path-replayed: the preparation leg (events located here) and the cleanup after braid 2 to the endpoint.

## 5. Self-corrections this entry
- None to the physics. The ledger exists because the record-keeping errors of v041 and v046 were mine; a generated table is the fix, not a resolution to be more careful.
