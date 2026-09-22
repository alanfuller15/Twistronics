# An energy-aware interior inventory

The inherited checkpoints provide (i) a unique local q crossing in explicit
three-variable `(f1,f2,E)` tubes, (ii) a gapped moving based contour, and (iii)
continuous geometric attachment of that contour to q. What they did not rule
out was another crossing elsewhere inside the ring. This calculation addresses
that finite, local interior, throughout D38–39 rather than at discrete stations.

All bounds below have exact mathematical implications if their numerical inputs
are enclosed correctly. This implementation uses ordinary floating point and
declared allowances, **not outward-rounded interval arithmetic**. The conclusion
remains conditional on the accuracy of eigensolutions, norms, frames and bounds.

## Domain and inherited core

Use the accepted q tubes from each of the inherited 8- and 16-interval campaigns
in each engine. At a reference midpoint D0, let the inherited predictor be
`ybar(D)=y0+v(D-D0)`, with `y=(f1,f2,E)`. Write `u=f-fbar(D)`.

For each reference interval, clip every contour interval to it and evaluate
every ring vertex at both clipped endpoints. Both original contour meshes and
both radii are included. Set each outer halfwidth Rj to the largest absolute
vertex displacement from fbar plus `1e-10`. Because vertex displacements are
affine on each clipped interval, and the ring interiors are convex, the complete
moving polygons lie inside `|uj|≤Rj`. This inventories a containing rectangle,
including its corners outside the rings.

The inner rectangle retains the **unchanged parent momentum radii**. Its energy
radius is also unchanged. The parent's contraction and endpoint-linking evidence
gives one continuous q root in the full three-variable tube. However, uniqueness
in that tube does not by itself imply uniqueness in its momentum projection:
an additional candidate crossing could, in principle, have a different energy.
The energy-capture step below closes that specific logical gap.

## Fixed-frame Schur complement

Keep the parent's real two-band frame F fixed over the reference interval and
complete it by an orthogonal Q. At the reference point define

```
K0 = Qᵀ H0 Q - E0 I
G0 = min |eig(K0)|
T = AD + v1 A1 + v2 A2
K = Qᵀ H(f,D) Q - E I
B = Qᵀ H(f,D) F
S = Fᵀ H(f,D) F - E I₂ - Bᵀ K⁻¹ B.
```

When K is invertible, a flat-band double eigenvalue is equivalent to `S=0`.
Other-band gaps are bounded separately, so the crossing of interest has the
same ordered indices as the parent's q pair.

For a cell in `(u1,u2,d)`, where `d=D-D0`, let

```
L = max|u1| ||A1|| + max|u2| ||A2|| + max|d| ||T-vE I||
e0 = max of |the two reference pair eigenvalues - E0|
W = e0 + L + allowance.
```

Weyl's eigenvalue inequality implies that **any** candidate double eigenvalue
of this ordered pair in the cell has `|E-Ebar(D)|≤W`. This is a candidate-energy
window, not an assumption about where an optimizer converges. It also gives
`||K-K0||≤L+W` at any such candidate.

## Weighted resolvent bound

Let `R=|K0|^(-1/2)`, where the absolute value retains eigenvectors and replaces
eigenvalues by their magnitudes. Then

```
R K R = sign(K0) + R(K-K0)R
eta = (L+W)/G0
||[R K R]⁻¹|| ≤ 1/(1-eta),  when eta<1
||Bᵀ K⁻¹ B|| ≤ ||R B||²/(1-eta).
```

The sign matrix is orthogonal, so its least singular value is one; subtracting
the perturbation norm proves the inverse bound. This retains the energy scales
of the complementary bands in the numerator instead of assigning all their
couplings the smallest complementary gap.

The cross block is affine:

`B=B0+u1 B1+u2 B2+d BT`.

The calculation retains all 2×2 Gram blocks `Biᵀ |K0|⁻¹ Bj`. They reproduce
`||RB||²` as the largest eigenvalue of a 2×2 quadratic matrix. The operator norm
of an affine matrix is convex, so its maximum over a rectangular cell is bounded
by the maximum at the eight vertices. Denote that norm bound by b. After the
declared allowances, use `N=b²/(1-eta)` as the Schur correction bound. The frozen
gate is stricter than invertibility alone: `eta<0.9`.

## Energy capture inside the core

Apply the same candidate-energy and correction bounds over the unchanged parent
momentum box and complete D interval. Taking the trace of `S=0` gives

`E-Ebar = g0_trace + d residual_trace + trace_gradient·u - tr(BᵀK⁻¹B)/2`.

The three quantities before the correction are computed directly from the
parent fixed frame, with the small predictor residual retained. Thus every
candidate double eigenvalue in the core has

```
|E-Ebar| ≤ max_d |g0_trace+d residual_trace|
           + sum_j |trace_gradient_j| core_radius_j + N.
```

Require this entire bound, with allowance, to be strictly smaller than the
parent energy radius. Then every candidate in the momentum core belongs to the
full parent uniqueness tube and is the already continued q root. The parent
existence bound also puts that root strictly inside the momentum core.

## Excluding crossings outside the core

The two traceless components of `FᵀHF-EI` do not depend on E. In comoving
coordinates they are

`z(u,d)=g0_traceless + J_momentum u + d residual_traceless`.

At the D-cell midpoint, the minimum of `||z||₂` on a momentum rectangle is the
distance from zero to a parallelogram. It is zero if the unconstrained zero is
inside; otherwise the minimum occurs on one of the four edges, where a clipped
one-dimensional quadratic minimizer gives it directly. Subtract the bounded
D variation and floating allowance to obtain a uniform lower bound l.

For any real symmetric 2×2 matrix Nmat, the Euclidean norm of its traceless
component vector is at most `||Nmat||₂`. Therefore **l>N** rules out `S=0` in
the entire cell and its full candidate-energy window. The code requires an
additional `1e-7 meV` positive exclusion margin. No search for a small gap, and
no interpolation of sampled root locations, substitutes for this inequality.

Four closed rectangular strips tile the outer rectangle outside the inner core
with disjoint interiors. Extrude each through the reference D interval. Failed
bounds are bisected along the largest width times Hamiltonian derivative norm.
Every node in each subdivision tree is retained. The frozen depth and split-node
budgets terminate unresolved regions without changing the path, core or thresholds.

## Isolation of the remaining gaps

Fresh five-band spectra at reference centers cover ordered indices 296–300.
For the entire outer box, the same L bounds each adjacent gap from below by its
center gap minus `2L` and allowance. Require gaps 296/297, 298/299 and 299/300
to exceed `0.001 meV`. The selected three-band block remains isolated and its
upper internal gap stays open. Flat-band exclusion and core uniqueness then
account for every degeneracy **of the selected block inside this local domain**.
This is not an inventory of all 596 bands or of the full Brillouin zone.

## Interpretation with the earlier contour evidence

If every gate passes, the tested ring interiors contain precisely the continued
q crossing of the selected block for each D. The inherited convex-contour
attachment places q inside each ring, while the interior inventory excludes any
additional relevant crossing there. The inherited fixed three-band chart covers
the ring interiors because its rectangular domain contains all their vertices.
The inherited stem and swept surface remain gapped.

These facts support interpreting the previously measured `+k` based-loop charge
as belonging to q **in the declared reference-frame and stem convention**. The
absolute signed label is not asserted to be convention-independent. No new
band-charge calculation is performed here. This does not establish a complete
braid, an Euler-class change, novelty, infinite-cutoff convergence or an
experimental realization. The strain and tunnelling are fixed; D is the model's
opposite layer potential `±D meV`, not a calibrated experimental field.

## Numerical checks and limitations

Energy and Hamiltonian-norm allowances are `1e-7`; the weighted-norm allowance
is `1e-7 sqrt(meV)`, and geometry padding is `1e-10` in fractional coordinates.
The independent report reconstructs the weighted Gram matrices from retained
frames and the Hamiltonians, native five-band spectra, every cell inequality,
core energy capture, domain containment and full subdivision coverage.

The controls include an affine multiband model with a second analytically known
double eigenvalue. The inventory must retain unresolved cells containing that
node. A rejected bound indicates an unresolved region, not necessarily a new
physical crossing. The controls also reject an insufficient energy window and
a complementary gap closing between parameter endpoints.

For context on genuinely verified floating-point norm enclosures, see Rump,
[Verified bounds for singular values, in particular for the spectral norm of a
matrix and its inverse](https://www.tuhh.de/ti3/paper/rump/Ru10a.pdf),
*BIT* 51, 367–384 (2011). Those verification algorithms are not implemented
here. The specific weighted Schur inventory and energy-capture bounds are
derived above; their numerical implementation remains explicitly conditional.
