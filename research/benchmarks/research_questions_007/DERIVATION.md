# A controlled corner repair and the topology it does not select

This additive proposed proof follows questions 006 and the retained partner
boundary note at `fe5438438ea3bcac5e0a70011f660bf7001d0835`.
It is submitted for independent partner review. Its construction acts on
specified real, oriented rank-two fibres. It does not construct a physical
graphene sewing, repair production code, or certify floating-point error.

## 1. Setting and an exact corner repair

Let E be an oriented rank-two Euclidean bundle on the closed rectangle
[0,Lx] x [0,Ly], with C2 boundary fibres and C2 orientation-preserving
isometries

```
J1(y): E(0,y) -> E(Lx,y),
J2(x): E(x,0) -> E(x,Ly).
A = J2(Lx) J1(0),       B = J1(Ly) J2(0).
```

Both A and B map E(0,0) to E(Lx,Ly). Their discrepancy D=A*B is an SO(2)
automorphism of the SOURCE fibre. Let I_x be rotation by +pi/2 on the
oriented fibre E(x,0). Orientation-preserving isometries intertwine these
canonical complex structures. No arbitrary moving-frame convention enters.

If eta=||A-B||<2, D has the unique principal rotation angle delta in
(-pi,pi), with D=exp(delta I_0) and

```
eta = 2 sin(|delta|/2),      |delta| = 2 asin(eta/2).
```

This is a principal angle of a specified SO(2) matrix, not a bound on an
unknown lifted path. Reflection data and the antipodal point are excluded.
A certified bound eta<=b<2 gives |delta|<=2 asin(b/2). The earlier
telescoping b=sum epsilon_i may be used if it is itself certified and <2.

Put u=x/Lx and choose the fixed quintic profile

```
chi(u)=10u^3-15u^4+6u^5,
chi(0)=0, chi(1)=1, chi'(0)=chi'(1)=chi''(0)=chi''(1)=0.
```

Primes on chi in this display denote u derivatives. Define

```
Q(x)=exp(delta chi(x/Lx) I_x),
J2_tilde(x)=J2(x) Q(x),       J1_tilde=J1.
```

At x=0 the transition is unchanged. At x=Lx, naturality of I gives

```
J2_tilde(Lx) J1(0) = A exp(delta I_0) = A D = B
                  = J1(Ly) J2_tilde(0).
```

Thus the corner closes EXACTLY in exact arithmetic. Since 0<=chi<=1,

```
sup_x ||J2_tilde(x)-J2(x)|| = eta.
```

This is optimal among repairs changing only J2, fixing J2(0), and requiring
corner equality: the endpoint change at Lx is already forced to have norm
eta. It is not a unique repair, a physical selection rule, or a theorem of
global smooth descent of the original projector/connection. Corner values
do not by themselves verify collar/derivative compatibility. This pass
proves a C2 edge map and corner closure; those further obligations remain.

## 2. Covariant derivative cost

For the metric connections on the bottom and top fibres define
DJ = nabla_top J - J nabla_bottom. The canonical I_x is parallel for an
oriented rank-two metric connection: in oriented orthonormal coordinates
both connection matrices are scalar multiples of the fixed rotation
generator G=[[0,-1],[1,0]], which commutes with G.

Consequently nabla Q = delta chi_x I_x Q, and the product rule gives

```
D(J2 Q) = (D J2) Q + J2 (nabla Q),
||D J2_tilde|| <= ||D J2|| + |delta| |chi_x|,
sup |chi_x| = 15/(8 Lx),
integral_0^Lx |delta chi_x| dx = |delta|.
```

The correction derivative vanishes at both endpoints. This does not make
the original connection defect vanish. Nor does vanishing endpoint
derivative establish all cross-boundary jets of a physical model.

In oriented frames write J2=R(beta), A_bottom=a0 G dx and A_top=a1 G dx.
Then DJ2=(beta'+a1-a0) G R(beta). This expression transforms covariantly
under independent smooth endpoint frame rotations; beta' alone does not.
The fixed diagnostic checks this with nonzero a0,a1 and changing gauges.

## 3. Seam-aware phase variation, conditional on the declared connection

On a rectangle choose an oriented frame and write the metric connection
as G(a_x dx+a_y dy). With the coefficient convention nabla=d+A, its
curvature is G f dx wedge dy, where f=partial_x a_y-partial_y a_x.
Forward transport up the rectangle has angle -integral a_y dy.
The backward closed-path candidate W=T_y^(-1) J2 has angle

```
phi(x) = beta(x) + integral_0^Ly a_y(x,y) dy,
phi'(x) = [beta'(x)+a_x(x,Ly)-a_x(x,0)] + integral_0^Ly f(x,y) dy.
```

The bracket is exactly the scalar covariant seam defect. For the repaired
map add delta chi_x. If |f|<=F and ||DJ2||<=kappa everywhere, then

```
|phi_tilde(x+h)-phi_tilde(x)|
 <= (F Ly + kappa) h + |delta| |chi((x+h)/Lx)-chi(x/Lx)|
 <= [F Ly + kappa + 15|delta|/(8Lx)] h.
```

This is a local phase-variation result on the interval. To call W a closed
torus holonomy scan also require left/right transport compatibility:
DJ1=0 along those edges, as well as the repaired corner relation. It then
intertwines the up transports, and W(Lx) is conjugate to W(0). In oriented
rank two the scalar rotations agree. General data without that hypothesis
do not receive a periodic-scan certificate from this repair.

If the questions-005 link theorem applies uniformly, its per-loop phase
error is E_loop. An independently certified arithmetic error tau and exact
application of the specified repaired sewing give the sufficient adjacent
unwrapping condition

```
[2 p_x p_y Ly + kappa + 15|delta|/(8Lx)] h_x + 2 E_loop + 2 tau < pi.
```

Use pi/2 for the earlier calibrated policy guard. A winding interpretation
additionally needs the stated periodicity and uniform, continuous error
lifts. This pass supplies no physical values of kappa, delta, gaps or tau.
In particular, a small corner defect does not bound kappa elsewhere.

## 4. Extra full turns: the ambiguity an endpoint repair cannot resolve

Replacing delta by delta+2pi m, for any integer m, gives the SAME repaired
corner because the endpoint rotation is unchanged. The principal repair
is the one within the chosen short-arc class. Other choices can be far from
the initial transition and have larger connection cost. Endpoint equality
alone cannot distinguish them.

A complete synthetic example uses a constant oriented plane over the
rectangle, J1=I and

```
J2_m(x)=R(2pi m x/Lx).
```

All boundary singular values are identically one, the determinant is +1,
and all corner products agree for every integer m. These maps extend
smoothly on the periodically identified x edge. With the flat rectangle
connection the backward candidate has winding m. The zero rectangle
connection is not compatible with this sewing for m!=0.

An explicit COMPATIBLE metric connection on the glued bundle is

```
A = G a,      a = -(2pi m y/(Lx Ly)) dx,
Omega = dA+A wedge A = G (2pi m/(Lx Ly)) dx wedge dy.
```

It obeys dJ2+A_top J2-J2 A_bottom=0 and is compatible with J1=I.
Use the same curvature-component orientation convention as the earlier
passes: e=(1/(2pi)) integral Omega_12. Since G_12=-1, the Euler value
of THIS explicitly glued synthetic bundle is -m, while the raw backward
winding is m. Reversing the declared fibre orientation changes the Euler
sign. There is no assignment of these integers to graphene here.

Thus exact corners, orientation and even zero sewing singular-value loss
everywhere do not select the physically intended bundle. A justified
reference transition or relative homotopy class is still essential.

A useful sufficient relative-class check is available: if two closed
SO(2) transition loops J_a,J_b on the same identified fibres obey
sup ||J_a-J_b||<2, their relative loop avoids -I and has a single continuous
periodic principal angle. Scaling that angle gives a homotopy, so their
transition windings agree. This requires a UNIFORM continuous bound and
already consistent loops, not just four corner measurements. Distinct
J2_m examples reach distance exactly 2 somewhere. The diagnostics retain
one deliberately aliased comparison that misses this between samples.

## 5. Fixed evidence and limits

The script uses 2x2 rotations, algebraic derivatives, one fixed
Gauss-Legendre quadrature rule for the polynomial profile, and explicit
closed transition loops. Its fixed scalar corner angles include the two
already retained partner examples. It executes no archived production API,
Hamiltonian, eigensolver, physical mesh, random search or parameter sweep.
The formulas above, rather than sampled maxima, justify continuous bounds.

Negative controls refuse orientation reversal, nonisometry and the
principal-log branch cut. A 16-turn transition is identical to I at the
declared 16 interval endpoints but antipodal at one retained midpoint;
its winding is analytically 16. This is a reference-selection diagnostic,
not a new physical observation. Earlier evidence is unchanged.

The exact corner equation is now addressed for the declared rank-two
setting. Physical reference selection, compatible collars/jets and
connections, continuous-boundary invertibility, certified arithmetic,
real structure and domain-wide isolation remain separate requirements.
The sign-convention investigation and Fable v078 corrections remain open.

## Primary source context, accessed 2026-09-23

- Allen Hatcher, *Vector Bundles and K-Theory*, Version 2.2 (2017),
  section 1.2 on clutching and section 3.2 on oriented Euler classes:
  https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf .
  This supplies background on gluing and its dependence on transition
  homotopy; the explicit rectangle calculations are derived above.
- *Connections, curvatures and characteristic classes*, author-hosted
  Notre Dame lecture notes, sections 1 and 4:
  https://academicweb.nd.edu/~pmnev/f19/Chern-Weil.pdf .
  Background on metric connections and curvature normalization. Matrix
  and sign conventions are fixed explicitly above rather than imported
  silently from the notes' row-index convention.

These sources do not establish our physical hypotheses or attest this
new proposed repair argument. No novelty or formal-proof claim is made.
