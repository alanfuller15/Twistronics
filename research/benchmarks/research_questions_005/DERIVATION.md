# A direct bound from polar links to continuous projector transport

This additive argument is submitted for partner proof review. It uses exact
finite-dimensional matrices. Its numerical controls do not certify arithmetic
error or a physical graphene invariant. Questions 001--004 remain frozen.

## 1. Hypotheses and the uniformity clarification

Let P(t) be a C2 orthogonal projector of constant rank r in a fixed real or
complex ambient space on a whole edge [0,h]. Suppose, everywhere on that edge,
`||P'|| <= p` and `||P''|| <= q` in operator norm. Set

```
d = p^2 h^2/2,   m = 1-d,   k = p(q+p^2)h^3/6.
```

The result below requires d<1. The norm estimate applies to any rank. Only
the real, oriented rank-two specialization below supplies an SO(2) phase.
For a torus scan all bounds must hold for every continuous transverse x,
including between sampled rows and across the identified boundaries.

This explicitly adds Claude's clarification to questions 004: in the sphere
case `||n_y||<=1`, `||n_yy||<=4`, `h_y<pi/2` and `h_y^2/2<1` hold for ALL
`x in [-pi,pi]`. Hence that pass's ribbon error is continuous and periodic in
x. The old evidence is unchanged; sampled hypotheses alone would not suffice.

## 2. Compare in a horizontal frame

Choose an orthonormal frame Y(0) for ran P(0), and transport it by

```
Y' = [P',P]Y = P'Y.
```

The commutator is skew-adjoint, preserves orthonormality, and intertwines P.
Indeed `[[P',P],P]=P'`, from differentiating P^2=P. Also `Y*Y'=0` because
PP'P=0. These are exact identities, so no smooth eigenbasis within an
internally degenerate cluster is assumed. Differentiation gives

```
||Y'|| <= p,   Y'' = P''Y + (P')^2Y,   ||Y''|| <= q+p^2.
```

Write A=Y(0)*Y(h), S=(A+A*)/2, K=(A-A*)/2. Horizontality gives

```
A-I = - integral_0^h integral_0^t Y'(s)*Y'(t) ds dt.
```

Consequently `||A-I||<=d` and `S>=m I`. To bound the skew part, subtract
the Hermitian matrix Y'(t)*Y'(t) inside the integrand. Since
`||Y'(s)-Y'(t)|| <= (q+p^2)(t-s)`,

```
||K|| <= integral_0^h integral_0^t p(q+p^2)(t-s) ds dt = k.
```

This cubic estimate needs only P''; a third derivative is not assumed.

## 3. A polar homotopy and explicit constant

Consider B(u)=S+uK, 0<=u<=1. Its Hermitian part is S>=mI, so
`||B(u)v|| >= Re(v*B(u)v) >= m` for any unit v, and its least singular
value is at least m. Write its unique polar decomposition B=U H, H>0.
At u=0, U=I. Let Omega=U*U', which is skew-adjoint. Differentiating B=UH
and subtracting adjoints gives

```
H Omega + Omega H = U*K - K*U.
```

The inverse of this positive Sylvester operator is the integral
`X=integral_0^infinity exp(-Hs) C exp(-Hs) ds`, with norm at most
`||C||/(2m)`. Thus `||Omega||<=||K||/m<=k/m`, and the polar path from
I to polar(A) has operator-norm length at most

```
epsilon(p,q,h) = p(q+p^2) h^3 / [6(1-p^2 h^2/2)].
```

In particular `||polar(A)-I||<=epsilon`. For real rank two, this path lies
in SO(2), and its continuously lifted rotation angle has magnitude at most
epsilon. The norm inequality alone is not being converted to a phase bound;
the SO(2) path length supplies it directly.

For arbitrary endpoint frames F0=Y(0)G0 and F1=Y(h)G1, polar covariance
gives the sampled backward link `G0*polar(A)G1`, whereas exact backward
transport is `G0*G1`. Therefore the same error bound holds in endpoint
coordinates. This directly compares the actual polar-overlap operation with
the true connection, without assuming a geodesic approximation theorem.

The square polar-factor perturbation literature provides related estimates;
the displayed homotopy/Sylvester proof supplies the specific constant used
here. This is a derived bound, with no novelty claim.

## 4. Loops, phase scans, orientation and boundaries

For N_y edges of width h_y, uniform constants p_y,q_y give
`E_loop=N_y*epsilon(p_y,q_y,h_y)`. Telescoping products of unitary factors
gives a norm error at most E_loop at any rank. In a real oriented rank-two
bundle, consistent oriented frames identify the fibre maps with SO(2), so
the continuous per-edge phase lifts add to a real loop error beta with
`|beta(x)|<=E_loop`.

Assume P(x,y) is C2 and periodic on a rectangular torus of dimensions
L_x,L_y, in a fixed real ambient basis, with a specified global fibre
orientation and exact identity sewings. There need not be one global frame.
Require d_y<1 uniformly for ALL continuous x. The above polar homotopies
and Kato transport depend continuously on x; their scalar SO(2) generator
is invariant under changes of oriented local frame. Their summed lift beta
is therefore continuous and periodic in x. Polygonal and true holonomy
have the same winding. Orientability is a hypothesis, not a consequence of
small local steps.

In an oriented local frame the curvature is `F_xy=Y^T[P_x,P_y]Y`, so
`|F12| <= 2 p_x p_y`. Its Euler normalization is 1/(2*pi), as in questions
004. Continuous holonomy changes across a transverse width h_x by at most
`F_strip=2 p_x p_y L_y h_x`. A sufficient condition for principal-difference
unwrapping is therefore

```
2 p_x p_y L_y h_x + 2 E_loop < pi.
```

If the algorithm propagates orientation by base links, require
`d_x=p_x^2 h_x^2/2<1` for those edges too; positivity in a horizontal
frame fixes their determinant sign relative to the specified orientation.
The archived overlap floor 0.5 is ensured by `1-d_x>=0.5` and
`1-d_y>=0.5`. These conditions do not certify a nonidentity or truncated
sewing. They apply only when the stated periodic identification is exact.

Replacing pi by pi/2 guarantees the declared calibrated phase guard. The
lift recovers the backward holonomy winding; retain the documented
`oriented_euler=-fibre_sign*raw_winding` conversion. If a certified numerical
per-loop phase error tau is separately supplied, add 2*tau to the step
bound; after unwrapping, endpoint error is at most tau/pi winding units.
No such certified tau is supplied here.

### Applying the general constants to the retained sphere

For P=I-nn^T, use `p_x=a`, `p_y=1`. The earlier normal bounds imply the
conservative `q_y=2||n_yy||+2||n_y||^2<=10` globally. We intentionally use
the generic curvature bound 2a in this comparison. For a=1 the general
theorem is inconclusive at N=24, guarantees unwrapping at N=48, and also
guarantees the pi/2 guard at N=96. The sharper sphere-specific theorem in
questions 004 still applies at 48; the weaker general bound does not
invalidate it. These are bound evaluations against retained evidence,
not new two-dimensional production runs.

## 5. A sharp normalized-spinor acceleration bound

The retained basis uses `v(z)=(1,-z)/sqrt(1+|z|^2)` along a straight line
`z(t)=z0+u*t`. The derivative is with respect to this affine parameter, not
an arbitrary reparameterization or an arbitrarily changing phase gauge.
For u=0 the claim is immediate. Otherwise a constant unitary rotation of
the second component makes u=c=|u| real. Write z=s+i*b and C=1+b^2>=1.
An exact differentiation of this real-normalized vector gives

```
||v''||^2 = c^4 C(C+4s^2)/(C+s^2)^4
          = c^4 (1+4t)/(C^2(1+t)^4),  t=s^2/C >= 0.
```

Since `(1+t)^4-(1+4t)=6t^2+4t^3+t^4>=0`, it follows that
`||v''||<=|u|^2`. Equality holds at z=0 for any nonzero u. This is a
global analytic proof for this fixed normalized lift; no sampled supremum
or informal circle argument is used.

Disjoint column supports transfer the bound to the retained V. With
`H-cI=V*(A-cI)V`, `||A-cI||<=R=47`, the revised constants are:

| Affine direction | ||V'|| | ||V''|| | ||H'|| | ||H''|| |
|---|---:|---:|---:|---:|
| Unit K direction, fixed Q | 1 | 1 | 94 | 188 |
| Unit Q direction, fixed K | 1/2 | 1/4 | 47 | 47 |

The earlier conservative 470/117.5 second-derivative bounds remain true.
These improved values enter the previously derived isolated-cluster bounds
`p1=sqrt(r)*L/g`, `p2=sqrt(r)*M/g+6r*L^2/g^2`. For an embedded projector
VPV*, the K-direction bounds become `p1+2` and `p2+4p1+4` (previously
the final constant was 10). The Q analogues are `p1+1` and `p2+2p1+1`.
At small g, the unchanged L^2/g^2 term can dominate: the reduction in M
must not be described as an equally large improvement in the whole p2.

## 6. What this transfers, and what is still missing

The local link theorem applies to C2 orthogonal projectors in any fixed
finite-dimensional ambient space, real or complex. The winding result
additionally requires a globally oriented REAL rank-two periodic bundle,
the specified boundary identifications, and uniform constants everywhere.
The direct-projection family supplies analytic H derivative constants but
has not met all those requirements on a physical domain. Small disks from
questions 003 have only ordinary floating-point gap inputs. Their reuse
here is explicitly conditional arithmetic, not interval-certified gaps.

The general link theorem removes one conceptual transfer gap. Verifying
real structure and orientation, domain-wide isolation, physical boundary
sewings and arithmetic error remains necessary before a graphene claim.
The Vafek sign question and Fable's v078 corrections remain separate.

## Source context

- Avron, Seiler and Yaffe, *Adiabatic Theorems and Applications to the
  Quantum Hall Effect*, Commun. Math. Phys. 110 (1987), pp. 33--49,
  [author-hosted paper](https://phsites.technion.ac.il/avron/wp-content/uploads/sites/3/2013/05/commun_math_phys_110_33-49_1987.pdf).
  Sections 1--2 develop projection-based parallel transport and intertwining.
  The finite-dimensional identities needed here are derived explicitly above.
- Ren-Cang Li, *New Perturbation Bounds for the Unitary Polar Factor*,
  [Berkeley report CSD-94-852](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1994/Archive/CSD-94-852.pdf),
  later SIAM J. Matrix Anal. Appl. 16 (1995), 327--332,
  [DOI](https://doi.org/10.1137/S0895479893256359).
  Context for polar-factor perturbation bounds; the cubic transport estimate
  above is our explicitly supplied combination, not a quoted theorem there.

Both primary PDFs were accessible on 2026-09-23. No formal proof checker,
novelty assessment or independent material-model validation is claimed.
