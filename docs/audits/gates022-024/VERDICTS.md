# Codex independent numerical verdicts: PASS for 022, 023 and 024

Date: 26 September 2026. Frozen reviewer source `28d093c49bd49ca1f646478c0499c6920826936e`; pre-launch PR plan 5845281014. Exactly one launch, 200 full-spectrum solves, 26 jobs / two isolated single-thread workers. All jobs exited normally with empty groups. Batch 58.6455 seconds; no retry or adaptive work. Full spectra, four-state frames, native provenance, receipts and actual progress are retained in `execution/` (188 archive files). Archive replay independently reproduced 200 spectrum/gap comparisons and all 64 byte comparisons, without eigensolves.

| Packet | Independent recalculation | Maximum gap difference (meV) | Verdict |
|---|---|---:|---|
| CONTROLS-E-022 | e at 24 corners spanning all six local loops | 3.4923175462608924e-12 | PASS |
| CUTOFF-F-023 | f at 48 corners spanning all twelve loops | 3.602451670303708e-12 | PASS |
| 023 retained-e regression | All 64 declared points; full evr | 0; 64/64 complete spectra and four-state arrays byte-identical | PASS |
| SWEEP-D-024 | Both a/d at 32 fixed points, including all 8 historical regression points | 8.171241461241152e-12 | PASS for sampled-map scope |

Independent comparisons use the original Arb affine matrix construction and NumPy full eigh. This does not adopt a different production eigensolver. Maximum four-state residual is 2.16e-12 meV; maximum frame residual norm 1.99e-8. Every frozen tolerance passed.

## 022 and 023

Read together with `../controls022-cutoff023/README.md`, retained review, replays and supervisor controls. The earlier PENDING numerical status is now closed by these recalculations. All 108 + 144 loop/cutoff/group products were independently rebuilt from retained frames. 896 historical gap values and 896 arrays match byte-for-byte; all 60 reused-file bindings and all 384 source mappings were checked. f was re-derived as sorted(set(e + b-stencil)): 249 vectors / dimension 996 / selected pair [497,498]. All twelve loops preserve e/f patterns. Maximum retained e-to-f gap change is 4.092726157978177e-12 meV. Agreement between finite cutoffs is not infinite-cutoff convergence.

The historical concurrent supervisor's abnormal-exit cleanup defect remains a documented finding, not an endorsement. Successful historical executions have normal receipts and matching numerical evidence. The additive replacement (e039de6ae4b6a9285fad0fa63155c1324ba45a55) has Claude infrastructure PASS 5845181342 and was used here. Only that replacement is policy for new runs.

## 024

Implementation `528a9cccd71714770993d2fff971e23a52e07702`, execution `994ed33839fd1f346604068d4f7c8c905be3873d`. Exact implementation/execution runner, SPEC and 86 dependency bytes verified. Unchanged replay checked all 166 files and reproduced MAP, REGRESSION and SUMMARY exactly. Separate `review024.py` decoded all 8,208 full spectra, rebuilt all 4,104 sample gaps, exact 64x64 grid geometry, extrema/medians, a/d changes, strict periodic eight-neighbor minima, nearest-candidate distances and flags. All match. Historical 32 gap comparisons max error 7.123190925995004e-12 meV (tolerance, not byte identity).

Two lower-gap and three upper-gap sampled strict local minima. The lower d minimum is 1.1919622005548947 meV near R2; the upper d minimum is 1.2163534419857633 meV near R3. The fifth upper sampled minimum is 17.4144598543 meV away from the four local candidate neighborhoods. Zero flags under the <1 meV / distance >2/64 rule: every sampled lower/upper d gap already exceeds 1 meV. This does not establish a complete basin inventory or exclude narrow unsampled features. No follow-up refinement/loop was run. Same historical supervisor caveat applies.

## Progress-log recovery disclosure

Post-run archival checks found three local PROGRESS.ndjson files were truncated prefixes although their supervisor receipts bound complete files. All numerical arrays, RESULTS and other receipt hashes matched. Deterministic serialization from each receipt-bound RESULTS reproduced the complete progress text, and its SHA-256 and byte count matched the already-written supervisor receipt in all three cases. The archive preserves the observed prefixes separately, the recovered complete logs, and `PROGRESS_RECOVERY.json`. The cause of truncation is unknown. No receipt was rewritten and no calculation repeated. These recovered logs are disclosed as reconstructed evidence; numerical verdicts also rest on the retained arrays/results and independent replay.

## Publication scope

These are Codex numerical PASS verdicts for Claude's packets. Claude should review this Codex-produced recalculation packet. v30 may now be prepared and saved, but deployment still requires Claude's presentation PASS binding exact source/mirror SHAs and file hashes. PRs #2/#3 stay unmerged; next new research remains Alan's decision.

Claim ceiling: finite-cutoff numerical evidence consistent with candidate touching(s), with negative discrete (real-overlap) loop sign(s). No certified touching, count, charge, partner correspondence, continuous isolation or infinite-cutoff convergence. The 0.5 link threshold is discrete conditioning only. Adds no accepted coverage area.
