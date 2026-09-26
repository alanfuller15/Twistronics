# LOOP-CUTOFF-D-013 execution: results

**Implementation:** `7635c8586e13865487b396ea21ec7d274c13976e`, frozen and pushed before any physical call.
**Producer:** a Claude Code session.
**Independent review:** Codex, **PASS** ([5844109917](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5844109917); review evidence `8988bb9a`). All 192 cutoff-d points were recomputed independently.

## Run

- **Scale:** 192 points × cutoffs a/b/c/d = **768 eigensolves**, in 32 sequential jobs of 6 points.
- **Time:** 203.8 s summed; the longest job took 8.2 s. Every job had `NORMAL_EXIT`, exit code 0 and an empty process group.
- **Environment:** the locked wheel python-flint 0.9.0 (`376b88ca…4d76`) with bound native libraries, one thread.
- **Residuals:** the nested residuals (a⊂b, b⊂c, c⊂d) are all **0.0**. The largest eigenpair residual is 1.95e-12 meV.
- **Regression:** 128 reused coordinates × a/b/c = **384 upper gaps reproduce the audited 007/011 values exactly (0.0 meV)**.
- **Replay:** `check_replay.py` verifies all 165 files and re-derives MAP, REGRESSION, HOLONOMY and SUMMARY **byte-identically**, with zero eigensolves.

## Loop signs (hi band; hi+1 and the selected pair give the same sign; the four-state group is +1 on every loop and cutoff)

| Loop | a | b | c | **d** | det at d | min link σ at d | min sampled hi/hi+1 gap at d (µeV) |
|---|---|---|---|---|---:|---:|---:|
| R3, radius 2⁻²⁰ | +1 | −1 | −1 | **−1** | −0.7592 | 0.954 | 0.0808 |
| R3, radius 2⁻²¹ | +1 | −1 | −1 | **−1** | −0.7592 | 0.954 | 0.0404 |
| R3, off-node control | +1 | +1 | +1 | **+1** | +0.9608 | 0.994 | 0.242 |
| R1, radius 2⁻¹⁶ | −1 | −1 | −1 | **−1** | −0.8320 | 0.985 | 2.39 |
| R1, radius 2⁻¹⁷ | −1 | −1 | −1 | **−1** | −0.8320 | 0.985 | 1.20 |
| R1, off-node control | +1 | +1 | +1 | **+1** | +0.9896 | 0.998 | 7.29 |

**c → d along every loop:**

| Site | Largest \|Δ upper gap\| | Largest four-state angle | Pair-in-four containment |
|---|---:|---:|---:|
| R3 | 3.0e-5 µeV | 6.1e-4° | 1.0 (to double precision) |
| R1 | 5.4e-7 µeV | 1.1e-4° | 1.0 (to double precision) |

## Reading

- **Both sites keep the negative discrete loop sign at cutoff d.** It holds on the full- and half-radius loops, while the translated controls stay positive.
- **The determinants and link overlaps at c and d agree** to four or more digits.
- **R3** is negative at b, c and d but positive at a. **R1** is negative at all four cutoffs.
- **Half-radius loops.** At each site the half-radius loop gives the same determinant as the full-radius loop, and the sampled gap halves. This is what a locally linear, cone-like splitting centered inside the loop would produce. It is an observation, not a fit claim.

## Claim ceiling

This is finite-cutoff numerical evidence consistent with a candidate external touching at each site, with a negative discrete real-overlap sign on these loops.

- The 0.5 link threshold is discrete conditioning. The sampled gaps along the loops do not certify continuous isolation.
- This does not establish a node count, a charge, a partner correspondence, Euler or braiding data, or infinite-cutoff behaviour.
- The coordinates are momentum coordinates, not time.
