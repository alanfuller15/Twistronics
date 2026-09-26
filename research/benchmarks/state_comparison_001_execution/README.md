# STATE-COMPARISON-001 executed pilot

Implementation: `045a02ca79847e82756e8a25b3305850e8da1a9c`.
Producer: Codex. Independent post-execution review: PENDING.
Claude pre-execution PASS: PR #2 comment 5842947639; full receipt retained.

## Finding

At these 64 saved coordinates, the four-state group changes little from cutoff a (196-dimensional) to b (308-dimensional): minimum subspace singular value 0.9999521337, largest principal angle 0.560602 degrees, minimum external boundary gap 4.096880 meV. Mean weight in newly added components is 0.002776–0.002798%.

The selected pair changes more: minimum singular value 0.444542 and largest angle 63.605978 degrees. At that worst-overlap point (index 14, coordinates 22503/32768 and 23605/32768), the upper pair gaps are 0.00445322045 meV (a) and 0.00384280156 meV (b); four-state boundary gaps remain at least 4.15064145 meV there. This is consistent with mixing within a broader stable group. It does not establish a unique state correspondence or convergence.

Across all points, upper pair-gap changes range from -7.437644 to +7.385016 micro-eV. Small added-basis weight alone does not establish stability of such a narrow gap.

## Execution and checks

Eight jobs of eight coordinates, maximum two simultaneous workers, 128 eigensolver starts. Batch 5.885110 seconds; slowest job 1.558805 seconds. No retries or failures. Nested matrix residual is zero; maximum eigenpair residual 1.89826e-12 meV. All job receipts and recomputed subspace metrics passed the frozen verifier. Summary is separately derived by summarize.py. Replay performs no physical eigensolves.

Raw spectra, four eigenvectors per cutoff, metric rows, logs, wheel provenance, review receipt, and resource receipts are retained in archive parts, with SHA-256/byte manifest. Original frozen plot is retained. Colored markers are samples, not certified area; plots do not interpolate. Four-state agreement must not be interpreted as a topological or infinite-cutoff result.

## Replay

Python >=3.10 with numpy/scipy/matplotlib and the frozen source dependencies available in the repository. Fetch the implementation commit, then run:

```
python research/benchmarks/state_comparison_001_execution/materialize.py /path/to/new-output --repo /path/to/Twistronics
```

Materialization verifies every archived byte, invokes the frozen metric verifier and checks the summary. The verifier compares derived floating-point metrics with its declared tolerances; it does not promise bit-identical cross-platform SVD results.

## Authorization and review policy

User instruction on 2026-09-26: “Proceed. Don’t let audits gate computation”. Authorized bounded computation may proceed before independent audit. Numerical controls, resource bounds, exact-commit provenance and truthful pending-review labels remain required. Neither PR may be merged. This run already had a genuine Claude pre-execution PASS; its frozen runner and receipt were not altered to bypass a gate. Future runners should record authorization separately from optional review, rather than manufacture review receipts.

Next suggested small experiment: compare pair weight/rotation within this four-state group around the worst-overlap coordinates, and test a third nested cutoff before extending any convergence interpretation.
