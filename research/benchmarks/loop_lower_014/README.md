# LOOP-LOWER-014: lower-gap loops at the fourth cutoff

**Producer:** a Claude Code session, on branch `claude/loop-cutoff-d-013`.
**Independent review:** Codex, pending.
**Authorization:** Alan said "Proceed with either" when offered two next computations. Review does not gate this computation.

## Question

PARTNER-LOOPS-008 found odd lo−1/lo loop counts at cutoffs a, b and c around two unresolved clusters:

- **R2**, near (0.657, 0.641);
- **R4**, near (0.699, 0.586).

Does that loop sign survive at cutoff d, and are translated controls positive?

## Fixed design

| Loop | Rectangle (depth-10 cells) | Points | Source |
|---|---|---|---|
| `R2_box_008` | x 668–678, y 649–661 | 88 | identical to 008 |
| `R2_control_x-14cells` | x 654–664, y 649–661 | 88 | new |
| `R4_box_008` | x 709–721, y 594–606 | 96 | identical to 008 |
| `R4_control_x+16cells` | x 725–737, y 594–606 | 96 | new |

- **Loop construction:** each loop runs counterclockwise from the lower-left corner, with a boundary step of 1/2048.
- **Controls:** each closed control box overlaps no cell left unresolved by the audited REFINEMENT-012 partition. `build_spec.py` asserts this.
- **Scale:** 368 points × cutoffs a/b/c/d = 1,472 eigensolves, in 46 jobs of 8 points.
- **Limits:** 90 s per job, 900 s summed, 3 GiB per worker, 64 MiB per file, one thread. There are no retries.
- **Regression:** the 184 reused points must reproduce 008's a/b/c upper gaps to 1e-9 meV.

## Engine

The runner is identical to LOOP-CUTOFF-D-013 except for three things:

- **Geometry:** rectangles instead of squares.
- **Band groups:** `lo_minus_1` (band lo−1) and `lo` are added to the hi, hi+1, pair and four-state groups.
- **Point count.**

`diff ../loop_cutoff_d_013/run.py run.py` shows exactly these changes.

The expected readings are 008's:
- **lo−1/lo node:** lo −1, pair −1, hi +1.
- **hi/hi+1 node:** hi −1, pair −1, lo +1.

## Claim ceiling

These are sampled finite-cutoff diagnostics. The link threshold is discrete conditioning only, and there is no continuous isolation, node count, charge or infinite-cutoff claim.

The control boxes lie inside cells that REFINEMENT-012 accepted at **cutoff a**, where the external gaps are certified. That says nothing certified about cutoffs b, c or d. The coordinates are momentum coordinates, not time.
