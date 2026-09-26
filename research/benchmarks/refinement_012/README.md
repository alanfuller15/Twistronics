# Depth-12 refinement

Continue the independently reviewed depth-11 partition only. The111 unresolved parents become444 depth-12 children. All3040 accepted cells are inherited exactly. Each of23 actual jobs handles at most20 cells, and all four children of a parent have the same owner. No recursive refinement.

Uses the same method004 primitive, strict verifier, fixed cutoff a,128-bit arithmetic and exact locked python-flint wheel. Limits:180s/job,1200s/batch,4 workers,3GiB/process,64MiB/file,8 endpoint factorizations/cell (3552 total maximum), no retries. Producer checks are not an independent audit.

Freeze this packet on GitHub before running. Commands from repository root:

```sh
python research/benchmarks/refinement_012/run.py controls
python research/benchmarks/refinement_012/run.py run --commit FULL_SHA --wheel /locked/wheel.whl --output /new/depth12
python research/benchmarks/refinement_012/run.py replay --commit FULL_SHA --output /new/depth12
```

The user authorized advancing the research engine after the depth-11 audit. This independently frozen one-level extension is not a pre-execution review PASS. Results require Claude review before any scientific promotion. No topology, seam, infinite-cutoff, experimental or project-completion claim. Neither PR is merged.
