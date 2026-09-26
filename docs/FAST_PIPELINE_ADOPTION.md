# Fast pipeline adoption for new frozen runs

Alan authorized this pipeline on 26 September 2026. This policy applies to new runs; historical frozen implementations and evidence remain unchanged.

Source: Claude's `research/tools/fast_pipeline/` subtree at `a56d0c6a2f7957f4239d6f1ec80641c35af7443d`, imported byte-for-byte (tree `4737565465b0647536b9d6c08eaeb702f4f6c54c`).
Independent Codex review: https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5844535047.
Review evidence: `cc60ef8fb6db1b8e7bac11d9d8b27716ed812088`, `docs/audits/fast-pipeline/`.

## Required use

1. Build one `FastPointMatrix(base, assembly, coef)` per cutoff per job and reuse it for that job's points. Preserve the reviewed CASE FC49-77-K-Bm025-v2 assembly, Arb 128-bit context, `mid_float` semantics and one thread. Coefficients and precision stay fixed during the instance lifetime.
2. Freeze and push implementation, SPEC, controls and exact dependency bindings before physical calls. Include the fast-pipeline files in those bindings. Run `controls.py` at that exact frozen commit, supplying retained `--states` fixtures, and retain its result before any physical call. The independent review's 240 matrix comparisons and 24 state round trips do not substitute for the new run's controls.
3. Use jobs of at most 32 points, retaining the existing per-job subprocess isolation, resource limits, wheel/native provenance, receipts and 90-second limit. Keep full-spectrum eigensolves; subset eigensolves are not adopted. `reproduce_021.py` is a diagnostic, not a replacement production supervisor.
4. Retain all full spectra and real four-state arrays using `pack_states`, verify bit-identical unpacking, and hash the whole container in the evidence manifest. Store binary when the transport permits; base64 is only a transport representation when text is required. GitHub's blob API accepts base64 input to store a binary blob.
5. Keep normal Python execution: the reviewed controls and unpacker use assertions. Maintain manifest checks for both headers and payloads.
6. Post a frozen-plan comment on PR #2 before physical execution, execute without retries, commit evidence separately, and request Claude review bound to exact implementation and evidence commits. If a physical launch fails, stop and report.

The local review runtime verifies the locked wheel and installed native bytes, but does not expose `/proc/self/maps`. Its mapped-library provenance is therefore unverified. This documented limitation must not be converted into a claim that a physical worker passed full provenance.

## Standing scope

Computation is not gated on audits. Site publication requires the separate authorization and review process. Keep PRs #2 and #3 unmerged. Coordinate substantive results and corrections on PR #2; correct erroneous comments in place.

The result wording ceiling remains: "finite-cutoff numerical evidence consistent with candidate touching(s), with negative discrete (real-overlap) loop sign(s)". No certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff convergence is established. The 0.5 link threshold is discrete conditioning only. Fitted minima below fit residuals carry no gap information: "consistent with zero within the descriptive fit residual".

No new physical experiment or site version is created by this adoption. Further compute and a v29 site update remain Alan's decisions.
