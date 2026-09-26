# UPPER-029 execution: results

**Implementation:** `918f66f4605ffb44a21a798aa08d935c7a37bb32`, frozen before any physical call.
**Independent review:** Codex, requested but not awaited.

## Run

- **Scale:** 35090 eigenvalue-only `evr` solves at cutoff d, in four batches (184.4, 194.2, 194.0 and 191.2 s), all supervisor PASS with every job `NORMAL_EXIT`.
- **Replay:** `check_replay.py` verifies 7737 files and re-derives the four batch MAPs and the SUMMARY byte-identically with 0 eigensolves.

## Results (1/1024, cutoff d; interior local minima)

| Box | Upper gap | Lower gap | Pair gap |
|---|---|---|---|
| R3 (x 643–763, y 665–809) | **one** minimum: 0.0709 meV at (11/16, 369/512), 0.0008 from R3 | none (minimum 1.21 meV at the box corner toward R2) | none (minimum 13.4 meV) |
| R1 (x 308–428, y −54–90) | **one** minimum: 0.0420 meV at (23/64, 19/1024), 0.0002 from R1 | none (at least 67.3 meV) | none (at least 31.3 meV) |

## Reading

Together with VALLEY-027 (the R2 and R4 lower-gap minima only), every 1/1024 box around the four candidates has exactly **one** sampled local minimum of the relevant external gap, at the candidate, and no other interior minimum.

## Claim ceiling

These are sampled values only. There is no certified isolation, touching, count, charge or infinite-cutoff claim.
