# Plan amendment and synthetic calibration

Date: 2026-09-23. Plan: **FC49-77-PLAN-002**. Case:
**FC49-77-K-Bm025-v2**, still **DECLARED_UNEXECUTED**.

This amendment supersedes the execution design and readiness status of
[PLAN.json](PLAN.json) / [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) at
`96b0c96009a34ecbcd69724d8b460547674d32c1`. Those files and their eight-file
receipt remain historical, unchanged. The mathematical case, thresholds,
orientation convention, seams and outcome definitions in CASE.md/CASE.json
are unchanged. This amendment does not release S1–S4 for physical execution.
It implements only the bounded **S0a** subset specified in
[PLAN_002.json](PLAN_002.json).

The triggering design audit is Claude comment
[5792741427](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5792741427),
followed by Codex review
[5289509618](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5289509618).
This is a new evidence packet for review, not a second reply to that source.

## 1. Corrections to the feasibility discussion

The earlier first-order Weyl debit, about `647.157 * 2^-d meV`, is a useful
cost warning. A complete quadtree through depth four uses 341 attempted
cells. A 512-attempt ceiling leaves 171 child attempts, enough to completely
refine 42 further cells. These counts alone do not prove failure or establish
an uncovered area fraction: the stopping pattern and center gap bounds matter.

We now independently extracted the retained floating diagnostics from the
hash-bound ZIP. The filter `kind=frame`, `case` beginning `B-0.25_v+1_`,
`lo=97`, in `RUN/DIAGNOSTICS.jsonl` returns 1,486 rows at 1,476 distinct
coordinates. Their upper external gaps range from 2.9009084271499184 to
32.752750455204854 meV. They belong to the two retained loop cases r0.008
and r0.012; they are not a uniform rectangle cover or interval certificates.
The member SHA-256 is
`66eecedbc8b98dabdab56db37844c309e50d8270862c3ab52c55184b346d2930`.

**Qualification of our preceding review:** a small sampled gap at an arbitrary
point does not establish that the center-based Weyl test fails in every cell
containing that point. The center gap can differ within the same Lipschitz
bound. Likewise, an upper bound on `||[P',P]||` is not a lower bound on
transport cost or measured interval wrapping. The prior feasibility verdict
should therefore be read as an unresolved budget risk, not an impossibility
result. This packet provides calibration, without claiming to settle that risk.

The inspection command reads archived JSON only; it imports no model code.
[Its receipt and script](../../research/benchmarks/certification_s0a_001/README.md)
make this extraction reproducible.

## 2. Correct congruence and a conditional uniform cell theorem

Let H(x) be exact real symmetric on a connected closed cell X. Choose one
fixed real square V for the cell. A certified bound

`eta >= ||I-V^T V||_2`, `eta < 1`

implies `sigma_min(V) >= sqrt(1-eta) > 0`. A Frobenius bound suffices for eta.
For each real shift s, use the complete congruence

`K(x,s) = V^T H(x) V - s V^T V = V^T (H(x)-sI) V`.

Sylvester inertia then gives the eigenvalue count below s. Omitting the Gram
factor is invalid: H=1, V=2, s=2 gives K=-4, whereas `V^T H V-sI=+2`.
V may be specified exactly by dyadic entries and all products enclosed by
Arb. An uncertain basis is acceptable only if the enclosure certifies every
necessary statement for the particular exact V used. No floating eigenbasis
is accepted on its asserted orthogonality alone.

Partition K into a small selected block and its complement:

$$K=\begin{pmatrix}A & B^T \\ B & D\end{pmatrix}.$$

If D(x) is uniformly invertible, block elimination is a congruence:

`inertia(K) = inertia(D) + inertia(A-B^T D^{-1} B)`.

Indeed substitute `v -> v-D^{-1}Bu` into the quadratic form. The cross
terms vanish, leaving `u^T(A-B^T D^{-1}B)u + v^T D v`. This proof permits
indefinite D. A usable sufficient certificate consists of:

1. A validated inertia of D at one point in X.
2. A fixed approximate inverse R with `q >= sup_X ||I-RD(x)||_2 < 1`.
   The Neumann series gives `nu = ||R||_2/(1-q) >= sup_X ||D(x)^{-1}||_2`.
   Continuity and connectedness then fix the inertia of D throughout X.
3. Bounds `a >= sup_X ||A(x)-A0||_2` and `beta >= sup_X ||B(x)||_2`.
   Then the exact Schur complement lies within `a+beta^2*nu` of A0.
4. Certified eigenvalue enclosures of A0, enlarged by that debit, which
   exclude zero and determine its signed inertia over the whole cell.

Each inequality is an outward-rounded norm bound. Failure to certify any
one of them is INCONCLUSIVE, not a sign or gap failure. All spectral shifts,
both external neighbors and complete domain coverage remain required.
This is a sufficient test, not a statement that the physical cell will pass.

If `B=B0+Delta B`, use `beta <= ||B0||+sup||Delta B||` including the center
residual. A quadratic off-block debit occurs only when B0 is zero or suitably
small; the direct selected-block variation a still exists. Preconditioning
does not eliminate first-order eigenvalue motion. The implemented S0a code
tests point inertia in full dimensions and one 2-by-2 uniform Schur example;
it does **not** yet implement this full uniform-cell algorithm.

Unpivoted LDL remains the first prototype. A zero-containing pivot means
INCONCLUSIVE even for a nonsingular matrix. Symmetric pivoting is not
mathematically forbidden: a permutation and an LDL factorization with
certified 1-by-1/2-by-2 blocks are congruences and preserve inertia. For the
standard factorization form see the primary
[LAPACK DSYTRF documentation](https://netlib.org/lapack/explore-html/d8/d0e/group__hetrf_ga431b081d6c9c48af82ec003a7d3070ff.html).
No pivoted interval implementation is supplied or assumed here.

## 3. Replace raw transport boxes with a norm-defect enclosure

The exact Kato gauge in CASE v2 is preserved. For a real orthogonal
projector P, `A=[P',P]` is skew-symmetric. Its exact evolution U(t,s) is
orthogonal. Let Y be a differentiable, explicitly represented approximation
to `F'=AF`, and put `r=Y'-AY`. Variation of constants gives

`||F(t1)-Y(t1)||_F <= ||F(t0)-Y(t0)||_F + integral ||r(t)||_F dt`.

Proof: the error solves `e'=Ae-r`. Orthogonality gives `||Ue||_F=||e||_F`;
integrate the equation and apply the triangle inequality. There is no
exponential factor from taking entrywise absolute values of A. This argument
requires the exact generator to be skew; an arbitrary interval matrix is
not itself assumed skew merely because it encloses A.

For a parameter strip, take a bound uniform in the entire strip, including
the initial frame error. If Y is built for a center generator A0, bound

`||Y'-A(x,t)Y||_F <= ||Y'-A0(t)Y||_F + ||A(x,t)-A0(t)||_2 ||Y||_F`.

Taylor coefficients, residual integrals and parameter variation must all be
enclosed. Replacing a computed endpoint by an exact dyadic midpoint adds
the complete endpoint rounding radius to the carried error. It never resets
the previous error. The midpoint need not be orthonormal: it represents a
ball around the exact oriented Kato frame, not a change of gauge. The same
rule must cover bottom transport, its x-dependence, and vertical strips.

The constant skew specialization is implemented. For `A=omega J`, `J^T=-J`
and `J^2=-I`, the degree-m Taylor polynomial has the operator remainder

`||exp(hA)-sum_{k=0}^m(hA)^k/k!||_2 <= (h|omega|)^(m+1)/(m+1)!`.

This follows from the integral Taylor remainder and the orthogonality of
`exp(tA)`. It applies to the exact center state; multiply by its Frobenius
norm, add the arithmetic radius, and carry previous error additively.
The retained n=196 and n=308 examples use 512 steps, degree 20 and omega=1000.
The full n-by-2 state is propagated, but the generator is block diagonal and
the polynomial reduces to two scalar coefficients. These timings do not
measure dense variable-coefficient Kato work or projector construction.

For an uncertain rate `omega +/- 1/1000`, Duhamel adds `sqrt(2)/1000` on the
unit interval. This exceeds the synthetic 1e-8 target. Removing wrapping
does not remove real parameter variation. A valid variable-coefficient
residual implementation and its cost remain open gates.

## 4. Retained S0a result and resource implications

[All ten frozen jobs](../../research/benchmarks/certification_s0a_001/RUN/RESULTS.json)
passed in 24.018 seconds total with no retries. The regression job contains
seven known-answer/control checks; seven other jobs check dense point
inertia, and two check constant skew transport. Rounded figures below are
readability summaries; JSON retains exact dyadic endpoints for every bound.

| Synthetic job | Total seconds | Negative eigenvalues | Largest pivot radius, approximately |
|---|---:|---:|---:|
| 196, raw, s=+1, 128 bits | 0.974 | 99 | 6.77e-17 |
| 196, congruence, s=-1, 128 bits | 1.248 | 97 | 7.68e-35 |
| 196, congruence, s=+1, 128 bits | 1.078 | 99 | 7.68e-35 |
| 308, raw, s=+1, 128 bits | 3.052 | 155 | 6.05e-18 |
| 308, congruence, s=-1, 128 bits | 3.806 | 153 | 2.37e-34 |
| 308, congruence, s=+1, 128 bits | 3.657 | 155 | 2.37e-34 |
| 308, congruence, s=+1, 256 bits | 5.213 | 155 | 6.97e-73 |

The synthetic V is deliberately an exact eigenbasis times a nonsingular
diagonal scale. This favorable case tests the Gram correction and sign
enclosures, not realistic approximate eigenvectors or difficult cells.
Congruence tightens the pivot enclosures here and costs additional time;
the experiment does not establish a speedup or a physical success rate.

Both transport examples yield a global error upper endpoint below
`1.807e-11`, with the independent closed-form endpoint enclosed inside it.
The arithmetic-radius sums are below `3.417e-35`; truncation dominates.
Their combined time is about 2.180 seconds. The largest worker RSS observed
in the complete run is about 124.1 MiB. These are observations on one machine,
not hardware-independent limits or a native-library correctness proof.

At this observed implementation cost, executing all 8,192 full-size LDLs
would greatly exceed the old 600-second S1 stage cap. That ceiling need not
be consumed, so this is not a lower bound on case runtime. Do not enlarge
physical budgets or declare them sufficient based on this favorable family.
The next bounded packet must test the actual uniform Schur algorithm and
variable-coefficient residual transport before proposing S1–S4 caps.

## 5. Backend, dependency and status accounting

The retained run used CPython 3.12.14, python-flint 0.9.0, native FLINT 3.6.0,
one thread and the x86_64 Linux abi3 wheel. The wheel SHA-256 is
`376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`.
[ENVIRONMENT.json](../../research/benchmarks/certification_s0a_001/RUN/ENVIRONMENT.json)
binds the wheel and installed extension/FLINT/GMP/MPFR binaries.
[MANIFEST.json](../../research/benchmarks/certification_s0a_001/RUN/MANIFEST.json)
binds the frozen spec, executed source and all result files. Arithmetic
trust remains conditional on this software and hardware; the record is not
a formal verification of FLINT, Python, the compiler or operating system.

The first retained run passed; no failed runs were replaced. API exploration
preceded the frozen list. S0a uses a 100-second per-job timeout, 900-second
global timeout, 2-GiB address-space ceiling, one worker and zero retries.
No physical Hamiltonian, physical eigensolver or parameter sweep was run.

S0a is **IMPLEMENTED_SYNTHETIC_PASS / INDEPENDENT_REVIEW_PENDING**. S0 as a
whole is incomplete: inverse/quadrature, polar, phase, whole-cell Schur and
variable parametric transport primitives still need implementation and tests.
Physical S1–S4 are **NOT_IMPLEMENTED / NOT_RUN / BUDGET_NOT_FROZEN**.
An unresolved a-pivot still makes the dependent signed b-convention
unavailable, with the original failure/inconclusive distinction preserved.
No absolute-class fallback is added. No physical gap, frame, seam, integer
or two-cutoff agreement has been certified.

The shell-residual/deletion-projector identities and shared cross-gap
bookkeeping from the audited design remain useful conditional optimizations;
they are not exercised by this synthetic packet. The q001–q008 packages,
the archived physical evidence and the separate v078 implementation remain
unchanged.
