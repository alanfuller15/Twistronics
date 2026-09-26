# Bounds on variation between retained samples

These bounds apply to two explicitly given finite matrix families. They do not
select the physical sign convention of the paper, prove convergence of a
continuum truncation, or certify an Euler calculation. The algebra supplies
uniform bounds; finite numerical witnesses below only check their implementation.

## 1. The folded sphere references

Use radian coordinates on the torus, with positive integer fold `a`:

```
d(x,y) = (sin(a*x), sin(y), m+cos(a*x)+cos(y))
n = d / ||d||
H = 2 n n^T - I_3,   P = I_3 - n n^T.
```

For `m=-1`, `||d||^2=1+2(1-cos(a*x))(1-cos(y)) >= 1`.
For `m=-3`, the third component is at most -1, also giving `||d||>=1`.
Differentiating normalization gives `dn=(I-n n^T) dd/||d||`, hence
`||partial_x n||<=a` and `||partial_y n||<=1`. Because `n^T dn=0`,
the operator norm of `d(n n^T)` is exactly `||dn||`. Integration yields

```
||n(k')-n(k)|| <= a |dx| + |dy| = eta
||P(k')-P(k)||_op <= eta
||H(k')-H(k)||_op <= 2 eta.
```

For a rectangular cell with widths `(h_x,h_y)`, use
`eta_cell=a*h_x+h_y`, valid relative to **any corner throughout the cell**.
This is a cell-diameter bound, not a nearest-node radius and not a finite
difference estimate. Periodicity handles seam cells in a lifted coordinate.

When `eta_cell<1`, the plane remains in a projector chart about that corner;
the least frame overlap is at least `sqrt(1-eta_cell^2)`. When the bound is
larger, report **not certified**, not a detected discontinuity. The exact
external gap of this reference is always 2 regardless of the fold.

For the N-interval square grid, `h_x=h_y=2*pi/N`. Fold 1 passes this
sufficient local-chart condition at N=48 and 96. Folds 49 and 97 do not.
The threshold 1 is the mathematical chart boundary, not an empirically tuned
acceptance threshold. Even a positive chart condition is not by itself a
certificate for the archived Wilson-phase unwrapping algorithm.

### Nested-grid alias

At `x=-pi+2*pi*j/N`, `(97-1)*x=-96*pi+192*pi*j/N` is a multiple
of `2*pi` for N=48 and N=96. The 97-fold and once-folded Hamiltonians
are identical on both grids in exact arithmetic. Precomposition by the
orientation-preserving 97-fold torus covering multiplies the known reference
degree by 97: the oriented Euler number is 194. Sampled guards nevertheless
return approximately 2 on both grids, as independently replayed in this pass.
The analytic variation screen refuses local-chart certification for both.

This is not a claim that any retained graphene label is wrong.

## 2. The retained projected Vafek matrix

Target: `vafek_2025/model.py:Model.direct_projection`, default retained
parameters. Coordinates are the source's dimensionless `K=v*k/gamma` and
`Q=v*q/gamma`; energies are meV. The matrix acts on fixed four-component
coefficient coordinates. Neither `Model.h` nor a repaired Hamiltonian is
substituted. No physical convention is selected by this calculation.

The first four rows of the source's 12-by-4 projection are zero, so all gamma
couplings into those rows drop out. The remaining expression is exactly

```
z = (x+Q/2+i*y, x+Q/2-i*y, -x+Q/2+i*y, -x+Q/2-i*y)
C = diag((1+|z_j|^2)^(-1/2))
V = [ C ; -diag(z) C ],                 V^dagger V = I_4
A = [ M (I tensor X) + hc,     -i cpp eps (Z tensor Z) ;
      (+i cpp eps (Z tensor Z)), delta (Z tensor Y) + hf ]
H_direct = V^dagger A V.
```

`A` is constant in K and Q; **all** retained momentum dependence, including
the moving projection basis, is in `V`. Each column has disjoint two-entry
support and is a normalized spinor `v(z)=(1,-z)/sqrt(1+|z|^2)`. Direct
differentiation gives

```
||dv||^2 = |dz|^2/(1+|z|^2)
           - (Re(conj(z)*dz))^2/(1+|z|^2)^2 <= |dz|^2.
```

At fixed Q, every channel has `|dz|=sqrt(dx^2+dy^2)`, so
`||dV||_op <= ||dK||_2`. At fixed K, `||dV||_op <= |dQ|/2`.
For any constant real scalar c, differentiating
`H-cI=V^dagger(A-cI)V` yields the global bounds

```
||H(K',Q')-H(K,Q)||_op <= 2 R ||K'-K||_2 + R |Q'-Q|
R >= ||A-cI||_op.
```

This is a bound on the full retained projected expression, not just its
named kinetic velocities.

### A conservative constant without optimizing a sampled norm

The source has `a=P0-I/2`, with `P0` an orthogonal rank-one projector;
therefore `||a||=1/2`. Triangle inequalities give

```
alpha = |M| + |-2 W3-c| + |J|/2
beta  = |Mf eps| + |-2(U1+6 U2)-c| + |U1|/2
||A-cI|| <= max(alpha,beta) + |cpp eps|.
```

For the declared shift `c=-132.5 meV` and the retained decimal parameters:
`alpha=44`, `beta=43.9106`, `|cpp eps|=2.92494`. Their bound is
`R=46.92494 meV`. The implementation computes this with rational arithmetic
and rounds **up to 47 meV**, giving `L_K=94 meV` per unit dimensionless K
and `L_Q=47 meV` per unit dimensionless Q. The shift changes the bound,
not the eigenvectors or physical matrix. Measured spectral norms are checks,
not the basis of this constant.

## 3. What a cell bound actually establishes

Let `H0` be a cell centre and `g0` its external gap for the fixed ordered
middle pair (zero-based eigenvalue indices 1,2). For a Euclidean disk of
radius rho in K at fixed Q, set `epsilon=94*rho`. Weyl's inequality gives
the uniform external-gap lower bound `g0-2*epsilon`. A positive value
establishes isolation of that pair throughout this disk in exact arithmetic.
A nonpositive value means this sufficient test is inconclusive.

For completeness, a conservative projector bound follows from the residual
equation, without assuming an unjustified factor-one formula. Expand each
perturbed target eigenvector in the eigenbasis of H0. Its components outside
the target pair have denominators at least `g0-epsilon`, by Weyl. Summing
the squared residuals for the two orthonormal target vectors gives, when
`epsilon<g0`,

```
||P(K)-P(K0)||_op = ||sin Theta||_op
  <= ||sin Theta||_F <= sqrt(2)*epsilon/(g0-epsilon).
```

One may always replace an upper bound larger than 1 by the trivial bound 1.
This elementary residual argument works for Hermitian matrices. For related
separation conditions and constants, see Yu, Wang and Samworth,
[arXiv:1405.0680, Theorems 1 and 2](https://arxiv.org/pdf/1405.0680).
Their stated real-symmetric theorem is not silently used as a factor-one
complex-Hermitian formula here.

There is a further distinction between coefficient-space and ambient
projectors: the eight-component embedded projector is `Pi=V P V^dagger`.
The triangle inequality gives `||Pi-Pi0|| <= ||P-P0||+2*rho`, capped at 1.
Thus a claim about physical embedded subspaces cannot simply drop the
motion of V. No Berry connection or Euler transport for that embedded
bundle is computed in this pass.

## 4. Limits and next proof obligation

The analytical inequalities are uniform. The retained numerical gap values
and eigenvectors use ordinary floating point, with eigendecomposition
residuals recorded; they are not interval-certified eigenvalue enclosures.
The integer bound R has deliberate margin, but the complete computation
is not a formally verified numerical certificate.

Only three declared centres, two declared radii, one Q and eight boundary
witnesses per disk are evaluated. Boundary witnesses do not prove uniformity;
the derivative bound does. The six disks do not cover a research domain.

Next: connect a declared continuous interpolation of sampled projectors to
the true bundle, with consistent orientation and boundary sewing, and then
connect that interpolation to the actual Wilson estimator. Until that is
done, a local variation/isolation screen is not a certified Euler number.
Finite-cutoff TBG sewing, the paper's sign convention and Fable's consumer
repairs remain separate open items.
