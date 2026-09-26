# DYNAMICS-002 executed packet — independent review pending

Implementation frozen at `b95e5000f98995d4229fc9f6b7d3d1dae353e924` before all new grid 64 computations. Predecessor execution `3f52be02cf0dd27ac1d6c1cece8d45045358f2b4`, independently reviewed by Claude in PR #2 comment 5842413474. This packet contains every output from 205 actual jobs (204×20 points, final 16), all full eigenvectors, residuals, source bindings via implementation commit, native-wheel provenance and process receipts. No job was retried. All 4096 eigensolver starts completed normally in 54.11 s total; maximum job 1.113 s. Every process group was empty at receipt creation.

The retained grid 32-only diagnostic selected a conservative common 0–125fs window before grid 64 execution. Times are fixed 2.5 fs apart. This changes the observation window transparently after the predecessor's failed16/32 comparison; that failed packet remains unchanged. Coarse grid 32 modes and results must match the hashes frozen in SPEC.json.

| Packet width | Maximum common-window L1 | Maximum grid 32 edge mass | Maximum grid 64 edge mass |
|---|---:|---:|---:|
| 0.07 | 0.012583430088022115 | 0.009077206815471417 | 0.0009381357684840053 |
| 0.11 | 0.010271817794869728 | 0.004880162063816473 | 0.0005733987963151277 |

Both pass the frozen numerical thresholds: L1≤0.05 and edge mass≤0.01 on both boxes at every retained time. Probability error≤3.34e-16. These are numerical producer checks, not an independent audit. Site promotion remains **PENDING_INDEPENDENT_REVIEW**.

Restore from repository root with Python 3.12+ (tarfile data filter), numpy and scipy:

```sh
python research/benchmarks/three_front_001_execution/materialize.py /new/predecessor
python research/benchmarks/dynamics_002_execution/materialize.py /new/dynamics002 --repo . --coarse /new/predecessor/dynamics32 --replay-output /new/dynamics002-replay
```

The first command restores the reviewed predecessor. The second restores all 827 files and checks each SHA-256/size, all 205 source-bound receipts, complete distinct point ownership, deadlines, normal termination and exact locked-wheel provenance. It then reconstructs all 51 frames from stored 32/64 modes and compares every render byte and JSON result with the retained original. It makes **zero eigensolver calls**. Omit the optional flags for a receipt/hash-only restoration. Full physical recomputation uses the frozen runner and exact wheel, separately from replay.

`SUMMARY.json` mirrors the retained render result. `MANIFEST.json` binds all files, transport parts and producer Python/numpy/scipy versions. Reciprocal-component probabilities are summed incoherently: this is a coarse-grained envelope in the fixed cutoff-a central pair, not microscopic density. No cutoff convergence, seam, topology, experimental or certified-area claim. Both PRs remain unmerged.
