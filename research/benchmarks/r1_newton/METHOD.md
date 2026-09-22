# Guarded projected Newton: method and acceptance scope

This is a numerical solver-validation batch in the finite R1 model. It implements the projected-derivative idea in the partner engine study while preserving that supplied study verbatim in `partner_engine_study.zip` and `partner_fast_engine.py`. The frozen plan records their SHA-256 hashes. The candidate uses the existing real affine Hamiltonian family from `r1_holonomy`; its measured change is the root-search algorithm.

## Local step

At fractional momentum f and fixed D, diagonalize the selected adjacent pair and its exterior neighbors. Let F contain the pair's two real eigenvectors and g its energy gap. In this instantaneous frame the traceless components are d = (-g/2, 0). For each fractional axis j, compute Pj = Fᵀ Aj F, where Aj is the existing exact affine Hamiltonian derivative. The local Jacobian has columns

Jj = ((Pj,11 - Pj,22)/2, Pj,12).

The candidate solves J Δf = -d. This Jacobian is exact for the Hamiltonian projected into the **frozen frame at that evaluation**. It is not asserted to be the exact derivative of the changing, anchor-aligned residual used by the fallback. Recompute the eigenframe at every trial. Limit the step to 0.02 in Euclidean fractional coordinates, stay within the original local box, and backtrack until the actual recomputed gap decreases or meets the stopping tolerance.

The default box is the seed ±0.08 in each coordinate intersected with [0,1]². An explicit box can replace it; the near-merger tests use the preserved local merger box. No periodic relabeling or step outside the box is permitted.

## Guards and fallback

The coefficients must be finite, real and symmetric within the declared matrix tolerance. SciPy's eigensolver retains finite-input checking. Every evaluated pair must have finite eigenvalues/eigenvectors, an orthonormal frame, exterior gaps at least 0.001 meV and an overlap singular value at least 0.1 with the original seed's pair subspace. These are sampled checks, not bounds between solver evaluations.

Newton requires a projected Jacobian minimum singular value of at least 1e-4 meV per fractional-coordinate unit and condition number at most 1e8. The same rank/conditioning gate applies to **final acceptance**, even if the residual gap is zero. This prevents a sampled singular degeneracy from being accepted as a simple root.

Newton stops at a gap of at most 1e-10 meV. If it exhausts its budget, fails its conditioning gate or cannot take an acceptable step, the fallback runs bounded least squares inside the same box from the last accepted evaluation. It uses the original seed anchor and the same two-component polar-aligned residual formula as the existing solver. Every fallback evaluation receives the domain, isolation and overlap checks. Acceptance requires optimizer success, gap at most 1e-8 meV and the final Jacobian gate. Invalid coefficients/input or an invalid initial pair are rejected directly.

The fallback uses SciPy's numerical Jacobian for that anchored residual; the projected Newton Jacobian is not substituted into it. See the official [`least_squares` documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html) for the bounded interface and derivative options.

## Consistent failure records

Every returned position refers to an explicit saved evaluation index. Its returned gap comes from that same evaluation. The solver never updates a returned position without evaluating its gap. If an invalid input or initial pair prevents a valid evaluation, the returned position and gap are null and the rejection reason remains visible.

The original partner routine's exhausted-iteration behavior is retained as a regression comparison: its returned position can have moved beyond the position used for the reported gap. A control reproduces that discrepancy; a separate control verifies that the new variant returns a consistent position/gap pair on exhaustion. The partner file is not edited or silently substituted.

## Frozen validation

The primary comparison uses both N8 Hamiltonian implementations, 17 retained D stations from 38 through 39 meV, three roots p/q/upper and two seed choices: 204 cases. One seed is offset from the stored root by (0.002,-0.001). The other is the previous retained station's root, with a fixed opposite offset at the first station. This tests sampled warm starts; it does not certify continuous identity or propagate a uniquely proved root tube.

The reference is the unchanged `r1_events.Solver.root` through `Family.solver`. Both methods receive identical seeds. All reference eigensolver calls are counted, including finite-difference Jacobian evaluations. Native complex Hamiltonians independently check every returned primary candidate's four-band spectrum. The two solvers' coordinates and the retained root must agree within 1e-9 fractional units; native residual gaps must be below 1e-8 meV. Native matrix checks are performed at every D station.

Six additional N8 cases disable Newton to exercise successful fallback. Separate near-merger checks test both known local roots at D=40.38 and search from the stored fold coordinate at D=40.40. Native matrix checks at these two values verify use of the affine family outside the primary interval. A rejected post-merger candidate is a failed local search, not a root-absence certificate.

The analytic controls test a known node, constant real-basis/sign changes, exhausted-iteration consistency, fallback, isolation, singular and ill-conditioned final roots, an out-of-box root, nonfinite inputs/coefficients, nonreal/nonsymmetric coefficients and the original partner bug. They validate specific mechanisms and do not certify all possible inputs.

`report.py` independently reconstructs saved spectra-derived gaps, Jacobian singular values, step equations, step lengths, backtracking conditions, box containment, complete case coverage and returned-evaluation consistency. It freshly diagonalizes all final primary/fallback/stress positions to check spectra and projected Jacobian singular values. Original source and result hashes are checked before reconciliation.

## Timing and adoption limits

Timings are single-thread, local measurements with alternating method order. They include solver initialization, guards and diagnostic recording; common family construction and the subsequent native verification are outside the timed calls. Medians describe this workload and environment, not a hardware-independent performance guarantee. Eigensolve counts are a less noisy measure of work. Timing is not an acceptance criterion.

This checkpoint makes `solver.solve` available as an explicitly named candidate variant. It is not a replacement for the native Hamiltonian or a new charge/Euler calculation. The original partner's direct-assembly variant is retained as provenance, while the new solver uses the existing affine assembly. Existing topology calculations and their limitations retain their original meaning.

The finite R1 model has fixed strain, layer potentials ±D meV and N=8 (596 dimensions). There is no experimental displacement-field calibration, infinite-cutoff error certificate, independent physical validation, continuous node-identity proof or full braid acceptance. Both Hamiltonian engines share this solver diagnostic.

## Reproduce and call

From the repository root with NumPy, SciPy and Matplotlib installed:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_newton/controls.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_newton/run.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_newton/report.py
python research/benchmarks/r1_newton/figure.py
```

The runner refuses to overwrite `RESULTS.json`. Preserve the published evidence and use a separate checkout with that output moved aside for a replay. Controls, report and figure regenerate their derived files. A changed source or runtime requires fresh evidence.

`solve(family, D, lo, seed, box=None, config=None, fallback=True)` returns a dictionary. `lo` is the zero-based lower band index of the targeted pair. An explicit box is `[[f1_min, f2_min], [f1_max, f2_max]]`. Callers must check `accepted`; returned candidates with `accepted=False` remain rejected regardless of optimizer flags or small residuals. The `method`, `newton_reason`, fallback metadata, evaluation history and exact effective configuration are retained for provenance.
