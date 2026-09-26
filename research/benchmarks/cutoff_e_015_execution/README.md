# CUTOFF-E-015 execution: results

**Implementation:** `8cba7ef0f07d099c57d03b3efdba8aae49bb0512`, frozen and pushed before any physical call on this design.
**Producer:** a Claude Code session.
**Independent review:** Codex, **pending**.

## Run

- **Scale:** 41 points × a/b/c/d/e = **205 eigensolves**, in 7 jobs.
- **Time:** 88.8 s summed; the longest job took 15.6 s. Every job had `NORMAL_EXIT` and an empty process group.
- **Environment:** the locked wheel, one thread.
- **Residuals:** nested residuals (a⊂b⊂c⊂d⊂e) are all **0.0**. The largest eigenpair residual is 2.16e-12 meV.
- **Regression:** **164/164** a/b/c/d upper gaps equal CUTOFF-SHELL-012 and LOOP-CUTOFF-D-013 exactly (0.0 meV).
- **Replay:** `check_replay.py` verifies all 40 files and re-derives MAP, REGRESSION, HOLONOMY and SUMMARY **byte-identically**, with zero eigensolves.

## Successive cutoff changes on the R3 3×3 patch (step 2⁻²²)

| Link | Largest \|Δ upper gap\| (µeV) | Largest four-state angle | Largest pair angle |
|---|---:|---:|---:|
| a → b | 7.44 | 0.559° | 67.4° |
| b → c | 0.0253 | 0.0209° | 42.6° |
| c → d | 3.03e-5 | 6.05e-4° | 51.8° |
| **d → e** | **2.69e-8** | **1.72e-5°** | **0.148°** |

The gap change shrinks by about 10³ per shell step from b onward. The pair angle, which stayed large while successive models disagreed on the microelectronvolt-scale gap, drops to 0.15° once d and e agree on it.

**Patch center gap:** c 2.8508e-5, d 5.6863e-6, e 5.6852e-6 µeV.

**Descriptive 9-point gap² fits:** at b, c, d and e the fitted minimum gap² is zero at double precision, and the extremum lies inside the patch.

| Cutoff | Fitted offset (x, y), in units of 2⁻²² |
|---|---|
| c | (−1.33e-3, −1.33e-4) |
| d | (−3.16e-5, −1.108e-4) |
| e | (−3.01e-5, −1.105e-4) |

The d and e extrema agree to about 2e-6 step, roughly 5e-13 in fractional coordinates. Cutoff a's extremum lies far outside the patch.

## R3 loop (32 points, half-width 2⁻²⁰)

| Cutoff | hi sign | det | min link σ | min sampled hi/hi+1 gap (µeV) |
|---|---|---:|---:|---:|
| a | +1 | +0.999932 | 1.0000 | 7.24 |
| b | −1 | −0.753269 | 0.9263 | 0.0714 |
| c | −1 | −0.759231 | 0.9542 | 0.0807 |
| d | −1 | −0.759231 | 0.9542 | 0.0808 |
| **e** | **−1** | **−0.759231** | **0.9542** | **0.0808** |

hi+1 and the pair give the same sign, and the four-state group is +1 at every cutoff.

## Reading

At R3 the successive finite cutoffs b, c, d and e agree increasingly closely:

- the gap landscape, with changes falling about 10³ per step;
- the four-state span;
- the location of the fitted near-degeneracy;
- the negative discrete loop sign, which is unchanged at e.

The remaining center gap (5.7e-6 µeV) is consistent with the center's offset of about 1e-4 step from the fitted extremum. It is not a measured gap floor.

## Claim ceiling

These are finite-cutoff sampled diagnostics at one site.

- The rapid decrease between successive cutoffs is observed over four steps. **It is not a proof of infinite-cutoff convergence.**
- The fits are descriptive.
- There is no certified touching, node count, charge or continuous isolation.
- The coordinates are momentum coordinates, not time.
