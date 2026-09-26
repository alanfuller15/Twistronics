# Parallel full-domain continuation 003 — two-host executed packet

Status: **INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE — unreviewed.** Independent
post-execution audit by Codex is pending. Claude coordinated and executed this
batch, so Claude is not an independent reviewer of it.

| Measure | Before (batch 002) | After batch 003 |
|---|---|---|
| Accepted full-square area | 209439/262144 = 79.89% | **259295/262144 = 98.91%** |
| Accepted cells | 1,191 | 1,730 |
| Frontier cells | 483 | 253 |
| Unresolved depth-9 cells | 40 | 40 |

Added area: exact `779/4096` (19.02 percentage points). Quadrants q01
(x ∈ [0,½], y ∈ [½,1]) and q10 (x ∈ [½,1], y ∈ [0,½]) now have no frontier
and no unresolved cells: every cell in them is accepted. The remaining area is
in q00 (58 frontier cells) and q11 (195 frontier cells plus the 40 inherited
unresolved narrow-gap cells).

| Shard | Host | Attempts | New accepted | Frontier left | Unresolved | Exit | Wall (s) |
|---|---|---:|---:|---:|---:|---|---:|
| q00h0 | 0 | 120 | 86 | 58 | 0 | NORMAL_EXIT | 459 |
| q00h1 | 1 | 86 | 75 | 0 | 0 | NORMAL_EXIT | 265 |
| q01h0 | 0 | 56 | 51 | 0 | 0 | NORMAL_EXIT | 242 |
| q01h1 | 1 | 108 | 90 | 0 | 0 | NORMAL_EXIT | 328 |
| q10h0 | 0 | 16 | 16 | 0 | 0 | NORMAL_EXIT | 74 |
| q10h1 | 1 | 16 | 16 | 0 | 0 | NORMAL_EXIT | 54 |
| q11h0 | 0 | 120 | 104 | 92 | 40 (inherited) | NORMAL_EXIT | 511 |
| q11h1 | 1 | 120 | 101 | 103 | 0 | NORMAL_EXIT | 368 |

Totals: 642 attempts and 4,724 endpoint factorizations. Every shard stayed
within its 120-attempt and 960-factorization caps and the 600 s watchdog.

## What ran

- The runner `parallel_domain_003/parallel.py` at
  `32ea5246b9bc34b1602a1cf705d2df81fc47e96d`, under its `EXECUTION_AUTHORITY.json`.
- Two cloud hosts, each with 4 cores and 4 concurrent single-thread workers,
  running at the same time on 25–26 September 2026 UTC.
  - Host 0 is the coordinating Claude session.
  - Host 1 is a sibling Claude session. It verified the locked wheel SHA-256
    `376b88ca…4d76`, passed the synthetic controls, and published
    `host1/` at `34f64e4c` (see `host1/HOST_NOTES.md`).
- Predecessor: the batch-002 partition
  (`parallel_domain_002_execution/HOSTED/PARTITION.json`), bound by SHA-256 in
  `parallel_domain_003/SOURCE_BINDINGS.json`.

## Verification

Each host replayed its own shards. The coordinator then rebuilt host 1's logs
from the pushed parts and checked each against its receipt's byte count and
SHA-256. It then ran the merged verifier over all eight shards, which checks:

- source bindings and the locked-wheel runtime provenance;
- hash chains and the exact per-shard queue order;
- the per-record physical-evidence verifier (method-004 evidence, both
  congruences, inertia counts and window widths);
- per-worker and aggregate factorization caps;
- exact deadlines;
- a 512×512 raster showing that accepted, frontier and unresolved cells form a
  complete disjoint partition of [0,1]².

The merged replay passes.

## Reproduce

```sh
python research/benchmarks/parallel_domain_003_execution/materialize.py /tmp/pd003-replay
```

## Claim ceiling

Finite-cutoff-a local cell isolation and exact area accounting only. Accepted
area is not project completion. The 40 unresolved cells lie in the narrow-gap
strip, where point samples show a gap down to about 3 μeV; they may resist
this method at any feasible depth. No topology, seam, cutoff-convergence, v078
or experimental claim.
