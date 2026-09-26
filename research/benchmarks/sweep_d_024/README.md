# SWEEP-D-024: full-domain gap maps at cutoffs a and d

**Producer:** a Claude Code session, on branch `claude/loop-cutoff-d-013`.
**Independent review:** Codex, pending.
**Authorization:** Alan selected "New compute: domain sweep". Review does not gate this computation.

## Question

The depth-12 coverage certifies external isolation at cutoff a everywhere except four small clusters, which contract to R1–R4. Two questions follow:

- Does the sampled gap landscape at the converged-scale cutoff d show any other low-gap region?
- How large are the a→d gap changes across the whole cell?

## Fixed design

- **Grid:** a 64×64 exact cell-centred grid, x = (2i+1)/128 and y = (2j+1)/128, over the periodic unit cell k = xG₁ + yG₂.
- **Regression points:** 8 points reused from LOOP-LOWER-014 (a and d, lower and upper gaps, 1e-9 meV).
- **Scale:** 4104 points × cutoffs a and d = 8208 eigensolves.
- **Eigenvalues only:** scipy `evr` with `eigvals_only=True`. The sweep uses no eigenvectors, and full spectra are retained with `pack_states`.
  - Eigenvalue-only solves differ from full solves by about 1e-11 meV, so the regression is a 1e-9 meV tolerance, not byte identity.
- **Jobs:** 32 jobs of 129 points, with 4 concurrent single-thread workers.
  - At about 23 ms per point the 32-point cap would make setup dominate, while each job still stays well under the unchanged 90 s limit.
- **Limits:** 90 s per job, 600 s wall clock, 3 GiB, 64 MiB. There are no retries and no adaptive points.

## Outputs

- **Maps:** lower gap (e[lo]−e[lo−1]), upper gap (e[hi+1]−e[hi]) and internal pair gap at a and d, with their minima and medians.
- **a→d changes:** the largest and median gap changes between cutoffs a and d.
- **Local minima:** periodic 8-neighbour local minima of the lower and upper gaps at d, with their distance to R1–R4.
- **New-region rule (predeclared):** a local minimum below 1 meV at d that is more than 2/64 from every candidate is flagged for a separately frozen refinement run. Nothing is refined here.

## Claim ceiling

These are sampled gap values on a 1/64 grid, which cannot resolve features narrower than its spacing.

- There is no certified isolation, touching, count or infinite-cutoff claim.
- The coordinates are momentum coordinates, not time.
