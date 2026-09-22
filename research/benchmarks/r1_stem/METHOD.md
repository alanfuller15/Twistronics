# A bounded crossing of a moving comparison stem

Let a(D) and b(D) be the inherited base and ring-anchor vertices of the straight
comparison stem S. Each is affine between the retained contour stations.
Let f(D) be the continuously identified upper-gap node. We test the signed area

`s(D) = cross(b(D)-a(D), f(D)-a(D))`.

A zero is a crossing of the supporting line. It is a crossing of the segment
only when `t=((f-a)·(b-a))/|b-a|²` lies strictly between zero and one.
Here cross is the oriented determinant in the declared fractional momentum
coordinates; these areas and slopes are not Cartesian physical distances.

The exact vertices are interpolated. In general, interpolating each normalized
p–q direction at the stations differs from normalizing an interpolated p–q
direction. The earlier numerical crossing control used the latter construction.
This checkpoint uses exactly the original piecewise-affine base-to-anchor stem.

## Root identity and its exact derivative

The inherited continuation supplies a unique root in a moving three-variable
box about `ybar(D)=y0+v(D-D0)`, with `y=(f1,f2,E)`. In a fixed pair frame F and
orthogonal complement Q its equation is the three real symmetric components of

`S = FᵀHF - E I₂ - BᵀK⁻¹B = 0`,

where `B=QᵀHF` and `K=QᵀHQ-EI`. The inherited complementary gap G, inertia,
contraction q and self-map bounds establish existence, uniqueness and the
ordered band indices conditionally on their numerical inputs.

For comoving displacement u, write the Schur equation as `g(u,D)=0`. The
projected linear Jacobian is J and C is its numerical inverse. The nonlinear
term is `N=BᵀK⁻¹B`. For

`T=AD+v1 A1+v2 A2`,

the fixed-u D derivatives satisfy `BD=QᵀTF` and `KD=QᵀTQ-vE I`.
If the inherited tube bounds are `||B||≤Bmax` and `||K⁻¹||≤1/G`, then

`||ND|| ≤ 2 ||BD|| Bmax/G + Bmax² ||KD||/G² = nD`.

Every one of the three symmetric components is bounded in magnitude by the
operator norm. The projected moving-D residual is `rD=gD_projected+Jv`, which
is retained rather than assumed to vanish. Let R be the diagonal matrix of
parent tube radii. The contraction bound implies

`||R⁻¹ (I-C gy) R||∞ ≤ q < 1`.

Consequently the inverse of `R⁻¹ C gy R` has infinity norm at most `1/(1-q)`.
Differentiating `g(u(D),D)=0` gives a uniform bound

```
etaD = max_i [(|C rD| + rowsum(|C|) nD)_i / radius_i]
|y'_i-v_i| ≤ radius_i etaD/(1-q).
```

The implicit-function derivative exists because this same bound makes gy
invertible throughout the tube. The derivative is that of the actual Schur
root; the frozen projected Jacobian alone is not used as the true derivative.
The previously established endpoint links identify the same continuous root
across reference intervals. The retained inner radii bound its position.

Any newly calculated tube must lie strictly inside the original inherited
full `(f1,f2,E)` tube throughout its complete D interval. Affine center
differences achieve coordinatewise absolute maxima at the endpoints, making
this containment test finite. The new tube's existence and parent uniqueness
then identify the same root. Point certificates use the same rule at one D.
No mere overlap of boxes establishes identity.

## Uniform geometry bounds

Set `e=b-a` and `w=fbar-a`. Both are affine on a cell. The predictor area
`cross(e,w)`, dot product `e·w` and squared length `e·e` are quadratic in the
normalized cell coordinate x. For power coefficients `(c0,c1,c2)`, the degree-two
Bernstein coefficients are `(c0,c0+c1/2,c0+c1+c2)`. Their minimum and maximum
enclose the polynomial throughout the cell, without sampling its interior.

Add the root-position uncertainty to obtain the side and dot-product bounds.
For side, the error is `max|e2| rf1 + max|e1| rf2`; for dot product it is
`max|e1| rf1 + max|e2| rf2`. Coordinate maxima of affine e occur at endpoints.
Divide the dot-product interval by the strictly positive length-squared interval
using all four endpoint quotients to bound t.

The exact side derivative is

`s' = cross(e', f-a) + cross(e, f'-a')`.

Its predictor value is affine in D. Add uncertainty

`|e2'| rf1 + |e1'| rf2 + max|e2| rv1 + max|e1| rv2`,

where rv is the newly bounded velocity radius. A strictly negative upper bound
proves transversality and monotonicity on that cell.

## Existence, count and location

The fixed event window is `[38.0625,38.125] meV`, chosen from the previously
known numerical event. Outside it, every accepted cell must separate the whole
node enclosure from the supporting line. Inside it, every cell must have
strictly negative side derivative and an along-segment parameter strictly
between zero and one. Independently bounded point roots must give positive
side at the window's left endpoint and negative side at its right endpoint.

Continuity and the intermediate value theorem give an event; strict monotonicity
gives uniqueness in the window; the finite-segment bounds make it a segment
crossing; the exterior side bounds exclude any further crossing by this tracked
node over D38–39. The conclusion counts this node's crossings, not crossings
by unknown nodes. Failed bounds are retained and subdivided to a frozen depth.

Once existence and uniqueness are established, a point bound `s(m)∈I` and a
uniform nonzero derivative interval J imply, by the mean value theorem, that
the event belongs to `m-I/J`. Intersect this enclosure with the current interval
at every step. Interval division uses all four endpoint combinations. This
interval-Newton contraction stops at the frozen `1e-4 meV` target width or its
iteration/progress limit. Reported endpoint digits identify reproducible
enclosures, not physical accuracy.

## Numerical status and interpretation

All inequalities use ordinary floating-point eigensolutions, norms and declared
allowances. They are conditional numerical bounds, not outward-rounded interval
certificates. New center frames, complementary spectra, full solver histories,
native Hamiltonian and spectrum comparisons, geometric polynomials and every
attempt are retained. A separate report reconstructs the primitives, inequalities,
coverage and event enclosures; it checks polynomial extrema independently of
the producer's Bernstein calculation.

The nine initial analytic controls precede production. A separately frozen
post-production supplement adds two intervals of an analytically curved
four-band root to exercise nonzero complementary coupling in the velocity
bound. Its exact derivative is monotone, so endpoint derivative values bound
the whole interval. The original controls, production records and thresholds
remain unchanged; the supplemental plan and results are retained separately.

This establishes a specific obstruction to transporting the straight comparison
stem through the path. The inherited detoured contour remains gapped and carries
the established +k label. No new charge is measured here. The upper-node crossing
is consistent with the inherited endpoint conjugation relation, but absence of
other nodes on the entire swept straight stem has not been established. This
checkpoint does not by itself assign the complete sign change uniquely to this
one event, establish a full braid, or calculate an Euler-class change.

N8, strain, twist and constant tunnelling remain fixed. D is the opposite layer
potential amplitude ±D meV, not a calibrated experimental field. The two
Hamiltonian implementations share the diagnostic framework.
