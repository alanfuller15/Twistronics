# SWEEP-D-024 execution: results

**Implementation:** `528a9cccd71714770993d2fff971e23a52e07702`, frozen and pushed before any physical call (plan 5844882305).
**Producer:** a Claude Code session.
**Independent review:** Codex, **pending**.

## Run

- **Scale:** 4104 points × cutoffs a/d = **8208 eigenvalue-only solves**, in 32 jobs of 129 with 4 concurrent workers.
- **Time:** **35.6 s wall clock** (141.6 s summed). Every job had `NORMAL_EXIT`, on the locked wheel.
- **Regression:** 32/32 gap values at the 8 reused 014 points agree within **7.1e-12 meV** (threshold 1e-9 meV; eigenvalue-only solves, so this is a tolerance check).
- **Fast-pipeline controls** at the frozen commit pass.
- **Replay:** `check_replay.py` verifies all files and re-derives MAP, REGRESSION and SUMMARY byte-identically with 0 eigensolves.
- **Figure:** `GAP_MAPS_d.png` is a post-hoc rendering of MAP.json. It is not part of the frozen derivation.

## Results (sampled, 1/64 grid)

| Gap | Minimum at a | Minimum at d | Median | Largest \|a→d\| | Median \|a→d\| |
|---|---:|---:|---:|---:|---:|
| Lower e[lo]−e[lo−1] | 1.193 meV | 1.192 meV (85/128, 81/128) | 79.3 meV | 0.044 meV | 0.59 µeV |
| Upper e[hi+1]−e[hi] | 1.216 meV | 1.216 meV (89/128, 93/128) | 32.4 meV | 0.143 meV | 0.74 µeV |
| Internal pair e[hi]−e[lo] | 1.782 meV | 1.785 meV | 36.0 meV | 0.022 meV | 0.95 µeV |

**Local minima at d (periodic 8-neighbour), over the whole cell:**
- **Lower gap: 2**, at 1.192 meV (0.0097 from R2) and 1.310 meV (0.0037 from R4).
- **Upper gap: 3**, at 1.216 meV (0.0105 from R3), 1.301 meV (0.0094 from R1), and one shallow minimum of 17.41 meV at (127/128, 49/128), 0.36 from the nearest candidate.
- **New-region flags (predeclared rule: under 1 meV and more than 2/64 from every candidate): 0.**

## Reading

- On this grid, the only low-gap basins of the lower and upper external gaps anywhere in the cell are the ones containing R2/R4 and R3/R1.
- The single other local minimum (upper gap, 17.4 meV) is far from closing.
- Gaps change from a to d by a median below 1 µeV, and by at most 0.14 meV, the largest at the grid corner next to the cell origin.
- This agrees with the depth-12 coverage at cutoff a, which certifies isolation outside four clusters around R1–R4, and extends the sampled picture to cutoff d.

## Claim ceiling

These are sampled gap values on a 1/64 grid, which cannot resolve features narrower than its spacing.

- There is no certified isolation at d, no touching, no count and no infinite-cutoff claim.
- The coordinates are momentum coordinates, not time.
