# S0d: projector, seam-map and continuous-lift primitives

2026-09-23. This additive successor implements the bounded next step from
Claude source comment 5799275603 and completed Codex
[review 5294252575](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5294252575).
It preserves S0a-S0c and the declared physical case unchanged. The package is
synthetic and awaits independent review. Physical S1-S4 remain unimplemented,
unexecuted and budget-unfrozen.

## 1. Reviewed clarifications H1-H4

**H1 — the branch gate is charged through approximations.** If each two-map
path has error `b=2 eta+eta^2`, then an observed approximate distance `d_tilde`
certifies the exact gate only when

`d_tilde + 2 b <= 1`.

At `eta=1/128`, `b=257/16384` and the maximum admissible approximate
distance is `7935/8192 = 0.9686279296875`. The positive control uses `15/16`;
the refusal control uses `63/64`, which is below one but exceeds the charged
threshold. The exact gate gives `|delta|<=pi/3`; adding the declared `3/16`
corner allowance remains separated from the principal cut at `+-pi`.

**H2 — congruence inputs share provenance.** The new boundary accepts one
enclosed tuple `(V,H0,Hx)` and constructs `V^T H0 V`, `V^T Hx V` and `V^T V`
inside the certified function before invoking the reviewed spectral-window
primitive. The fixed six-dimensional control certifies the declared pair
`[2,3]` with counts 2 and 4. It is a binding test, not a physical S1 run.

**H3 — recognized enclosure overflow is inconclusive.** Only the explicit
backend messages `nonfinite bound` and `nonfinite LDL pivot` are translated to
`INCONCLUSIVE / NONFINITE_ENCLOSURE`. The fixed control reaches this from the
exponential of a finite enclosure large enough to exceed the backend range;
it does not inject a nonfinite input. Shape, schema and unrelated exceptions
remain execution errors. Separate fixed controls reach both classifications.

**H4 — conditional budget naming is explicit.** The reviewed ledger now
returns `BUDGET_CONDITIONALLY_SUFFICIENT`. This name is reserved for a
sufficient inequality under supplied error assumptions; it is not a geometric
or physical certificate.

## 2. Circular Riesz quadrature

For a real self-adjoint `H`, circle center `c`, radius `r`, and `N` roots of
unity, the trapezoid sum collapses algebraically to

`Q_N = [I - ((H-cI)/r)^N]^-1`.

If the target spectrum obeys `|lambda-c|/r <= alpha < 1` and all other
spectrum obeys `|lambda-c|/r >= beta > 1`, spectral calculus gives

`||Q_N-P|| <= alpha^N/(1-alpha^N) + 1/(beta^N-1)`.

The implementation adds the full Frobenius radius from interval evaluation
as a sufficient operator-norm debit. It does not infer the spectral split;
that remains an explicit upstream certificate. The positive fixture uses a
Householder-rotated spectrum `[-3,-2,0,0,2,3]`, circle `(c,r)=(0,1)`,
`alpha=0`, `beta=2`, and eight nodes. Its analytic term encloses `1/255` and
the total is below `1/64`. A four-node control using only the valid but weak
lower bound `beta=5/4` refuses the same target budget.

## 3. Oriented polar and seam-map enclosure

For a 2x2 overlap `M`, define

`a=M00+M11`, `b=M10-M01`, and
`U=[[a,-b],[b,a]]/sqrt(a^2+b^2)`.

When the denominator and positive determinant are certified, `U` is the
orientation-preserving polar factor. The seam primitive accepts two common-
ambient frame enclosures, checks their Gram defects, constructs `M=F^T G`
internally, and evaluates `F U G^T` with outward rounding. The interval radius
of the complete expression bounds uncertainty from the supplied frame balls,
polar evaluation and arithmetic. The positive 3x2 fixture fits the `1/128`
map budget. A reflection overlap makes the conformal denominator exactly zero
and is refused before division.

This establishes a primitive on the specified synthetic inputs. It does not
certify physical frame enclosures, intended translation, oriented torus
gluing, or corner compatibility.

## 4. Continuous phase lift and integer isolation

For ordered phase-vector enclosures `(c_j,s_j)`, every sample must remain
nonzero and every adjacent dot product must be separated above a fixed floor.
Then the local increment is evaluated on one continuous branch as

`theta_j = atan(cross(z_j,z_{j+1}) / dot(z_j,z_{j+1}))`.

The primitive sums the interval increments, separately checks endpoint
closure, and accepts an integer only when the entire quotient interval
`sum(theta_j)/(2*pi)` lies strictly inside one nearest-integer cell. Sixteen
fixed samples around one positive turn certify integer `+1`. A direct
antipodal step is refused at the local branch gate. A wider, still locally
separated enclosure reaches the final integer test and remains inconclusive.

The routine does not sample an unknown continuous physical path: its input
must already enclose the whole per-step variation and endpoints. Nor does it
construct the physical corner repair. Those are upstream S2-S4 obligations.

## 5. Evidence boundary and remaining work

The frozen specification contains 13 jobs at 128-bit precision, one worker,
30 seconds per job, 180 seconds overall, 1 GiB address space and no retries.
The first fixed run completed all expected behaviors: six synthetic
CERTIFIED implications, six INCONCLUSIVE controls and one deliberate
EXECUTION_ERROR. Ten protocol checks passed. The run snapshots every source
dependency and reports zero physical evaluations.

The next gate is independent reproduction and audit. After that, S0 still
needs composition tests tying projector error to continuous frames, seam maps,
the exact principal repair, both repaired edge lifts and the final joint
relative integer enclosure. Only then should the fixed physical case enter S1.
No physical gap, frame, seam, winding, Euler class or cutoff agreement is
claimed here.
