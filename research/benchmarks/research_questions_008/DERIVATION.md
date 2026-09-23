# Corrected seam index, an abstract collar, and a joint reference gate

Status: explicit proposed derivations awaiting independent partner audit.
This pass follows q007 at 78cbdd026a633f7a0e0c3403a768f0b3710d1ede,
Claude comment 5791262731 and Codex review 5288415946. It preserves all
earlier packages. The constructions concern specified oriented real rank-two
boundary data; they assign no invariant to a physical graphene Hamiltonian.

## 1. Setting and the integer carried by two seams

Let R=[0,Lx] x [0,Ly], with Lx,Ly>0 and base orientation dx wedge dy.
Choose a global oriented orthonormal frame of a C2 metric rank-two bundle
on R. The frame is available because the rectangle is contractible.
Let G=[[0,-1],[1,0]], R(t)=exp(tG), and write the C2 oriented isometries

    J1(y): E(0,y) -> E(Lx,y),    J1(y)=R(alpha(y)),
    J2(x): E(x,0) -> E(x,Ly),    J2(x)=R(beta(x)).

Real C2 lifts alpha,beta exist on their respective intervals. Neither map
is assumed to be a closed loop. Assume the EXACT corner equation

    J2(Lx) J1(0) = J1(Ly) J2(0).

Define Delta alpha=alpha(Ly)-alpha(0), Delta beta=beta(Lx)-beta(0). Then

    q = (Delta beta - Delta alpha)/(2 pi) is an integer.            (1)

Indeed the rotation of the difference of the two sides is the identity.
Changing either lift by a constant multiple of 2 pi does not change q.
Approximate corner closure alone does not license rounding (1).

## 2. Transport proof and connection-independent correction

Let the rectangle metric connection be nabla=d+G a, where
a=a_x dx+a_y dy is C1. It need not descend through the seams. Put

    k1(y) = alpha'(y)+a_y(Lx,y)-a_y(0,y),
    k2(x) = beta'(x)+a_x(x,Ly)-a_x(x,0),
    K1 = integral_0^Ly k1 dy,  K2 = integral_0^Lx k2 dx.

Thus DJi=ki G Ji in the specified frame. With U_L(y),U_R(y) forward
parallel transport up the left/right edges, define
C(y)=U_R(y)^(-1) J1(y) U_L(y). Differentiation using the transport ODE
gives C'=k1 G C, hence

    C(Ly)=R(K1) J1(0).

For W(x)=U_x(Ly)^(-1)J2(x) choose the continuous real phase lift

    phi(x)=beta(x)+integral_0^Ly a_y(x,y) dy.

Insert the exact corner equation into the transport identity:

    W(Lx) J1(0) = R(K1) J1(0) W(0).

This yields endpoint equality modulo 2 pi. The full lifts give the stronger
exact real identity

    Delta phi - K1 = Delta beta - Delta alpha = 2 pi q.           (2)

The correction is independent of the rectangle connection, since the two
integrals of a_y cancel. If K1=0 the endpoint rotations of W agree, but a
periodic-looking scan with nonzero K1 can carry the wrong raw integer.
The sufficient condition DJ1=0 implies K1=0. DJ1=0 is NOT necessary for
endpoint periodicity: K1 in 2 pi Z is enough, and still can shift the raw
winding by an integer. This distinction sharpens the q007 discussion.

Let f=partial_x a_y-partial_y a_x. Stokes on the rectangle gives

    2 pi q = integral_R f dx dy + K2 - K1.                        (3)

The curvature of a non-descending rectangle connection alone is not the
Euler curvature of the glued bundle. Both seam terms in (3) matter.

For a frame change e_new=e_old R(gamma(x,y)),
a_new=a+d gamma, alpha_new=alpha+gamma_left-gamma_right and
beta_new=beta+gamma_bottom-gamma_top. The k_i and phi are invariant,
and the mixed corner differences cancel in (1). These statements are
restricted to consistently oriented frames; reflections change conventions.

## 3. An explicit abstract C2 collar extension

There is an abstract extension for these SO(2) data; one need not assume
that a previously prescribed collar has compatible jets. Set

    b(x)=beta(x)-(x/Lx) Delta alpha-2 pi q x/Lx,
    theta(x,y)=(x/Lx) alpha(y)+(y/Ly) b(x).

Equation (1) gives b(Lx)=b(0), even if derivatives at the endpoints differ.
Under the frame change by theta, the boundary transitions become

    J1_new=I,    J2_new(x)=R(2 pi q x/Lx).                         (4)

Extend alpha(y) and b(x) to real C2 functions on the line, for example by
their endpoint quadratic Taylor polynomials outside the closed intervals.
This matches value, first and second derivatives at each endpoint; it
does not require b to have a periodic derivative. The same expression
defines a C2 extension of theta on all of R2. Write X=(Lx,0), Y=(0,Ly).
In the original rectangle frame define deck transition angles

    g1(z)=theta(z+X)-theta(z),
    g2(z)=2 pi q x/Lx+theta(z+Y)-theta(z).

They restrict to alpha on x=0 and beta on y=0. At every z,

    g2(z+X)+g1(z)-g1(z+Y)-g2(z)=2 pi q,

so their rotations satisfy the exact cocycle on a WHOLE neighborhood,
indeed globally. The translations and these fibre rotations define a C2
oriented metric bundle on the torus. This is a concrete abstract collar
construction, with the given edge values intact.

The compatible connection in the canonical frame is

    a_can=-(2 pi q y/(Lx Ly)) dx.

In the original frame use a_star=a_can-d theta. Its C1 coefficients satisfy
d g_i+a_star(z+shift_i)-a_star(z)=0 as full one-forms, so the connection
descends under both deck transformations. The exact differential drops
out of its curvature:

    Omega_star=G (2 pi q/(Lx Ly)) dx wedge dy,
    e = integral Omega_star_12/(2 pi) = -q.                      (5)

Here the sign follows the declared coefficient convention G_12=-1 and
base orientation. It agrees with q007's compatible canonical family.
For smooth edge data choose smooth extensions; for C2 data this is a C2
bundle with C1 connection, sufficient for the displayed curvature identity.

This proves existence of AN abstract extension and compatible connection.
It does not preserve a prescribed physical collar, projector embedding,
Kato connection, Hamiltonian covariance, or physical translation. No small
bound on a_star-a has been proved. A fixed original connection descends
only if it obeys the corresponding full transition law on overlaps (and
the required regularity there), not merely its tangential edge restriction.

In particular, a discrepancy that is constant through second order at a
point need not be constant nearby: R(s^3) has the identity's 2-jet at zero
but is not the identity on any neighborhood. Finite jet matching does not
prove an exact collar cocycle. This qualifies the sufficient-collar phrase
in Claude's comment 5791262731; it does not affect the q007 edge repair.

## 4. Comparing two edge systems: the joint corner condition

First identify both systems' fibres over the entire rectangle by declared
continuous oriented isometries. Two cutoffs with different ambient spaces
cannot be subtracted without this identification. Gauge choices must be
tracked in those identifications, not fitted independently at each sample.

For two already corner-consistent systems J_i^a,J_i^b, suppose on each
whole edge sup ||J_i^a-J_i^b||<2. The relative rotations have unique
principal lifts gamma_i in (-pi,pi). Then

    q_b-q_a = [Delta gamma2-Delta gamma1]/(2 pi).                 (6)

The numerator is an integer multiple of 2 pi, but need NOT be zero.
This is different from q007's criterion for already CLOSED individual
transition loops, where each principal relative lift has equal endpoints.

Explicit counterexample with reference J1^a=J2^a=I:

    alpha_b(y)=0.9 pi-1.8 pi y/Ly,
    beta_b(x)=-0.1 pi+0.2 pi x/Lx.

Both corner products equal R(pi)=R(-pi), and q_b=1, while q_a=0.
The continuous maximum relative distances are

    eta1=2 sin(0.45 pi)<2,    eta2=2 sin(0.05 pi)<2.

Each individual edge passes the distance-2 screen. Scaling both principal
angles by t produces a corner discrepancy R(2 pi t); thus the naive
short-arc interpolation fails the corner equation for 0<t<1.

A sufficient joint test is Delta gamma2-Delta gamma1=0 exactly. The
interpolation J_i(t)=J_i^a R(t gamma_i) then preserves corners for all t
and is a homotopy of the edge gluing systems. A conservative sufficient
norm-only version uses uniform bounds eta_i<2 and

    rho_i=2 asin(eta_i/2),    rho1+rho2<pi.                       (7)

The absolute numerator in (6) is at most 2(rho1+rho2)<2 pi. Its
integrality forces zero. In particular eta1,eta2<sqrt(2) suffices.
Larger bounds can also be accepted when the joint lifted corner condition
is certified directly. This criterion selects a relative finite class,
not an infinite-cutoff or physical reference class.

## 5. A conditional certification contract

The algebra is exact; ordinary floating-point observations do not certify
its hypotheses. Before accepting a physical q require:

1. Continuous oriented edge data, positive uniform overlap invertibility,
   and an exact specified corner repair or exact corner consistency.
2. A justified physical reference and explicit common-fibre identification
   for comparisons. Apply the closed-loop theorem only to actual loops;
   otherwise apply the joint condition (6) or sufficient bound (7).
3. A correct continuous lift of phi. A sufficient adjacent sampling guard
   is a certified variation bound V_j plus the two endpoint phase error
   bounds strictly below pi, with the chosen initial lift. This is an
   interval-path unwrapping condition and does not assume W is periodic.
4. A certified error bound for K1. If |k1'|<=L_j on interval length h_j,
   midpoint quadrature has error <=sum L_j h_j^2/4. Add sum h_j eps_j
   for certified point-evaluation errors eps_j. This follows by integrating
   |k1(y)-k1(midpoint)|<=L_j|y-midpoint|.
5. An enclosure z in [z_hat-E,z_hat+E] for z=Delta phi-K1, including
   endpoint phase, quadrature and arithmetic errors. Require exactly one
   multiple of 2 pi in this enclosure. With the integer theorem's
   hypotheses established, that integer is q. Zero or multiple candidates
   must be refused. Directed arithmetic must also enclose pi and all
   bound calculations; the present script is NOT such an implementation.

The diagnostic tests this last decision using rational numbers in units
of 2 pi, so its interval decisions are exact for the declared synthetic
inputs. It does not turn floating-point geometric checks into enclosures.

## 6. Fixed validation and next scope

The preregistered fixed cases exercise: a hidden left/right integer,
noninteger raw phase changes, connection and frame independence, mixed
seams, an abstract collar with deliberately mismatched boundary jets,
full one-form transition compatibility, the two-edge distance counterexample,
its joint replacement, the finite-jet false inference, and exact rational
accept/refuse decisions. There is no parameter search or physical sweep.

Next partner audit: check all signs in (2)-(5), the global deck cocycle,
the distinction between constructed and prescribed collars, and (6)-(7).
The physical work remains gated on declared model/fibres/real structure,
reference identifications, uniform isolation and boundary estimates,
certified arithmetic, and a finite-to-infinite comparison. Fable's v078
corrections remain owned by the other conversation.

## Primary-source context (accessed 2026-09-23)

Hatcher, Vector Bundles and K-Theory v2.2 (November 2017), sections 1.2
and 3.2, supplies background on clutching and oriented Euler classes:
https://pi.math.cornell.edu/~hatcher/VBKT/VB.pdf

Philippe Mathieu, Connections, curvatures and characteristic classes
(September 2019), sections 1 and 4, supplies background on metric
connections and Pfaffian/Euler normalization:
https://academicweb.nd.edu/~pmnev/f19/Chern-Weil.pdf
That source uses its own connection and area-form sign conventions; the
coefficient convention and sign calculation in (5) are stated explicitly.
The formulas and constructions above are explicit derivations for review,
not quotations, novelty claims or formal machine-checked proofs.
