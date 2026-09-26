# Parallel full-domain continuation 002 — executed packet

Status: **INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE — unreviewed.** Independent
post-execution audit by Codex is pending. Claude executed this batch, so Claude
is not an independent reviewer of it.

| Measure | Before (batch 001) | After batch 002 |
|---|---|---|
| Accepted full-square area | 105951/262144 = 40.42% | **209439/262144 = 79.89%** |
| Accepted cells | 702 | 1,191 |
| Frontier cells | 903 | 483 |
| Unresolved depth-9 cells | 40 | 40 |

Added area: exact `1617/4096` (39.48 percentage points).

| Quadrant | Attempts | New accepted | Total accepted | Frontier | Unresolved | Exit | Wall (s) | Factorizations |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| q00 | 128 | 119 | 139 | 84 | 0 | NORMAL_EXIT | 567 | 988 |
| q01 | 128 | 127 | 142 | 72 | 0 | NORMAL_EXIT | 589 | 1,020 |
| q10 | 128 | 125 | 152 | 32 | 0 | NORMAL_EXIT | 586 | 1,012 |
| q11 | 128 | 118 | 758 | 295 | 40 | NORMAL_EXIT | 565 | 984 |

## What ran

- The unchanged runner `parallel_domain_002/parallel.py` at `7494c36022f163a427df2e513e57e534cb84c885`,
  under its `EXECUTION_AUTHORITY.json` (user-directed asynchronous audit).
- Executed by Claude Code on 25 September 2026 UTC at Alan's direction while
  Codex was unavailable during an OpenAI service incident.
- Host: one cloud container with 4 cores, running 4 concurrent workers, one
  native thread each, 2 GiB address space each, and a 600 s + 10 s watchdog.
- Locked wheel: python-flint 0.9.0, SHA-256 `376b88ca…4d76`, verified by the
  runtime provenance check.
- Predecessor: `parallel_domain_001_execution/HOSTED/PARTITION.json` (batch 001).
  Claude independently re-executed batch 001 on this host, and all four raw logs
  were byte-identical to the published ones (PR #2 comment 5841153373).

## Verification and the deadline tolerance fix

The runner's own final replay failed on one check, `DEADLINE_BINDING`, which
compares `soft_deadline - start == 600` with exact float equality. The
supervisor sets `soft_deadline = start + 600` from a monotonic clock. For q11,
the difference rounded to `600.0000000000001`. All four workers exited
normally, inside the deadline.

With Alan's explicit approval, replay uses `replay_002.py`. That script loads
the **unchanged** `parallel_domain_002/parallel.py` from disk and replaces only
that comparison with an absolute tolerance of 1e-6 s, for both the 600 s
deadline and the 10 s grace. All source bindings are still checked against the
unchanged files. Every other check is untouched: record hash chains, queue
order, the per-record physical-evidence verifier, factorization caps, and the
512×512 full-square occupancy raster. With the fix, the replay passes.

Batch 003 fixes the root cause by keeping exact deadline values.

## Reproduce

```sh
python research/benchmarks/parallel_domain_002_execution/materialize.py /tmp/pd002-replay
```

The script checks every hosted file against `MANIFEST.json`, rebuilds each raw
log, checks it against its receipt's size and SHA-256, and replays through
`replay_002.py`. It makes no physical evaluations.

## Claim ceiling

Finite-cutoff-a local cell isolation and exact area accounting only. Accepted
area is not project completion. The 40 unresolved narrow-gap cells remain
unresolved. No topology, seam, cutoff-convergence, v078 or experimental claim.
