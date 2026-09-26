# Parallel full-domain continuation 005 — executed packet

Status: **INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE — unreviewed.** Executed by
Claude at Alan's direction; independent audit by Codex pending.

Final depth-9 attempts on the 179 frontier cells left by batch 004 (all in
q11), using runner `parallel_domain_005/parallel.py` at
`accee93c4d4e4ad89045c6c31cdf0faa7523ec8a`. Four slots ran at once on one
4-core machine, and every slot exited normally.

| Measure | Before (batch 004) | After batch 005 |
|---|---|---|
| Accepted full-square area | 65469/65536 = 99.898% | **262021/262144 = 99.953%** |
| Accepted cells | 2,154 | 2,299 |
| Frontier cells | 179 | **0** |
| Unresolved depth-9 cells | 89 | 123 (123/262144 = 0.047%) |

Of the 179 attempts, 145 were accepted and 34 became unresolved at depth 9.
No frontier remains at depth 9. Every remaining cell is a depth-9 cell that
this method did not certify, and batch 006 refines exactly those cells.

Verification: the merged verifier replays all 16 shards and checks bindings,
provenance, hash chains, queue order, per-record method-004 evidence, caps,
exact deadlines and the 512×512 full-square raster. It passes.

```sh
python research/benchmarks/parallel_domain_005_execution/materialize.py /tmp/pd005-replay
```

Claim ceiling: finite-cutoff-a local cell isolation and exact area accounting
only. No topology, seam, cutoff-convergence, v078 or experimental claim.
