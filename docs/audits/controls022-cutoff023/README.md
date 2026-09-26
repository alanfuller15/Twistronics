# CONTROLS-E-022 / CUTOFF-F-023 partial review and workflow upgrade

Reviewer: Codex. Producers of 022/023: Claude. Date: 26 September 2026.

## Status

**Retained evidence checks: PASS. Concurrent-supervisor failure handling: MATERIAL_FINDING. Overall independent numerical verdicts: PENDING.** No independent physical e/f eigensolve was launched in this review. The 64 e regression results in 023 were verified as hash-bound producer assertions and source logic, not independently re-solved. This packet must not be cited as the two numerical PASS verdicts required for site v30.

Alan then clarified that the immediate objective is to upgrade the workflow. Codex added a replacement supervisor and a job-local reuse loader, with synthetic/retained-data controls. These additions are submitted for Claude's independent review; historical frozen sources/evidence are unchanged. No new region scan, partner study, cutoff g, site update or PR merge occurred.

| Packet | Frozen implementation | Execution |
|---|---|---|
| 022 | `4e0e6c4378609189a4fafc0c25ba06a0ac68bb81` | `75d9d5806d65ba81a37b5b109a36d489d3c34096` |
| 023 | `99c0c4ee6845fb6b637dc11c670f684129c20436` | `6394c414dee22421b370a312d80bbc03c3bae168` |
| 021 source | `ff61f6c8060c83e75d085dae21abbe5900b501eb` | `38204bfc987108e60d7e2c1b9561fdd0fe3c6057` |

Plans/results: PR #2 comments 5844662485 / 5844681636 and 5844709836 / 5844720468. Prior fast-pipeline review/adoption: 5844535047 / 5844544676.

## What was checked

- Exact implementation/execution bindings for all 84 dependencies of 022 and 86 of 023; runner/SPEC bytes unchanged at the bound execution commits.
- Unmodified `check_replay.py` passed for 022 (37 files) and 023 (86 files); MAP, REGRESSION, HOLONOMY and SUMMARY reproduced byte-identically with zero physical eigensolves. The unmodified 021 materializer also passed, checking all 125 extracted files and replay.
- A separate decoder and loop implementation reproduced all 108 022 and 144 023 loop/cutoff/group products, including signs, reversal signs, raw determinants, log determinants, polar determinants, minimum link singular values and sampled external gaps. `RETAINED_REVIEW.json` records all rows and comparison errors.
- 022: 896/896 historical energy/vector arrays and 896/896 gap values bit-identical to 013/015/016. The 013/015 execution trees differ from their historical source commits only in README corrections. The 016 archive's 40 extracted file hashes were verified.
- 023: all 60 reused files match SPEC and their source manifests; all 384 point/source/job/row mappings were independently reconstructed. The 021 manifest hash matches the bound source. The predeclared 64-point subset is exactly R3_r1_32 plus R2_baseline; every corresponding producer assertion is true. The worker compares newly solved full spectra and four-state bytes before setting that assertion.
- Re-derived b-to-c-to-d-to-e-to-f shell extensions. f has 249 vectors, dimension 996, central pair [497,498]. Independently derived e-to-f maximum absolute lower/upper gap changes are 4.092726157978177e-12 / 2.7995383788947947e-12 meV from retained spectra. Agreement between finite cutoffs is not infinite-cutoff convergence.

The 022 diff against 015 retains the full-spectrum `evr` solve, midpoint/eigenpair/nesting logic, metrics, loop-product function and reversal calculation. Changes restrict cutoffs to c/d/e, use six 013 loops, add lower single-band groups, use reviewed FastPointMatrix/pack storage, compare both external gaps, omit the 015 patch fit, and replace serial scheduling with concurrent scheduling and wall-clock accounting. The worker's numerical changes are consistent with the declared design. The new scheduling failure paths are not acceptable for reuse.

## Material supervisor finding

Both frozen `run()` functions raise from `finish()` on one failed/timed-out worker, or propagate a launch exception, without cleaning up other active process groups. They have no enclosing whole-batch cleanup. The top-level batch-deadline assertion can also escape without cleanup. Thus the watchdog/no-retry policy does not bound all workers after a failure.

`supervisor_faults.py` compiles only the unchanged producer `run()` AST and supplies deterministic fake process/clock/OS interfaces. For **each** producer, five scenarios were tested. Normal completion works. Worker failure, job timeout and batch timeout leave three other workers active without receipts; failure of the second launch leaves the first worker active without a receipt. These are control-flow reproductions, not real OS/process tests or physical launches. `SUPERVISOR_FAULTS.json` binds both source-file SHA-256s.

The retained actual executions have normal exits and recorded empty groups, so this finding does not itself demonstrate corruption of their numerical evidence. It prevents approving the historical supervisor as a template for future runs.

## Additive replacement and controls

`research/tools/concurrent_supervisor.py` / `bounded_worker.py` introduce fresh-directory-only scheduling, up to four isolated single-thread workers, per-job and batch deadlines, resource limits before worker exec, and cleanup of all active groups on observed failure, launch exceptions and SIGTERM/SIGINT. Direct children are reaped before writing failure receipts. No retries/resume. Receipts report planned points, not inferred actual eigensolver counts. Numerical acceptance remains separate.

`UPGRADED_SUPERVISOR_TESTS.json` records **14 real-process synthetic controls**: normal 1/2/4-worker executions with byte-identical synthetic outputs, worker failure, job timeout, batch timeout, file and memory limits, descendant cleanup, second-launch exception, supervisor SIGTERM, rejection of existing output directories, unbalanced jobs and overlapping points. Every attempted-job receipt was checked, process groups were empty, direct workers were reaped, and queued jobs were not admitted after observed failure. No physical matrices/eigensolves are involved.

`research/tools/retained_states.py` checks all source files at preflight, then each worker verifies and decodes only the exact bytes needed for its owned points. It returns read-only owned arrays, validates geometry labels/shapes/finite sorted spectra/orthonormality, and does not bypass per-point physical residuals or regression solves.

`REUSE_LOADER_TESTS.json`: all 768 arrays at 384 points match a separate decoder bit-for-bit. Seven negative controls reject wrong hashes, coordinates, labels, row mapping, dimensions, path traversal and duplicate point requests. On the same 16-job 023 partition, worker file checks drop **960 to 72** and worker bytes hashed **415,906,688 to 37,845,269**. The all-source preflight additionally reads 60 files / 25,994,168 bytes. These are I/O counts, not measured wall-time savings.

## Provenance and remaining work

`PREFLIGHT.json` records PASS from the unchanged reviewed loader-inventory checker: locked wheel SHA-256 `376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`, 42 installed native members, the loaded Python extension and three loaded libraries. This runtime lacks `/proc/self/maps`; the frozen 022/023 setup already uses `dl_iterate_phdr` and records `proc_maps_checked=false`. No gate was relaxed. No physical launch followed this preflight.

Before the overall numerical reviews can close: freeze/push an independent e/f recomputation harness and plan, post that plan, execute once with the required physical-worker provenance, and report evidence without retries. Then assess the two complete reviews. v30 must wait for those PASS verdicts and a separate Claude presentation PASS. New research choices remain Alan's decision.

Claim ceiling: finite-cutoff numerical evidence consistent with candidate touching(s), with negative discrete (real-overlap) loop sign(s). No certified touching, count, charge, partner correspondence, continuous isolation or infinite-cutoff convergence. The 0.5 threshold is discrete conditioning only. These checks add no accepted coverage area.
