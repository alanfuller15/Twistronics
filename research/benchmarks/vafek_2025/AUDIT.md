# v067 intake audit and benchmark boundary

## Summary

The uploaded v067 package retains internally consistent frozen inputs and checkpoint records. Its stored 107-pass test report agrees with the retained JUnit count and artifact hashes; those historical tests were not rerun here. The project contains many archived versions, so the scanner ranking is dominated by historical code and its own bundled scanner. The new paper benchmark passes two spectral formula checks but remains unresolved off-axis; no complete Figure 5 reproduction or novelty claim follows. This audit is sampled, not complete.

## Ranked actions

| Priority | Problem and action | Tier | Verdict |
|---|---|---|---|
| Red | Off-axis benchmark assemblies disagree; reconcile basis/sign conventions before using this as a topology validation gate. | Published equations + sandbox comparison | Unresolved |
| Red | Initial whole-domain count expectation and enlarged-domain search disagree; retain failure and improve node inventory before claiming completeness. | Sandbox, self-tested | Fails initial gate |
| Yellow | The current v067 batch only tracks U1/U2, with no fresh X-node inventory. Complete adjacent-gap coverage before extending topology claims. | Checked source and retained report | Limitation confirmed |
| Yellow | No microscopic correspondence established between the paper's interacting valley boost and the uploaded model controls. Keep the benchmark separate. | Fetched paper + checked source | Unverified mapping |
| Yellow | Static test labels are not execution coverage. Archived duplicates and basename matching can distort priorities. | Checked scanner source | Heuristic only |
| Green | Frozen inputs, runner hashes, ten checkpoint/aggregate matches and frame hashes match their stored records. | Sandbox read-only inspection | Holds internally |
| Green | Retained JUnit has 107 cases with no failure children and matching report-artifact hashes. | Sandbox read-only inspection | Holds as retained evidence, not fresh execution |

## Inventory and review scope

Layer 1 examined 1,411 code files, 67,923 scanner-counted lines, 175 test files, and zero recognized fixture files. It flagged 817 files without a detected test relationship, 16 TODO-like markers and zero matches to its limited secret patterns. Zero detections are not a security clearance. The complete per-file inventory is in `audit-layer1.json`; its original ordering is preserved.

Ranking is `(no detected test ? 3 : 0) + 5*secret_hits + TODO_count + (lines>200 ? 1 : 0)`. This orders review attention, not scientific or security severity. The scanner reported normal coverage confidence, which does not establish test execution coverage.

Deep-read cutoff: nine source files. Original ranks 1 and 2 are the bundled `audit.py` and `tool_quality_weighting.py`; byte comparison confirms they match the uploaded scanner sources inspected before execution. Seven current v067 files were explicitly promoted for relevance: `transport.py` (934), `reconcile.py` (935), `evidence.py` (937), `run_window.py` (938), `numerics.py` (940), `joins.py` (942), and `acceptance.py` (944). Original ranks 3–5 are historical numerical sources and were not deep-read; there is no claim to have reviewed the top nine in order. The v067 report and numerical plan were also inspected. Unreviewed scientific engines, historical code and dependency CVEs remain outside this audit.

| Claim | Tier | Verdict | Provenance |
|---|---|---|---|
| Scanner does not execute project code in this invocation | Checked scanner source and command | Holds | No `--run-tests`; only subprocess call guarded by RUN_TESTS |
| Scanner has no output writes | Checked source | False if reporting flags used | `--json` and `--sarif` write requested files; JSON was requested here |
| Scanner makes network requests/deletes files | Checked execution path | No such operation found | Scanner and imported weighting module reviewed |
| Roots reject failed solves, large residuals and out-of-domain results | Checked source | Holds as implementation | `numerics.root` checks optimizer, gap and domain |
| Frame joins bind predecessor records and array hashes | Checked source + hashes | Holds internally | `joins.py`; `v067-inspection.json` |
| Transport establishes a certified continuous gap bound | Checked source | Does not hold | Finite sampling and located minima only |
| Report gate checks full phase outcomes and JUnit identities | Checked source | Present, not rerun | `acceptance.py` |
| 107 historical tests passed in this session | Sandbox | False | Only saved records inspected |
| Two numerical engines provide independent physical validation | Checked report/source | Not established | Shared measurement layer and model assumptions |
| New benchmark establishes an Euler class or non-Abelian charge transport | Sandbox | Not implemented | RESULTS.json limits |

`evidence.py` describes itself as read-only but defines a `write` helper; the intake inspection did not call it. No archived project module was imported for this audit. The scanner's optional weighting import may create Python bytecode caches; its source inspection found no external I/O at import time. `genesis.py` is absent from the uploaded plug-in; the boot directions were inspected manually. The existing user instruction to proceed supplies the objective; no charter amendment or ratification is inferred.

Verification vocabulary: spectral comparisons against fetched formulas are reference checks; internally authored code and diagnostic tests remain self-tested. No external scientific validation or execution attestation is claimed. A reviewer can reproduce the benchmark with the README commands and inspect the unresolved cases. The report remains unconfirmed as consumed until Alan has reviewed it.
