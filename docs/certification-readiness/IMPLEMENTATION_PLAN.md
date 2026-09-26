# Bounded implementation design FC49-77-PLAN-001

Date: 2026-09-23. DESIGN_REVIEW_PENDING / NOT_IMPLEMENTED / NOT_RUN.
This is the proposed implementation contract for
[FC49-77-K-Bm025-v2](CASE.md), not an executable certificate.
[PLAN.json](PLAN.json) fixes limits. No runtime or successful-certification
claim is made; the tight declared gaps may exhaust these limits.

## 1. Dependency lock and first deliverable

Target CPython 3.12.14 and python-flint==0.9.0. Before accepting any
implementation, S0 must retain the exact package artifact, SHA-256,
native FLINT version/build, platform/ABI, Python build and a locked
dependency manifest. Those native-build fields are currently unresolved;
do not invent them or promote this packet to executable readiness.
The public package version is a design choice, not evidence of a locally
installed validated backend.

Use Arb/acb ball arithmetic with precision 128, then 256, then 512 bits.
Inputs are exact rationals/integers; decimal model constants never pass
through Python float. Elementary functions use their certified ball
operations. Export outward dyadic/rational bounds with explicit units.
A failed comparison is not necessarily a proved opposite comparison.

S0 implements only the arithmetic adapter, exact endpoint serialization,
norm bounds, interval LDL inertia, residual-certified inverse, 2x2 polar,
contour remainder and validated linear-ODE primitives. Its fixed synthetic
set must include repeated eigenvalues inside a selected pair, an external
gap closure, a nonzero matrix with a zero leading LDL pivot, a nearly
singular Gram matrix, branch-cut arcs and a rotating projector with
known transport. These exercise refusal and inconclusive paths as well
as success. Use at most 12 matrices (dimension <=8) and four ODE examples.
Analytic known results, not agreement with a second floating solver, are
the references. Passing tests is necessary evidence for code review,
not a proof of every numerical primitive.

The next deliverable is that small S0 implementation and its retained
results for independent review. No physical model is evaluated in S0.
S1-S4 below describe the bounded intended continuation; their code must
be reviewed before use. There is no automatic physical run from accepting
this design document.

## 2. Independent exact-model assembly and source bridge (S1)

Construct the two real symmetric affine matrices
H_a(x,y)=H_a0+x H_ax+y H_ay and H_b likewise from the pinned archive
formulas, in the declared realify coordinates and explicit index lists.
Enclose the real geometry inverses, trigonometric constants, reciprocal
vectors and all scalar coefficients. Prove geometry denominators nonzero.
Store a term-by-term map to the archived constructor, static terms,
kinetic terms and sine-sigma_z harmonic.

Construct symmetric counterparts from the same mathematical coefficient;
do not discard a numerical imaginary part to establish reality.
Retain coefficient enclosures and their arithmetic radius contributions.
For the whole rectangle, the sum of operator-norm arithmetic radii must
be <=1e-8 meV. Domain variation of x,y is a separate spectral term,
not assembly roundoff. If that target remains unresolved at 512 bits,
return INCONCLUSIVE rather than weakening it.

Check algebraically that the embedded principal submatrix is H_a and
that the inclusion/shift real-basis identities use the declared ordering.
The coefficients are index-local; the source coupling stencil is covered
by the chosen shell. No full finite-shift covariance is assumed.

A later diagnostic bridge may compare the archived floating assembler
at exactly (0,0), (1,0), (0,1), for both declared bases. Record its actual
binary inputs and errors separately. Agreement at these points is only
a diagnostic; the formula mapping and outward assembly bounds provide
the mathematical bridge. No such evaluation occurs in this packet.

## 3. Ordered spectral enclosures without a simple-eigenvalue assumption (S1)

At a rational cell center, bound ||H|| by a certified row-sum or Frobenius
upper bound M and choose an exact rational B>M+1. The spectrum lies
strictly inside (-B,B). For any rational shift s, compute an unpivoted
interval LDL^T factorization of H-sI. Only accept it if all pivot balls
exclude zero and the interval operations enclose the exact recurrence.
Then Sylvester inertia gives the exact number N(s) of eigenvalues below
s from the certified negative pivot count. No approximate eigensolver
order, unverified Cholesky sign or determinant rounding is used.

Failure of a leading pivot to exclude zero is inconclusive for that
shift, even when H-sI itself is nonsingular. For each bisection round try
the midpoint, then the 3/8 and 5/8 positions of the current bracket in
that fixed order, with the three precision levels. If none certifies,
the cell remains unresolved. This intentionally conservative method has
no guaranteed success or practical cost claim.

Enclose each zero-based eigenvalue lambda_j by a bracket [a_j,b_j] with
N(a_j)<=j and N(b_j)>=j+1. Only four indices are needed for a selected
pair [l,h]: l-1,l,h,h+1. Repeated eigenvalues inside the pair are allowed.
A spectral budget cap is global, including unsuccessful precision retries.

For a cell of half-widths dx,dy, a certified
r=||H_x|| dx+||H_y|| dy bounds variation from its center by Weyl's theorem.
Lower bounds for the two external gaps throughout the cell are

a_l-b_(l-1)-2r, and a_(h+1)-b_h-2r.

Require both >=1e-5 meV. All center enclosures already include arithmetic
error. Keep a closed-cell covering of the whole rectangle; overlapping
cell edges must not leave holes. Subdivide unresolved cells breadth first
in fixed dyadic order until success or a declared cap. A sufficient
cell bound failing is not a proof that the exact gap fails.

## 4. Projectors, derivatives and identification (S2; bounded calls later)

For each accepted domain cell choose a rational rectangular contour
whose vertical sides lie in the two certified external spectral gaps
and whose horizontal sides have nonzero rational imaginary heights.
It encloses precisely the selected pair for the whole cell.
Use the Riesz formula P=(1/(2pi i)) integral (zI-H)^(-1) dz.

Every inverse must be certified. With a dyadic approximate inverse B,
certify eta=||I-B(zI-H)||<1; then the exact inverse differs from B by
at most eta||B||/(1-eta). The approximation can come from a heuristic,
but only the outward residual inequality licenses its use.
Retain the residual and bound for every contour interval.

Use a rigorous derivative remainder for each straight contour segment.
For a segment of length h and integrand Lipschitz bound L, midpoint
integration error is at most L h²/4. For the resolvent,
||dR/ds||<=||R||² under unit-speed parameterization. Gap/imaginary-distance
bounds give a resolvent bound along the entire segment, not just its
midpoint. Sum quadrature and ball errors and divide by an outward
enclosure of 2pi. Corner junctions are separate segment endpoints.

First and second parameter derivatives follow by differentiating the
resolvent: partial_i R=R H_i R and
partial_ij R=R H_i R H_j R+R H_j R H_i R.
The assembly is affine. Bound their contour remainders with the same
validated differentiation and segment method. These enclose derivatives
of the exact spectral projector, rather than derivatives of rounded
eigenvectors. Local contours describe the same globally ordered pair.

Use the declared fixed pivot for F_a0, and certify Q(p0) to define F_b0.
On any local rank-two frame, compute the polar through the SPD Gram
matrix G. For 2x2 positive G,

sqrt(G)=(G+sqrt(det G) I)/sqrt(tr G+2sqrt(det G)).

Certify its denominators and use a validated inverse. This preserves the
unique positive polar convention without arbitrary eigenvector signs.

For whole-domain Q and seam bounds use direct verified Gram matrices,
or the sufficient residual bounds in CASE.md section 4. The latter
require cross-spectrum separation, a Frobenius residual bound and, for
partial shifts, deletion loss. Merely certifying two individual gaps
does not certify cross-spectrum separation. Failure of a residual bound
does not override a direct certified overlap or prove a violated gate.

## 5. Whole-parameter Kato transport (S3)

Integrate the exact linear equation F'=A F with A=[partial P,P].
The bottom path uses A_x; each vertical path uses A_y.
Enclose all x in each parameter strip during vertical integration,
including an enclosure of the bottom transported initial frame for
every x in that strip. Retain dependence conservatively by interval
inclusion; independent sample trajectories do not cover a strip.

For a time interval [0,h] and parameter strip X, obtain a rigorous
coefficient enclosure A(X,[0,h]) from projector derivative bounds.
Find a tube Z containing the Picard image
F_start(X)+[0,h] A(X,[0,h]) Z strictly in its interior, and certify
h sup||A||<=1/4. The enclosure must include the complete initial set.
This self-map and contraction bound validate the tube and give endpoint
F_end(X) inside F_start(X)+h A(X,[0,h]) Z. Use outward interval inclusion,
at most eight deterministic tube inflations, then halve the step.

This basic interval method can wrap excessively and stop. It does not
promise the efficiency of a Taylor-model or Lohner implementation.
Do not silently substitute such an algorithm; retain a reviewed amendment
if a different enclosure strategy is needed. Parameter derivatives needed
for edge variation must also be certified, through differentiated transport
equations (including the x-dependent bottom initial data), or a rigorously
enclosed complete phase arc on each strip. Neither finite differences nor
mesh agreement is a derivative bound.

Frames are the exact orthonormal Kato solutions. Rounded arrays enclose
them; any numerical reorthogonalization must preserve an explicit error
bridge to those same solutions and cannot redefine the declared gauge.

## 6. Seams, exact repair and both phase lifts (S4)

Evaluate both polar seam families in the validated frames; certify their
restricted singular values and positive orientation. Certify each
unrepaired corner discrepancy <=1, then enclose the exact principal delta
and the exact R_rep defined in CASE.md. A midpoint substitute is prohibited.
Positive polars, isolated projectors and the endpoint-flat polynomial
supply the declared smoothness conditionally on their margins.

Compute the unrepaired J1 angle alpha and repaired J2 angle beta. Use
certified atan2 arcs, splitting coordinate charts if required; a principal
branch crossing is not itself a discontinuity of the circle-valued map.
For every complete parameter interval certify a single lift continuation
whose variation plus endpoint enclosure errors is <=pi/2.
A continuous-arc enclosure or a certified derivative bound may establish
this; discrete endpoint closeness alone may not. Keep the integer 2pi
offset on every lifted interval.

The vertical Kato gauge gives q=(Delta beta-Delta alpha)/(2pi), with no
separate defect quadrature. Enclose both increments, exact repair,
transport errors and pi together. Require half-width <=1/8 and a unique
integer candidate after the individual exact gluing prerequisites hold.
Do not treat narrow numerics as evidence of integrality.

Then certify Q over the whole rectangle and the two complete repaired-edge
comparison bounds, under this one identification, for the relative result.
Preserve valid individual integers when only this sufficient comparison
is unresolved. If all joint gates certify but integers disagree, terminate
EXECUTION_ERROR and retain the contradictory witnesses.

## 7. Fixed work limits and result semantics

| Stage | Wall cap | Main work caps |
|---|---:|---|
| S0 primitives | 120 s | 12 synthetic matrices, dimension <=8; 4 ODE examples |
| S1 assembly/isolation | 600 s | 512 attempted cells per cutoff, depth 8; 8192 total inertia factorizations; 64 bisection rounds/index |
| S2 projector/basepoint | 600 s | 1024 total projector queries, 2048 contour segments/query |
| S3 frames/overlaps | 600 s | 512 x strips/cutoff, 8192 transport attempts/cutoff, minimum step 1/65536 |
| S4 repair/lifts/comparison | 300 s | 4096 edge intervals/cutoff, depth 12 |

The cumulative cap is 2220 wall seconds, resident memory 2 GiB, one worker,
one case, and no parameter sweep. Native calls require a subprocess
watchdog, so an individual factorization cannot evade a wall cap.
Counters include failed attempts and precision retries. Shared primitive
caps continue to apply when used in later stages. The first reached cap
stops the affected run with INCONCLUSIVE/BUDGET and a checkpoint.
No silent restart, precision increase, threshold change, extra cutoff
or revised pivot follows an unfavorable outcome.

A mathematically certified violation gives the appropriate refusal status;
failure to establish an inequality is inconclusive. Undefined exact
geometry refuses the model hypothesis. Invalid enclosures, inconsistent
source/build locks or contradictions in proved conditions are
EXECUTION_ERROR. An unavailable runtime is an execution blocker, not
evidence that the model fails.

## 8. Retained evidence and audit request

An immutable run directory must bind CASE.json, PLAN.json, implementation
SHA, all input/source hashes and environment artifacts. Retain exact
endpoint serialization, coefficient enclosures, geometry denominator
proofs, accepted/unresolved domain cells, all inertia shifts and signs,
projector contours/remainders, base frames and transport tubes, deletion
and leakage bounds, seam signs, both exact-delta enclosures, both complete
lift chains, integer intervals and the individual/relative status vector.
Logs record commands, precision, resource counters and reason codes.
No overwrite of an earlier attempt; no rounded printed value serves as
a certificate endpoint.

Review requested: fixed-pivot convention and status semantics; the
Frobenius/deletion-loss qualifications; the inertia bracketing and cell
coverage; contour and whole-parameter transport enclosures; both-lift
error accounting; and whether these budgets and evidence records define
a genuinely bounded first implementation. Native dependency locking and
all numerical primitives remain unimplemented.

Backend primary references (checked 2026-09-23):
- [python-flint official repository and releases](https://github.com/flintlib/python-flint)
- [Arb scalar construction and bounds](https://python-flint.readthedocs.io/en/stable/arb.html)
- [Ball arithmetic and comparison semantics](https://python-flint.readthedocs.io/en/stable/general.html)

These references document the backend interface. The proposed certification
chain above requires its own implementation, mathematical audit and
retained execution evidence.
