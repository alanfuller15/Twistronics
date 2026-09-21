# TWISTRONICS LOG — v050 — Last windows adopted; v047 and v049 narrowed; ledger authority transferred

**Scope.** Disposition of the team's v048 package. Adopted: flat birth and final annihilation in both engines at \(N=4,6\), plus 32 sampled gapped states joining the upper collision to the birth window and the final annihilation to the endpoint. Accepted: five corrections to v047, one to v049's wording, one to the ledger's status. Transferred: ledger authority to the team generator. New/changed: `prep_detail.py` (banner), `ledger.py` (formatter status, no hardcoded footer), `LEDGER_historical.md`; the team's `LEDGER.md`, `COVERAGE.json`, `SCHEMA.md` filed as canonical.

---

## 1. Adopted from the team's v048

| event | engine | \(N\) | critical parameter | v049 fold extrapolation |
|---|---|---|---|---|
| flat birth (\(w_0/w_1\)) | bm_lab | 4 | 1.0529704128 | 1.0534 |
| | ref_lab | 4 | 1.0529719222 | |
| | bm_lab | 6 | 1.0520969426 | — |
| | ref_lab | 6 | 1.0520984612 | |
| final annihilation (\(A\)) | bm_lab | 4 | −0.3177787436 | −0.3178 |
| | ref_lab | 4 | −0.3177799654 | |
| | bm_lab | 6 | −0.3171450604 | — |
| | ref_lab | 6 | −0.3171462891 | |

Eight fold windows, 72 root-continuation states, 16 charge stations, both stations OPPOSITE in every window, nondegenerate-fold and open-gap checks passed, roots joining between the windows. The 32 gapped states join the upper collision through the ratio-1.04 bridge to the birth window and the final annihilation to the endpoint; all five band/group \(w_1\) labels reproduce; smallest sampled gap 0.05655940 meV. The v049 anchors were within \(4\times10^{-4}\) (birth) and \(1\times10^{-5}\) (annihilation) of the accepted roots; that is what a fold-law extrapolation from two-seed brackets is worth, and no more.

**Coverage under the declared model, both engines, path-replayed:** braid 1 → deepening → un-linking → v028 → first annihilation → post-transfer → braid 2 → cleanup → upper collision → (ratio-1.04 bridge) → flat birth → final annihilation → endpoint. The post-braid-2 late windows and sampled joins are covered. **Not replayed:** the preparation route (candidates only) and the lower un-link collision. The campaign is not "fully replayed", and the team's `COVERAGE.json` is the statement of record on what is.

## 2. Corrections accepted

| entry | said | corrected |
|---|---|---|
| v047 §1–2 | "three events located" | **candidates / brackets.** `prep_detail.py` samples five positive remote gaps and extrapolates (its "bisection" banner was false and is fixed); the extra-pair birth and annihilation are bracketed by finite global-search node counts, and a search miss is not a disappearance proof. Acceptance needs two-seed fold, charge and open-side checks, which are the team's. Preparation rows stay in the provisional section. |
| v047 §2 | "2e-5 … below the team's join tolerance; the residual is seed refinement" | **fails as stated.** \(2\times10^{-5}>10^{-6}\); the primary BM path was linear and TBG exact; fresh matched-model roots join to \(4\times10^{-15}\), BM linear/exact differ by \(8\times10^{-7}\) at that state, printed-seed rounding is \(5\times10^{-5}\); the old unrounded B-sweep roots were not saved, so that residual is **unattributed**, not explained. |
| v047 §2 | "a lower-gap node has appeared" at \(B=-0.25\) | **undercount.** Two lower-gap roots resolve in BM linear, BM exact and TBG exact, separation 0.06814524 (exact), both gaps \(<5\times10^{-13}\) meV. The birth location is still unresolved. |
| v047 §3, v049 | "every number … from the records"; ledger as validator | **table reproduction holds; the rest fails.** The footer event values and coverage status were literal strings; the kinetic header was not validated; the script reads arbitrary JSON without requiring ACCEPT, hashes, or complete engine/cutoff rows. It is a formatter. |
| v046 | "v046" adopted the team's v044 | the team's own v046 (cleanup, upper collision, v045 qualifications) is a separate record; both preserved with their source identities. |

## 3. Ledger authority

From v048 the ledger of record is the team's generator (`ledger_guard.py` → `LEDGER.md`, with `COVERAGE.json` for reviewed coverage annotations and `LEDGER_SOURCES.json` for digests), which requires `status == ACCEPT`, the version and kinetic tags, the protocol hash, complete case–engine–cutoff rows, finite values and bound source hashes, and keeps provisional preparation rows separate. My `ledger.py` is retitled a formatter for the historical summaries, its footer replaced by a pointer to `COVERAGE.json`, and its output renamed `LEDGER_historical.md`. The reader note in the team's `SCHEMA.md` (folds[], gapped_cases[], aggregate counts not to be merged, unknown schemas never inherit ACCEPT) is adopted as the contract for any future reader I write.

## 4. Next
Team `NEXT_SEQUENCE`: the preparation route with its event candidates under the acceptance gate, then the lower un-link collision. Toolkit: nothing named; if a reader for a new schema is needed I write it to `SCHEMA.md`. Standing limits unchanged: constant tunnelling, local-only \(N=8\), no physical-bilayer validation.

## 5. Self-corrections this entry
- "Located" for bracketed candidates, twice (v047, echoed in v049 §4 as "anchored"). Language now: candidate, bracket, extrapolation — until the team's gate accepts.
- A false banner in a script that made it into a share. Fixed in the script, recorded here.
- The ledger was sold as more than it was. Retitled.
