# From the seam theorem to the archived finite model

Date: 2026-09-23. Status: source-level proof independently audited for the
declared case. Claude comment [5791880416](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5791880416)
and Codex review [5288846821](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5288846821)
record the audit. The fixed-case audit is recorded in Claude comment
[5792152685](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5792152685)
and Codex review [5289043968](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5289043968).
The [v2 declaration](CASE.md) and [bounded implementation design](IMPLEMENTATION_PLAN.md)
incorporate its qualifications. Synthetic arithmetic has advanced through
[S0d](S0D_PRIMITIVES.md) and [PLAN_005](PLAN_005.json); physical S1-S4 remain
unimplemented and no physical run has been performed.

This note follows q008 at `4b01d0867a85a92e9bc634cc852c32b4c219cef3`,
Claude comment [5791531635](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5791531635),
and completed Codex review [5288583561](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5288583561).
The q008 audit is complete under its stated abstract hypotheses. Its frozen
package remains unchanged. This note connects one hypothesis to the archived
finite model; it does not assign an Euler class to graphene.

## 1. Exact source boundary

The input is `research/benchmarks/migration_contract_review/partner_v078p.zip`,
SHA-256 `d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e`.
The source baseline is `44dc66951057a995ee0999c785aca3e0e6c67092`.
`SOURCE_BINDINGS.json` records the archive chain, member hashes and inspected
definition spans. Files were read and parsed without importing archived code.

The archived `migrated_valley_control.build` calls `BM` with its declared
`MODEL_DEFAULTS`, an explicit index set and valley, then `add_harmonic` with
`mat=sz`, `use_sin=True`, `layer_sign=1`. Defaults include mass=0, N=4,
kinetic=`lab_nn_full`, geometry=`exact`, and w_kappa=0. The retained basis
contains 49 reciprocal indices and both sublattices in both layers, giving
dimension 196. B is -0.25 or -0.30 in the eight-case migration plan.

The proof below concerns those formulas interpreted in exact arithmetic,
with real finite parameters, a fixed finite index set, and well-defined
geometry. It does not prove that a floating-point execution evaluates them
without error, nor certify constructor/plan agreement for arbitrary runs.

## 2. Finite-model real-structure proof

Let X be sigma_x on every layer/reciprocal-index sublattice pair and K be
entrywise complex conjugation in that fixed ordering. Set C=X K.
X is real and X^2=I, so C^2=I. For a 2x2 block define
T(A)=sigma_x conjugate(A) sigma_x. It is conjugate-linear, multiplicative,
and commutes with taking adjoints. Direct Pauli algebra gives

```
T(I)=I,  T(sigma_x)=sigma_x,  T(sigma_y)=sigma_y,
T(sigma_z)=-sigma_z,  T(i sigma_z)=i sigma_z.
```

Every block in the declared massless model is fixed by T:

| Source term | Why it is fixed |
|---|---|
| `BM._H_K` kinetic blocks | Real coefficients multiplying sigma_x and sigma_y. Strain, rotation and pseudo-gauge operations change only those real coefficients. |
| `BM.__init__` tunnelling `T[j]`, inserted by `_build_static` | Real linear combinations of I, sigma_x and sigma_y. Reverse blocks are adjoints, which preserve the condition. |
| `_build_static` scalar moire potential | Real coefficient times I. |
| `_build_static` displacement field | Real layer-dependent coefficient times I; zero in the declared run. |
| `add_harmonic` with real amplitude and `sz`, `use_sin=True` | Each directed block has a purely imaginary coefficient times sigma_z. Conjugating the coefficient and reversing sigma_z cancel. Opposite directions are adjoints. |

A nonzero real mass times sigma_z fails this condition. For real nonzero
Fourier amplitudes, cosine-sigma_z and sine-{I,sigma_x,sigma_y} also break
this C; cosine-{I,sigma_x,sigma_y} and sine-sigma_z preserve it. These claims
concern the individual nonzero terms, absent cancellations. The declared
pairing, real amplitude, real layer_sign and real w1 are explicit hypotheses.
The proof does not rely on an assertion serving as input validation.

Finite truncation removes complete sublattice pairs and block connections.
C acts within each retained pair, so it preserves the finite space for any
fixed index set of this form. No symmetry of that index set under n -> -n
is needed for this particular antiunitary. Deleting blocks and their
adjoints preserves the block identities and Hermiticity. Therefore

```
X conjugate(H_K(k)) X = H_K(k),   C^2=I,
```

for every real k where the declared formulas are defined. The archived
valley +1 path does not coerce k to float; real k must be a caller
precondition. Complex-step and contour evaluations are outside this proof.
The archived
valley wrapper is H_Kprime(k)=conjugate(H_K(-k)). Conjugating the identity
above gives X H_K(-k) X=conjugate(H_K(-k)), which proves the same C symmetry
for the wrapper. This is an algebraic partner valley, not an independent
K-prime implementation or physical validation of the wrapper.

Let u=[[1,i],[1,-i]]/sqrt(2) and U be its direct sum over all pairs. Then
X conjugate(U)=U, so U fixes the real form of C. Equivalently,

```
u^dagger sigma_x u = sigma_z,
u^dagger sigma_y u = -sigma_x,
u^dagger sigma_z u = -sigma_y.
```

Consequently U^dagger H U is real and, since H is Hermitian, symmetric.
The four block expressions in archived `fast_engine.realify` are precisely
the expansion of U^dagger H U. The sine harmonic becomes a real
antisymmetric 2x2 directed block; its reverse transpose makes the full
Hamiltonian real symmetric. There is no need to discard an imaginary
component to establish this exact algebraic statement.

The archived `shift_matrix` has real entries and shifts whole sublattice
pairs without mixing their two components. It commutes with X and U,
so it is compatible with this ambient real form. As established in q006,
it remains a rank-deficient partial shift. This compatibility does not
make it unitary, an exact covariance of the finite H, or a valid torus seam.

## 3. What this does and does not close

The independent audit supports a specified ambient real structure for the
exact declared finite model at every real k. This replaces a missing
algebraic definition with an explicit source-level construction.

For an isolated rank-two spectral cluster, its projector commutes with C
by spectral calculus. With a uniform gap and suitable regularity, it
therefore defines a real rank-two bundle on the contractible rectangle,
where the bundle is trivial and orientable. Those isolation hypotheses
have not been certified here. A real structure alone proves
neither orientability on the glued torus nor the existence of an oriented
periodic frame. It also does not establish that the modeled antiunitary
matches every physical symmetry, perturbation or experimental sample.

`Sampler.frame` checks Hermiticity and the maximum entrywise imaginary
residual at evaluated coordinates before diagonalizing the real part.
These are sampled floating-point diagnostics. To connect the executed
matrix to this exact model still requires assembly, eigensolver and
projector error enclosures in a declared norm. For a D-by-D matrix,
||Im R||_2 <= ||Im R||_F <= D max_ij |Im R_ij|, so the 1e-9 meV entrywise
gate bounds the discarded part by 1.96e-7 meV at D=196, assuming that
entrywise bound is established for the represented matrix. It does not
enclose assembly roundoff, trigonometric/inverse errors, eigensolver errors
or the difference from the exact model. An observed rounded residual is
not a replacement for outward-rounded bounds on those quantities.

Raw links between independent eigenframes can have negative determinants
because eigenvector column signs are arbitrary. Rejecting such raw links
on determinant sign would be wrong. Orientation is tested on seam maps
expressed in consistently oriented continuous rectangle frames. A real
structure does not determine that seam orientation. Stability of w1 along
a gapped continuous family presupposes a continuously specified gluing
family under declared identifications; independently changing the gluing
is not covered by a gap-only argument.

## 4. Ordered readiness map

The model/error, isolation, continuous boundary/orientation, and corner
conditions below must be proved separately for BOTH finite systems before
using a cross-cutoff comparison. Orientation precedes principal repair.

| Gate | Accessible evidence | Required before a certified finite relative class |
|---|---|---|
| Model and domain declaration | Exact archived constructor and harmonic; frozen N=4 basis and eight local-path cases | Select one parameter setting, rectangle, band pair, orientation convention and comparison cutoff with explicit index sets. Local node loops and transport paths do not supply a whole-rectangle certificate. |
| Ambient real structure | Audited proof in section 2, bound to actual archived definitions | An error bridge from floating-point matrices to the exact real model for each finite system. |
| Isolated real two-plane field | Sampled neighboring energies in the migration records | Certified uniform external spectral gap over the declared rectangle and seams, with regularity bounds. Internal degeneracy of the selected pair need not destroy the pair projector. |
| Boundary polar maps and orientation | `shift_matrix`, `sewing`, and `Sampler.link`; q006 loss/mismatch identities | Continuous selected-fibre invertibility, positive seam determinant in consistently oriented frames, and its relation to the intended physical translation. The determinant of a raw eigenframe link is not this test. |
| Corner repair | q007 principal construction; q008 audit composition warning | Certified margin below 2 for each unrepaired corner discrepancy, then the specified principal repair and continuous maps for the repaired system. |
| Cross-cutoff identification | No such object is supplied by this reviewed N=4 migration package | Explicit continuous oriented isometry between the selected fibres over the whole rectangle. Ordered ambient index inclusion alone does not identify the selected eigenspaces. |
| Joint class comparison | q008 equations (6)-(7) | Certify the joint lifted-corner condition or uniform sufficient bound for the repaired systems under that single identification. Endpoint agreement is insufficient. |
| Integer extraction | q008 section 5 conditional contract | Certified phase variation, endpoint errors, pi and directed arithmetic; exactly one integer candidate in the final enclosure. The declared vertical Kato gauge reduces the defect integral to an edge-phase increment; see CASE.md. |
| Physical/infinite-cutoff interpretation | Not established by this packet | Separate physical reference and controlled finite-to-infinite comparison. Agreement of two finite classes is insufficient. |

The migration ledger has 5,944 frame, 8,224 link and 2,304 angle records.
None of its links has sewing=true. There are 4,457 negative raw-link
determinants, which are not by themselves orientation defects. It stores
neither the eigenframes returned by `Sampler.frame` nor a second cutoff.
Its scalar records cannot
reconstruct a continuous field or a cross-cutoff identification. This is
an evidence-availability limit of that delivery, not evidence that its
retained SAME/OPPOSITE labels are wrong. Earlier historical cutoff studies
are not being assessed or promoted into continuous certificates here.

## 5. Next bounded handoff

The source-level and v1 declaration audits are complete. The pre-execution
[v2 amendment](CASE.md) fixes a certifiable pivot, keeps the principal repair
exact, uses both complete edge-phase lifts in the Kato gauge, and records
individual and relative outcomes separately. No model parameters, bases,
band pairs or existing numerical targets were changed.

[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) and [PLAN.json](PLAN.json)
choose a ball-arithmetic backend, certified inertia method, projector and
transport enclosure strategy, hard work limits, and an evidence contract.
They also retain two qualifications: general Sylvester residual bounds use
the Frobenius norm, and partial-shift overlap needs deletion loss as well as
off-target leakage. These bounds are conditional mathematics, not case results.

S0a-S0c are independently reproduced. S0d adds fixed synthetic circular Riesz
quadrature, oriented polar/seam-map and continuous phase-lift primitives, plus
the reviewed branch-margin, congruence-provenance, nonfinite-outcome and naming
corrections. Its first fixed run passed all 13 expected behaviors and 10
protocol controls; independent review is pending. The next bounded slice is
composition of these primitives with the exact principal repair and joint
relative integer enclosure before any physical-model execution. The v078
correction owner retains that work; frozen q001-q008 are unchanged.

## S0e correction handoff

[S0e corrections](S0E_CORRECTIONS.md) and [PLAN_006](PLAN_006.json) supersede the
S0d next-step status above. All 14 fixed expected outcomes and 10 protocol checks
pass; independent review is pending. Full geometric composition remains open.
