# S0c: reviewed budget and outcome corrections

2026-09-23. Follows Claude source comment 5798619931 and completed Codex
[review 5293785199](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5293785199).
This additive successor supersedes the candidate error ledger and outcome
implementation in PLAN_003/S0b; it preserves the old evidence byte for byte.
S0c is a bounded synthetic correction package pending independent review.
Physical S1–S4 remain unimplemented, unexecuted, with budgets unfrozen.

## 1. A corner allowance justified by the declared errors

Let each exact oriented seam map be a norm-one isometry on its selected
fibres, in a certified common ambient identification, with approximation
error at most eta. Each two-map path A or B then has error bounded by
b=2 eta+eta². The product C=A^T B has error at most

`z = 2 b+b² = (2 eta+eta²)(2+2 eta+eta²)`.

Approximate maps need not themselves be orthogonal. Exact A and B have
norm at most one on the ambient extensions used here. Restricting C to
the oriented corner frame F gives an SO(2) matrix. If the approximate
frame has error at most epsilon, its compressed product error is bounded by

`d_corner = 2 epsilon+epsilon²+(1+epsilon)² z`.

The same frame appears twice, but expansion plus the triangle inequality
requires no independence. The conformal-part disk lemma from S0b gives a
corner angle error <= asin(d_corner), provided d_corner<1. Its angular
comparison is local on a common lift; principal branch separation must
also be certified. The exact case gate ||A-B||<=1 implies |delta|<=pi/3.
An enclosure must respect that gate and remain separated from +/-pi.

With epsilon=1/16 and eta=1/128, the endpoint bound is
d_edge=2 epsilon+epsilon²+(1+epsilon)² eta. The revised allocation is:

| Error source | Allowance |
|---|---:|
| Each frame, operator norm (Frobenius sufficient) | 1/16 |
| Each unrepaired seam map, operator norm | 1/128 |
| Corner repair angle, geometric error | 3/16 rad |
| All additional phase extraction/arithmetic error | 1/64 rad total |
| Final q half-width | 1/8 |

The code must separately prove asin(d_corner)<3/16 and

`[4 asin(d_edge)+3/16+1/64]/(2 pi) < 1/8`.

The expected sufficient bounds are <0.165353 rad and <0.120287 respectively;
the retained run provides outward-rounded dyadic endpoints. Additional
phase arithmetic includes corner angle extraction error beyond the
geometric disk bound. All errors in projector, polar/seam construction,
identification, assembly and transport must already be in the frame and
map certificates, or in the explicitly allocated arithmetic remainder.
The repair is charged once via chi(1)-chi(0)=1 in the unrepaired-lift
formula. Charging repair again inside eta would require a different ledger.

The old 1/32 cap fails this sufficient implication. This does not prove
that any actual corner error exceeds it; tighter separate input estimates
can still establish that earlier gate. A 1/4 repair allowance, conversely,
overspends the final q budget. Both are fixed inconclusive controls.
This allocation proves no actual frame, seam, lift, orientation, compatible
gluing, integrality or physical class. Those gates remain mandatory.

## 2. Numerical uncertainty remains inconclusive

The corrected Schur primitive preserves the S0b enclosure argument.
It catches ZeroDivisionError only around the center complement inverse.
That exception yields INCONCLUSIVE / COMPLEMENT_INVERSE_NOT_CERTIFIED.
A successful center inverse followed by a whole-cell residual >=1 yields
INCONCLUSIVE / COMPLEMENT_RESIDUAL_NOT_CERTIFIED. These distinct paths
are tested on fixed six-dimensional ball matrices. Ambiguous inertia and
an unproved Gram-defect bound likewise remain inconclusive. A malformed
matrix shape remains a programming error, not a numerical conclusion.

The worker transports raw CERTIFIED, INCONCLUSIVE and EXECUTION_ERROR
records without converting them to PASS. The separate regression harness
matches the frozen expected status, reason and (for the deliberate fault)
exception type. It continues after expected controls, and stops on any
unexpected result. This is a synthetic test policy; it implements no
physical subdivision, refusal hierarchy or retry policy. Complete records
with NOT_PASSED status are not accepted numerical results.

## 3. Spectral windows must enclose the declared pair

For zero-based inclusive pair [l,h], with both external neighbors present,
the lower window needs equal counts l at its two endpoints; the upper
window needs equal counts h+1. Endpoint nonsingularity and equal counts
at another index still prove that window spectrum-free, but do not isolate
the declared pair. The candidate cell result is then INCONCLUSIVE /
DECLARED_INDEX_NOT_CERTIFIED, not a claim that the model hypothesis fails.

For the declared rank-two pairs the required counts are 97/99 at dimension
196 and 153/155 at dimension 308. This code derives them from [97,98] and
[153,154], rather than from the synthetic eigenvalue oracle. The fixture
uses known center labels only to select the Schur block. Inertia decides
the counts. The known-answer checks live in the separate verifier.

The full-size fixed family is the same perturbed rational family and
width 1/8 as S0b. A six-dimensional family diag(-4,-3,0,0,3,4) supplies a
wrong-pair control [1,2] and a correct-pair control [2,3]. Both use the
same windows and exact matrices, so the distinction is the declared index.
This is not an adaptive search for favorable shifts or bands.

## 4. Bounded evidence and remaining work

SPEC.json is frozen before the first execution: eleven jobs, 128-bit
arithmetic, one worker, 90 seconds per job, 300 seconds overall, 2 GiB
worker address space, no retries. The run locks the same python-flint
0.9.0 / FLINT 3.6.0 wheel and installed native artifacts as S0b, snapshots
the full dependency sources, and writes portable atomic records with the
manifest-bound completion marker. Eight fixed protocol controls check
uncertainty/error separation and failure propagation.

No old frozen evidence is edited. The full-size fixtures retain favorable
synthetic structure; they do not measure physical conditioning. General
Riesz projectors/quadrature, polar-map error enclosures, phase lifts,
physical coefficient assembly and projector-derived transport are still
the next implementation gates. Magnus transport and a sharper Schur
spectral perturbation test remain optional, unimplemented candidates.
