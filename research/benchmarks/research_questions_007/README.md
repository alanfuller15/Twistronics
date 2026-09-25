# Research questions 007: controlled corner repair and reference ambiguity

Status: proposed exact-arithmetic construction, awaiting partner proof review.

The previous pass found that individually acceptable sewing links can fail
the corner cocycle. This pass supplies a concrete repair for a specified
oriented real rank-two edge system, with explicit costs. It also shows why
closing corners cannot by itself choose the physical bundle.

## What is established under the stated hypotheses

For two corner paths A,B with eta=||A-B||<2, let delta be the principal
angle of A*B. Multiply one boundary transition by the intrinsic rotation
`exp(delta*chi(x/Lx)*I_x)`, using the fixed quintic chi.

- The corner equation closes exactly in exact arithmetic.
- The largest change to the repaired edge map is eta; this is optimal
  when the other three corner maps and the starting endpoint are fixed.
- The added covariant connection-defect bound is
  `15*|delta|/(8*Lx)` pointwise and `|delta|` integrated along the edge.
- Curvature flux plus the covariant seam defect controls transverse
  phase variation. The derivation states the extra compatibility needed
  before treating that interval scan as a periodic winding.

This closes a limited algebraic repair question. It does not certify the
physical reference transition, all collar/derivative compatibility, or
global descent of the original projector connection.

## The reference ambiguity matters

The explicit constant-plane construction `J1=I`, `J2(x)=R(2*pi*m*x/Lx)`
has exact corners, positive orientation and zero singular-value loss at
every point for every integer m. Its declared compatible metric connection
has Euler value -m in the stated orientation, and backward winding m.
These are different synthetic glued bundles. They share local acceptance
properties; those properties do not select the physical topology.

A uniform distance below 2 between already consistent SO(2) transition
loops supplies a useful sufficient relative-homotopy check. Sampled
distances do not suffice: the retained 16-turn example looks like identity
at 16 interval endpoints yet is antipodal at the first midpoint.

## Retained outcome

First execution: **60/60 checks, exit 0**, Python 3.12.14, NumPy 2.3.5.
There was no failed attempt and no threshold adjustment.

| Declared scalar corner angle | Original defect eta | Repaired corner residual | Added connection bound, Lx=2 |
|---:|---:|---:|---:|
| 0.0814555875953 | 0.0814330703437 | 2.29e-16 | 0.0763646133706 |
| 0.000505966774673 | 0.000505966769276 | 5.55e-17 | 0.000474343851256 |

These two input angles come from Claude's retained fixed-matrix examples.
They are realized here in explicitly declared two-dimensional boundary
coordinates. This is not a reconstruction of a physical band boundary.
The other controls are zero, positive and negative principal angles,
endpoint gauge covariance, profile derivatives, the flux/seam identity,
orientation/nonisometry/branch-cut refusals and three integer twists.

The maximum repaired-corner residual across all five declared cases was
2.37631e-16; the maximum gauge-covariance residual was 3.79194e-16.
The 16-turn alias had sampled distance at most 1.07794e-14 and midpoint
distance 2. Numerical values are ordinary floating point, not enclosures.

## Evidence and reproduction

- `DERIVATION.md`: hypotheses, construction, norm and derivative bounds,
  seam-aware variation formula, integer ambiguity and primary-source context.
- `UPSTREAM.json`: exact-commit identities of the corrected partner note
  at `fe5438438ea3bcac5e0a70011f660bf7001d0835`, its numerical inputs and
  verified four-file manifest. This also verifies the requested prose
  correction to the orthogonal-control value; no new acknowledgment was sent.
- `PLAN.json`: six source bindings, cases and tolerances fixed before execution.
- `boundary_repair.py`: bounded synthetic calculation; no production imports.
- `RESULTS.json`, `RUN.log`, `RUN_RECEIPT.json`: complete outcome and provenance.
- `MANIFEST.json`: SHA-256 of the other eight package files.

From the repository root, choose a fresh output directory:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -B research/benchmarks/research_questions_007/boundary_repair.py \
  --output /tmp/twistronics-questions007-fresh
```

The directory must not already exist. The script checks bound input hashes
before its calculation, retains failed predicates and returns nonzero on
failure. The profile's continuous maxima come from the proof, not the
sampled checks. No numerical sweep, physical eigensolver or production
Euler API is executed. All previous research-question packages are frozen.

## Next review and physical gates

Claude is asked to audit multiplication order, orientation, principal-log
hypotheses, the derivative cost, periodicity qualifications and the signed
synthetic Euler calculation. A short-arc choice alone is not a physical
selection rule. The next physical gate is a justified reference transition
or relative homotopy class, followed by uniform boundary/collar and
connection control, certified arithmetic, real structure and isolation.
Fable's v078 corrections and the paper's sign convention remain separate.
