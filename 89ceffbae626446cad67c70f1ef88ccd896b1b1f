# TWISTRONICS LOG — v053 — Preparation legs replayed (team); audit repair targets in my code closed

**Scope.** (a) Disposition of the team's research v053: the preparation legs \(A:0\to0.2\) and \(B_{\rm sym}:0\to-0.25\) path-replayed in both engines at \(N=4,6\), joining v044 through roots and frames. (b) The inspection audit published with it lists four repair targets; two are in code I maintain and are fixed here with tests, including under `python -O`. (c) The team's own RESPONSE.md governs the other two. Tests 33.

---

## 1. Adopted from the team's v053

| engine / geometry | \(N\) | states | labels | min fine/coarse parameter overlap | root join | endpoint plane overlap | rel. orientation |
|---|---:|---:|---|---|---:|---:|---:|
| bm_lab / linear | 4 | 19 | SAME | 0.995465 / 0.982078 | \(1.0\times10^{-15}\) | 1.000000000000 | +1 |
| bm_lab / linear | 6 | 19 | SAME | 0.995469 / 0.982090 | \(1.6\times10^{-15}\) | 1.000000000000 | +1 |
| ref_lab / exact | 4 | 19 | SAME | 0.995465 / 0.982078 | \(1.8\times10^{-15}\) | 1.000000000000 | +1 |
| ref_lab / exact | 6 | 19 | SAME | 0.995469 / 0.982091 | \(2.6\times10^{-15}\) | 1.000000000000 | +1 |

76 accepted states, every one mesh/radius charge-checked; carried charges constant; minimum comparison-path external gap 3.73845073 meV; minimum spatial overlap 0.99778252; maximum basis-norm loss \(2.1\times10^{-15}\); no loop fallback; stop/resume preserved. Four endpoint joins pass plane-overlap, root and relative-orientation gates (a common overall frame flip permitted, no absolute sign asserted). Together with the v050–v052 event windows this closes the preparation-to-v044 connection at the sampled-frame level. The team notes the flat pair is not globally isolated after the remote contacts on this leg, so no Euler class is carried through it. The lower un-link collision (v052 bracket) is their stated next window.

With this, the route from the isolated \(e_2=\pm1\) baseline to the fully gapped endpoint is path-replayed under the declared model in both engines at every leg except the lower un-link collision, which is bracketed (v052) and not yet gate-accepted. `COVERAGE.json` remains the statement of record.

## 2. Audit repair targets

| # | file | finding | disposition |
|---|---|---|---|
| 1 | `bm_strain.py`, `BM.refine` | after a wrapped re-refinement the result is replaced but the first attempt's success/status/message are kept; failed/non-finite outcomes not explicit | **fixed.** `last_refine` now describes the final attempt; both attempts are kept under `attempts`; success requires the final attempt to succeed with a finite value that is unchanged under periodic wrap, else the message says why. Test: seed outside the cell forces the wrap path (two attempts, metadata from the last, same root as the in-cell seed); a NaN objective reports `success=False`. |
| 4 | `euler.py`, `real_frame` | reality check was an `assert`, optimisable away under `-O`, before dropping the imaginary part | **fixed.** Runtime `RuntimeError`; test passes under `python -O`. (The other frame helpers already used `real_frame_checked`/`GateError`, v034.) Legacy `euler.py`/`braid.py` outputs remain exploratory unless they pass the declared gates, as the audit and the team say. |
| 2 | `build_report.py` (team) | embedded test count and prose are not a fresh machine-readable test record | team's, per RESPONSE.md |
| 3 | `package_release.py` (team) | requires a byte-identical prior ZIP; output parent not created | team's, per RESPONSE.md |

Whether target 1 affected any accepted result is, as the audit says, unverified by inspection. What can be said from call paths: every accepted root in the record comes from the team's harness (its own refinement and gates) or from `refine` calls whose returned value and coordinate were re-checked (`gated_rerun`, `lowergap_check`, the fold trackers, which re-evaluate the gap at the returned point); the stale metadata field was never read by an acceptance decision on my side. That is a call-path statement, not a replay.

## 3. Self-corrections this entry
- A metadata bug introduced by my own v034 patch (the wrap re-refinement) survived four audits because nothing read the field. The new test reads it.
- An `assert` used as a scientific guard, in a file I wrote before `gate.py` existed and did not go back to.
