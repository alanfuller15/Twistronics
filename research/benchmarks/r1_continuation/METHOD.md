# Conditional local node continuation

This checkpoint asks whether each of three named nodes can be followed from
`D = 38` to `39 meV` as a unique local crossing in an explicit moving neighborhood.
The Hamiltonian, finite cutoff and path are inherited unchanged. This is a
different question from locating small gaps at discrete stations.

The mathematical implication below is exact when its input bounds are exact.
The implementation evaluates them in ordinary floating point, with fixed
allowances and reconciliation checks. It does **not** implement outward-rounded
interval arithmetic. Its numerical conclusion is therefore conditional, including
the accuracy of eigenvalue/norm calculations and orthogonal frames.

## Fixed-frame residual

Write the real affine family as

`H(f,D) = H0 + f1 A1 + f2 A2 + (D-38) AD`.

At an interval midpoint, refine the intended root and fix a two-column real frame
`F` and its orthogonal complement `Q`. The frame is fixed throughout this interval;
it is not differentiated. With `y = (f1,f2,E)`, define

```
P = Fᵀ H F - E I₂
B = Qᵀ H F
K = Qᵀ H Q - E I
S = P - Bᵀ K⁻¹ B
g(S) = (tr(S)/2, (S₀₀-S₁₁)/2, S₀₁).
```

When `K` is invertible, block elimination gives
`nullity(H-EI) = nullity(S)`. Since `S` is real symmetric, `g(S)=0` means
`S=0`: a double eigenvalue of `H`. At the midpoint, count negative and positive
eigenvalues of `K`. Requiring counts `(lo, dim-lo-2)` fixes the double eigenvalue
to zero-based band indices `(lo,lo+1)`. A uniform nonzero bound on `K` preserves
this inertia throughout the connected tube. Thus the other bands cannot join
this crossing inside the accepted tube. `Gfull` below bounds the complement
matrix, not directly the neighboring band gaps of the full Hamiltonian.

We compute the actual center cross block `B0`, rather than silently treating a
computed eigenframe as exactly invariant. Let `y0` be the center, and let `J`
have columns `g(Fᵀ A1 F)`, `g(Fᵀ A2 F)` and `g(-I₂)`. Set

```
C = numerical inverse of J
gD = g(Fᵀ AD F)
v = -C gD
ybar(D) = y0 + v (D-D0).
```

The exact projected linear residual at the predictor is
`g0 + (gD+Jv)(D-D0)`, where `g0 = g(P(y0,D0))`.
The code retains both `g0` and `gD+Jv`, as well as `I-CJ`.

## Uniform bounds on the nonlinear term

Each scalar component of `g(S)` has absolute value at most `||S||₂`.
For an interval halfwidth `h` and box `|yi-ybar_i(D)| ≤ ri`, define

```
aj = ||Aj||₂                      (j = 1,2)
bj = ||Qᵀ Aj F||₂
b0 = ||B0||₂
T = AD + v1 A1 + v2 A2
bv = ||Qᵀ T F||₂
nv = ||T - vE I||₂
G0 = min |eig(K0)|

Gline = G0 - h nv
Gfull = Gline - a1 r1 - a2 r2 - rE
bline = b0 + h bv
bfull = bline + b1 r1 + b2 r2.
```

Weyl's inequality and the triangle inequality give `||K⁻¹||₂ ≤ 1/Gfull`
throughout the tube. Along the predictor line, `||Bᵀ K⁻¹ B||₂ ≤ bline²/Gline`.
Differentiating this term with respect to `y` gives the componentwise bounds

```
nj = 2 bj bfull/Gfull + bfull² aj/Gfull²   (j = 1,2)
nE = bfull²/Gfull².
```

The cross block has no energy derivative because `QᵀF=0`. These are uniform
derivative bounds on the fixed-frame Schur residual. A projected Newton Jacobian
at one point, by itself, would not supply them.

## Contraction and self mapping

Apply the fixed-point map `Phi_D(y) = y - C g(S(y,D))` in the weighted maximum
norm `max_i |yi|/ri`. Write `ci = sum_j |Cij|`. A bound on the displacement of the
predictor is

```
Yi = |(C g0)i| + h |(C (gD+Jv))i| + ci bline²/Gline.
```

The frozen radius rule is `rho=max(10⁻⁶, 4 max_i(Yi/ci))` and `ri=rho ci`.
The implementation includes the allowances listed below when evaluating `Y`.
An upper bound on the derivative norm is

```
qi = [sum_j |(I-CJ)ij| rj + ci sum_j nj rj] / ri
q = max_i qi
Ynorm = max_i Yi/ri.
```

If `q<1` and `Ynorm+q≤1`, the map is a contraction and maps the box into itself.
Banach's theorem gives exactly one zero in the box. Its distance from the
predictor is at most `beta ri`, where `beta=Ynorm/(1-q)`. The retained gates
are stricter: `q≤0.5`, `Ynorm+q≤0.8` and `Gfull>0.001 meV`.

Changing variables to `z=y-ybar(D)` puts all boxes on one fixed domain. The map
is continuous in `D` and uniformly contractive, so its unique fixed point
depends continuously on `D`. This proves the exact conditional local statement
over an entire accepted interval, rather than just at evaluated stations.

## Joining intervals

Two outer tubes overlapping does not establish that their roots coincide.
At **every** leaf endpoint we construct a separate point certificate with `h=0`.
Its tighter enclosure `y0 ± beta r` must lie strictly inside each incident tube's
cross section. This identifies the endpoint root of each tube with the same
double eigenvalue. Initial and final endpoints are also checked. The proof
then joins the local branches over the declared parameter interval.

For every node pair and every overlap of their parameter partitions, differences
of predictor coordinates are affine in `D`. Their endpoint extrema, minus both
tube radii, must strictly separate the boxes in at least one momentum coordinate.
This prevents an exchange of these three labels inside the covered tubes. It
does not exclude other nodes elsewhere in momentum space.

## Numerical and provenance limits

The computation subtracts `10⁻⁷ meV` from the center complement separation,
adds `10⁻⁷` to each operator/cross-block norm, adds `10⁻⁷ meV` to the scalar
nonlinear residual bound, and adds `10⁻¹²` to each entry of `|I-CJ|`. These are
declared numerical allowances, not proved enclosures of all roundoff errors.
Units for derivative norms follow their respective coordinates (`f1,f2`
dimensionless, `D,E` in meV). Real symmetry, finite values and orthogonality are
checked. Original complex-model matrices and spectra are checked at every
distinct center. Independent reconstruction checks retained frames, primitive
bounds, partitions, endpoint containment and node separation.

For context on what genuinely verified norm bounds require, see S. M. Rump,
[Verified bounds for singular values, in particular for the spectral norm of a
matrix and its inverse](https://www.tuhh.de/ti3/paper/rump/Ru10a.pdf),
*BIT* 51, 367–384 (2011). This checkpoint does not implement that paper's
verification algorithms. The specialized Schur bounds above are derived here.

All original paths, grids, thresholds, controls and adaptive limits appear in
`PLAN.json`, frozen before the controls and production run. Every attempted
interval is retained; unresolved intervals or joins are not replaced by sampled
agreement. Coarse and fine grids are independently bounded but share centers
where their parameter values coincide.

This finite-model check uses fixed strain, constant tunnelling and opposite
layer potentials `±D`; the layer potential difference is `2D`. `D` has not been
calibrated to an experimental field. Both Hamiltonian implementations share this
diagnostic framework. No global node inventory, complete braid, Euler-class
change, experimental validation, novelty, or infinite-cutoff conclusion follows.
