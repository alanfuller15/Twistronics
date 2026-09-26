# LOOPS-028 execution: results (with the VALLEY-027 grid summary)

**Implementation:** `e20cafd967346ced573191402ffcb2b13ca91575`, frozen before any physical call.
**Independent review:** Codex, requested but not awaited.

## Run

- **Loops:** 575 loop points with full `evr` and vectors, in 20 jobs under the reviewed supervisor. Batch PASS, every job `NORMAL_EXIT`.
- **Grid summary:** derived with zero solves from the hash-bound VALLEY-027 A/B MAPs: 17545 points at 1/1024.
- **Replay:** `check_replay.py` re-derives `L/MAP.json` and `SUMMARY.json` byte-identically.

## Result 1: the 1/1024 valley map

On the valley map (x 0.621–0.738, y 0.540–0.681, cutoff d), the lower gap has exactly **two** interior local minima:
- **0.1000 meV at (673/1024, 655/1024)**, beside R2;
- **0.1381 meV at (179/256, 75/128)**, beside R4.

These are identical to the LOWER-LOCATE-017 sampled minima. **The SWEEP-D-026 "1.577 meV dip" at (171/256, 159/256) is not a local minimum at 1/1024.** It was a 1/128-grid sampling artifact on the valley slope.

The upper and pair gaps have no interior local minima in this region: the upper gap is at least 6.84 meV and the pair gap at least 1.80 meV.

## Result 2: loops around the 026 location (predicted all +1; **matched**)

| Loop (1/4096) | lo−1 / lo / hi / hi+1 / pair / four | min link σ | det(lo) | min sampled lower gap |
|---|---|---:|---:|---:|
| DIP_r32 | +/+/+/+/+/+ | 0.9990 | +0.9730 | 0.983 meV |
| DIP_r16 | +/+/+/+/+/+ | 0.9993 | +0.9782 | 1.252 meV |
| DIP_ctrl_y+64 | +/+/+/+/+/+ | 0.9977 | +0.9561 | 0.458 meV |

These signs are consistent with SIGNS-025.

## Claim ceiling

These are sampled values and discrete signs only. There is no certified isolation, touching, count, charge or infinite-cutoff claim.
