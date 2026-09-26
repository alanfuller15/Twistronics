# Checker readiness receipt

This is an execution-readiness check: it confirms this cloud workspace can run the existing baseline record checker. It is **not** a new scientific result, and it does **not** close the partner verifier defect. No numerical consumer, full replay, partner `verify_migration.py`, other mutation, sweep or implementation repair was run.

## What the runner does

```sh
OPENBLAS_NUM_THREADS=1 python docs/intake-evidence/run_intake_checks.py   # the two checks
python docs/intake-evidence/test_run_intake_checks.py                     # synthetic runner regressions
```

1. Checks `partner_v078p.zip` against the trusted SHA-256 `d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e`.
2. For each check, extracts the archive into its own fresh temporary directory using the review's `review_inputs.extract`, which also verifies every member against `INPUT_MANIFEST.json`.
3. Runs the unchanged `check_records.py` with the trusted `CONTRACT_EXPECTATIONS.json` on the retained positive `RUN`:
   - **intact:** no mutation.
   - **wrong_label:** first calls `contract_probes.mutate(RUN, 'wrong_label')`. This flips the first row's SAME label to OPPOSITE and refreshes `RUN/MANIFEST.json`, exactly as `contract_probes.py` prescribes. `contract_probes.run()` itself is not used, because it runs all 13 mutations plus the partner verifier and consumer workers.
4. Writes everything to a new `runs/<UTC timestamp>/` directory and refuses to reuse an existing one. Earlier receipts are kept as history, and an old `checker_result.json` can never stand in for the current subprocess's output.

The runner exits 0 only when every one of the following holds:

- **intact:** exits 0, `accepted: true`, and `errors: []`.
- **wrong_label:** exits 1, `accepted: false`, and `errors` is exactly `["label from winding product B-0.25_v+1_r0.012"]`. Any other refusal reason counts as a failure.
- **Both checks:** the current output file exists, parses as JSON, and has the right schema: `accepted` is a boolean, `checks` is a positive integer, and `errors` is a list of strings.
- **Originals:** the bound original files have the same hashes after the run as before.

The first runner judged each check only by its `accepted` flag. Codex's review 5286495246 showed that swapped exit codes, or the wrong refusal reason, would still have passed. `test_run_intake_checks.py` covers both counterexamples, plus missing, malformed and wrong-schema output.

## Runs

| Run | Runner | intact | wrong_label | Runner exit |
|---|---|---|---|---:|
| Top-level `RECEIPT.json`, `intact/`, `wrong_label/` (commit `9126bb2`) | First runner, which checked only the `accepted` flag. Kept as history. | accepted, 51,050 checks, exit 0 | refused, exit 1, `label from winding product B-0.25_v+1_r0.012` | 0 |
| `runs/20260923T031203Z/` | Corrected runner, sha256 `21801fdc…24f5` | accepted, 51,050 checks, exit 0, no errors | refused, exit 1, exactly the intended label error | 0 |

Both runs match the committed `CHECKER_REGRESSIONS.json` entries for `intact` and `wrong_label`. `runs/20260923T031203Z/RUNNER_TESTS.log` records the 12 synthetic runner regressions passing.

## Runtime

Python 3.12.3 and numpy 2.3.5, in a fresh virtual environment. The review recorded Python 3.12.14 and numpy 2.3.5 (`RUNTIME.json`). The system Python in this workspace is 3.11 with no numpy, so a separate environment was needed.

## Files per run

- `RECEIPT.json`: run id, baseline commit, repository head, runner hash, bound file hashes, runtime, commands, return codes, per-check outcome with reasons, and what was not run.
- `intact/checker_result.json` and `intact/checker.log`: full checker output.
- `wrong_label/checker_result.json` and `wrong_label/checker.log`: full checker output.
- `wrong_label/ROWS.jsonl.diff` and `wrong_label/MANIFEST.json.diff`: the exact mutation.
