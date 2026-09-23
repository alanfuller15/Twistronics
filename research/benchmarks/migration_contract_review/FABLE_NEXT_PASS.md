# Fable: close the remaining acceptance gaps

v078p makes substantive progress. The original all-rejected, no-pair and later-discovery controls now return failure with complete case accounting. The positive run reproduces the eight labels; full model/basis/geometry/diagnostic records are present. The assertion-versus-diagnostic distinction and metamorphic failure exit are fixed. Keep these changes.

The title “migration contract finished” is premature. The remaining issues concern acceptance of evidence and failure finalization, not a demonstrated numerical error in the supplied eight measurements.

## 1. Use a checker that validates content relationships

`verify_migration.py` accepts all ten invalid record variants in `CONTRACT_PROBES.json` after the specified changes to the run's own manifest. It can accept no rows, a duplicate case, the wrong charge label, a zero-overlap link, wrong source/model/basis identity, the wrong coordinate for a frame, missing link/transport/loop-frame records, and an empty manifest. File integrity alone does not verify these relationships.

The review supplies **`check_records.py`**, with a separate hash-bound **`CONTRACT_EXPECTATIONS.json`**, as an executable reference for this exact eight-case package. It accepts the intact supplied and fresh replay records; all 15 negative cases are refused. `CHECKER_REGRESSIONS.json` records the outcomes. This checker is deliberately bounded to v078p and is not a general topology validator.

Carry its contract into the delivery gate:

- Require the complete manifest key set and verify actual source and plan hashes against trusted expected identities.
- Validate a unique expected case list and a one-to-one actual row list. Derive accepted/rejected/blocked/error/missing summaries from those rows.
- Bind each row's full parameters to its model, harmonic, ordered basis, geometry, policy and absolute band indices.
- Require complete, nonoverlapping diagnostic slices and every expected frame/link/angle role in order. Match coordinates to their exact roles, not membership in a rounded set.
- Reconstruct root/external gaps and winding sums. Enforce recorded overlap, reality, Hermiticity, loop splitting, phase and winding thresholds; derive SAME/OPPOSITE from the winding product.

Do not copy only the pass count. Use the retained mutations as regressions. The checker cannot prove that stored records arose from an authentic execution or reconstruct frame overlaps without eigenvectors. Preserve that limitation.

## 2. Make consumer completion follow those checks

The real known refusal paths are improved, but `main()` still counts a normal return as ACCEPTED without checking its returned gate status. An injected result with `status='REJECTED'` is marked ACCEPTED and the run returns zero. Require `PASSED_SAMPLED_GATES` and validate the result schema.

Reject duplicate case identifiers before work begins. In the retained duplicate-plan control, two identical settings produce eight accepted rows but only four unique cases; the consumer reports COMPLETE and returns zero. Compare exact unique expected and observed inventories, not just lengths. Reconcile plan parameters with the actual constructor arguments rather than leaving `plan.model_defaults` informational.

After finalizing evidence, acceptance must require the record checker to succeed. Keep execution success, evidence integrity and sampled numerical acceptance explicit; each must affect the CLI result when required by the command's contract.

## 3. Finalize evidence after errors outside discovery

The discovery-specific fix works. A synthetic exception in geometry construction after the first B still leaves four row records and their diagnostics but no model file, geometry file, summary or manifest. The rows survive; their referenced context does not.

Use an outer failure/finalization boundary around geometry, model construction, sampling and output stages. Persist referenced model/geometry records before publishing a completed row, and write a structured INCOMPLETE summary for a caught exception. Mark pending cases explicitly. Avoid truncating an existing run silently; use a fresh run directory or a declared, tested replacement policy. This does not require a claim of recovery from arbitrary hardware failure.

## Small remaining pre-delivery fixes

The four new lint fixtures pass, but `LINT_PROBES.json` retains two false acceptances:

- `overlap 0.730` binds to an unrelated field in the cited JSON even though its overlap is 0.995703.
- `1.530e-10` binds to 1.5259312e-10 because significant trailing zeros are stripped. At four written significant digits, the correct value is `1.526e-10`.

Use explicit metric/JSON-pointer bindings and preserve intended precision; the broad relative-tolerance fallback still does not establish correct rounding. The README linter reports 18 findings, many involving nested paths or JSONL support; do not present that count as 18 numerical errors.

`failure_controls.py` currently records outcomes but does not assert its expected outcomes or return nonzero when they regress. Turn the suite itself into an enforcing gate. Preserve both forced and clean metamorphic records and subprocess logs instead of overwriting the forced JSON with the clean result.

## Return one focused package

Keep the same eight cases and thresholds. Return the unchanged input archive, focused source diff, consumer and verifier regression results, one clean positive run, all failure artifacts, source/model/path bindings, and a generated concise README. Do not add another consumer or a larger numerical sweep in this pass.

Retain these scope limits: same finite model and shared guarded framework; sampled checks; no continuous-path proof, complete inventory, independent physical validation, Euler-class change or cutoff-convergence claim.
