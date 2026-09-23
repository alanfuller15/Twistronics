# Team handoff: migration-contract review

This page is the shared starting point for anyone, human or Claude, joining Alan Fuller's Twistronics migration-contract work. It records what is established, what is still open, what evidence closes an item, and which claims are out of scope.

## Who wrote this

Claude Code wrote this page in a cloud session opened on 2026-09-23. **This session had repository context only.** It read the files listed below at the checkpoint. It did **not** have the original Claude conversation's full history, including its reasoning, unpublished intermediate results or anything else not committed. Where this page and the committed review files disagree, the review files are authoritative.

Another Claude conversation is already implementing the corrections listed below. This page does not duplicate them, and this session ran no numerical sweeps or replays.

## Baseline

| Item | Value |
|---|---|
| Base branch | `migration-contract-review` |
| Checkpoint commit | `44dc66951057a995ee0999c785aca3e0e6c67092` ("Retain v078p evidence, contract counterexamples and stricter checker") |
| Partner attachment under review | `partner_v078p.zip`, SHA-256 `d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e` |
| Prior review | v077p, `partner_v077p.zip`, SHA-256 `bb46d2eec44f253d866104e4a7b14cee32aef7493e69e5b935969b07f10f45e1` |

Files read for this handoff:

- `research/benchmarks/migration_contract_review/README.md` (v078p review)
- `research/benchmarks/migration_contract_review/FABLE_NEXT_PASS.md` (implementation request)
- `research/benchmarks/partner_migration_review/README.md` (v077p review)

### What the checkpoint establishes

- The v077 failure paths reviewed there are repaired. All-rejected and no-pair runs return 1 with eight accounted rows. A later discovery failure keeps four accepted rows and four blocked rows with INCOMPLETE status.
- The eight labels reproduce in a fresh extraction. B = −0.25 is SAME and B = −0.30 is OPPOSITE, in both valleys and both coupled radius/mesh settings. Row numerics differ from the submitted values by at most 3.33067e-16, and diagnostics by at most 8.88178e-16, excluding timings.
- 42 tests pass: 38 helper tests and 4 lint fixtures.
- The reviewer's `check_records.py` with `CONTRACT_EXPECTATIONS.json` accepts the intact records and the fresh replay, and refuses all 15 negative cases. The 16 regression cases pass.

### What the checkpoint does not establish

- The delivery contract is **not** finished. The partner `verify_migration.py` accepts 10 of the invalid record variants in `CONTRACT_PROBES.json`.
- These failures are in acceptance and finalization software. They are not a demonstrated numerical error in the eight supplied measurements.

## Outstanding review items

These come from `FABLE_NEXT_PASS.md`. The other conversation owns implementing them.

1. **Content-level record checking.** The delivery gate must check that records agree with each other, not only that file hashes match. That means the complete manifest key set, and source and plan hashes checked against trusted identities. Expected cases must be unique and map one-to-one to rows, and the summary must be derived from the rows. Each row must bind its parameters to its model, basis, geometry, policy and band indices. Diagnostic slices must be complete, non-overlapping and matched to their exact coordinate roles. Gaps and windings must be reconstructed, thresholds enforced, and SAME/OPPOSITE derived from the winding product.
2. **Consumer completion.** A returned result must carry `status == PASSED_SAMPLED_GATES` and a valid schema. Duplicate case IDs must be refused before any work starts. Plan parameters must match the actual constructor arguments. Acceptance must require the record checker to pass.
3. **Finalization after non-discovery errors.** An error in geometry construction currently leaves rows but no model or geometry records, summary or manifest. Add an outer finalization boundary. Write referenced context before publishing a row. Write a structured INCOMPLETE summary that lists pending cases. Never silently truncate an existing run.
4. **Smaller pre-delivery fixes.**
   - The claim linter accepts `overlap 0.730` by matching an unrelated field. It also accepts `1.530e-10` for 1.5259312e-10 because it strips trailing zeros. Use explicit metric or JSON-pointer bindings and keep the written precision.
   - `failure_controls.py` must assert its expected outcomes and exit nonzero on regression.
   - Keep the forced and clean metamorphic records separately.

## Evidence requirements for closing an item

A correction counts as closed only with committed evidence, not a description:

- The unchanged input archive, with its hash, and a focused source diff.
- Consumer and verifier regression results that reuse the retained mutations in `CONTRACT_PROBES.json` and `CHECKER_REGRESSIONS.json`. Each invalid variant should now be refused, and the intact run should still be accepted. A pass count on its own is not enough.
- One clean positive run over the **same eight cases and thresholds**, reconciled against the checkpoint values.
- All failure artifacts, with subprocess exit codes and logs, for the injected controls: bad returned status, duplicate plan, and geometry-stage error.
- Source, model and path bindings, plus a generated concise README.
- Separate reporting of execution success, evidence integrity and sampled numerical acceptance.

Keep these limitations explicit. The checker cannot prove that the records came from an authentic execution. It also cannot recompute frame overlaps without the eigenvectors, which are not retained. Report lint finding counts as software findings, not as numerical errors.

## Scientific scope limits

The work covers one N = 4 model family and two coupled radius/mesh settings, (0.012, 96/300) and (0.008, 192/600). Radius and resolution are not varied independently. It covers both valleys and uses the same shared guarded framework throughout. All checks are sampled. None of the following is claimed or supported:

- a continuous-path proof,
- a complete node inventory,
- independent physical or experimental validation,
- an independent K′ implementation,
- a change in Euler class,
- cutoff convergence.

Do not add another consumer or a larger numerical sweep in this pass. The remaining consumers and sparse Newton/event detection stay outside this migration.

## Collaboration notes

- Branch from `migration-contract-review` and open pull requests against it.
- State the checkpoint commit you started from, and say whether you had the full conversation history or only the repository.
- Recurring automation and Auto-fix were left disabled for the initial connection test.
