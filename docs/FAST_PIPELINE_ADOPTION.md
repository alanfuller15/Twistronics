# Fast pipeline adoption for new frozen runs

Alan authorized this pipeline on 26 September 2026. This policy applies to new runs; historical frozen implementations and evidence remain unchanged.

Original reviewed source: Claude's `research/tools/fast_pipeline/` subtree at `a56d0c6a2f7957f4239d6f1ec80641c35af7443d`, first imported byte-for-byte at `28e8586b7675c2f2bf028a0ab2e0c2528859a0e1` (tree `4737565465b0647536b9d6c08eaeb702f4f6c54c`). The copy on this branch includes Claude's subsequent documentation-only corrections; new SPECs must bind the actual files they use.
Independent Codex review: https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5844535047.
Review evidence: `cc60ef8fb6db1b8e7bac11d9d8b27716ed812088`, `docs/audits/fast-pipeline/`.

## Required use

1. Build one `FastPointMatrix(base, assembly, coef)` per cutoff per job and reuse it for that job's points. Preserve the reviewed CASE FC49-77-K-Bm025-v2 assembly, Arb 128-bit context, `mid_float` semantics and one thread. Coefficients and precision stay fixed during the instance lifetime.
2. Freeze and push implementation, SPEC, controls and exact dependency bindings before physical calls. Include the fast-pipeline files in those bindings. Run `controls.py` at that exact frozen commit, supplying retained `--states` fixtures, and retain its result before any physical call. The independent review's 240 matrix comparisons and 24 state round trips do not substitute for the new run's controls.
3. Use jobs of at most 32 points, retaining the existing per-job subprocess isolation, resource limits, wheel/native provenance, receipts and 90-second limit. Keep full-spectrum eigensolves; subset eigensolves are not adopted. `reproduce_021.py` is a diagnostic, not a replacement production supervisor.
4. Retain all full spectra and real four-state arrays using `pack_states`, verify bit-identical unpacking, and hash the whole container in the evidence manifest. Store binary when the transport permits; base64 is only a transport representation when text is required. GitHub's blob API accepts base64 input to store a binary blob.
5. Keep normal Python execution: the reviewed controls and unpacker use assertions. Maintain manifest checks for both headers and payloads.
6. Post a frozen-plan comment on PR #2 before physical execution, execute without retries, commit evidence separately, and request Claude review bound to exact implementation and evidence commits. If a physical launch fails, stop and report.

## Concurrent workers and retained-state reuse

Alan requested these workflow upgrades on 26 September 2026. These are policy requirements for new frozen implementations; they do not modify or retroactively approve historical runs. Codex's additive implementation is in `research/tools/concurrent_supervisor.py`, `bounded_worker.py`, and `retained_states.py`; Claude infrastructure review passed at PR #2 comment 5845181342, binding e039de6ae4b6a9285fad0fa63155c1324ba45a55. Computation is not audit-gated, but physical execution still requires a frozen, pushed implementation, passing pre-call controls and a frozen-plan comment.

7. Use up to four isolated single-thread workers. Make the number of jobs a multiple of the worker count, for example 16 jobs of 24 points for four workers. Preserve the 32-point ceiling, 90-second job limit, 600-second batch wall limit, 3 GiB per-worker address-space limit and 64 MiB per-file limit. Freeze any tighter limits. The batch deadline governs admission and monitoring; separately declare the bounded cleanup grace and include cleanup in the elapsed-time report.
8. On any observed job failure, launch exception, timeout, SIGTERM or SIGINT, stop admitting work; terminate **all** active process groups, reap every direct worker, check group emptiness and retain failure receipts. Never resume or retry a physical batch. A new output directory is mandatory. Do not copy the 022/023 supervisors: their failure paths leave other workers running. Normal-exit evidence from 022 reproduces 896 historical arrays byte-for-byte; that is evidence for the tested workload, not a universal concurrency-invariance proof. Synthetic controls for the additive replacement cover 1/2/4-worker byte identity and failure cleanup. SIGKILL or host loss cannot guarantee cleanup or receipts and must never be treated as successful completion.
9. Bind every reused file by SHA-256 in SPEC, including both retained states and the SAMPLES rows that bind their coordinates. Preserve exact source commits and manifest identities. Check all declared reused files before a batch; inside each worker hash the exact bytes being decoded for the needed source jobs. Job-local loading is permitted, but cached data must never bypass these bindings. `retained_states.load_job` implements this without an inter-process cache.
10. At every reused-cutoff point, rebuild H and check both the nested-cutoff residual and the retained eigenpair residual. Reuse is of eigensystems, not an exemption from matrix/residual checks. Freeze their tolerances (022/023 used nested <1e-10 meV and eigenpair <1e-8 meV).
11. Predeclare a regression subset containing at least one complete loop or job per source. Re-solve with the historical full-spectrum `evr` path and require byte-identical full energies and retained four-state vectors. Keep the subset fixed; no adaptive replacements after a mismatch. Record the equality check and hashes of recomputed/reference arrays, in addition to ordinary job receipts. Source review and replayed assertion flags are not an independent physical recomputation.
12. Keep full-spectrum `scipy.linalg.eigh(..., driver='evr')` in production. Do not adopt `evd`, subset eigensolves or multithreaded BLAS within a job. The original reviewed float/Arb evaluation order and precision remain fixed. Alternative solvers in a separately declared independent review are comparisons, not replacements for the production method.

The new job-local loader reproduced all 768 reused arrays across 023's 384 points. With the same 16-job partition, per-job file checks fell from 960 to 72 and bytes hashed from 415,906,688 to 37,845,269; an additional all-source preflight checks 60 files / 25,994,168 bytes. These are verified I/O counts, not an end-to-end timing claim. 023's producer used 448 rather than 768 eigensolves (41.67% fewer); Codex independently re-solved all 64 e regression points byte-identically and compared 48 f points; numerical PASS is documented in `docs/audits/gates022-024/VERDICTS.md`.

Evidence and limitations: `docs/audits/controls022-cutoff023/README.md`. No higher-order momentum terms or effective-Hamiltonian reduction are introduced by these upgrades. Such a model change needs its own physical justification, frozen specification and comparison with the full finite-cutoff model.

## Runtime provenance

The earlier fast-pipeline control review could not complete its `/proc/self/maps`-based check. This environment still lacks that interface. The exact `three_front_001` setup used by 022/023 instead calls the previously reviewed glibc `dl_iterate_phdr` inventory in `docs/audits/parallel-domain-002-006/spotcheck.py`. The current zero-eigensolve preflight passed that unchanged check: locked wheel, 42 installed native members, the loaded extension and three loaded native libraries. It records `proc_maps_checked=false` honestly. This preflight does not stand in for the required check inside each physical worker.

## Standing scope

Computation is not gated on audits. Site publication requires the separate authorization and review process. Keep PRs #2 and #3 unmerged. Coordinate substantive results and corrections on PR #2; correct erroneous comments in place.

The result wording ceiling remains: "finite-cutoff numerical evidence consistent with candidate touching(s), with negative discrete (real-overlap) loop sign(s)". No certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff convergence is established. The 0.5 link threshold is discrete conditioning only. Fitted minima below fit residuals carry no gap information: "consistent with zero within the descriptive fit residual".

No physical experiment or site version is created by this workflow upgrade. The overall 022/023 numerical reviews now have Codex PASS after the frozen 200-solve independent review. v30 still requires Claude's presentation PASS binding its exact saved source before deployment. The next research computation remains Alan's decision; PRs #2/#3 stay unmerged.
