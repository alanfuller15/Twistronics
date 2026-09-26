# SWEEP-D-026 execution: results

**Implementation:** `3eced802b1a646ad94909fdefad62f9ad4257942`, frozen and pushed before any physical call.
**Independent review:** Codex, requested but not awaited ("no gates").

## Run

| Batch | Points | Solves | Jobs | Time | Result |
|---|---:|---:|---:|---:|---|
| A | 8200 | 16400 | 260 | 180.5 s | PASS |
| B | 8192 | 16384 | 256 | 179.1 s | PASS |

- **Scale:** **32784 eigenvalue-only `evr` solves** in total, under the reviewed supervisor with 4 workers, 0 retries and every receipt `NORMAL_EXIT`.
- **Regression:** the 8 reused 024 points reproduce exactly (**0.0 meV**).
- **Replay:** `check_replay.py` verifies all 3620 files and re-derives both batch MAPs, REGRESSION and SUMMARY byte-identically with 0 eigensolves.
- **Figure:** `GAP_MAPS_d_128.png` is a post-hoc rendering.

## Results (sampled, 128×128 grid)

| Gap | Minimum at d | Median | Largest \|a→d\| | Median \|a→d\| |
|---|---:|---:|---:|---:|
| Lower | 0.569 meV at (169/256, 163/256), 0.0041 from R2 | 79.3 meV | 0.045 meV | 0.58 µeV |
| Upper | 0.480 meV at (177/256, 185/256), 0.0051 from R3 | 32.3 meV | 0.147 meV | 0.74 µeV |
| Pair | 0.405 meV | 36.0 meV | 0.023 meV | 0.95 µeV |

**Local minima at d over the whole cell:**
- **Lower gap: 3.**
  - Beside R2: 0.569 meV.
  - Beside R4: 1.261 meV.
  - A **shallow 1.577 meV dip at (171/256, 159/256)**, in the lower-gap valley between R2 and R4, 0.021 from R2.
- **Upper gap: 3.**
  - Beside R3: 0.480 meV.
  - Beside R1: 0.683 meV.
  - The 17.39 meV minimum already seen in 024.
- **New-region flags (below 1 meV and more than 2/64 from every candidate): 0.**

## Reading

- At 4× the density of 024, the only sub-meV basins in the cell are still the four containing R1–R4.
- The new shallow lower-gap dip (1.58 meV) lies inside both the SIGNS-025 `B_R2` loop and the `B_R2R4` loop. Their discrete signs matched the R2-only and R2+R4 predictions, which is consistent with this dip carrying no net discrete sign, that is, a gapped local minimum. This is an inference from sampled signs, not a certificate.
- Gaps change from a to d by a median below 1 µeV.

## Claim ceiling

These are sampled values; features narrower than 1/128 are not resolved. There is no certified isolation, touching, count or infinite-cutoff claim.
