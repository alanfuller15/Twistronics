# REFINE-012 executed evidence — independent review pending

Frozen implementation: `1e25050bc3e4d69c94b9b5ae7a303b8114bd1db6`. Predecessor `3f52be02cf0dd27ac1d6c1cece8d45045358f2b4` was independently reviewed by Claude in PR #2 comment5842413474. The execution plan was posted before computation in comment5842775522.

## Retained outcome

- 111 depth-11 unresolved parents became444 depth-12 children.
- 333 children accepted;111 remain unresolved.
- All3040 inherited accepted cells are unchanged; final accepted count3373.
- Accepted full-square area: **16777105/16777216 = 99.999338388%**.
- New accepted area: **333/16777216**; subdivision itself adds no area.
- 65 parents fully resolved; accepted-child distribution `{"0": 13, "1": 9, "2": 8, "3": 16, "4": 65}`.
- Unresolved by quadrant: `{"q00": 15, "q01": 0, "q10": 0, "q11": 96}`.
- Status: `INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE`. Producer verification is not an independent review.

## Actual execution units

23 independent jobs:22×20 cells and one4-cell job; at most4 workers. Every parent's four children remain together. All444 cells have one owner and a retained evidence record. No retry or recursive refinement. Total3108 endpoint factorizations, cap3552. Batch352.369s against1200s; longest job68.651s against180s. Every receipt reports normal exit0 and an empty process group. All native runtime inventories bind the exact python-flint0.9.0 wheel SHA256376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76.

## Full replay, zero physical recomputation

From a checkout of this execution commit with Python3.12+, numpy and python-flint0.9.0 installed:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/refinement_012_execution/materialize.py /new/depth12 --repo .
```

The materializer restores every receipt, runtime inventory, cell evidence object and result byte; checks each SHA-256/size; then invokes the frozen strict verifier over all444 records. The verifier checks ownership, per-cell factor counts, deadlines, runtime wheel binding, inherited cells and complete nonoverlapping4096² occupancy. It independently reconstructs exact rational area, summary and partition from the records. SUMMARY.json and PARTITION.json must replay byte-identically. It makes no physical probe/eigensolver calls. Source files are checked against the exact implementation Git objects. Full physical reruns are separate and require the exact wheel.

No new accepted region may be presented as independently reviewed until Claude audits this exact execution commit. Scope remains fixed-cutoff-a local external-band isolation/accounting; no topology, seam, infinite-cutoff convergence, experimental or project-completion claim. Neither PR is merged. No site coverage update is included.
