# LOOP-LOWER-014 execution: results

**Implementation:** `0453e09a4b2721f3dd51166a9bda064d4693d125`, frozen and pushed before any physical call.
**Producer:** a Claude Code session.
**Independent review:** Codex, **pending**.

## Run

- **Scale:** 368 points × cutoffs a/b/c/d = **1,472 eigensolves**, in 46 sequential jobs of 8 points.
- **Time:** 360.7 s summed; the longest job took 8.5 s. Every job had `NORMAL_EXIT`, exit code 0 and an empty process group.
- **Environment:** the locked wheel, one thread.
- **Residuals:** the nested residuals (a⊂b, b⊂c, c⊂d) are all **0.0**. The largest eigenpair residual is 2.44e-12 meV.
- **Regression:** 184 reused coordinates × a/b/c = **552 upper gaps equal PARTNER-LOOPS-008 exactly (0.0 meV)**. 008 is a Claude-session run and has not yet been independently reviewed.
- **Replay:** `check_replay.py` verifies all 235 files and re-derives MAP, REGRESSION, HOLONOMY and SUMMARY **byte-identically**, with zero eigensolves.

## Loop signs

The signs are identical at a, b, c and d on every loop.

| Loop | lo−1 | lo | hi | hi+1 | pair | four | lo det | lo min link σ | min sampled lo gap (µeV) |
|---|---|---|---|---|---|---|---:|---:|---:|
| R2 (008 box) | −1 | −1 | +1 | +1 | −1 | +1 | −0.8885 | 0.988 | 572 |
| R2 control, −14 cells in x | +1 | +1 | +1 | +1 | +1 | +1 | +0.9971 | 1.000 | 1899 |
| R4 (008 box) | −1 | −1 | +1 | +1 | −1 | +1 | −0.8929 | 0.992 | 705 |
| R4 control, +16 cells in x | +1 | +1 | +1 | +1 | +1 | +1 | +0.9942 | 0.999 | 1652 |

- **Determinants:** the lo, hi and pair determinants agree across a to d to at least 4 digits.
- **c → d along every loop:** the largest |Δ upper gap| is ≤1.4e-5 µeV, the largest four-state angle is ≤3.2e-4°, and pair-in-four containment is 1.0.

## Reading

- **R2 and R4 show the lower-gap pattern at all four cutoffs.** The pattern is lo−1 −1, lo −1, pair −1, hi +1. It matches 008's reading of an odd lo−1/lo count, and the upper gap shows no hi/hi+1 signature there.
- **Both translated controls are +1 for every group.**
- **The large rectangles make this robust.** They pass far from the enclosed candidate points: the sampled lo gap stays ≥0.57 meV and the links are well conditioned (σ ≥0.988). So at this scale the result does not change from a to d, unlike the µeV-scale R3 loops.

## Claim ceiling

This is finite-cutoff numerical evidence consistent with candidate lo−1/lo touchings inside the R2 and R4 rectangles, with negative discrete loop signs that persist at cutoff d, while the controls are positive.

- There is no node count, charge, partner correspondence, continuous-isolation or infinite-cutoff claim.
- The controls lie in cells certified only at cutoff a.
- The coordinates are momentum coordinates, not time.
