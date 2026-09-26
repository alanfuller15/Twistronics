# LOOP-CUTOFF-D-013: loop signs at the fourth cutoff

**Producer:** a Claude Code session, on branch `claude/loop-cutoff-d-013`.
**Independent review:** Codex, pending.
**Authorization:** Alan asked this session to "continue compute here". Review does not gate this computation.

## Question

Does the negative discrete real-overlap loop sign found at cutoffs b and c survive at cutoff d (dimension 604)? The sign was found around two candidate external touchings:

- **R3:** the Q11 site, LOOP-ROBUSTNESS-007.
- **R1:** the Q00 site, PARTNER-WINDING-011.

CUTOFF-SHELL-012 added cutoff d and compared gaps and subspaces on 3×3 patches at these sites, but it computed no loops.

## Fixed design

There are six counterclockwise square loops, each with 32 exact-rational points (8 per side). Every point is solved at cutoffs a, b, c and d.

| Loop | Center | Half-width | Source |
|---|---|---|---|
| `R3_r1_32` | R3 rounded c candidate | 2⁻²⁰ | identical to 007 `center_c_r1_32` |
| `R3_rhalf_32` | R3 | 2⁻²¹ | identical to 007 `center_c_rhalf_32` |
| `R3_offnode_xplus4r_32` | R3 + 4·2⁻²⁰ in x | 2⁻²⁰ | identical to 007 `offnode_xplus4r_32` |
| `R1_r1_32` | R1 rounded c candidate | 2⁻¹⁶ | identical to 011 loop |
| `R1_rhalf_32` | R1 | 2⁻¹⁷ | new |
| `R1_offnode_xplus4r_32` | R1 + 4·2⁻¹⁶ in x | 2⁻¹⁶ | new |

- **Scale:** 192 points, 768 eigensolves, in 32 jobs of 6 points.
- **Limits:** 90 s per job, 600 s summed, 3 GiB per worker, 64 MiB per file, one thread. There are no retries and no adaptive points.
- **Reused points:** 128 points are reused from audited runs. Their a, b and c upper gaps must reproduce the retained values to 1e-9 meV (`SPEC.regression`).

## Engine

- **Physics:** the assembly, the four cutoffs, the embeddings and the adjacent comparisons are exactly those of CUTOFF-SHELL-012. The c and d shells are re-derived and asserted at run time.
- **Loop metric:** the holonomy (the sign of the determinant of the ordered product of real overlap matrices, for the hi, hi+1, selected-pair and four-state groups) is copied from LOOP-ROBUSTNESS-007.
- **One deliberate difference:** the legacy projector distance √(2r − 2Σσ²) is **not recorded**. CUTOFF-SHELL-012 showed that it cancels near identical subspaces, and it is not needed here. The principal angles, singular values and containment are kept.

## Reproduce

```sh
python research/benchmarks/loop_cutoff_d_013/run.py controls --output /tmp/controls.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python research/benchmarks/loop_cutoff_d_013/run.py run --commit FROZEN_SHA --wheel /path/python_flint-0.9.0-...whl --output NEW_DIR
python research/benchmarks/loop_cutoff_d_013/run.py replay --commit FROZEN_SHA --output NEW_DIR   # zero eigensolves
```

`build_spec.py` regenerates `SPEC.json` from the byte-identical replays of the 007 and 011 MAP files.

## Claim ceiling

These are sampled finite-cutoff diagnostics. The 0.5 link threshold is discrete conditioning only. There is no certified node count, charge, continuous isolation along the loop, or infinite-cutoff claim. The coordinates are momentum coordinates k = xG₁ + yG₂, not time.
