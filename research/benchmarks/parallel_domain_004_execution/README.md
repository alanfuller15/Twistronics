# Parallel full-domain continuation 004 — executed packet

Status: **INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE — unreviewed.** Independent
post-execution audit by Codex is pending. Claude coordinated and executed this
batch, so Claude is not an independent reviewer of it.

| Measure | Before (batch 003) | After batch 004 |
|---|---|---|
| Accepted full-square area | 259295/262144 = 98.913% | **65469/65536 = 99.898%** |
| Accepted cells | 1,730 | 2,154 |
| Frontier cells | 253 | 179 (all depth 9) |
| Unresolved depth-9 cells | 40 | 89 |

Added area: exact `2581/262144` (0.985 percentage points). What remains is
268 depth-9 cells, 268/262144 ≈ 0.102% of [0,1]²:

- 179 frontier cells. All are at the maximum depth, so one further attempt
  settles each as accepted or unresolved.
- 89 unresolved cells, found in both q00 and q11.

| Shard | Machine | Attempts | New accepted | Frontier left | Unresolved | Exit | Wall (s) |
|---|---|---:|---:|---:|---:|---|---:|
| q00h0 | 1 (coordinator) | 31 | 27 | 0 | 0 | NORMAL_EXIT | 131 |
| q00h1 | 1 (coordinator) | 35 | 25 | 0 | 5 | NORMAL_EXIT | 133 |
| q00h2 | 2 (sibling) | 34 | 20 | 0 | 9 | NORMAL_EXIT | 145 |
| q00h3 | 2 (sibling) | 26 | 19 | 0 | 4 | NORMAL_EXIT | 129 |
| q11h0 | 1 (coordinator) | 120 | 90 | 37 | 43 (40 inherited) | NORMAL_EXIT | 473 |
| q11h1 | 1 (coordinator) | 120 | 88 | 33 | 6 | NORMAL_EXIT | 464 |
| q11h2 | 2 (sibling) | 120 | 72 | 57 | 16 | NORMAL_EXIT | 518 |
| q11h3 | 2 (sibling) | 120 | 83 | 52 | 6 | NORMAL_EXIT | 558 |

The q01 and q10 shards had no frontier and exited immediately; those quadrants
were fully accepted in batch 003. Totals: 606 attempts and 4,120 endpoint
factorizations, all within caps.

## What ran

- The runner `parallel_domain_004/parallel.py` at
  `e12b74eb137a1623968b2bf459474942ffd55929`. Only q00 and q11 had frontier
  cells, so each quadrant's frontier was dealt round-robin over four slots.
  Each 4-core machine ran two slots at once, keeping all cores busy.
- Machine 1: the coordinating Claude session (slots 0 and 1).
- Machine 2: a sibling Claude session (slots 2 and 3). It verified the locked
  wheel SHA-256 `376b88ca…4d76`, passed the controls, and pushed its outputs
  at `8f1c0c03` (`SLOTS23_NOTES.md`).
- Predecessor: the merged batch-003 partition
  (`parallel_domain_003_execution/PARTITION.json`), bound by SHA-256.

## Verification

The coordinator rebuilt slots 2 and 3 from the pushed parts, checking each log
against its receipt's byte count and SHA-256. It then ran the merged verifier
over all 16 shards, which checks:

- source bindings and runtime provenance;
- hash chains and queue order;
- per-record method-004 evidence;
- caps and exact deadlines;
- the 512×512 full-square raster.

It passes.

```sh
python research/benchmarks/parallel_domain_004_execution/materialize.py /tmp/pd004-replay
```

## Claim ceiling

Finite-cutoff-a local cell isolation and exact area accounting only. The 89
unresolved cells are depth-9 cells that did not certify. They are not evidence
of gap closure, but this method cannot certify them at depth 9. No topology,
seam, cutoff-convergence, v078 or experimental claim.
