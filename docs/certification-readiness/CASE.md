# Fixed declaration FC49-77-K-Bm025-v2

Date: 2026-09-23. Status: DECLARED_UNEXECUTED; revision/design review pending.
No gap, frame, seam or class outcome has been measured or certified.
[CASE.json](CASE.json) is the machine-readable declaration.
[DECLARATION_CHECKS.json](DECLARATION_CHECKS.json) records static integrity
and finite-set checks only.

This version explicitly supersedes unexecuted v1 at
`bb159404c1286387b1e0f2125b295b7d586042a9`, following Claude source comment
[5792152685](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5792152685)
and Codex review [5289043968](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5289043968).
It changes the orientation pivot convention and arithmetic design before
any outcome is observed, clarifies integer extraction, and separates
individual from relative outcomes. The model, bases, band pairs, seams,
identification and previous numerical targets are unchanged.

## 1. Exact model and finite systems

Use the archived real, massless K-valley model at B="-0.25", with all
constructor constants in CASE.json interpreted as exact rationals and the
sine-sigma_z harmonic on all three directions. Trigonometric and geometric
values are mathematical functions of those inputs, not stored NumPy
approximations. The archived formulas are the source reference; a later
floating execution needs an error bridge to this exact model.

The domain is the whole fractional rectangle [0,1]² with k=x G1+y G2,
base orientation dx wedge dy, and increasing coordinate parameters on both
edge pairs. This is a proposed abstract finite gluing problem, not the
migration consumer's local-circle calculation.

Lambda_a is the ordered 49-vector RUN/BASIS.json list. With
D={(0,0),(1,0),(-1,0),(0,1),(0,-1),(-1,1),(1,-1)}, define
Lambda_b=sort_lex(Lambda_a+D), removing duplicates. Its 77 indices form one
neighbor shell, not an N=6 radial cutoff. Both explicit lists and their
canonical hashes are in CASE.json. Both constructors receive index_set;
the unchanged N=4 argument must not regenerate either list.

The real dimensions are 196 and 308. The chosen zero-based ordered
eigenvalue pairs are [97,98] and [153,154]. These candidate clusters are
not asserted to be the same physical bands. Certify each pair's rank,
ordering and external gaps without changing its indices.

The ambient inclusion is the exact isometry
e_(2*49*layer+2*i+s) -> e_(2*77*layer+2*j(i)+s),
where j preserves the reciprocal index and s is the adjacent component
in the fixed realify basis. CASE.json retains all 196 target row indices.
It intertwines the declared ambient real structures. It does not by
itself identify spectral fibres.

## 2. Projectors, fixed orientation and identification

Let P_a,P_b be the exact real rank-two projectors for those pairs.
Certify external gaps >=1e-5 meV on the whole closed rectangle.
Internal degeneracy within the pair is allowed. The affine Hamiltonian
and gap hypotheses give smooth pair projectors; that conclusion is
conditional on geometry being well-defined and the gaps being certified.

At p0=(0,0), use the two real coordinates [48,49] in system a: layer 0,
reciprocal index (0,0), position 24 in the retained list. Set
v=P_a(p0)e_48, w=P_a(p0)e_49 and G=[v,w]^T[v,w].
Require det G >= 1e-12, then use ordered Gram-Schmidt with positive
normalizing roots to define F_a0. This threshold is a newly declared
dimensionless convention target, not an expected observed value.
There is no pivot search or fallback. A certified failure refuses this
orientation convention; an unresolved interval is inconclusive. Neither
implies absence of a rank-two bundle. V1's lexicographic rule is removed:
ordinary intervals cannot generally certify all preceding determinants
to be exactly zero.

Define T=P_b iota P_a restricted to E_a, and Q=polar(T).
Require its restricted smallest singular value >=1/2 over the rectangle.
Set F_b0=Q(p0)F_a0. Thus b's declared orientation depends on certifying Q
at p0; if that cannot be established, q_b is unavailable in this convention.

For each system transport its base frame first along (0,0)->(x,0),
then vertically to (x,y), by F'=[P',P]F. This exact Kato path family
defines continuous oriented rectangle frames. It asserts neither path
independence nor a periodic torus frame. Q's continuous invertibility
and its positive orientation at p0 ensure its orientation throughout
the connected rectangle. Full-domain Q certification remains a separate
gate even when its basepoint value is known.

## 3. Partial seams, corner repair and comparison

Use the archived valley +1 shifts d1=(-1,0), d2=(0,-1).
They represent k->k+G_i with index n->n-e_i in infinite indexing, but
their finite restrictions are partial shifts; finite covariance is not
assumed. Define
J1(y)=polar(P(1,y) S_d1 P(0,y)) on E(0,y), and
J2(x)=polar(P(x,1) S_d2 P(x,0)) on E(x,0).

For each system separately:

1. Certify restricted seam singular values >=19/20 along both complete edges.
2. In the continuous oriented rectangle frames, certify positive seam
   determinant. Raw independently chosen eigenframe signs are not this
   gate. A certified negative determinant refuses the chosen oriented
   hypothesis. Before compatible O(2) gluing exists, it does not establish
   a global nonorientable torus bundle.
3. Form A=J2(1)J1(0), B=J1(1)J2(0), and certify ||A-B||_2<=1<2.
   Define the exact principal delta=Arg(A^T B) in (-pi,pi).
   With chi(x)=10x³-15x⁴+6x⁵, set
   R_rep(x)=exp(delta chi(x) I_source) and
   J2_repaired(x)=J2(x) R_rep(x); leave J1 unchanged.
   I_source is the positive 90-degree structure [[0,-1],[1,0]]
   on the oriented source plane, not an identity matrix.

The exact delta defines the repaired system. An interval encloses that
delta; replacing it by its midpoint defines a different system and does
not satisfy the exact corner identity. The declared principal construction
and C² endpoint-flat collar are those of q007/q008.

Only after each individual repair is valid, compare
Q(target)^T J_i^b Q(source) with J_i^a along the complete repaired edges.
Require each uniform operator-norm distance <=1. The resulting angular
bounds rho_i<=pi/3 satisfy rho1+rho2<=2pi/3<pi, giving q008's joint
sufficient condition. Endpoint agreement alone is inadequate.
Failure of this conservative screen is inconclusive about class equality;
do not substitute a new reference, threshold or homotopy after observing it.

## 4. Residual bounds: norms and lost components

These are optional sufficient routes for a future implementation.
They are not retained numerical evidence.

For an orthonormal selected source frame F0, A0=F0^T H0 F0 and target
projector P1, define R=(I-P1)S F0. The exact Sylvester identity is

H1_perp R - R A0 = Bperp,
Bperp=(I-P1)(H1 S-S H0)F0.

A certified separation delta_cross between spec(A0) and the whole target
complement gives ||R||_2 <= ||R||_F <= ||Bperp||_F/delta_cross.
The safe general bound uses a Frobenius residual. An operator-norm
residual with the same constant is not assumed for arbitrary two-sided
spectra. Same-system gap bounds are not automatically cross-system
spectral separation bounds.

For the nested inclusion, index-local coefficients and the shared
coupling stencil give iota^T H_b iota=H_a for the exact source formulas.
This identity must also be checked in the independent assembly bridge.
Since iota is an isometry, smin(P_b iota F_a)^2 >=1-r² when r bounds
||(I-P_b)iota F_a||_2. Thus r²<=3/4 suffices for the identification target.

For a partial seam shift let L=F0^T(I-S^T S)F0 and M=P1 S F0. Exactly,

M^T M = I-L-R^T R.

If ell>=||L||_2 and r>=||R||_2, then smin(M)^2>=1-ell-r².
The seam target follows from ell+r²<=39/400.
Off-target residual control alone is insufficient: deletion loss L must
also be bounded. Covariance on a surviving index window is not covariance
of the entire truncated Hamiltonian. A failed sufficient bound alone
cannot be reported as a failed exact overlap hypothesis.

## 5. Arithmetic and integer extraction

Use operator norms with proved Frobenius upper bounds where appropriate.
The assembly target is <=1e-8 meV per system; spectral and projector
certificates must include assembly error, not merely meet that target.

The proposed backend is python-flint 0.9.0 with Arb outward ball arithmetic.
Decimal inputs enter as exact rationals, never binary floats. Export
certified dyadic/rational endpoints, including pi and elementary-function
enclosures. The native build and artifact hashes remain to be locked in
stage S0; no backend is implemented in this packet.
[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) specifies the methods,
[PLAN.json](PLAN.json) their finite budgets. Rounded diagnostics do not
replace outward enclosures.

Let alpha be a continuous angle lift of J1 in the declared frames, and
beta a continuous lift of repaired J2. The vertical Kato equation gives
F^T partial_y F=0: the commutator maps the selected plane into its
orthogonal complement, so its compression vanishes. Hence q008's
K1=Delta alpha and phi=beta, giving

q=(Delta beta-Delta alpha)/(2pi).

No separate seam-connection quadrature is needed in this gauge. Both
complete lifts must still be certified, including the repair angle and
validated transport errors. The vertical transport is parameterized by
all x; checking isolated vertical paths is insufficient.
Each accepted phase step must bound variation plus endpoint errors by
pi/2. Each final q interval must have half-width <=1/8 and exactly one
integer candidate. Integrality is invoked only after continuous oriented
repaired gluing has been established.

## 6. Outcomes and execution boundary

Retain a result vector (q_a, q_b, relative), not one destructive status.
Possible individual statuses are CERTIFIED_FINITE_CLASS,
REFUSED_HYPOTHESIS, REFUSED_ORIENTATION_CONVENTION, INCONCLUSIVE and
EXECUTION_ERROR; all are currently NOT_RUN with null integer fields.

- A proved violation of an exact hypothesis is a refusal; inability to
  prove it is INCONCLUSIVE, with the unresolved enclosure retained.
- Budget exhaustion is INCONCLUSIVE/BUDGET, not a hypothesis failure.
- Individually certified integers remain valid if a later full-domain Q
  or relative sufficient screen is inconclusive. Their own orientation
  prerequisites, including Q(p0) for b, must already hold.
- CERTIFIED_RELATIVE_FINITE_CLASS requires all joint gates and equal
  individually certified integers. Unequal integers with all joint gates
  certified imply EXECUTION_ERROR in the certification chain.
- A negative seam sign retains the local obstruction evidence without
  claiming a global bundle exists.

This v2/design packet awaits independent review. The next implementation
slice is S0 arithmetic and synthetic validation, followed by code review
before physical execution. No archived module was imported, Hamiltonian
assembled, eigensolver run or sweep performed here. No physical or
infinite-cutoff result follows from the declaration. The v078 owner and
frozen q001-q008 work are unchanged.
