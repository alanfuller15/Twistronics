# TWISTRONICS LOG — v034 — Audit response

**Scope.** Response to the audit of 20 September 2026 (inspection-mode run of the AUDIT plugin over the v023–v033 bundle). The audit's central question was the right one: the toolkit had guard gaps, and nobody had shown whether any of them touched a recorded conclusion. This entry (a) fixes every code finding, (b) adds the assertion suite and environment record the audit asked for, and (c) re-runs the four measurements the campaign's conclusions rest on through a numerical acceptance gate. **Result: all four reproduce with the same labels; windings within 0.001 of ±1; no gate violations.** New files: `gate.py`, `test_regression.py`, `gated_rerun.py`, `requirements.txt`, `ENVIRONMENT.txt`. Patched: `bm_strain.py`, `braid.py`, `nodewind.py`, `final_check.py`, `descend*.py`, `scan_state.py`.

The audit did not execute project code and did not claim the physics was wrong; it graded specific claims about the code. The dispositions below grade the same claims after the changes.

---

## 1. The acceptance gate (audit action 1)

`gate.py` now stands between every raw number and every label:

| check | rule | audit ID |
|---|---|---|
| reality residual | every real-basis frame is built by `real_frame_checked`, which raises if \(\max|{\rm Im}\,H_R|>10^{-9}\) meV | F04 |
| frame transport | `ortho_checked` refuses any QR with \(\min|R_{ii}|<10^{-6}\) instead of zeroing a column | F03 |
| labels | `classify(w_a,w_b)` returns INDETERMINATE unless both windings are finite and within 0.15 of ±1; a zero product is never "OPPOSITE" | F05 |
| node counts | `require_nodes` raises on insufficient nodes | F13 |
| optimiser | `refine` records `success/status/message/nfev`; a node found across a BZ edge is re-refined in the canonical frame and the displacement (`wrap_shift`) is recorded | F08 |
| geometry | `segment_geometry` lifts both the segment and the compared point by the shortest periodic displacement and raises on coincident endpoints | F02 |

The gate is deliberately strict: the first re-run of this entry was stopped by it (§4).

## 2. Finding-by-finding disposition

| ID | audit verdict | action | status now |
|---|---|---|---|
| F01 | endpoint claims unverified | §3 re-runs the four decisive measurements under the gate; independent reproduction by a second implementation is still open | partially addressed |
| F02 | descent geometry inconsistent, /0 on coincidence | `descend3` uses `segment_geometry`; audit's own example (F1=(.99,.5), F3=(.01,.5), Q=(0,.5)) is a regression test and gives \(t=0.5\) | **fixed, tested**. Historical effect: none — the tracked F nodes in v027–v028 stayed within \(f\in[0.5,0.85]\), never near an edge; the one script that did hit an edge (`scan_U.py`) was already wrapped in v031 |
| F03 | `ortho` zeros a column on singular input | replaced by `ortho_checked` everywhere | **fixed, tested** |
| F04 | `final_check.frame` discards Im without checking | uses `real_frame_checked`; `euler.real_frame` already asserted | **fixed, tested** (forbidden harmonics now raise, allowed ones pass) |
| F05 | zero labelled OPPOSITE | `classify` | **fixed, tested**. Historical effect: every recorded label in v026–v033 printed its windings alongside, all with \(|w|\ge0.96\); none was near zero |
| F06 | unknown sweep key silently ignored | allowlist in `scan_state.py` | **fixed** |
| F07 | checkpoints not atomic, no environment identity | write-to-temp then `os.replace`; python/numpy versions stored | **fixed** |
| F08 | refine drops optimiser status | see §1; also the wrap check the audit suggested | **fixed, tested** |
| F09/F10 | no test suite; coverage credits false | `test_regression.py`, 17 assertion tests, expectations exact-by-symmetry or independently derived (§5). The scanner's doctest heuristic is a plugin issue, noted for the AUDIT repo | **addressed** |
| F11 | no dependency manifest | `requirements.txt` (numpy, scipy, pytest, pinned to the versions used) and `ENVIRONMENT.txt` | **fixed** |
| F12 | CVE status unverified | out of scope for a single-user research sandbox; versions now recorded so it can be checked | open, low |
| F13 | winding drivers assume ≥2 nodes | `require_nodes` guard | **fixed** |
| F14 | `braid.transport` docstring promises two returns | docstring corrected | **fixed** |
| S03–S07 | scanner heuristics | belong to the AUDIT plugin, not this project; forwarded | n/a here |

## 3. Gated re-run of the four decisive measurements

Environment: Python 3.12.3, NumPy 2.4.4, SciPy 1.17.1, scipy-openblas. \(N=4\) as in the originals.

| campaign step | state | measurement | windings | label | refine ok | wrap shift |
|---|---|---|---|---|---|---|
| v026 braid 1, before | \(A=0.2,\ B_{\rm sym}=-0.25\) | flat pair, straight segment | +0.999, +1.000 | SAME | yes/yes | 0, 0 |
| v026 braid 1, after | \(B_{\rm sym}=-0.30\) | | −1.000, +1.000 | **OPPOSITE** | yes/yes | 0, 0 |
| v029 pre-annihilation | \((0,-0.40,-0.70,65^\circ)\) | flat pair, sep 0.0216 | −1.000, +1.000 | **OPPOSITE** | yes/yes | 0, 0 |
| v031 braid 2, before | \(w_0/w_1=0.99\) | U pair, (flat\(_2\), upper) frame | +1.000, +0.999 | SAME | yes/yes | 0, 0 |
| v031 braid 2, after | \(w_0/w_1=1.00\) | | +1.000, −0.999 | **OPPOSITE** | yes/yes | 0, 0 |
| v033 endpoint | \((-0.30,-0.40,-1.8,80^\circ,1.10)\) | per-band sign holonomy, gated frames | flat\(_1\): \(k_1\) −1, −1; \(k_2\) +1, +1. flat\(_2\): all +1 | \(w_1(\text{flat}_1)=(1,0)\) | — | — |

No `GateError` was raised on any frame. Node positions agree with the logged values to \(10^{-4}\). The audit's RED item 1 is therefore answered for the conclusions that matter: they are not artefacts of the missing guards.

## 4. What the gate caught on first use

The first gated re-run returned INDETERMINATE for v026 and v029. Cause: an off-by-one in my re-run script's gap index, which made the "flat pair" search land on lower-gap nodes (\(|w|\approx0.01\)). Under the old `'SAME' if w1*w3>0 else 'OPPOSITE'` this would have printed OPPOSITE for v026 at \(-0.25\) — the wrong answer, confidently. The gate refused to label it. The audit's F05 is vindicated by the first thing that happened after fixing it.

Second catch: the new wrap check in `refine` fired on a U node at \(f_2\approx1.01\). The truncated plane-wave basis is only approximately periodic, so a node located just across an edge sits at slightly different coordinates once wrapped. Handled by re-refining in the canonical frame and recording the shift (0 in all rows of §3; the U node was re-found at \(f_2=0.0126\) with no residual).

## 5. The regression suite

`test_regression.py`, 17 tests, ~6 s:
- unstrained Dirac points exactly at \(K_M=(0,0)\) and \(K'_M=(\tfrac13,\tfrac13)\), \(\Gamma_M\) gapped (exact by symmetry);
- flat bandwidth 6–9 meV and \(\Gamma_M\) remote gap 18–23 meV at \(1.05^\circ\), \(w_0/w_1=0.8\) (literature range);
- all six allowed harmonic types preserve \(C_{2z}T\); all four forbidden types raise (the v026 §1 rule, now executable);
- strained baseline nodes and remote gap at \(N=4\) reproduce v023 §3 to \(2\times10^{-3}\) / 0.05 meV;
- `segment_geometry` on the audit's example; coincident endpoints raise;
- `ortho_checked` refuses `diag(1,0)`, orthonormalises a regular input;
- `classify` never labels 0, 0.5, or NaN;
- `refine` reports success and value.

## 6. Still open
- **Independent reproduction** (F01). Everything here is one implementation checking itself more carefully. A second, independently written strained-BM model reproducing v023 §3 and one braid would be worth more than any further guard.
- The scanner-side findings (S03–S07) go to the AUDIT plugin's own log.
- Bandwidth caveat unchanged: every result after v026 is a statement about the real two-band bundle at 50–80 meV bandwidth, not about flat-band physics.

## 7. Self-corrections this entry
- Off-by-one gap index in `gated_rerun.py` (§4). Caught by the gate before any label was printed.
- The first version of the wrap check flagged a legitimate near-edge node as a failure; corrected to re-refine and report, which is what the audit's F08 note actually asked for.
