# Correction intake: v078p follow-up package

This page defines how the next corrected partner package will be reviewed when it arrives. The acceptance request is `research/benchmarks/migration_contract_review/FABLE_NEXT_PASS.md` at baseline `44dc66951057a995ee0999c785aca3e0e6c67092`. If this page and that file disagree, that file wins.

**Status: every correction below is UNREVIEWED.** No corrected package has been received in this workspace. The original Claude conversation owns the implementation fixes. Nothing on this page, and nothing in `docs/intake-evidence/`, means those fixes are done.

This session can't retrieve unpublished files from the original Claude conversation. It sees only what is committed to this repository or attached to this PR.

## Correction map

Paths are relative to `research/benchmarks/migration_contract_review/` unless they are prefixed with `partner:`. That prefix means a file inside the partner archive.

| # | Correction | Existing probe or script | Baseline behavior (v078p) | Evidence needed to close | Status |
|---|---|---|---|---|---|
| 1 | Content-consistency checking in the delivery gate | `contract_probes.py` (13 verifier mutations), `check_records.py` + `CONTRACT_EXPECTATIONS.json`, `CHECKER_REGRESSIONS.json` | `partner:verify_migration.py` accepts 10 of the invalid variants. The reviewer checker refuses all 15 negative cases. | The new gate refuses every invalid variant in `CONTRACT_PROBES.json` after the prescribed manifest refresh, accepts `intact`, and is run on the retained mutations. A pass count alone does not close this. The checker's limits stay stated: it can't prove the records came from an authentic run, and it can't recompute overlaps without the eigenvectors. | UNREVIEWED |
| 2a | Returned gate status and result schema | `consumer_control_worker.py wrong_gate_status` via `contract_probes.py` | A normal return with `status='REJECTED'` is recorded as ACCEPTED, and the run exits 0 as COMPLETE. | Consumer control shows a nonzero exit, a non-ACCEPTED row, and a non-COMPLETE summary. Acceptance requires `PASSED_SAMPLED_GATES` and a valid schema. | UNREVIEWED |
| 2b | Unique case inventory | `consumer_control_worker.py duplicate_case`, verifier mutation `duplicate_row` | A duplicate plan gives 8 rows but only 4 unique cases, reported as COMPLETE with exit 0. | The malformed plan is refused before any measurement. The unique expected inventory matches the observed inventory exactly, not just by count. | UNREVIEWED |
| 3 | Plan-to-constructor parameter binding | Verifier mutation `wrong_model`. No consumer-level probe exists yet. | `plan.model_defaults` is only informational. A row with changed strain still verifies. | A focused source diff reconciles plan parameters with the actual constructor arguments. A regression shows a mismatched parameter refused, and `wrong_model` is refused by the delivery gate. | UNREVIEWED |
| 4a | Finalization after geometry or other non-discovery errors | `consumer_control_worker.py late_geometry` | Exits 1 with only `BASIS.json`, `ROWS.jsonl` and `DIAGNOSTICS.jsonl`. No model or geometry records, summary or manifest. | The same injection keeps model and geometry context for every published row, writes a structured INCOMPLETE summary with pending cases, and exits nonzero. The complete failure artifacts are retained. | UNREVIEWED |
| 4b | Behavior when the run directory already exists | None exists. | Not tested in v078p. | A fresh run directory, or a declared and tested replacement policy, with a regression showing no silent truncation. | UNREVIEWED |
| 5 | Linting bound to the right metric, with correct precision | `lint_probes.py`, `LINT_PROBES.json` (cases `wrong_field`, `incorrect_trailing_zero_precision`) | The linter accepts `overlap 0.730` against an unrelated field, and accepts `1.530e-10` for 1.5259312e-10. | Both cases are refused, and the three currently correct cases still behave as before. Claims use explicit metric or JSON-pointer bindings and keep the written precision. Lint counts are reported as software findings, not numerical errors. | UNREVIEWED |
| 6a | Failure controls that enforce their outcomes | `partner:failure_controls.py`, `SUPPLIED_CONTROLS.log`, `SUPPLIED_CONTROLS_EVIDENCE.zip` | Records outcomes but exits 0 regardless. | The suite asserts its expected outcomes and exits nonzero when a deliberately regressed control is introduced. That regression run must be shown. | UNREVIEWED |
| 6b | Forced and clean metamorphic evidence kept separately | `partner:metamorphic.py`, `partner:METAMORPHIC.json` | The clean result overwrites the forced MR1 JSON. | Separate forced and clean records plus their subprocess logs. Forced MR1 exits nonzero. The clean run keeps 8 asserted rows plus 1 diagnostic-only row. | UNREVIEWED |

## Incoming delivery requirements

A corrected package is ready for review only when all of the following are present:

- **Archive:** the corrected archive preserved byte for byte, with its SHA-256 and its producer baseline (the commit or archive it was built from).
- **Source changes:** a focused source diff against the v078p sources. Any change to the hashes in `CONTRACT_EXPECTATIONS.json` must come from an explicit, reviewed source change. The trusted expectations must never be rewritten just to make a new package pass.
- **Cases and thresholds:** the same eight cases and the same thresholds. No additional consumer and no larger sweep.
- **Regressions:** consumer and verifier regression outputs that enforce their outcomes through exit codes, reusing the retained mutations and consumer controls above.
- **Positive run:** one clean positive run, reconciled against the baseline labels and scalar values.
- **Failure artifacts:** the complete failure artifacts for every injected control, with subprocess exit codes and logs.
- **Separate reporting:** execution success, evidence integrity and sampled numerical acceptance reported separately.

If something is missing, it is listed as missing. This repository contains no placeholder files standing in for evidence that hasn't been received.

## Checker readiness

`docs/intake-evidence/` holds a receipt showing that this cloud workspace can run the existing baseline checker. It is an execution-readiness check only. It is not a new scientific result, and it does not close the partner verifier defect.

## Scope limits (unchanged)

The scope is the same finite N = 4 model family and two coupled radius/mesh settings, both valleys, and the shared guarded framework. All checks are sampled. There is no continuous-path proof, complete inventory, independent physical validation, Euler-class change or cutoff-convergence claim.
