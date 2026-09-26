# CONTROLS-E-022: R3/R1 half-radius and translated controls at cutoff e

**Producer:** a Claude Code session, on branch `claude/loop-cutoff-d-013`.
**Independent review:** Codex, pending.
**Authorization:** Alan asked for a "new calculation run … we're actively computing the space. Let's use it". Review does not gate this computation.

## Question

The site (v29) states that at R3 and R1 the half-radius and translated-control loops were checked only up to cutoff d (013). 015 and 016 took only the baseline loops to e.

Do all six 013 loops keep their signs at cutoff e (dimension 788)?

## Fixed design

- **Points:** all six 013 loops, 192 exact points, solved at cutoffs c, d and e: 576 eigensolves.
  - R3: `r1_32`, `rhalf_32`, `offnode_xplus4r_32`
  - R1: the same three loops
- **Groups:** all six are reported: lo−1, lo, hi, hi+1, pair and four.
- **Jobs:** 6 jobs of 32 points (one loop per job), with up to 4 concurrent single-thread workers.
- **Limits:** 90 s per job, 600 s wall clock per batch, 3 GiB, 64 MiB. There are no retries and no adaptive points.
- **Regression:** 896 gap values, lower and upper, must match within 1e-9 meV.
  - c and d at all 192 points against 013.
  - e at `R3_r1_32` against 015 and at `R1_r1_32` against 016.

## Engine

- **Physics, comparisons and holonomy:** identical to CUTOFF-E-015, restricted to c/d/e.
- **Fast pipeline:** reviewed by Codex (PASS 5844535047).
  - `FastPointMatrix` is byte-identical to `point_matrix`.
  - Jobs are 32 points each.
  - States are stored with `pack_states` as binary `STATES.pack`, not base64.
- **New to this run: concurrent workers.** Up to 4 workers run at once. Each is still its own process group with one thread, its own rlimits, receipts and watchdog.
  - Because every job runs single-threaded on fixed inputs, running jobs concurrently cannot change the results.
  - The exact regression against 013, 015 and 016 checks this at 896 values.

## Reproduce

```sh
python research/tools/fast_pipeline/controls.py . fast_controls.json --states <retained STATES.npz fixtures>
python research/benchmarks/controls_e_022/run.py controls --output /tmp/controls.json
python research/benchmarks/controls_e_022/run.py run --commit FROZEN_SHA --wheel /path/python_flint-0.9.0-...whl --output NEW_DIR
python research/benchmarks/controls_e_022/run.py replay --commit FROZEN_SHA --output NEW_DIR   # zero eigensolves
```

## Claim ceiling

These are sampled finite-cutoff diagnostics.

- The 0.5 link threshold is discrete conditioning only.
- There is no certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim.
- The coordinates are momentum coordinates, not time.
