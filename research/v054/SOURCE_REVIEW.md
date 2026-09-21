# v054 repair review and scope

This is an implementation/impact batch authorized after the inspection-only audit. It executes project tests and numerical models. The audit archive and frozen v053 files are unchanged; the scanner's inspection-only result is not relabeled as execution evidence.

## Source findings

- F01: BM.refine overwrote the optimizer object after wrapping without refreshing success/status/message. The new helper preserves both attempts, reports the final termination fields, checks coordinate/value finiteness and canonical-value consistency, and raises on rejected default calls. Explicit result inspection returns rejection reasons. SciPy defines these termination fields for each result: [SciPy 1.17.0 OptimizeResult](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.optimize.OptimizeResult.html).
- F02: report generation now consumes a complete-suite execution record, actual collected test IDs and call outcomes, JUnit, and source/test/input/environment hashes before writing. The runner uses a fixed shell-free subprocess and disables automatic pytest plug-in loading. Artifact disagreement and changed inputs reject publication. This is a consistency mechanism, not an authenticity guarantee against a producer who rewrites every artifact. [pytest output and JUnit documentation](https://docs.pytest.org/en/stable/how-to/output.html).
- F03: the new packager explicitly adopts a verified extracted-tree provenance contract, rather than requiring or reconstructing the missing prior ZIP. It verifies the prior manifest and every member, rejects unsafe/symlink paths, creates output parents, refuses overwrite, and verifies the delivered ZIP. Frozen historical packagers are preserved, not rewritten.
- F04/F05: Euler reality and the adjacent harmonic Hermiticity guard use runtime exceptions; legacy Euler/braid/knob analysis requires exploratory opt-in. This marks those routines as exploratory rather than asserting their winding/closure diagnostics now constitute full scientific acceptance. [Python assertion semantics](https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement).

## Active-path trace

The primary chain is impact_replay → replay_prep.run → Sample.node/frame/winding and spatial/frame/basis helpers. Sample.node uses scipy.optimize.least_squares and checks its success and node residual. It does not call BM.refine. The models adapter uses BM.H or TBG.H; the harmonic builder modifies a matrix, not a node search. The unused braid import was moved inside exploratory knob analysis.

Static separation is reinforced by eleven fail-on-call traps during the entire fresh preparation replay. Numerical agreement and zero calls support a route-specific non-impact result only. The stored runtime guard record is not a historical process trace; it cannot establish that every earlier campaign used the same path.

## Review boundary and remaining limits

Deep review covered the active replay/measurement/transport/acceptance path, endpoint/checkpoint code, report and package generation, the BM engine (especially refine), legacy Euler/braid/knob entry points, new evidence handling and new tests. The reference Hamiltonian and unrelated nested historical drivers received change/hash checks, not a new full semantic audit. No whole-archive coverage or comprehensive security claim follows.

NumPy 2.3.5, SciPy 1.17.0 and pytest 9.1.1 remain unchanged. threadpoolctl 3.6.0 records the loaded native libraries. The evidence records installed versions and native binary hashes; it is not a resolved wheel lock or new CVE scan. No physical-model claim requires a new literature interpretation in this batch. The three linked authoritative API sources were checked for the repair semantics.

The full-suite passing count and impact outcomes are generated into REPORT.md after execution. Do not substitute this source review, the preliminary development checks, or the historical 18-pass log for that bound evidence.
