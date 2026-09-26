# CUTOFF-F-023 execution: results

**Implementation:** `99c0c4ee6845fb6b637dc11c670f684129c20436`, frozen and pushed before any physical call (plan 5844709836).
**Producer:** a Claude Code session.
**Independent review:** Codex, **pending**.

## Run

- **Scale:** 384 points at f (dimension 996) + 64 e re-solves = **448 eigensolves**, in 16 jobs of 24 with 4 concurrent workers.
- **Time:** **45.4 s wall clock** (176.9 s summed). Every job had `NORMAL_EXIT`, on the locked wheel.
- **Reuse:**
  - All 384 points use retained e states from 60 files, all verified by SHA-256.
  - **64/64 e re-solves are byte-identical** to the retained arrays.
  - The retained e eigenpairs have a maximum residual of 2.5e-12 meV against the rebuilt e matrices, and the e⊂f nested residual is 0.0.
- **Other checks:**
  - The largest eigenpair residual is 2.5e-12 meV.
  - The fast-pipeline controls at the frozen commit pass.
- **Replay:** `check_replay.py R021` verifies 86 files and re-derives MAP, REGRESSION, HOLONOMY and SUMMARY byte-identically with 0 eigensolves.

## Loop signs (lo−1 / lo / hi / hi+1 / pair / four): identical at e and f

| Loop | Signs at e and f | det at f | min link σ at f | min sampled gap at f |
|---|---|---:|---:|---:|
| R3 baseline / half-radius | +/+/−/−/−/+ | hi −0.759231 | 0.9542 | 0.081 / 0.040 µeV (hi) |
| R3 translated | all + | +0.960832 | 0.9938 | 0.242 µeV |
| R1 baseline / half-radius | +/+/−/−/−/+ | hi −0.831987 | 0.9851 | 2.39 / 1.20 µeV (hi) |
| R1 translated | all + | +0.989590 | 0.9984 | 7.29 µeV |
| R2 baseline / half-radius | −/−/+/+/−/+ | lo −0.701373 / −0.668428 | 0.8874 / 0.8249 | 1.48 / 0.58 µeV (lo) |
| R2 translated | all + | +0.998883 | 0.9998 | 13.2 µeV |
| R4 baseline / half-radius | −/−/+/+/−/+ | lo −0.716990 / −0.713728 | 0.9333 / 0.9222 | 1.96 / 0.91 µeV (lo) |
| R4 translated | all + | +0.998469 | 0.9997 | 12.1 µeV |

**e → f across all 384 points:**

| Quantity | Largest value |
|---|---:|
| \|Δ lower gap\| | 4.1e-12 meV |
| \|Δ upper gap\| | 2.8e-12 meV |
| Four-state angle | 4.3e-7° |
| Pair angle | 1.2e-6° |
| Pair-in-four containment (minimum) | 0.99999999999995 |

These changes are at the level of solver round-off (independent solvers agree to about 2e-12 meV). At these loops, the sampled quantities have stopped changing with cutoff to double precision.

## Claim ceiling

This is finite-cutoff numerical evidence consistent with candidate touchings at R3 and R1 (upper pair) and at R2 and R4 (lower pair). The negative discrete real-overlap signs persist at the sixth cutoff f on baseline and half-radius loops, and the translated controls are positive.

- Agreement to round-off between two finite cutoffs is **not** a proof of infinite-cutoff convergence.
- The 0.5 threshold is discrete conditioning only.
- There is no certified touching, node count, charge, partner correspondence or continuous isolation.
