# CONTROLS-E-022 execution: results

**Implementation:** `4e0e6c4378609189a4fafc0c25ba06a0ac68bb81`, frozen and pushed before any physical call (plan 5844662485).
**Producer:** a Claude Code session.
**Independent review:** Codex, **pending**.

## Run

- **Scale:** 192 points × c/d/e = **576 eigensolves** in 6 jobs of 32, with 4 concurrent single-thread workers.
- **Time:** **22.8 s wall clock** (70.3 s summed across jobs). Every job had `NORMAL_EXIT` and an empty process group, on the locked wheel.
- **Residuals:** nested residuals are 0.0; the largest eigenpair residual is 2.2e-12 meV.
- **Fast-pipeline controls** at the frozen commit (`FAST_PIPELINE_CONTROLS.json`): 240/240 byte-identical matrices, and 7 retained 013 state fixtures round-trip exactly.
- **Regression:** **896/896** lower and upper gap values reproduce exactly (0.0 meV). That is c/d at all 192 points against 013, and e on the baselines against 015 and 016.
- **Bitwise cross-check** (`CROSSCHECK.txt`): energies and four-state vectors are bit-identical to the retained arrays for **768/768** c/d arrays against 013, **64/64** e arrays against 015 (R3 baseline) and **64/64** e arrays against 016 (R1 baseline).
  - This shows that the fast builder, 32-point jobs and concurrent workers reproduce earlier runs bit for bit.
- **Replay:** `check_replay.py` verifies all 37 files and re-derives MAP, REGRESSION, HOLONOMY and SUMMARY byte-identically with zero eigensolves.
- **States:** stored as binary `STATES.pack` (`pack_states`), with no base64.

## Loop signs (lo−1 / lo / hi / hi+1 / pair / four)

| Loop | c | d | **e** | det(hi) at e | min link σ(hi) at e | min sampled hi gap at e |
|---|---|---|---|---:|---:|---:|
| R3 baseline 2⁻²⁰ | +/+/−/−/−/+ | same | **+/+/−/−/−/+** | −0.759231 | 0.9542 | 0.0808 µeV |
| R3 half-radius 2⁻²¹ | +/+/−/−/−/+ | same | **+/+/−/−/−/+** | −0.759231 | 0.9542 | 0.0404 µeV |
| R3 translated +4r | all + | all + | **all +** | +0.960832 | 0.9938 | 0.242 µeV |
| R1 baseline 2⁻¹⁶ | +/+/−/−/−/+ | same | **+/+/−/−/−/+** | −0.831987 | 0.9851 | 2.39 µeV |
| R1 half-radius 2⁻¹⁷ | +/+/−/−/−/+ | same | **+/+/−/−/−/+** | −0.831986 | 0.9851 | 1.20 µeV |
| R1 translated +4r | all + | all + | **all +** | +0.989590 | 0.9985 | 7.29 µeV |

**d → e across all 192 points:**

| Quantity | Largest value |
|---|---:|
| \|Δ lower gap\| | 2.5e-11 meV |
| \|Δ upper gap\| | 3.2e-11 meV |
| Four-state angle | 1.7e-5° |
| Pair angle | 1.9e-5° |
| Pair-in-four containment (minimum) | 0.9999999999999 |

## Reading

- **At cutoff e, both R3 and R1 keep negative hi/hi+1/pair signs on full- and half-radius loops**, and both translated controls are positive in every group.
- Their control structure at e now matches R2/R4 (021).
- The lower groups (lo−1, lo) are +1 on every R3/R1 loop, consistent with these being upper-pair candidates.

## Supervisor defect (found by Codex, 5845152992)

- **The defect:** the concurrent supervisor in this run's frozen `run.py` does not clean up the other active workers when a worker fails, times out, hits the batch deadline or fails to launch. They would keep running without receipts.
- **Reproduction:** Codex reproduced this for 022 and 023 with control-flow injection, with no physical calls. Claude reproduced the same result for 024 with Codex's harness.
- **Effect on this run:** none. Every job exited normally with an empty process group, so the retained evidence is unaffected.
- **Going forward:** do not reuse this supervisor. New runs must use the reviewed `research/tools/concurrent_supervisor.py` (Codex `e039de6a`).

## Claim ceiling

This is finite-cutoff numerical evidence consistent with candidate external touchings at R3 and R1, with negative discrete real-overlap signs that persist at cutoff e on baseline and half-radius loops, while the translated controls are positive.

- The 0.5 link threshold is discrete conditioning only.
- There is no certified touching, node count, charge, partner correspondence, continuous isolation or infinite-cutoff claim.
