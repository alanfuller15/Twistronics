# Checker readiness receipt

This is an execution-readiness check: it confirms this cloud workspace can run the existing baseline record checker. It is **not** a new scientific result, and it does **not** close the partner verifier defect. No numerical consumer, full replay, partner `verify_migration.py`, other mutation, sweep or implementation repair was run.

## What was run

Everything was run once, with `run_intake_checks.py`:

```sh
OPENBLAS_NUM_THREADS=1 python docs/intake-evidence/run_intake_checks.py
```

That script:

1. Checks `partner_v078p.zip` against the trusted SHA-256 `d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e`.
2. For each check, extracts the archive into its own fresh temporary directory using the review's `review_inputs.extract`, which also verifies every member against `INPUT_MANIFEST.json`.
3. Runs the unchanged `check_records.py` with the trusted `CONTRACT_EXPECTATIONS.json` on the retained positive `RUN`:
   - **intact:** no mutation.
   - **wrong_label:** first calls `contract_probes.mutate(RUN, 'wrong_label')`. This flips the first row's SAME label to OPPOSITE and refreshes `RUN/MANIFEST.json`, exactly as `contract_probes.py` prescribes. `contract_probes.run()` itself was not used, because it runs all 13 mutations plus the partner verifier and consumer workers.

The temporary extractions were deleted afterwards. The hashes of the committed originals were identical before and after the run (`originals_unchanged: true`).

## Results

| Check | Expected | Checker result | Exit code | Errors |
|---|---|---|---:|---|
| intact | accept | accepted, 51,050 checks | 0 | none |
| wrong_label | refuse | refused, 51,050 checks | 1 | `label from winding product B-0.25_v+1_r0.012` |

Both match the committed `CHECKER_REGRESSIONS.json` entries for `intact` and `wrong_label`.

## Runtime

Python 3.12.3 and numpy 2.3.5, in a fresh virtual environment. The review recorded Python 3.12.14 and numpy 2.3.5 (`RUNTIME.json`). The system Python in this workspace is 3.11 with no numpy, so a separate environment was needed.

## Files

- `RECEIPT.json`: baseline commit, bound file hashes, runtime, commands, return codes, outcomes, and what was not run.
- `intact/checker_result.json`, `intact/checker.log`: full checker output.
- `wrong_label/checker_result.json`, `wrong_label/checker.log`: full checker output.
- `wrong_label/ROWS.jsonl.diff`, `wrong_label/MANIFEST.json.diff`: the exact mutation.
