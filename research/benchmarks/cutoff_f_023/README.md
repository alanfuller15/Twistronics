# CUTOFF-F-023: the sixth cutoff f at all four candidates, reusing retained e states

**Producer:** a Claude Code session, on branch `claude/loop-cutoff-d-013`.
**Independent review:** Codex, pending.
**Authorization:** Alan said "Yes, proceed" to reusing hash-bound retained states for cutoffs that have already been computed, with a recomputed regression subset, and asked for a new calculation run.

## Question

Do the loop signs and gaps at R3, R1, R2 and R4 change one shell further, at cutoff f?

Cutoff f = sorted(set(e + b-stencil)): 249 vectors, dimension 996, central pair [497, 498].

## Fixed design

- **Points:** the twelve local loops, 384 exact points.
  - 0–191: the six CONTROLS-E-022 loops at R3 and R1.
  - 192–383: the six LOWER-CONTROLS-021 loops at R2 and R4.
- **Reuse (new):** cutoff-e energies and four-state vectors are read from the retained state files, with each file bound by SHA-256 in `SPEC.reuse`.
  - 022 files: 12 on this branch.
  - 021 files: 48, taken from Codex execution `38204bfc` and verified against its MANIFEST.
- **Only f is eigensolved:** 384 solves.
- **Reuse checks:**
  - At every point, the e matrix is rebuilt with no eigensolve. The e-in-f nested residual and the residual of the retained e eigenpairs against the rebuilt matrix must both be below 1e-10 and 1e-8 meV.
  - On 64 regression points (the `R3_r1_32` and `R2_baseline` loops), e is re-solved and must be **byte-identical** to the retained arrays: 64 extra solves.
- **Jobs:** 16 jobs of 24 points (a multiple of 4 workers), with 4 concurrent single-thread workers.
- **Limits:** 90 s per job, 600 s wall clock, 3 GiB, 64 MiB. There are no retries and no adaptive points.
- **Groups:** six (lo−1, lo, hi, hi+1, pair, four), at both e (from retained states) and f.

## Reproduce

```sh
python <codex-branch>/research/benchmarks/lower_controls_021_execution/materialize.py R021 --repo <codex checkout>
python research/benchmarks/cutoff_f_023/run.py controls --output /tmp/controls.json
python research/benchmarks/cutoff_f_023/run.py run --commit FROZEN_SHA --wheel WHEEL --reuse-021 R021 --output NEW_DIR
python research/benchmarks/cutoff_f_023/run.py replay --commit FROZEN_SHA --reuse-021 R021 --output NEW_DIR   # zero eigensolves
```

## Claim ceiling

These are sampled finite-cutoff diagnostics.

- The 0.5 link threshold is discrete conditioning only.
- There is no certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim.
