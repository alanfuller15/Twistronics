# Fable — next-pass brief and output quality standard

## Objective

Deliver a portable, reviewable sparse-mode contribution whose acceptance checks preserve absolute band identity, bounded roots, correct result attribution and complete work accounting. Measure its speed with those checks enabled.

Use commit `f9b7219091eb23b8ea7423611cea4f8e88438ceb` as the public baseline and the preserved `partner_v071p.zip` as the partner input. Keep a clear mapping between every correction and the retained review finding. The sparse assembly is useful, and the N10/N12 candidate coordinates survived dense checks. Preserve those useful results while addressing the unresolved implementation contracts.

This is an implementation and evidence task. A successful numerical sample or faster eigensolver does not by itself establish a continuous path, complete inventory or topological conclusion.

## Required corrections and acceptance evidence

| ID / priority | Requirement | Evidence needed to close it |
|---|---|---|
| F01 / integration blocker | Absolute band identity | Reproduce the accepted σ=100 meV window containing indices 173–178 where 171–176 were assumed. The corrected path must return the requested ordered bands or reject the request explicitly. Test the supported shifts, both engines and declared bases. State how index identity is established at every accepted frame/solve state. A straddling window, small eigenpair residual or one-time probe alone is insufficient. |
| F02 / integration blocker | Enforced numerical comparison policy | Replace the unused `RECERT` promise with an implemented policy. At each required check, reject nonfinite values, unavailable comparisons and errors beyond the declared threshold. Retain where checks occurred and their outcomes. Returning a disagreement number without enforcement is not a gate. Distinguish a numerical cross-check from a verified-arithmetic certificate. |
| F03 / integration blocker | Every root has the declared safeguards | Guard both flat nodes and the upper node, including a fixed reference box, coordinate domain, periodic image choice, isolation and the finite-segment conditions. Reuse the published guarded solver where possible. Reproduce the upper-node movement-by-0.2 counterexample with box 0.03, and show rejection. A per-step trust limit does not establish a full-run displacement bound. |
| F04 / integration blocker | Returned parameter and diagnostics refer to the same state | Cache by the actual parameter value, or explicitly evaluate the scalar solver's returned D. Emit the roots, offset, t and native checks from that exact record. Test a solver returning an earlier evaluated parameter. Also ensure an exhausted Newton return's gap is evaluated at its returned coordinate, or return the last evaluated coordinate with explicit failure. |
| F05 / required accounting | Count all work once | Correct repeated addition of cumulative `nS`. Retain distinct counts for sparse calls, dense comparisons, native spectra, failures and fallback work. Reproduce the 15-versus-7 synthetic case and the 19-versus-9 instrumented case. Make reported totals reconstructible from an evaluation ledger. Count constructor comparison work separately and include it in total time. |
| F06 / required input validation | Exact finite-model identity | Reject malformed, nonfinite, noninteger and duplicate index inputs before assembly. Adopt the existing accepted-path index policy for these campaigns. Bind the full ordered index list/hash, dimension, engine, model settings and source hashes to each run. Test ±1.9 explicitly. Keep the 87- and 89-vector N6 models distinct. |
| F07 / required portability | One reproducible entry point | Remove dependence on `/home/claude/joint/seeds_legA.json` and other private paths. Include the exact seed/model inputs used, a CLI/config example and dependency versions. A clean extraction must reproduce the declared smoke check. Preserve original partner input bytes. |
| F08 / required record integrity | Claims match retained evidence | Include every row supporting a table, every attempted evaluation needed to audit counts, and structured failures or stopping reasons. Do not advertise five retained cutoff rows when only two are included. State explicitly when a new follow-up uses reconstructed model metadata or different seeds. |

A narrower supported mode is acceptable when it is explicit and enforced. For example, rejecting nonzero shifts can close the unsupported-shift API behavior, but restricting σ to zero does **not** establish ordered-band identity throughout the remaining domain. That still requires a justified check. Do not silently expand support or weaken a tolerance to obtain a pass.

## Bounded workflow

1. Read the current review and record each finding as reproduced, disputed with evidence, or unresolved. Preserve the original archive.
2. Freeze the new plan: basis lists, state domain, solver and comparison thresholds, shifts, budgets, seeds and timing protocol. If it changes, version it and state why before rerunning the affected work.
3. Implement corrections in clearly identified new or corrected sources. Retain the existing dense acceptance path as the comparison baseline. Do not overwrite prior retained numerical records.
4. Run targeted positive and failure controls first. Include a case that would have falsely passed in v071p for each relevant correction. Explicitly label mocks and analytic controls; do not present them as physical examples.
5. Run a bounded numerical comparison on the documented event candidates. Reconcile outputs against native ordered-band spectra and the published dense path under exactly matching model/basis settings. Report any failed or unresolved cases without rescue tuning.
6. Benchmark the full supported path with its required checks enabled. Record setup/assembly, sparse solves, dense comparisons, total wall time, repeats/warmups, hardware and thread configuration. Keep the existing kernel-only timing separately labeled.
7. Produce the handoff package and fill out `FABLE_RESPONSE_TEMPLATE.md`. Run the documented commands from a clean extraction and retain their logs.

Do not launch a larger atlas or high-cutoff charge campaign as a substitute for closing the software contracts. Any wider scientific campaign needs its own declared plan and scope.

## Result and figure quality

Every result table must identify its finite model, units, seed/input source, pass/fail status, source record and scope. Separate numerical residuals, cross-engine differences, cutoff sensitivity and enclosure widths; they answer different questions. Display precision must not be described as physical accuracy.

Figures must be generated from retained, hash-bound records. Include readable labels, units, an informative caption and the relevant limitation beside the result. Provide the plotting source and vector output where applicable. Never plot assumed points, silently omit failed cases or use a smooth curve as evidence for behavior between samples. Use the exact reported run data rather than hand-transcribed example numbers.

## Required return package

- A short README with the concrete outcome, supported mode, remaining limitations and exact reproduction commands.
- A completed finding-response matrix with code paths and evidence paths for F01–F08.
- Original input archive plus its hash, source diff against the stated parent, and exact corrected sources.
- The frozen plan, model metadata, full basis lists, seeds and environment/version record.
- Control results, per-evaluation numerical records, complete counters and failure/stopping records.
- A reconciliation report and logs, plus a clean-extraction smoke log.
- Clearly separated kernel and full-path timings, with the measurement protocol.
- Reproducible figures/tables and a payload checksum manifest.

Use relative paths. Include no credential material, local caches or unneeded dependency environments. Every reported passing row must point to a retained result, and every retained result must point to its source and model identity.

## Definition of done

A contribution is **ready for integration** only when F01–F08 are closed for the declared supported mode, required controls pass, the bounded native/dense comparisons reconcile, and a clean extraction reproduces the documented check. A partial contribution can still be useful: name its unresolved gates and leave its integration status withheld.

Quality is demonstrated by reproducibility, correct attribution and honest bounds on the conclusion. A passing self-test suite, attractive plot or faster kernel alone does not close a reviewed defect.
