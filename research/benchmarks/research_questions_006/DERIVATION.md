# Boundary sewing: exact assumptions versus sampled diagnostics

This additive pass concerns the unchanged archived `shift_matrix`, `sewing`
and `Sampler.link` components. It does not run the physical Hamiltonian,
eigensolver, Euler consumer, node finder or migration consumer. It does not
repair the production implementation or establish that a retained physical
measurement is wrong. The general transport result of questions 005 remains
conditional on the boundary identification.

## 1. A finite translation is a partial isometry, not a unitary

Let Lambda be a nonempty finite subset of Z^2. For a nonzero integer d, the
archived shift maps e_n to e_(n+d) if n+d is in Lambda, and to zero otherwise.
It acts identically on each layer and sublattice. Define

```
D_in  = {n in Lambda : n+d in Lambda}
D_out = {n in Lambda : n-d in Lambda}.
S_d^T S_d = projector onto D_in (with four internal copies)
S_d S_d^T = projector onto D_out (with four internal copies).
```

At least one vector is lost: maximize n dot d on Lambda. Its translate has
larger dot product and is outside Lambda. Hence S_d is rank deficient and
`||I-S_d^T S_d|| = 1` for every such finite cutoff. This is an exact statement
about the ambient operator, not a convergence failure of low-energy states.
The rank is `4*|D_in|`; its singular values are exactly zero or one.

Opposite shifts obey `S_(-d)=S_d^T`, but neither product need be I. Distinct
compressed shifts need not commute: the two paths can encounter different
missing intermediate indices. Their column actions can be checked exactly
without eigenvectors. A commuting rectangular example would not prove that
another finite index set has the same property.

The fixed real-basis transform is block diagonal in sublattice, whereas S
only translates whole sublattice pairs. Therefore `U^dagger S U=S`. This
checks the representation of this operator; it is not a new proof of the
Hamiltonian's real structure or of a selected-band boundary condition.

## 2. What the archived sewing singular values control

Let F0 and F1 be real orthonormal r-frames at the two endpoints, P1=F1 F1^T,
and S any contraction, as is the truncated shift. Put

```
C = S F0,       M = F1^T C,
L = I-C^T C,    R = (I-P1) C.
I-M^T M = L + R^T R.
```

L is positive semidefinite and measures squared norm lost by S on the
selected input subspace. R measures the part of the shifted frame outside
the selected output subspace. These distinct errors are combined in M.

If `s_min(M)>=1-lambda>0`, then

```
||L|| <= 2*lambda-lambda^2,
||R|| <= sqrt(2*lambda-lambda^2).
```

Writing O=polar(M), endpoint fitting also gives

```
(C-F1 O)^T(C-F1 O) = 2*(I-|M|)-L,
||C-F1 O|| <= sqrt(2*lambda).
```

The current `sewing_loss_max=0.05` therefore permits a norm-loss amplitude
or off-target component as large as `sqrt(0.0975)=0.3122499...`, and gives
the fitting bound `sqrt(0.1)=0.3162278...`. It is not a 0.05-radian phase
error. The contraction hypothesis matters: arbitrary user-provided sewing
matrices need not satisfy it, even if one overlap passes the gate.

Two exact four-dimensional controls with M=0.96 I make the distinction:
one contracts F0 by 0.96 with no subspace mismatch; the other is an ambient
orthogonal rotation taking F0 partly outside P1 with no norm loss. They
have identical sewing singular values and both pass the current component
gate. A 0.94 contraction is refused by the 0.05 sewing-loss limit.

## 3. Singular values do not identify the physical transition or its phase

With F0=F1=(e1,e2), choose S to rotate their plane by theta and act as I on
its orthogonal complement. Then M=R(theta), all singular values are one,
the gate's sewing loss is zero, and its polar angle is theta. Thus a
singular-value check cannot bound the phase relative to the *separately
declared identity transition*. An arbitrary rotation is not intrinsically
wrong: it can be a legitimate transition when that is the specified bundle.
The check simply cannot decide which physical identification is intended.

Nor does checking each edge separately impose the corner cocycle. For a
rectangle with maps T1(y) from left to right and T2(x) from bottom to top,
the two paths from (0,0) must agree on that fibre:

```
T2(Lx) T1(0) = T1(Ly) T2(0).
```

For constant rank-two projector P, take T2=I and T1(y)=R(alpha*y/Ly) on P,
identity on its complement. All four corner overlap checks have singular
values one and positive determinant. For alpha=pi/3 the corner products
are nevertheless different. This is a synthetic edge-gate counterexample,
not an execution of the full Euler routine (which accepts constant matrices).

## 4. A narrow exact-sewing route, and the unresolved physical route

The identity-seam proof in questions 005 extends directly to *constant*,
real orthogonal, commuting ambient T1,T2 if the projector has a jointly C2
extension satisfying

```
P(x+Lx,y)=T1 P(x,y) T1^T,
P(x,y+Ly)=T2 P(x,y) T2^T.
```

Require equality and compatible derivatives at boundaries, not just at
sampled endpoints. Differentiation and Kato transport are covariant under
constant T, the corner is consistent, and no additional seam error is
introduced. The selected rank-two real bundle must still be oriented;
ambient orthogonality by itself does not guarantee that. Frames can be local.
The original continuous-x, gap, phase-unwrapping and arithmetic hypotheses
remain. This is an explicit sufficient special case, not a characterization
of all admissible transitions.

For variable ambient T the derivative of T contributes connection terms.
No unchanged transfer of the identity-seam flux formula is asserted here.
For the archived partial shifts, ambient orthogonality is false. A possible
selected-fibre construction is instead the polar isometry

```
J = P1 S P0 * (P0 S^T P1 S P0)^(-1/2) on range(P0),
```

when the restricted Gram operator is positive. In endpoint frames J has
matrix polar(M). This defines an isometry between two sampled fibres, but
does NOT yet show smoothness around the entire boundary, exact corner
compatibility, compatibility with the physical infinite-basis translation,
or equality of the estimator with the physically intended invariant.

The next retained evidence should distinguish these obligations:

1. Uniform selected-fibre leakage and mismatch (including between samples).
2. An explicit reference transition and controlled difference from it, or a
   precisely declared finite bundle with a valid smooth gluing construction.
3. Corner compatibility and orientation of those same transitions.
4. The resulting boundary contribution to transport/phase error, combined
   with interior discretization and certified arithmetic error.

The full-space defect of one cannot rule out a well-controlled selected
subspace. Passing the local singular-value tolerance cannot establish it.

## 5. Retained mesh-cost clarification from the partner review

For questions 005 let `A=p(q+p^2)/6`, loop length ell, and h=ell/N. The
accumulated **upper bound**, not the unknown actual error, is

```
B_loop = A*ell^3 / (N^2-p^2*ell^2/2).
```

For A>0 and ell>0, `B_loop<e` is equivalent to
`N^2 > A*ell^3/e + p^2*ell^2/2`, which also ensures the positive denominator.
Dropping the second term gives only an asymptotic sizing expression, not a
generally sufficient count. Rounding a displayed coefficient upward is not
a universal substitute. The source handoff's gap values near 6.996, 5.520
and 2.080 meV were centre gaps, whereas questions 005 used conditional cell
lower bounds near 6.808, 5.332 and 1.892 meV. Neither is interval certified.
This correction does not change the transport theorem or its stored checks.

## Evidence scope

All results in this pass are finite-index structural algebra, synthetic
endpoint-frame controls and conditional arithmetic. Selected archived
definitions are compiled unchanged from their AST, without module-level
activation; their full source hashes are retained. They are component
checks, not an end-to-end production replay. No physical eigenvectors or
Hamiltonians are computed. No theorem of cutoff convergence, physical Euler
value, changed braid label or paper sign convention is claimed.
