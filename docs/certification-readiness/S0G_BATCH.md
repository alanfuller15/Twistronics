# S0g: gauge conversion and restored run provenance

Parent: c3edcecfd7815e10226e2b573bc82de607ce4ac9. Addresses Claude
5805089819 and completed review 5805109052. Independent review pending.

This batch tests four adjacent prerequisites together: a vertical-Kato gauge
conversion, a seam between distinct planes, repaired analytic phase lifts,
and role/content refusal controls. All are fixed synthetic fixtures. It does
not implement the full geometric q composer or execute the physical case.

## Chosen gauge route

Keep the CASE vertical-Kato convention. S0f projected-polar frames can supply
local anchors or charts, but cannot be substituted directly into its q formula.
Let F(y) be a differentiable real orthonormal frame for P(y), and A=F^T F'.
Then A is skew symmetric. Solve O'=-AO with O(y0) in SO(2). Orthogonality and
orientation are preserved; K=FO satisfies K^T K'=0 and spans P. Differentiating
PK=K gives (I-P)K'=P'K; the zero tangential connection gives PK'=0. Since
PP'P=0, K'=[P',P]K. This proves conversion to the Kato solution with the
specified initial condition. The initial condition must itself match the
CASE horizontal-base transport. Changing anchors between charts requires
matching their continuous oriented transitions and initial data.

For an approximate solution Otilde and exact skew A, set
D=Otilde'+A Otilde. Variation of constants and orthogonality of the exact
propagator give ||Otilde(y)-O(y)|| <= initial_error + integral ||D||.
If only Atilde is available, bound D by the computed residual plus
||A-Atilde|| ||Otilde||. A physical implementation still needs certified
derivative bounds, integration and whole-domain chart coverage. Those are OPEN.

## Analytic gauge control

Fix c=24/25, s=7/25 and E=((c,0,-s),(0,1,0)). Set F(y)=Rz(y)E,
0<=y<=1. Exactly E^T E=I and F^T F'=c J, J=[[0,-1],[1,0]].
O(y)=R(-cy) therefore gives Kato K=FO and O(0)=I. The test evaluates the
unreduced expression over a ball covering the entire interval, but that broad
enclosure is only diagnostic. Its certificate rests on the explicit analytic
identity and exact rational cancellation c-c=0, recorded separately. Leaving
O=I retains connection cJ and is refused. This fixture does not claim that F
is the S0f projected-polar chart or prove a generic numerical ODE solver.

## Distinct-fibre seam

F0=(e1,e2), F1=((c,0,-s),e2), S=diag(1,1,0). The fibres differ.
M=F1^T S F0=diag(c,1), so polar(M)=I for c>0 and J_exact=F1 F0^T.
The reviewed S0f primitive constructs the seam and applies its 19/20 gate.
c=24/25 passes; c=9/10 fails. The retained record gives the exact map columns
as balls. This is an algebraic fixture, not a physical sewing certificate.

## Exact repair and two lifts

The raw SO(2) path is R((2pi*n+delta)t), delta=1/5, n=1 or 2, on [0,1].
The branch gate |delta|<pi/3 makes delta the principal corner angle.
Right multiplication by R(-delta*t) closes the path exactly to R(2pi*n*t).
Each of its 32 steps changes angle by at most pi/8, strictly below pi/2;
thus the supplied variation and closure premises follow analytically for
this generated family. The reviewed phase routine returns integers 1 and 2.
Omitting repair produces an enclosure excluding the proposed integer and
is refused. delta=4 is refused at the principal-branch gate.

The generated joint loop vector is (1,2,-1). Its roles carry canonical JSON
SHA256 hashes over their analytic inputs and arithmetic results. Swapping
roles or editing an integer fails the expected-hash comparison; replacing
a lift reason by a conditional frame reason fails even with a recomputed
hash. Expected hashes are generated internally in this fixture. This tests
record consistency, NOT authenticity or external geometric dependency binding.
These loop integers are not identified with CASE q_a or q_b. Gauge, seam and
loop fixtures are still separate; joining them into the same exact geometry
is the next required composition gate. No physical class is certified.

## Execution and retained evidence

SPEC.json freezes 12 expected outcomes at 128 bits, one thread, 10 seconds
per job, 120 seconds overall and 1 GiB per worker, with no retries.
The runner checks the locked python-flint 0.9.0 / FLINT 3.6.0 wheel and
installed native artifact hashes before starting. It snapshots executed
sources and this derivation, writes atomic records, and binds them through
MANIFEST.json and COMPLETE.json using the reviewed S0b record machinery.
Python/version metadata is recorded; no broader reproducibility is inferred.

Reproduce with the existing locked installation:

    python -B research/benchmarks/certification_s0g_001/driver.py --wheel <locked-wheel> --output <fresh-directory>
    python -B research/benchmarks/certification_s0g_001/verify.py

The prior exploratory attempt is retained outside this release. The release
record is RUN/. Physical evaluations: zero. v078 ownership is unchanged.

## Dependency order after this batch

1. Independent audit of this gauge lemma, analytic fixtures and runner records.
2. One consistent synthetic geometry connecting the projector/frames to seams,
   corner repair and both lifts, with externally verified dependency hashes.
3. Full-dimension Riesz wrapping and projector-derivative bounds; freeze budgets
   from those measurements before the physical S1-S4 implementation/execution.

An audit finding that invalidates an upstream assumption takes priority over
downstream implementation. Passing fixtures cannot waive those dependencies.
