# Research questions 004: bounding transport between samples

This pass supplies an explicit proposed bound between continuous sphere
parallel transport and the archived routine's polar-overlap product. Together
with a curvature bound, it gives sufficient conditions for recovering the
correct winding in exact arithmetic for the declared synthetic references.
The argument is submitted for partner proof review; it is not a floating-point
certificate or a graphene invariant.

It addresses the missing transport step identified in
[Claude's review](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5790083941)
and the [subsequent qualification](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5287576450).

## Main result

For `n=d/||d||`, `d=(sin(a*x),sin(y),m+cos(a*x)+cos(y))`, with integer
`a>=1` and `m=-1` or `-3`, the true y path satisfies `||n_y||<=1`,
`||n_yy||<=4`, and the tangent-plane curvature satisfies `|f_xy|<=a`.
Interpolating the true path to its normalized chord gives

```
per-link angle error <= v*A*h^3 / (12*(1-A*h^2/8)^2),
provided A*h^2/8 < 1.
```

For y loops with `h=2*pi/N_y`, use `v=1`, `A=4` and multiply by `N_y`
to obtain `E_loop`. When adjacent oriented normals are acute, polar links
are exactly backward transport on the short normal geodesics. The sufficient
transverse unwrapping condition is then

```
2*pi*a*h_x + 2*E_loop < pi.
```

Replacing pi by pi/2 also guarantees the calibrated phase policy. Identity
sewings, consistent fibre orientation, and the overlap floor are accounted
for separately in [DERIVATION.md](DERIVATION.md). A large sampled overlap
alone does not establish these path hypotheses.

For the once-folded model on square grids:

| Intervals per axis | Loop error bound (rad) | Combined step bound (rad) | Exact unwrapping condition | pi/2 policy bound |
|---:|---:|---:|---|---|
| 24 | 0.15391606 | 1.95276619 | Sufficient | Inconclusive |
| 48 | 0.03650980 | 0.89548663 | Sufficient | Sufficient |
| 96 | 0.00901028 | 0.42925408 | Sufficient | Sufficient |

Thus the proposed argument connects the smooth reference to the estimator,
rather than relying on agreement between meshes. The 49- and 97-fold
textures fail the sufficient hypotheses on these grids. The earlier retained
97-fold examples still return about 2 at 48 and 96 intervals despite analytic
Euler 194; this pass refuses to certify them. Failure of a sufficient bound
is not generally proof that an estimate is wrong.

## Checks and retained outcomes

The accepted run exited 0 in 1.76 seconds; **67/67 declared predicates** held.
They include expected failures and checks of bound arithmetic, not 67
independent scientific validations.

- Three acute-link controls agree with exact short-arc transport to less than
  `3.8e-16` in operator norm. The obtuse control has overlap `0.737394`, above
  the production floor 0.5, but transport discrepancy 2 and polar determinant
  -1. This documents why the acute-normal hypothesis matters.
- Six latitude polygons obey the ribbon bound when compared with their exact
  continuous holonomy. Two ODE solutions also agree with the exact latitude
  values at the declared tolerance.
- Fourteen fixed continuous sphere loops were integrated and compared with
  28 frozen production phases from questions 002. Maximum angular discrepancies
  are `0.00328349` rad at 48 and `0.00082013` rad at 96, below their respective
  bounds. The ODE is a numerical diagnostic, not an exact solution enclosure.
- Two fresh calls to the unchanged archived routine at 24 by 24 distinguish
  policy rejection from winding correctness: the calibrated pi/2 policy
  rejects a maximum step `1.5840365264` rad; the original default 3*pi/4 policy
  returns oriented Euler `1.9999999999999998`. Both policies were declared
  before the run. The calibration policy was not relaxed after a failure.

The first attempt failed while serializing a NumPy boolean into JSON. Its
source, original plan, traceback and process receipt are retained in
[attempt01_serialization_failure](attempt01_serialization_failure).
It produced no saved result table and supports no pass-count claim. The only
source change before the second attempt casts that boolean to native `bool`;
the plan's source hash and provenance were updated. Cases, mathematical
formulas and thresholds are unchanged.

## Further analytical progress and limits

The derivation also closes a symbolic derivative step for the retained
direct-projection expression: along a unit K direction, `||H'||<=94` and
`||H''||<=470` in the source's units. For an isolated rank-r Hermitian
cluster with true uniform external gap g, `||H'||<=L`, `||H''||<=M`,

```
||P'|| <= sqrt(r)*L/g,
||P''|| <= sqrt(r)*M/g + 6*r*L^2/g^2.
```

Moving-basis terms for the embedded projector are included. These are
conditional symbolic bounds, not a numerical domain certificate. A general
Grassmannian transport-error argument, verified real structure, finite-cutoff
sewings, domain-wide isolation and certified arithmetic remain open.

The sphere result is exact-arithmetic mathematics. No certified numerical
phase error is supplied for the eigensolver, SVD, ODE or angle operations.
No physical sign convention, braid or experimental conclusion follows here.
Fable's v078 consumer/verifier corrections remain separately owned.

## Reproduction and provenance

[PLAN.json](PLAN.json) binds seven sources and all declared cases;
[transport.py](transport.py), [RESULTS.json](RESULTS.json), [RUN.log](RUN.log)
and [RUN_RECEIPT.json](RUN_RECEIPT.json) retain the accepted execution.
[MANIFEST.json](MANIFEST.json) hashes the entire package except itself,
including the failed attempt. Pre-run plans are workflow records, not
independent timestamp attestations. Prior evidence packages are unchanged.

From the repository root, with questions 001's pinned dependencies:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -B research/benchmarks/research_questions_004/transport.py --output NEW_DIRECTORY
```

An existing output directory is refused. Full frame/link streams are hashed,
but only selected extrema, refusal records and complete Wilson phases are
retained. The accepted environment was Python 3.12.14, NumPy 2.3.5 and
SciPy 1.17.0. No production module was edited.
