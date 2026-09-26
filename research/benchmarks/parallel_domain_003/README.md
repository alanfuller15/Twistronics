# Parallel full-domain continuation 003 — two-host sharded run

Status: implementation, run under Alan's user-directed asynchronous audit
(`EXECUTION_AUTHORITY.json`). Independent audit by Codex is pending and does not
block execution.

## Why shards

On one 4-core host, four single-threaded workers each use a full core and
about 100 MB, so the host is CPU-bound. A fifth worker on the same host adds no
throughput. This packet adds a second host.

## Ownership

Each shard is a quadrant on a host: `q00h0 … q11h1`, 8 workers in total. For
each quadrant, the batch-002 frontier is sorted ascending and dealt
round-robin: host h owns sorted positions i with `i % 2 == h`. Every descendant
of an owned cell stays with its owner. Inherited accepted and unresolved cells
belong to host 0 only. Before any attempt, the union of all shards is exactly
the batch-002 partition, and a control proves this.

Each shard runs the unchanged method-004 evaluator. It works through its own
queue in ascending `(depth, ix, iy)` order, with at most 120 attempts and 960
factorizations, a 600 s + 10 s watchdog, 2 GiB, and one native thread.

## Replay and merge

- `parallel.py run --host h` runs that host's four shards, then replays them
  (`HOST_RESULTS.json`).
- Merging copies every shard directory into one tree. `parallel.py verify`
  then replays all eight shards and proves a complete, disjoint full-square
  partition with the 512×512 raster.
- A missing or swapped shard fails the merge.

The deadline check now recomputes the supervisor's exact expressions
(`start + 600`, `start + 600 + 10`) instead of differencing floats. That fixes
the batch-002 `DEADLINE_BINDING` artifact.

## Claim ceiling

Finite-cutoff-a local cell isolation and exact area accounting only. No
topology, seam, cutoff-convergence, v078 or experimental claim.
