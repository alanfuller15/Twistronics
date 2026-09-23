# Fixed declaration FC49-77-K-Bm025-v1

Status: DECLARED_UNEXECUTED; independent specification review pending.
This is one finite-model feasibility case. No gap, orientation, seam,
class agreement or integer outcome has been measured or certified.
`CASE.json` is the machine-readable declaration. `DECLARATION_CHECKS.json`
checks its source bindings, finite sets and index maps only.

## Purpose and chosen inputs

Choose the archived real, massless K-valley model at B="-0.25", with the
exact decimal parameters in CASE.json and the sine-sigma_z harmonic.
This reuses one retained parameter value, while specifying a new whole-cell
problem. All decimal strings designate exact rational input values;
trigonometric constants and geometry are mathematical values to enclose,
not exact values of a prior NumPy evaluation. The archived formulas and
operation conventions are the model reference. Floating execution would
need an explicit error bridge to these values.

The rectangle is fractional [0,1] x [0,1], with base orientation dx wedge dy,
and k=x G1+y G2. Positive coordinate direction is the traversal convention
on both edges. This is a proposed full-cell finite gluing problem; it is
not the pair of local circles used by the migration consumer.

Lambda_a is the ordered 49-vector basis from the retained RUN/BASIS.json.
Define D={(0,0),(1,0),(-1,0),(0,1),(0,-1),(-1,1),(1,-1)} and
Lambda_b=sort_lex(Lambda_a+D). This is a deliberate one-neighbor-shell
enlargement with 77 reciprocal indices, not a radial N=6 cutoff or a
claim of cutoff convergence. Both explicit ordered lists and their hashes
are retained in CASE.json. Both constructors receive those lists via
index_set; N=4 remains only the archived constructor argument and must not
be used to regenerate either list.

Both layers contain the same index list with two sublattices at each index.
Thus dimensions are 196 and 308. Select zero-based ordered eigenvalue
indices [97,98] and [153,154], respectively. These are explicit candidate
clusters, not an assertion that two middle pairs represent the same
physical bands. Certify their rank, ordering and uniform external gaps
separately. Refuse this case if they fail; do not silently move the pair.

The ambient inclusion iota maps

```
e_(2*49*layer + 2*i + s) -> e_(2*77*layer + 2*j(i) + s),
```

where j(i) is the position of the same reciprocal index in Lambda_b.
The explicit 196-entry column-to-row map is retained. It preserves layers
and sublattice pairs and satisfies iota^T iota=I exactly. It is not a
selected-fibre identification until the projector condition below holds.

## Selected fibres, orientation and reference identification

Let P_a(k),P_b(k) be exact real rank-two spectral projectors for the
declared clusters in their fixed realify bases. First certify uniform
external gaps at least 1e-5 meV on the closed rectangle for each system.
The selected pair may have an internal degeneracy; no internal-gap gate
is imposed for this pair-projector problem.

Use p0=(0,0). In the real ambient coordinates for system a, choose the
lexicographically first i<j for which P_a(p0)e_i and P_a(p0)e_j are
independent. Ordered Gram-Schmidt with positive normalizing square roots
defines F_a0 and its orientation. This is a fixed conditional construction,
not a retained numerical frame. A future implementation must identify and
certify that pivot pair, retain its vectors, and refuse if it cannot prove
the selection; it must not orient each sample independently.

Propagate the oriented frame over the rectangle by exact Kato transport:
first along (0,0)->(x,0), then (x,0)->(x,y), with W'=[P',P]W.
This declared path family defines a continuous rectangle frame when the
regularity and gap hypotheses hold. It does not assert path independence
or periodicity, and does not assume a trivial torus bundle.

Define T(k)=P_b(k) iota P_a(k): E_a(k)->E_b(k). Require the smallest
singular value of this restricted map to be at least 1/2 everywhere on
the rectangle. The intended identification is its polar isometry

```
Q=T (T^T T restricted to E_a)^(-1/2).
```

Set F_b0=Q(p0)F_a0, then use the same coordinate path family for system b.
Q is orientation-preserving at p0 by this definition. Its continuous,
everywhere-invertible extension preserves that sign over the connected
rectangle; this conclusion depends on certifying those hypotheses. A
whole-rectangle margin is required, not just a base-point overlap.

No numerical frames, pivots or projector fields exist in this declaration.
Their construction is fully specified conditionally; the resulting
objects must be retained and certified during a future approved execution.
If lexicographic pivot selection cannot be resolved by the chosen exact
and interval reasoning, report that failure rather than changing the rule.

## Seam directions, repair and joint comparison

For each finite basis use the archived valley +1 shifts d1=(-1,0) and
d2=(0,-1). In the infinite plane-wave indexing convention these represent
k->k+G1 and k->k+G2, respectively: the same total momentum is indexed by
n-e_i at the translated k. Their finite restrictions are partial shifts,
so exact finite Hamiltonian covariance is not assumed.

On the left/right edge define J1(y)=polar(P(1,y) S_d1 P(0,y)) as a map
between the selected fibres. Define J2(x) similarly from (x,0) to (x,1).
For EACH finite system, separately:

1. Certify the restricted overlap singular value is at least 19/20 on
   every complete edge. This adopts the old 0.05 loss tolerance as a
   new continuous target; its satisfaction has not been observed here.
2. In the consistently oriented rectangle frames above, certify every
   seam map has positive determinant. A negative raw eigenframe-link
   determinant is irrelevant to this condition. Stop if orientation fails.
3. Let A=J2(1)J1(0), B=J1(1)J2(0). Require ||A-B||_2<=1, a declared
   strict margin from the antipodal threshold 2. Define delta=Arg(A^T B)
   in (-pi,pi), and repair J2(x) by right composition with
   exp(delta*chi(x)*I_source), chi(t)=10t^3-15t^4+6t^5, as in q007.
   Retain the exact repair rule, delta enclosure and corner relation.

Here I_source is the positive 90-degree complex structure on the oriented
source two-plane, not the identity operator. In an oriented orthonormal
frame it is [[0,-1],[1,0]].

Only then compare the two repaired systems under Q. Pull the large
system's map back as Q(target)^T J_i^b Q(source), and require its uniform
operator-norm distance from J_i^a to be at most 1 for each edge.
Then rho1+rho2<=2*pi/3<pi, so q008's joint sufficient condition applies.
This v1 declaration uses that conservative screen only. A failed screen
does not prove different classes; it returns INCONCLUSIVE and cannot be
replaced after seeing results by another reference or threshold.

These choices define candidate abstract finite gluing systems. Repair and
class agreement do not prove preservation of physical reciprocal sewing
or select the infinite-basis graphene reference class.

## Arithmetic, refusal policy and staged execution boundary

Use the spectral operator norm for perturbation, overlap and map bounds,
with a Frobenius upper bound permitted when proved. The exact-input target
Hamiltonian assembly error is at most 1e-8 meV in operator norm per system.
Gap certificates must already include assembly and spectral error; meeting
an assembly target alone does not certify a gap or projector.

The arithmetic design is exact rational intervals with outward enclosure
at every step. Elementary real functions require rational remainder bounds
(including a rational pi enclosure); inverse matrices require validated
residual bounds; ordered eigenvalue enclosures require verified inertia
or another reviewed spectral method. Inverse square roots, projectors and
Kato transport require reviewed enclosures derived from certified margins.
This specifies a method contract, not an implemented interval backend.
No double-precision diagnostic may be substituted as a certificate.

For EACH cutoff use q=(Delta phi-K1)/(2*pi), with phi, K1 and their sign
conventions defined in q008 DERIVATION.md sections 1-2 for the repaired
maps and projector connection. Require each sampling step's variation plus
its endpoint errors to be at most pi/2. Enclose K1 quadrature, endpoint
phase, transport/discretization and arithmetic errors together. Each final
q interval must have half-width at most 1/8 and contain exactly one integer;
otherwise refuse integer certification. The two integers must agree,
consistent with the independently certified joint comparison. These are
predeclared targets, not reported error bounds. Mathematical integrality
is used only after the continuous oriented repaired-gluing hypotheses
have been established.

Possible future terminal results are CERTIFIED_RELATIVE_FINITE_CLASS,
REFUSED_HYPOTHESIS, INCONCLUSIVE or EXECUTION_ERROR. Only the first requires
all the conditions above plus retained exact inputs, source identities,
frame/projector evidence, enclosures, logs and a complete error budget.
No outcome is currently selected. Failure remains a useful recorded result.

Before any physical execution, independently review this declaration,
then retain an implementation plan with a finite work budget, interval
backend/version, spectral method, subdivision limit and termination rules.
Those execution choices are still open. This packet authorizes no sweep
and supplies no runtime estimate. The v078 correction owner is unaffected.
