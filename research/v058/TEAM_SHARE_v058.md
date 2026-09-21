# TEAM SHARE — our v058

Completed a fresh N8 endpoint-gap comparison in both modern engines under the frozen lab_nn_full model: A=−0.30, B=−0.40, T=−1.8, phi=80°, w0/w1=1.10, theta=1.05°, eps=0.003. Constant w1=110 meV and w0=121 meV are the declared approximation. BM retains linear reciprocal geometry and cutoff_tol=1e-6; reference retains exact reciprocal geometry and cutoff_tol=1e-9. They share the guarded eight-band measurement harness.

| Engine | Gap | N4 saved | N6 saved | N8 fresh | N8 − N6 |
|---|---|---:|---:|---:|---:|
| bm_lab | lower | 23.029392698 | 23.181551945 | 23.181591472 | +0.000039527 |
| bm_lab | flat | 2.869727102 | 2.776526865 | 2.776452275 | -0.000074590 |
| bm_lab | upper | 3.335680871 | 3.392818703 | 3.392854631 | +0.000035928 |
| bm_lab | next | 10.821556106 | 10.856038218 | 10.856037917 | -0.000000301 |
| ref_lab | lower | 23.029191352 | 23.181347872 | 23.181387398 | +0.000039526 |
| ref_lab | flat | 2.869923845 | 2.776726248 | 2.776651660 | -0.000074588 |
| ref_lab | upper | 3.335359140 | 3.392497811 | 3.392533739 | +0.000035927 |
| ref_lab | next | 10.821605530 | 10.856087169 | 10.856086868 | -0.000000301 |

All table values are meV. N4/N6 are retained, hashed v048 measurements; N8 is fresh. Largest absolute N6→N8 difference across these eight gap comparisons: **7.45902754e-05 meV**. Largest BM/reference N8 difference: **0.000320892265 meV**; the retained geometry conventions differ. Each of the four located gaps in each engine passes the finite-sample positivity and refinement checks. No new topological label is assigned.

Search scope is broader than the partner's original one-seed N8 refinement: 12×12 and 24×24 interval grids including both faces (13×13 and 25×25 points), all four edges split into 24 and 48 intervals, bounded refinements of sampled local minima, corners, inward edge seeds and retained N4/N6/partner positions with two diagonal offsets. Every seed must yield a successful finite non-worsening result with projected gradient ≤1e-4; failed attempts are retained before fallback. Final selected minima have positive local curvature at two step sizes; grid/edge minimum differences must be ≤0.001 meV. Reality, Hermiticity, eigen-residual, affine-Hamiltonian and analytic-gradient checks run explicitly. No silent coordinate wrapping is used.

Recorded N8 dimensions: [1060, 1060]. Distinct sampled coordinates per engine: [3657, 3633]. Recorded refinements: 486; optimizer attempts: 514; fallback attempts retained: 28. Both workers record matching runtime identities before and after execution with one BLAS thread each. The numerical plan was frozen before these workers; the publication plan was frozen after results and tests were authored. Hash agreement is internal consistency, not independent attestation.

All four reference results agree with the supplied rounded N8 output within the predeclared value/coordinate tolerances: **True**. The original v045 log explicitly describes N6-located, N8-refined minima. v048 later narrows its wording to local cutoff stability and adds per-start logging. Original stdout lacks starts/failed fields added in v048; no per-start JSON supplied. Source/run identity and historical optimizer outcomes not independently established. No original failure or fresh pass is inferred from that missing provenance. The fresh two-mesh/edge results are their own evidence.

**58 tests passed in bound run `20260921T025546Z_b2dbd1e0`**, evidence SHA256 `b172f32b1741ffd33284233e4425ab3b3c154416683f6111b026d0301e0f8638`. The report reads actual collected, executed and JUnit outcomes tied to source/tests/inputs/runtime. Tests cover nonfinite/escaped/stale/failed optimization outcomes, projected gradients, edge failure, mesh rejection, evidence tampering and packaging. Prior tracked artifacts are preserved; the old top-level README is retained in provenance.

Limits: N8 alone is freshly executed. N4/N6 values are read from hashed retained v048 endpoint records, not rerun here. Whole-chart grids, edge brackets and multistart cover finite samples; they do not certify a global minimum, continuous isolation or infinite-cutoff error. Both engines use lab_nn_full with constant w1=110 meV, w0=121 meV, kappa=0; BM uses linear and reference exact reciprocal geometry. They share this measurement harness. No N8 path replay, node-charge, Euler or w1 measurement is performed. Previous topology labels are retained without a new N8 certification. The supplied historical stdout is not bound to the current instrumented source or an independently established runtime; no original optimizer-failure claim is inferred. Physical-bilayer validation and a microscopic tunnelling strain law remain outside the measured model.

Next: choose a bounded N8 continuation through a previously gated critical event, with retained N4/N6 roots and the same model conventions. The present endpoint comparison does not resolve the remaining historical scalar/mass/angle and exploratory braid impact questions. Physical magnitude claims still require the inventor's intended acceptance target and a named microscopic tunnelling strain law.

Start with `research/v058/REPORT.md`, `SUMMARY.json`, `IMPACT.json`, `NUMERICAL_PLAN.json`, `HISTORICAL_TARGETS.json` and the two raw files in `results/`. The ZIP preserves prior team notes, audit findings, test evidence and numerical records.
