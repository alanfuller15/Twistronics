# SWEEP-D-026: full-cell gap maps at 1/128 resolution, cutoffs a and d

**Producer:** a Claude Code session. **Independent review:** Codex, requested but not awaited.
**Authorization:** Alan said "Computation heavy workflows only now, no gates".

- **Purpose:** 4× the grid density of SWEEP-D-024. This addresses the review note that a 1/64 grid cannot rule out narrower features.
- **Grid:** 128×128 exact cell-centred points, plus 8 regression points from the 024 grid.
- **Scale:** 16392 points × cutoffs a/d = 32784 eigenvalue-only `evr` solves. Full spectra are retained.
- **Batches:** two predeclared batches under the Codex-reviewed `concurrent_supervisor`, with 4 workers and at most 32 points per job.
  - A: grid rows j < 64 plus the regression points, 260 jobs.
  - B: rows j ≥ 64, 256 jobs.
- **Rules:** one launch per batch, no retries. `combine` merges the replayed batches for the regression and the summary.
- **New-region rule:** the same as 024. A local minimum below 1 meV at d that lies more than 2/64 from every candidate is flagged. Nothing is refined in this run.
- **Claim ceiling:** these are sampled values only. Features narrower than 1/128 are not resolved.
