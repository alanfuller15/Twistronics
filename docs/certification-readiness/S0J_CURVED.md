# S0j: independent ambient sewing and curved analytic transport

This additive synthetic packet addresses review 5805883761 (S0i). It defines
ambient sewing without calling the measured frame, and exercises nonzero
curvature and a concrete change in transport order. It makes no physical claim.
The frozen nine jobs run at 128 bits, one thread, with no retries. The environment,
source snapshots, dependency hashes and complete record manifest are retained.

## Independent Rodrigues sewing

Write [n]_cross v = n cross v and

    Rot(n,f) = cos(f) I + sin(f) [n]_cross + (1-cos(f)) n n^T.

For the inherited flat fixture, t=1/d, c=(1-t^2)/(1+t^2),
s=2t/(1+t^2), phi=x/4+y/2+xy/4, and
n=(s cos(phi), s sin(phi), c). The new sewing module constructs n and Rot
directly from coordinates. It does not import or call a frame constructor.
The edge-2 map is D Rot(n, (2*pi*w+1/4) x), D=diag(1,1,0).
Edge 1 uses D. The measured oriented frame has column cross product n, so
Rot(n,f) K = K R(f); this is an analytic reduction, not a shared call.
The singular values and Frobenius norm diagnostics of the untwisted overlap
are preserved by right multiplication by R(f). Its Gram matrix is conjugated,
not generally unchanged entry by entry. The inherited seam variation and
corner-repair proof therefore apply. Both integer signs are exercised.

A reflected measured frame is rejected against the independently defined
normal before any integer is accepted. Equal- and unequal-class comparisons
still use the actual repaired paths and separate joint screen. The algebraic
parameters remain shared by design; this is construction independence from
the frame implementation, not a claim of wholly independent software stacks.

## A curved rank-two plane over the unit rectangle

Let c(x)=3/4-x/4, s(x)=sqrt(1-c(x)^2), phi=2*pi*y, and use columns

    F1 = (c cos(phi), c sin(phi), -s),
    F2 = (-sin(phi), cos(phi), 0).

Their cross product is n=(s cos(phi),s sin(phi),c). Throughout the rectangle,
s>0, so all these expressions are smooth and F is an oriented orthonormal
frame. With J=[[0,-1],[1,0]], direct differentiation gives

    F^T F_x = 0,     F^T F_y = 2*pi*c(x) J.

For P=FF^T the bottom-then-vertical Kato frame is

    K(x,y)=F(x,y) R(-2*pi*c(x)*y).

Indeed K_y=[P_y,P]K, and its bottom initial data satisfy the horizontal Kato
equation K_x=[P_x,P]K at y=0. These are exact identities throughout the
rectangle, obtained by removing F^T F_y with the internal rotation. The
connection of K is A_x=(pi/2)y J, A_y=0, and its curvature coefficient is
-pi/2. Independently, -n dot (n_x cross n_y)=-pi/2. The flux is -pi/2.
This fractional flux alone is not an integer class.

Transport in the reverse order instead gives

    K_rev(x,y)=F(x,y) R(-2*pi*c(0)*y).

This is horizontal along each x-line after transport on the left boundary.
Its vertical connection coefficient is 2*pi*(c(x)-c(0))=-pi*x/2. Thus it
fails the declared vertical gauge at x=1/2. At (1,1),
K_rev^T K=R(pi/2). The packet measures this relative rotation and rejects
the wrong-order frame using its actual Kato residual. This is an analytic
path-order fixture, not a validated general-purpose ODE integrator.

## Ambient seams and the integer oracle

Define theta by cos(theta)=c. The edge-1 ambient shift is
Rz(phi) Ry(theta(1)-theta(0)) Rz(-phi), implemented through exact sine and
cosine formulas without evaluating theta. It takes F(0,y) to F(1,y).
The edge-2 shift is Rot(n(x,0),2*pi*w*x), for declared integer w.
Both are orthogonal and map the corresponding planes exactly; their
overlaps have singular values exactly one. Independent ambient overlap
evaluation and polar normalization therefore yield

    J1(y)=R(-pi*y/2),
    J2(x)=R(2*pi*c(x)+2*pi*w*x).

The actual corners A=J2(1)J1(0), B=J1(1)J2(0) are equal because w is an
integer. No repair is required in this curved fixture. Exact closure follows
from this identity; a small computed corner residual is only a consistency
check and is not used to infer equality.

The continuous phase increments are Delta alpha=-pi/2 and
Delta beta=2*pi*w-pi/2. Hence (Delta beta-Delta alpha)/(2*pi)=w.
The implementation sums polar-overlap phase increments over 64 cells and
extracts the unique integer contained in the resulting enclosure; it does
not return the input w. The analytic speed bound
2*pi*max(1/4,abs(w-1/4)) makes each cell variation less than pi/2 for the
frozen w=0,+1,-1 cases. Thus no unseen full turn is lost between nodes.

## Evidence boundary

The exact analytic identities above supply the domain-wide premises. The
point residual, normal-density and corner checks detect implementation
inconsistency; they do not numerically certify identities over the domain.
Fields ending in residual_F enclose computed norm upper bounds, not lower
bounds on a true defect. The wrong-order defect has the explicit nonzero
analytic coefficient given above.

This packet does not add a curved relative-class comparison, a general
two-dimensional transport solver, realistic-width geometric uncertainty,
or uniform physical spectral isolation. S0i's full-dimension point timings
remain point calibration, not a continuous-domain resource estimate.
Physical S1-S4, their budgets and any physical class remain uncertified.
