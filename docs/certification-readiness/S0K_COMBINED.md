# S0k: curved partial-shift repair and relative composition

Additive response to Claude source 5806020671 and Codex review 5806035978.
This combines Q1 and Q2 in one analytic synthetic fixture. No physical model
is evaluated. Previous packets are unchanged and pinned by SHA-256.

## Exact domain and frame

For d=128 or 160, x,y in [0,1], define c(x)=1-1/d-x/(2d),
s=sqrt(1-c^2), phi=2*pi*y. The oriented frame F has columns
(c cos(phi),c sin(phi),-s) and (-sin(phi),cos(phi),0).
Its normal is n=(s cos(phi),s sin(phi),c). The measured frame is
K=F R(-2*pi*c(x)y). As in S0j, F^T F_x=0 and F^T F_y=2*pi*c J.
Thus K is the bottom-then-vertical Kato frame, A_y=0 and A_x=pi*y/d J.
The curvature and total flux are -pi/d. These are exact analytic premises,
not conclusions inferred from finite point checks. The orientation guard
checks both measured seam-end frames against n before computing overlaps.
A reflected-frame control is refused. Normal and ambient shift formulas do
not call the measured frame, although they share declared scalar parameters.

## Actual rank-deficient ambient maps and two deficits

Let D=diag(1,1,0). First construct the orthogonal ambient map U:
on edge 1 use Rz(phi) Ry(theta(1)-theta(0)) Rz(-phi), where cos(theta)=c;
on edge 2 use Rodrigues(n(x,0),(2*pi*w+epsilon)x), epsilon=1/4.
The code evaluates theta differences through sine/cosine algebra.
Then use S=D U on both edges. This is an actual rank-two partial isometry,
not an overlap supplied directly to the certifier. U takes the source plane
to the target plane, with the declared in-plane edge-2 rotation.

In the target F basis, F^T D F=diag(c_target^2,1), a positive matrix.
Consequently polar(K_target^T S K_source) has the same rotation as for U,
but its singular values are c_target^2 and 1. Uniformly over each edge,
s_min >= c(1)^2 >= 19/20 for the two retained d values. The d=8 control
fails this gate before integer extraction. No sampled singular value is
promoted to a uniform bound.

For M=K_target^T S K_source, compute both sides of

    I-M^T M = K_source^T(I-S^T S)K_source
              + ((I-P_target)S K_source)^T ((I-P_target)S K_source).

The two traces are exactly 1-c_target^2 and c_target^2(1-c_target^2).
Both are strictly positive, throughout these edge families. Their sum is
1-c_target^4. The code independently computes the two matrix terms and
retains their positive origin traces and an interval residual consistency
check. Domain-wide validity follows from the displayed exact reduction.

## Principal repair, signs and lift guard

The polar seams are J1(y)=R(-pi*y/d) and
J2(x)=R(2*pi*c(x)+(2*pi*w+epsilon)x).
Actual computed corners A=J2(1)J1(0), B=J1(1)J2(0) give
delta=Arg(A^T B)=-epsilon. The inherited charged corner branch gate is
applied to these actual matrices, with charge 1/128. Delta excludes zero.
Repair is J2_hat(x)=J2(x)R(delta*chi(x)), chi=10x^3-15x^4+6x^5.
The positive sign is enforced structurally before arithmetic. The
wrong-repair control refuses; it is not treated as a near-integer result.

The exact repaired corner closes because delta=-epsilon. The phase totals
are Delta alpha=-pi/d and Delta beta_hat=2*pi*w-pi/d, hence q=w.
The implementation sums 64 computed increments per edge and extracts the
unique integer enclosed, without consulting its expected-q oracle.
Uniform phase speed is pi/d on edge 1 and at most
abs(2*pi*w-pi/d+epsilon)+(15/8)*abs(delta) on repaired edge 2.
Each cell's variation is guarded below pi/2. Nonzero curvature, both
partial-shift losses, nonzero repair and both phase lifts are now composed.

## Independent relative comparison

Compare d=128 and d=160 under Q=polar(K_b^T K_a) computed from their
actual frames. The unrotated overlap has diagonal entries cos(theta_a-
theta_b),1. Since all c,s are positive, its least singular value is at
least c_a(1)c_b(1)>1/2 throughout the rectangle. The polar Q is
R(2*pi*(c_b-c_a)y). For equal w and epsilon, pulling back b's repaired
seams by Q gives a's repaired seams exactly. This algebra is a cross-check;
the code still performs its separate interval screen over 1024 cells per
edge and requires Frobenius distance <=1. Both individual integers are
retained before comparison. Opposite windings refuse that screen naturally.
The inherited combiner treats certified-screen/unequal-integer states as
execution errors; its injection control remains in S0i, not rerun here.

## Frozen evidence and boundary

Eight expected outcomes: q=-1,0,+1; orientation, repair-sign and singular-
gate refusals; equal-class certification and unequal-class screen refusal.
One thread, 128-bit arithmetic, fixed cell counts and no automatic retries.
The runner records environment, source snapshot, dependency hashes,
resources and a completion manifest. verify.py checks integer containment,
nonzero repair, both deficits and relative records, plus tamper controls.

This remains analytic geometry with arithmetic consistency checks and an
interval relative screen. It does not close Q3/P3: realistic-width geometric
integer extraction, general numerical Kato transport, uniform numerical
projector/derivative coverage and representative conditioning remain open.
These analytic shifts are not physical lattice translations. Physical
S1-S4, physical class assignment and cutoff agreement remain uncertified.
