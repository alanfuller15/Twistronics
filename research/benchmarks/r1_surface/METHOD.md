# Full swept-contour surface isolation

This checkpoint closes one specific gap left by `r1_temporal`: it checks the interiors of the surfaces between the spatial and temporal grid edges. The Hamiltonians, root samples, contour vertices, chart, and charge convention remain those of the published parent checkpoint. `PLAN.json` was frozen before the new controls and numerical runs.

## What is covered

For each neighboring pair of D stations and each oriented contour edge, let the four endpoint coordinates in (fractional f1, fractional f2, D) be c00, c01, c10, c11. Define

v(u,t) = (1-t)[(1-u)c00 + u c01] + t[(1-u)c10 + u c11],  0 <= u,t <= 1.

We cover both outgoing stem segments and every polygon edge. The incoming stem sweeps the same geometric surface with reversed orientation. All seams share the same endpoint data. Two radii and the parent's coarse and fine station/polygon geometries are tested separately. The surface between stations is explicitly this interpolation; it is not asserted to follow an exact node trajectory.

## Interior bound

The real finite Hamiltonian is affine: H(v)=H0+f1 A1+f2 A2+(D-38) AD. On a dyadic parameter rectangle, compute its center vc and its four mapped corners vi. Let nj=||Aj||2 and

δ = max_i Σ_j |vi,j-vc,j| nj.

A bilinear map on any subrectangle is a convex combination of its four corners. Thus ||H(v)-H(vc)||2 <= δ everywhere in that rectangle. Weyl's Hermitian eigenvalue bound gives, for every adjacent ordered pair,

gap(v) >= gap(vc) - 2δ.

The implementation evaluates ordered eigenvalues 296 through 300 (zero based), checking both gaps inside the selected three-band block and both exterior gaps. A cell passes only when **every** lower estimate exceeds 0.001 meV after subtracting a fixed 1e-7 meV floating allowance. Failed estimates cause adaptive bisection. An actual center gap below the margin, exhausted depth, or exhausted work budget leaves an explicit unresolved leaf. No corner-only test can accept a cell.

The full tree is retained: parameter rectangles, parents, children, centers, five eigenvalues, δ, four lower estimates and state codes. The independent report reconstructs interpolation, bounds, exact dyadic child partitions, tree reachability and leaf coverage. It checks native spectra at selected diagnostic locations. Controls include nodes hidden inside faces whose entire boundaries are gapped, plus gapped affine and bilinear examples with analytic eigenvalues.

These are **conditional floating-point bounds**, not an interval-arithmetic certificate. The allowance is a declared numerical tolerance, not a proved enclosure of all numerical error. Hamiltonian norms and eigensolutions must be accurate for the stated exclusion to hold.

## Chart and charge interpretation

Every corner is required to lie inside the previous full-box chart domain. Convexity then places the entire bilinear face inside it. The prior full-box exterior-gap and chart-rank checks are source-bound and reused; they are not rerun or counted as new controls. The previous signed +k transport result is also reused, not remeasured here.

A gapped swept surface, together with that fixed chart and carried base frame, supports a continuous deformation of the declared based contour throughout D=38 to 39. It strengthens the interpretation of the earlier charge transport beyond a collection of gapped grid edges. The role of based contours and conjugation follows the framework in [Wu, Soluyanov and Bzdušek, Non-Abelian band topology in noninteracting metals](https://arxiv.org/html/1808.07469v3), especially Supplement IV.3. This checkpoint computes no new Euler invariant.

## What root tracking establishes

The existing solver refines p, q and the upper node at sampled D stations and records residual gaps, anchor overlaps and a numerical Jacobian at each accepted root. The report summarizes those stored diagnostics. Nonzero sampled Jacobian singular values support local simplicity at the sampled roots, subject to numerical accuracy. They do not provide a uniform derivative enclosure, a continuation tube, uniqueness throughout each interval, or exclusion of additional roots. Interpolated node lines in the figure are guides between numerical samples.

A continuous node-identity claim would need controlled continuation neighborhoods with uniform invertibility/uniqueness bounds and overlap between neighboring neighborhoods, plus the inventory and band-isolation conditions relevant to a full braid claim. This checkpoint deliberately does not substitute dense sampling for those requirements.

Strain is fixed; D sets layer potentials +/-D meV, with layer difference 2D. D is not calibrated to an experimental displacement field. Both Hamiltonian implementations share the surface diagnostic. Results are for N=8, not an infinite-cutoff conclusion, novelty claim, complete braid acceptance, or experimental realization.

## Reproduce

From the repository root, with NumPy, SciPy and Matplotlib installed:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_surface/controls.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_surface/sweep.py --engine bm
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_surface/sweep.py --engine ref
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/benchmarks/r1_surface/report.py
python research/benchmarks/r1_surface/figure.py
```

The sweeps refuse to overwrite recorded output. To rerun, first preserve the published results and use a separate checkout with its `r1_surface/BM.json`, `REF.json` and eight engine case NPZ files removed. Keep the frozen sources and plan unchanged. Source hashes bind each calculation to its exact inputs.
