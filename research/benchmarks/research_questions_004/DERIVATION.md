# An explicit transport-error bound for the sphere references

This is a proposed exact-arithmetic argument, retained for partner proof
review. Numerical checks test its implementation and hypotheses. They are
not interval enclosures or independent validation of a material model.

The target is the unmodified archived `euler_wilson`: polar factors of frame
overlaps, loops along coordinate y, a transverse scan along x, identity
sewings, and the documented fibre-orientation conversion. All coordinates
below are radians. The energy gap of this synthetic reference is exactly 2.

## 1. Derivative and curvature constants

For integer a>=1, m=-1 or -3, use

```
d=(sin(a*x), sin(y), m+cos(a*x)+cos(y)), r=||d||, n=d/r,
P=I-n n^T, H=2n n^T-I.
```

As established in questions 003, r>=1 everywhere. Along either coordinate,
write b=a for x and b=1 for y. Then ||d'||<=b, ||d''||<=b^2,
|r'|<=b and ||n'||<=b. Differentiating d=r n twice, taking its tangent
and normal parts, gives

```
n''=(I-n n^T)d''/r - 2(r'/r)n' - ||n'||^2 n,
||n''|| <= 4 b^2.
```

This conservative bound includes the normal acceleration. It holds at
every point, including the seam, not just at sampled points.

For oriented tangent frames (e1,e2,n), let A12=e1 dot de2. Its curvature is
`F12=n dot (partial_x n cross partial_y n) dx wedge dy`, so the scalar
curvature obeys `|f_xy|<=a`. With this convention
`e2=(1/(2*pi))*integral f_xy=2 degree(n)`: it is 2a for m=-1 and 0
for m=-3. There is no additional factor 1/2 in this tangent-plane curvature.
The SO(2) Euler-flux normalization is consistent with Ahn, Park and Yang,
[arXiv:1808.05375v5, Sec. III A, Eq. (4)](https://arxiv.org/pdf/1808.05375v5).

## 2. Which path does a polar link represent?

Suppose two oriented normals p,q have angle theta<pi/2. In tangent frames
whose first axis is the common perpendicular to p and q and whose second
axes are matched by the short sphere rotation, the overlap matrix is
`diag(1,cos(theta))`. Its polar factor is I. Orthogonal changes of either
frame give the same identity covariantly. Thus `polar(Fp^T Fq)` is backward
parallel transport along the short normal geodesic, in endpoint frames.

The acute-angle hypothesis is essential. If theta>pi/2, the polar factor
instead removes the sign of the negative overlap singular direction. It
need not equal transport along the oriented-normal arc, even when the
smallest singular value exceeds 0.5. The retained theta=2.4 control exhibits
this distinction. We do not generalize from overlap invertibility alone.

For the grid, the sufficient conditions `a*h_x<pi/2`, `h_y<pi/2` ensure
acute normals on every base and loop edge. The archived base-frame flips
then make fibre orientation consistent along x: the overlap determinant's
sign is the product of the two fibre signs when cos(theta)>0. Interior
frame changes cancel in the closed overlap product. Identity endpoint
sewings close the same periodic bundle as the true normal field.

The separate archived overlap floor 0.5 is guaranteed if both coordinate
arc-length bounds are at most pi/3. All once-folded grids considered here
meet that stronger condition. An acute link alone need not pass that floor.

With a positively oriented initial tangent frame, the overlap product's
angle is the negative of forward parallel-transport angle. Hence the
retained conversion `oriented_euler=-fibre_sign*raw_winding` is the sign
used here, not a sign fitted to an output.

## 3. A ribbon bound with an explicit constant

Let n:[0,h]->S^2 be one true edge, with ||n'||<=v and ||n''||<=A.
Let `ell(t)=(1-t/h)n(0)+(t/h)n(h)` be its Euclidean chord. The integral
remainder for linear interpolation gives the vector inequality

```
||n(t)-ell(t)|| <= (A/2)t(h-t) <= A h^2/8 = delta.
```

Assume delta<1. The explicit homotopy from the true path to the normalized
chord is

```
w(t,u)=(1-u)n(t)+u ell(t),   S(t,u)=w/||w||,   0<=u<=1.
```

It never vanishes since ||w||>=1-delta. Moreover,
`||partial_t w||<=v`, because the chord derivative is an average of n',
and `||partial_u w||<=A t(h-t)/2`. The derivative of normalization has
operator norm 1/||w||. Therefore

```
|S dot (partial_t S cross partial_u S)|
  <= v A t(h-t) / (2(1-delta)^2).
```

Integrating over the parameter rectangle gives an absolute signed-area bound

```
epsilon_link <= v A h^3 / (12(1-A h^2/8)^2).
```

The normalized chord traverses the short spherical geodesic. Parallel
transport around the boundary of this ribbon has angle equal to its signed
spherical area, modulo 2*pi. One can select the real lift by following the
homotopy from u=0. Stokes' theorem on the pulled-back oriented frame bundle
over the rectangle gives the same formula even if its image overlaps itself;
the absolute integral above still bounds the lifted error.

For the standard holonomy/area identity see Hornung,
[Framed Curves, Ribbons, and Parallel Transport on the Sphere, Prop. 2.3](https://doi.org/10.1007/s00332-023-09930-0).
That proposition states the simple-domain case; the parameter-rectangle
argument and the interpolation estimate above are supplied here explicitly.

For N_y loop edges, each of width h_y=2*pi/N_y, SO(2) errors add. Using
v=1 and A=4 for our y paths gives the uniform loop-angle error

```
E_loop = N_y * 4 h_y^3 / (12(1-h_y^2/2)^2).
```

No derivative in x appears in this loop error: the production routine loops
in y, where the fold frequency is 1. The fold a does enter the transverse
curvature bound and the base-edge hypothesis.

## 4. The combined unwrapping condition

The exact continuous y-loop holonomy has a real lift phi(x) on the x
interval. Its change over h_x is bounded by curvature flux through the
strip:

```
|phi(x+h_x)-phi(x)| <= (2*pi)*a*h_x = F_strip.
```

The polygonal overlap product has a lift psi(x)=phi(x)+beta(x), with
`|beta(x)|<=E_loop`. The ribbon construction is continuous and periodic
in x, so beta has the same value at x=-pi and pi. The polygonal and
continuous holonomy maps therefore have the same winding.

The actual discrete transverse scan can recover that winding by principal
phase differences if

```
F_strip + 2 E_loop < pi.
```

This inequality leaves no 2*pi ambiguity between successive scan points.
For the calibrated pi/2 phase policy to be guaranteed to pass, replace pi
by pi/2. Both require the acute-link and nonvanishing-ribbon hypotheses
above. Policy failure and wrong winding are different questions.

For a=1 and square grids:

| N | E_loop (rad) | F_strip + 2 E_loop (rad) | Exact-arithmetic unwrapping | Guaranteed pi/2 policy |
|---:|---:|---:|---|---|
| 24 | 0.15391606 | 1.95276619 | Sufficient | Inconclusive |
| 48 | 0.03650981 | 0.89548664 | Sufficient | Sufficient |
| 96 | 0.00901028 | 0.42925408 | Sufficient | Sufficient |

The fold-97 alias fails the sufficient conditions at both 48 and 96. No
statement that its falsely returned integer is reliable follows from this
argument. A failed sufficient condition does not prove an estimate wrong;
the analytic degree establishes the error in this particular counterexample.

### Arithmetic and rounding are a separate layer

The theorem describes exact projectors, polar factors, phases and arithmetic.
If an additional certified phase error tau were available for each computed
loop, the scan condition would become `F_strip+2E_loop+2tau<pi`.
After the correct lift is chosen, endpoint phase errors give winding error
at most tau/pi, so tau<pi/2 would suffice for nearest-integer rounding.
We do not provide a certified tau for NumPy/SciPy. Numerical ODE comparisons
and exact latitude controls are diagnostics, not a substitute for it.

## 5. Transferable constants, without transferring the sphere theorem

For a real oriented rank-two projector in a fixed ambient basis, curvature
is `F_xy=E^T[P_x,P_y]E`. The exact safe bound is
`|F12|<=2 ||P_x|| ||P_y||`, with Euler normalization 1/(2*pi).
The sphere has the sharper bound a derived above. Applying the generic
formula requires a verified real structure and common basis.

The questions-003 spinor is v=w/||w|| with w affine along any straight
unit K direction and ||w'||=1. The same normalization calculation yields
`||v''||<=4`. Disjoint support gives `||V'||<=1`, `||V''||<=4`.
Consequently, at R=47 for the retained direct-projection expression,

```
||H'||<=2R=94,   ||H''||<=2R(4+1)=470
```

in meV per respective power of dimensionless K. Along unit Q variation,
the analogous constants are 47 and 117.5. These cover H, not automatically P.

A concrete gap-dependent projector bound can be obtained without choosing
smooth eigenvectors inside a possibly degenerate pair. Assume a C2 Hermitian
H(t), an isolated ordered rank-r cluster, a uniform external gap g>0,
`||H'||<=L` and `||H''||<=M`. Differentiating P^2=P shows P' is off-diagonal
between P and Q=I-P. In an eigenbasis at one point, the Sylvester equation
from [H,P]=0 gives

```
p1 := ||P'|| <= sqrt(r) L/g.
```

Here each entry of QP'P has a denominator of magnitude at least g;
its Frobenius norm is at most ||QH'P||_F/g <= sqrt(r)L/g.
For the second derivative, the off-diagonal block obeys

```
H_Q (QP''P) - (QP''P) H_P = -QH''P - 2Q[H',P']P.
```

Its norm is bounded by `sqrt(r)(M+4L*p1)/g`. The diagonal blocks follow
from P^2=P: `PP''P=-2P(P')^2P`, `QP''Q=2Q(P')^2Q`, each of norm
at most 2p1^2. Thus a conservative bound is

```
||P''|| <= sqrt(r) M/g + 6r L^2/g^2.
```

For r=2 this is `sqrt(2)M/g+12L^2/g^2`. An embedded projector VPV^dagger
has first-derivative bound p1+2 and second-derivative bound p2+4p1+10
along unit K directions. These are symbolic bounds conditional on g; the
previous floating-point centre spectra do not supply interval-certified g.

This does not extend the sphere ribbon/geodesic proof to arbitrary
Grassmannian paths or finite-cutoff TBG sewings. That extension, the real
structure, domain-wide certified isolation and arithmetic error remain open.
No sign convention, graphene invariant or experimental conclusion is chosen.
