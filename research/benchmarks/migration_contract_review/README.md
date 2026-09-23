# v078p migration-contract review

**The known v077 failure paths are repaired, the eight labels reproduce, and the submitted numerical records are consistent. The delivery contract is not yet finished: the partner verifier accepts invalid records, and errors outside discovery can leave incomplete evidence.**

This review adds `check_records.py`, a stricter acceptance reference for the exact eight v078p cases. It accepts the supplied and fresh replay records and refuses all 15 negative cases. The 16 regression cases, including the intact positive control, pass. It supplements the partner consumer; it does not silently replace or repair it.

## What improved and what remains

| v077 request | Verified progress in v078 | Remaining boundary |
|---|---|---|
| Reject failed/missing cases | All-rejected and no-pair controls return 1 with eight accounted rows | Duplicate case definitions can still produce a false COMPLETE; a returned bad gate status is ignored |
| Keep work after later failures | Later discovery failure retains four accepted rows and four blocked rows, with INCOMPLETE status | A geometry-stage error leaves rows/diagnostics but omits their model/geometry context and final summary |
| Retain model, basis, path and diagnostic evidence | Files and references are present; the intact and replayed records reconcile | The verifier misses content inconsistencies despite current file hashes |
| Supply a migration-specific plan | Plan explicitly declares discovery and two coupled settings; source diff is supplied | Case uniqueness and plan-to-constructor parameter agreement need enforcement |
| Enforce metamorphic assertions | Forced MR1 fails with code 1; clean run succeeds; MR6 is explicitly diagnostic-only | The enclosing failure-control suite does not enforce its expected outcomes |

The supplied control program calls `main()` directly for its three consumer controls, recording its return value; its own process exits zero. The CLI uses `sys.exit(main(...))`. The metamorphic controls record actual subprocess exits. Reviewer consumer controls exercise `sys.exit(main(...))` in separate processes.

## Numerical replay

The original attachment is retained unchanged as `partner_v078p.zip`, SHA-256 `d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e`. The original outer manifest, all four retained run manifests and bound source hashes check out. The guarded modules and nested v074p engines are unchanged from v077; see `SOURCE_COMPARISON.json`.

A fresh source extraction ran the full positive consumer once. Both the partner verifier and reviewer checker accept its eight rows. The supplied 38 helper tests plus four lint fixtures pass: **42 tests** (`TESTS.log`). The unchanged supplied failure-control script reproduces its recorded outcomes (`SUPPLIED_CONTROLS_EVIDENCE.zip`). Its clean metamorphic values match exactly: eight asserted rows and one diagnostic-only row.

| Case | Label | Largest node gap (meV) | Smallest link overlap |
|---|---|---:|---:|
| `B-0.25_v+1_r0.012` | SAME | 1.47056e-10 | 0.99802884 |
| `B-0.25_v-1_r0.012` | SAME | 1.47056e-10 | 0.99802884 |
| `B-0.25_v+1_r0.008` | SAME | 1.47056e-10 | 0.99951130 |
| `B-0.25_v-1_r0.008` | SAME | 1.47056e-10 | 0.99951130 |
| `B-0.30_v+1_r0.012` | OPPOSITE | 1.52593e-10 | 0.99785807 |
| `B-0.30_v-1_r0.012` | OPPOSITE | 1.52593e-10 | 0.99785807 |
| `B-0.30_v+1_r0.008` | OPPOSITE | 1.52593e-10 | 0.99920169 |
| `B-0.30_v-1_r0.008` | OPPOSITE | 1.52593e-10 | 0.99920169 |

Excluding measurement timings, 157 of 168 row numeric leaves match exactly; the maximum discrepancy is 3.33067e-16. All 16,472 diagnostic rows are retained; 120,332 of 120,720 numeric leaves match exactly, with maximum difference 8.88178e-16. Model, basis, policy and complete geometry values match exactly. These small differences are in floating-point diagnostics and winding values; labels agree.

The reviewer checker performs 51,050 record checks on the positive replay. These are numerous checks over repeated records, not that many independent scientific tests. It verifies case/source/model/basis identity, exact coordinate roles, complete diagnostic sequences and stored scalar gates. Full Hamiltonians/eigenvectors are not retained, so it does not independently recompute spectra, overlaps or eigenvector angles.

## Verifier controls

Each case begins with a fresh copy. Cases marked as refreshed in `CONTRACT_PROBES.json` recompute the run's own manifest after an explicitly invalid record mutation, as a producer writing a new file would. This distinguishes file-integrity checking from scientific-record consistency. It does not bypass an independently trusted outer archive hash or imply these defects occurred in the genuine run.

| Control | Change | Partner verifier | Reviewer checker |
|---|---|---|---|
| intact | No mutation | ACCEPT | ACCEPT |
| missing_geometry | Remove required geometry; retain original manifest | REFUSE | REFUSE |
| unrefreshed_angle | Alter one angle increment without refreshing manifest | REFUSE | REFUSE |
| empty_rows | Remove every row; leave COMPLETE/eight accepted summary | ACCEPT | REFUSE |
| duplicate_row | Replace last row with first; one expected case absent and another duplicated | ACCEPT | REFUSE |
| wrong_label | Flip first SAME label while retaining same-sign winding pair | ACCEPT | REFUSE |
| wrong_source | Wrong guarded source hash in summary | ACCEPT | REFUSE |
| wrong_model | Change row model strain from .003 to .02; retain plan and numerical records | ACCEPT | REFUSE |
| wrong_basis | Replace first basis vector; retain declared ordered-basis hash | ACCEPT | REFUSE |
| zero_overlap | Set a transport link overlap to zero, below policy .5 | ACCEPT | REFUSE |
| wrong_frame_role | Move transport:1 frame to a node coordinate that belongs to geometry but is not transport:1 | ACCEPT | REFUSE |
| missing_link_frames | Keep only node frames and angle increments; remove all links and other frames and update slice offsets/counts | ACCEPT | REFUSE |
| empty_manifest | Replace run manifest with empty mapping while keeping files present | ACCEPT | REFUSE |

The partner verifier correctly refuses a missing required file and unrefreshed corruption. It incorrectly accepts ten other invalid variants. In particular, a same-sign winding pair can be labeled OPPOSITE, and an overlap below the policy threshold can still verify. The genuine supplied run passes the stronger checks; these controls establish missing safeguards rather than observed bad physics.

The new checker is bounded to this specific case set and source identity through `CONTRACT_EXPECTATIONS.json`. It refuses incomplete runs for acceptance; refusal does not mean their retained failure records are useless. It is a reference to integrate and test, not a claim of a generally complete validator.

## Other retained controls

- **Late geometry failure:** process exits 1 after four synthetic accepted rows. Only `BASIS.json`, `ROWS.jsonl` and `DIAGNOSTICS.jsonl` exist; model/geometry records, summary and manifest are absent.
- **Bad returned gate status:** an injected normal return carrying `status='REJECTED'` is marked ACCEPTED; eight rows produce COMPLETE and process exit 0. This uses the declared measurement injection point and is not an observed behavior of the unchanged guarded API.
- **Duplicate plan cases:** duplicate settings/case IDs produce eight rows but only four unique cases; the consumer reports COMPLETE and exits 0. It should reject the malformed plan before measurements.
- **Claim linter:** Unicode minus and supplied rounding fixtures pass. A wrong-field value and an incorrect trailing-zero precision remain accepted. The README lint emits 18 findings and exits 1; many involve path/JSONL limitations, not false physical results.

`CONTRACT_PROBES_EVIDENCE.zip` stores exact changed files, deleted-file descriptions, subprocess output and original verification results for every verifier control, plus the complete synthetic consumer outputs. `LINT_PROBES.json` stores the prose, data and findings. `FABLE_NEXT_PASS.md` turns these into a focused implementation request.

## Reproduce and inspect

Python 3.12; package versions are in `REQUIREMENTS.txt`. The numerical runner uses two isolated worker processes at most, a single BLAS thread per process, and fixed time limits. It retains errors rather than enlarging the workload. No new cutoff, radius or mesh campaign was run.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python run_replays.py
python contract_probes.py
python lint_probes.py
python reconcile.py
python report.py
```

To run the bounded checker on an extracted partner source/run pair:

```sh
python check_records.py /path/to/partner/RUN /path/to/partner result.json
```

Read `SUMMARY.json`, `CHECKER_REGRESSIONS.json`, and `FABLE_NEXT_PASS.md` first. The original attachment and generated evidence ZIPs carry the complete underlying records; `MANIFEST.json` binds this review package. The numerical scope remains one N=4 model family, two coupled radius/mesh settings and both valleys, using shared guarded machinery. No continuous-path proof, complete inventory, physical validation, Euler-class change or cutoff-convergence claim follows.
