# S0b: spectral windows and an explicit phase-error budget

2026-09-23. **Candidate derivation and synthetic implementation, pending
independent review.** Follows Claude source comment 5797225243 and completed
Codex review [5292777390](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5292777390).
The frozen S0a evidence at `1d5cbd8a5c4febbf40447dfe4ec4b6ae91d14dcb`
is historical and unchanged. This is the next partial S0 packet; the physical
case remains DECLARED_UNEXECUTED, with S1–S4 budgets unfrozen.

## 1. Uniform spectral windows

For an exact continuous real symmetric H(x) on a closed cell, certify
H(x)-s_L I and H(x)-s_R I nonsingular, with the same inertia count N=k at
both shifts, and s_L<s_R. Then precisely k eigenvalues lie below either
shift, so the **closed** interval [s_L,s_R] is free of spectrum throughout
the cell. The adjacent eigenvalue gap is greater than s_R-s_L. Every
vertical complex line through c=(s_L+s_R)/2 has spectral distance at least
(s_R-s_L)/2. More generally the horizontal distance at a real abscissa
u in this window is at least min(u-s_L,s_R-u).

The Riesz contour also has horizontal segments. Their nonzero imaginary
height provides a separate distance bound; use the minimum over the
complete contour. Two window certificates do not remove that obligation,
nor do they replace uniform assembly error enclosures.

S0b uses the previously derived congruence/Schur method at four shifts.
For each shift the synthetic block selector takes two prescribed center
eigenvalue labels on each side, ordered by distance then original index.
The selected block is therefore 4-by-4. A physical selector must be frozen
separately; selection of approximate eigenvectors is a heuristic, while
the certified nonsingular congruence and subsequent inertia test establish
the count independently of their labels.

With K=V^T(H-sI)V partitioned into A,B,D, choose a fixed dyadic midpoint R
of an enclosed D(center) inverse. Certify q=||I-RD(X)||_F<1, giving
nu=||R||_F/(1-q) as an upper bound for ||D(X)^-1||_2. Certify the center
inertia of D by interval LDL; continuity and uniform invertibility fix it
over the connected cell. Let beta=||B(X)||_F. Every entry of
B^T D^-1 B has absolute value at most beta² nu. The implementation adds
the full upper endpoint of that debit to each selected-block entry and
uses interval LDL on the resulting symmetric enclosure. This enclosure
loses correlations and can be conservative, but contains every exact
Schur complement. Ambiguous pivots or q>=1 are INCONCLUSIVE.

The full Gram term -s V^T V is retained. A Gram-defect Frobenius bound
below one certifies nonsingularity. The perturbed synthetic V=Q(I+E)S
has nonzero center B, which is explicitly measured and retained. It is
not an exact eigenbasis. No second-order cancellation is assumed. The
full-rank matrix is dense, although the chosen rank-one E is structured;
these examples still do not represent all physical conditioning.

Narrow cells must certify both windows. Wide cells deliberately contain
gap closures; the sufficient method is expected to return INCONCLUSIVE.
The harness counts a correctly inconclusive control as a passed behavior
test, never as a certified cell. A three-dimensional control separately
shows why one successful separating shift does not guarantee a chosen
nonzero-width window.

## 2. Conditional phase-to-q ledger

Let F0,F1 be exact orthonormal frames and J an exact isometry mapping the
selected source plane onto the target, expressed in a common exact ambient
space. Then M=F1^T J F0 is in SO(2), once orientation has been certified.
Suppose approximate frames satisfy ||Ftilde_i-Fi||_2<=epsilon and an
approximate **unrepaired** seam map satisfies ||Jtilde-J||_2<=eta.
Their product differs from M by at most

`delta_M = 2 epsilon + epsilon² + (1+epsilon)² eta`.

This follows by first keeping J exact and expanding the two frame errors,
then adding the product containing Jtilde-J. Frobenius frame error bounds
are sufficient. Errors in the ambient identification, polar construction,
projector, assembly and seam evaluation must already be included in these
certificates; their existence is not assumed from a passing transport job.

Write G=[[0,-1],[1,0]]. The conformal projection C(E)=(E-GEG)/2 is a
contraction in operator norm and has the form aI+bG, whose norm is
sqrt(a²+b²). Thus the conformal coefficient of Mtilde lies in the disk
of radius delta_M around exp(i alpha). If delta_M<1, this disk misses zero
and its angle error is at most asin(delta_M). This proof uses the actual
oriented map, not a raw possibly singular shift compression.

In the declared gauge q=(Delta beta-Delta alpha)/(2pi). Evaluate the two
unrepaired seam lifts first, then add delta_corner*chi to the second one.
Since chi(1)-chi(0)=1, an enclosure error rho in the exact repair angle
contributes rho once to the final phase difference. This convention avoids
also charging the same repair inside eta; a direct repaired-map method
would need a different ledger. No statistical independence is required:
we use the triangle inequality, valid even for correlated errors.

The candidate sufficient allocation is:

| Quantity | Maximum absolute error |
|---|---:|
| Each frame, operator norm (Frobenius sufficient) | 1/16 |
| Each unrepaired seam map, operator norm | 1/128 |
| Exact corner repair angle | 1/32 rad |
| Additional angle extraction/arithmetic total | 1/64 rad |

It gives the final half-width bound

`[4 asin(delta_M) + 1/32 + 1/64] / (2pi) < 1/8`.

The four endpoint contributions are alpha(0), alpha(1), unrepaired beta(0)
and unrepaired beta(1). The corner-angle error cap is an **additional gate**;
it may require tighter corner frames than the coarse 1/16 allowance. This
ledger does not assert that four coarse endpoint enclosures alone deliver
that corner cap. The exact corner must also be certified away from its
principal branch cut before repair.

Endpoint error alone cannot certify a lift. Each edge interval must also
bound exact phase variation plus both endpoint errors and the allocated
evaluation errors by pi/2, as in CASE v2. Whole-path/branch, orientation,
corner-compatibility, integrality and unique-integer checks all remain
required. These are acceptance conditions, not outputs of S0b. The
1e-8 meV assembly tolerance is unchanged and has different units.

## 3. Variable, noncommuting transport with an exact solution

On each four-dimensional block define
U(t,x)=R01(a(t,x)) R12(b(t)), with the fourth coordinate fixed, where
a=20t+t²/2+xt, b=3t²/2, t in [0,1]. Set A=U_t U^T. In its active 3-by-3
block, A=a' G01+b' R01(a) G12 R01(a)^T. It is skew, varies with t, and
has noncommuting generators. The exact solution is U(t,x)F0, with F0 the
first two columns of a prescribed rational orthogonal Householder matrix.

At x=0, ||partial_t A||_2 <= |a''|+|b''|+2|a'||b'| <= 130. Over a step
of length h centered at c, use the exact midpoint-frozen flow exp((t-t0)A(c))
on the exact dyadic center state C. Its integrated residual is bounded by
130*h²*||C||_F/4. The preceding skew norm-defect lemma carries the old
error without amplification. The interval exponential and state product
are enclosed by Arb; the entire radius from recentering is added.

For |x|<=rho, ||A(t,x)-A(t,0)||_2 <= |x|(1+6t²) <= 7rho. Duhamel therefore
adds at most 7rho*sqrt(2) for the whole unit interval and entire parameter
strip. Initial F0 is parameter-independent in this example. Actual bottom
path uncertainty and projector derivatives remain unimplemented physical
inputs. This is a genuine varying-generator/strip test but uses repeated
small blocks, so its timing does not calibrate dense physical generators.

The sufficient error is tested against the ledger's 1/16 frame cap. The
three endpoint evaluations x=-rho,0,rho are consistency checks against a
closed-form solution. They are not the proof of the whole-strip bound,
which comes from the analytic derivative and Duhamel estimates above.
The same backend evaluates both expressions; no independent arithmetic
implementation is claimed. A coarse-step control is expected to remain
INCONCLUSIVE even if its endpoint happens to be accurate.

## 4. Portable runner and finite boundary

The new runner accepts fresh relative or absolute directories anywhere
writable. It snapshots its full executed source before starting workers;
the workers run that snapshot. Output-relative paths make the result
bundle movable without the original checkout. Each JSON write is atomic;
MANIFEST.json is written after results, then COMPLETE.json binds its hash.
A missing marker means incomplete records, and a completed NOT_PASSED run
does not become an accepted numerical result. Existing output directories
are refused. The historical S0a runner is retained as frozen evidence;
the repaired runner here is its successor.

The list and limits are fixed in SPEC.json before execution: nine numerical
behavior jobs, 900 seconds total, 180 per job, one worker, 2 GiB address
space and no retries. Ten separate standard-library runner controls cover
external/relative outputs, portability, reuse refusal, tamper detection,
write failure, missing completion, worker schema, exit and timeout.
No physical Hamiltonian, physical eigensolver or sweep is included.
