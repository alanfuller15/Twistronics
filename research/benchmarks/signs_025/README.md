# SIGNS-025: discrete sign accounting on large loops at cutoff d

**Producer:** a Claude Code session, on branch `claude/loop-cutoff-d-013`.
**Independent review:** Codex, pending.
**Authorization:** Alan asked to "proceed with research compute". Review does not gate this computation.

## Question

The local loops give a negative discrete sign at each of the four candidates:
- **R3 and R1:** hi, hi+1 and pair are −1.
- **R2 and R4:** lo−1, lo and pair are −1.

SWEEP-D-024 found no other low-gap basin. If these four are the only sign-carrying structures, then **any** larger loop should show, for each group, the product of the signs of the candidates it encloses:
- two enclosed −1 signs cancel to +1;
- an empty loop is +1.

## Fixed design

Seven exact counterclockwise rectangles on the 1/2048 lattice, with one point per lattice step, starting lower-left and closing last-to-first. The predictions are frozen in `SPEC.loops[].predicted_signs`.

| Loop | x (/2048) | y (/2048) | Encloses | Prediction (lo−1, lo, hi, hi+1, pair, four) |
|---|---|---|---|---|
| B_R2R4 | 1310–1470 | 1170–1350 | R2, R4 | +, +, +, +, +, + |
| B_R2R4R3 | 1310–1470 | 1170–1520 | R2, R3, R4 | +, +, −, −, −, + |
| B_R3 | 1370–1450 | 1430–1520 | R3 | +, +, −, −, −, + |
| B_R2 | 1310–1380 | 1270–1350 | R2 | −, −, +, +, −, + |
| B_R4 | 1395–1470 | 1160–1240 | R4 | −, −, +, +, −, + |
| B_R1 | 700–775 | 0–75 | R1 | +, +, −, −, −, + |
| B_ctrl | 400–480 | 600–680 | none | all + |

- **Placement:** the boundaries stay at least about 0.0145 from every enclosed candidate. The sweep's cell gaps on the boundaries are at least about 2 meV.
- **Scale:** 2453 distinct points (shared edges deduplicated), including 8 regression points from SWEEP-D-024, at cutoff d: 2453 full `evr` eigensolves with eigenvectors.
- **Jobs:** 80 jobs of at most 31 points, with 4 workers under the **Codex-reviewed `concurrent_supervisor`**. It is copied byte-identically from `e039de6a` and Claude reviewed it in 5845181342.
- **Limits:** 90 s per job, 600 s batch, 3 GiB and 64 MiB set before exec. There are no retries, no resume and no adaptive points.
- **Invalid loops:** any mismatch, or any loop with link σ below 0.5, is reported as found.

## Claim ceiling

A match means the discrete loop signs on these seven loops are consistent with the four-candidate inventory.

- It is **not** a node count, charge, partner correspondence, certified touching, continuous isolation or infinite-cutoff claim.
- The 0.5 link threshold is discrete conditioning only.
