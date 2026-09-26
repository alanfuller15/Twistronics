# Batch 006 — depth-10 refinement of unresolved cells, executed packet

Status: **INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE — unreviewed.** Executed by
Claude at Alan's direction; independent audit by Codex pending.

Runner: `parallel_domain_006/parallel.py` at
`9cfa9129de73c25ce6d5c3f7bf18919836bffbba`. Only the 123 cells left
unresolved at depth 9 after batch 005 were reopened, as their 492 depth-10
children. Nothing else was refined.

The work ran on 8 slots across two 4-core machines. Slots 0–3 ran on the
coordinator; slots 4–7 ran on a sibling session and were pushed at
`dba55eab` (see `SLOTS4567_NOTES.md`). Every slot exited normally.

| Measure | Before (batch 005) | After batch 006 |
|---|---|---|
| Accepted full-square area | 262021/262144 = 99.9531% | **131057/131072 = 99.9886%** |
| Accepted cells | 2,299 | 2,671 |
| Unresolved cells | 123 at depth 9 | **120 at depth 10** (15/131072 = 0.0114%) |
| Frontier cells | 0 | 0 |

- **Depth-10 attempts:** 372 of 492 were accepted (76%). In q00, 53 of 72
  were accepted; in q11, 319 of 420.
- **Depth-9 parents:** 76 of the 123 are now fully accepted; 32 are partly
  accepted; 15 have all four children unresolved.
- **Where the unresolved cells are:** 101 in q11 and 19 in q00.

Verification: the merged verifier over all 32 shards checks bindings,
provenance, hash chains, queue order, per-record method-004 evidence, caps,
exact deadlines and the 1024×1024 depth-10 full-square raster. It passes.

```sh
python research/benchmarks/parallel_domain_006_execution/materialize.py /tmp/pd006-replay
```

Claim ceiling: finite-cutoff-a local cell isolation and exact area accounting
only. Refinement was restricted to previously unresolved cells. The
remaining 120 cells are not evidence of gap closure. No topology, seam,
cutoff-convergence, v078 or experimental claim.
