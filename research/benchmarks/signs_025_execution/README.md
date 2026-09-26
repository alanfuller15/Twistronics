# SIGNS-025 execution: results

**Implementation:** `1f57b1c5ba6876125834d0ec2244038bf7c3f245`, frozen and pushed before any physical call (plan 5845284541).
**Producer:** a Claude Code session.
**Independent review:** Codex, **pending**.

## Run

- **Scale:** 2453 points at cutoff d = **2453 full `evr` eigensolves** with eigenvectors, in 80 jobs of at most 31 points under the Codex-reviewed `concurrent_supervisor`.
- **Time and status:** 4 workers at peak, **71.3 s** including cleanup. The batch status is PASS, with 0 retries and every receipt `NORMAL_EXIT` with an empty group.
- **Regression:** 8 SWEEP-D-024 points agree within 8.5e-12 meV.
- **Fast-pipeline controls** at the frozen commit pass.
- **Replay:** `check_replay.py` verifies 566 files and re-derives MAP, REGRESSION, HOLONOMY and SUMMARY byte-identically with 0 eigensolves.
- **States:** full spectra and four-state vectors, stored as `STATES.pack`.

## Result: **42/42 predicted signs matched**, with 0 invalid loops

| Loop | Encloses | lo−1 / lo / hi / hi+1 / pair / four | min link σ | det(lo) | det(hi) | min sampled gap lo / hi |
|---|---|---|---:|---:|---:|---:|
| B_R2R4 | R2, R4 | +/+/+/+/+/+ | 0.9993 | +0.961 | +0.991 | 2.29 / 6.89 meV |
| B_R2R4R3 | R2, R3, R4 | +/+/−/−/−/+ | 0.9993 | +0.967 | −0.979 | 2.29 / 2.46 meV |
| B_R3 | R3 | +/+/−/−/−/+ | 0.9994 | +0.998 | −0.973 | 17.05 / 1.59 meV |
| B_R2 | R2 | −/−/+/+/−/+ | 0.9982 | −0.961 | +0.997 | 1.51 / 10.20 meV |
| B_R4 | R4 | −/−/+/+/−/+ | 0.9984 | −0.962 | +0.998 | 1.61 / 9.05 meV |
| B_R1 | R1 | +/+/−/−/−/+ | 0.9998 | +1.000 | −0.980 | 43.66 / 2.83 meV |
| B_ctrl | none | all + | 1.0000 | +1.000 | +1.000 | 46.60 / 25.29 meV |

Reversing the traversal preserves every sign. Every link is well conditioned (σ ≥ 0.998).

## Reading

- On all seven large loops, every group's discrete sign equals the product of the local signs of the enclosed candidates.
- R2 and R4 cancel in the lower groups, and R2+R4+R3 leaves R3's upper-group sign. Single-candidate boxes reproduce the local signs, and the empty control is +1.
- This is consistent with R1–R4 being the only sign-carrying structures inside these loops at cutoff d.

## Claim ceiling

This is consistency of discrete real-overlap loop signs with the four-candidate inventory on these seven loops only.

- It is not a node count, charge, partner correspondence, certified touching, continuous isolation or infinite-cutoff claim.
- The 0.5 link threshold is discrete conditioning only.
