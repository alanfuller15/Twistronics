# TWISTRONICS LOG — v054 — Audit repairs reconciled; one refinement helper

**Scope.** Disposition of the team's v054. Adopted: their audit repairs, the instrumented re-run of all 76 preparation states (zero legacy-helper calls, no label change, root and gap differences from v053 exactly 0), and the bound 61-test run. Reconciled: their corrected `BM.refine` replaces my v053 version, so both trees carry one helper with one contract. Tests 33 (all pass under `python -O`).

---

## 1. Adopted

| engine | \(N\) | fresh states | labels | parameter checks | legacy calls |
|---|---:|---:|---|---:|---:|
| bm_lab | 4 | 19 | SAME | 9 | 0 |
| ref_lab | 4 | 19 | SAME | 9 | 0 |
| bm_lab | 6 | 19 | SAME | 9 | 0 |
| ref_lab | 6 | 19 | SAME | 9 | 0 |

Maximum root difference from v053: 0; maximum comparison-path external-gap difference: 0 meV; minimum old/new frame-plane overlap 1.000000000000 with signs compared explicitly. The suspect helper and legacy entry points were instrumented to fail if called and were not called: this supports non-use on the preparation route and, as the team says, clears nothing else. Test evidence is a recorded run bound to source, tests, inputs and runtime (61 passed, run `20260921T001901Z_99cfc67a`, digest `9130ef4f…`), which is the standard the audit asked for and the one this log adopts for any future count it quotes.

## 2. One `refine`

My v053 fix (final-attempt metadata, both attempts kept, explicit failure) and the team's v054 helper address the same audit target. Theirs is the stricter contract: seed and tolerance validated; a rejected refinement cannot be consumed silently by a plain call; `return_result=True` callers get `success=False` with `rejection_reasons`; the returned value is the objective at the canonical coordinate. It is adopted verbatim into `bm_strain.py` (diff against mine: only the helper and a legacy opt-in stub; no Hamiltonian, tunnelling or basis line changed). My test now reads their attempt schema (`value`, not `fun`) and passes with and without `-O`. `euler.py` keeps the v053 runtime guard; the team's additional `exploratory=True` opt-in for legacy Euler/braid entry points is their tree's rule and applies to those scripts in mine as well: they are exploratory unless a result passes the declared gates.

## 3. Status
Route path-replayed under the declared model in both engines from the baseline to the endpoint at every leg except the lower un-link collision (v052 bracket; the team's next window, both \(N=4\) engines first). Older campaign uses of legacy helpers are the team's separate impact-review task; on my side the call-path statement of v053 §2 stands unchanged. No interval proof, infinite-cutoff bound, dependency clearance or physical-bilayer validation.

## 4. Self-corrections this entry
- None to the physics. My v053 helper was correct as far as it went and is superseded by a stricter one; the test that would have failed on the old metadata now runs against the adopted schema.
