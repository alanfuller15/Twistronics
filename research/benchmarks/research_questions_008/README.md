# Research questions 008: corrected seam index and joint reference gate

Status: retained proposed derivations and fixed controls, awaiting Claude's
independent review. Previous evidence is frozen.

## Progress

The previous pass repaired one corner and exposed the physical-reference
ambiguity. This pass proves the proposed left/right seam correction under
explicit rank-two orientation and corner hypotheses, and gives a concrete
abstract extension through the corners.

The corrected integer is

    q = (Delta phi - integral k1 dy)/(2 pi)
      = (Delta beta - Delta alpha)/(2 pi),
    e = -q in the declared orientation.

The rectangle connection cancels from q. A raw vertical scan can be zero
while the missing left/right seam term carries one full integer. The proof
also records the corresponding curvature-plus-two-seams identity.

An explicit gauge converts the boundary data to J1=I and
J2=R(2 pi q x/Lx). Extending that gauge constructs exact deck transition
maps and a compatible metric connection on the whole plane, hence an
abstract torus bundle. This resolves abstract collar existence for the
stated data. Preserving a prescribed physical projector connection or
Hamiltonian translation remains a separate obligation.

## A material qualification for the next cutoff comparison

The q007 uniform-distance-below-2 criterion is valid for already CLOSED
transition loops. Arbitrary pairs of edge maps need a joint corner test.
Here is a counterexample against using separate distance-2 screens alone:

| Quantity | Retained value |
|---|---:|
| Uniform first-edge distance from identity | 1.9753766811902755 |
| Uniform second-edge distance from identity | 0.31286893008046174 |
| Difference of joint gluing integers | 1 |
| Corner defect halfway through naive interpolation | 2 |

Both complete edge systems close their corners. The individual edges are
not closed loops. Their joint class differs despite both uniform distances
being strictly below 2. The analytic endpoint extrema supply these uniform
bounds; sampling alone is not used to infer them.

For principal relative edge angles gamma1,gamma2, require
Delta gamma2-Delta gamma1=0. A conservative sufficient norm condition is
rho1+rho2<pi, with rho_i=2 asin(eta_i/2) and uniform eta_i<2.
The condition is meaningful only after a declared common-fibre
identification over the whole rectangle. It remains a finite relative
comparison, not a physical reference or cutoff-convergence result.

Matching second-order jets at one point is also insufficient for an exact
collar cocycle: R(s^3) supplies the retained counterexample. Our constructive
extension satisfies the entire cocycle identity instead.

## Retained validation

First execution: **58/58, exit 0**, Python 3.12.14, NumPy 2.3.5.
There were no failed attempts or post-result threshold changes.

| Fixed case | Raw phase change / 2 pi | Corrected q | Declared e |
|---|---:|---:|---:|
| Left/right twist with flat rectangle connection | 0 | -1 | +1 |
| Mixed seams with polynomial connection | 2.331042281631142 | 3 | -3 |
| Zero class with polynomial connection | 0.3676479185422782 | 0 | 0 |
| Top/bottom twist | 1 | 1 | -1 |

The maximum fixed collar-cocycle residual is 6.71860e-15. The maximum
full connection-compatibility residual is 2.05391e-15. These floating-point
checks illustrate the analytic identities; they are not interval proofs.

Six rational interval controls, expressed in turns, check unique-integer
acceptance and refusal of empty, ambiguous or invalid enclosures. Their
decisions use exact Fraction arithmetic. They do not certify any geometric
quantity or supply outward-rounded physical error bounds.

## Contents and reproduction

- DERIVATION.md: complete proofs, assumptions, counterexamples and the
  conditional numerical certification contract.
- UPSTREAM.json: exact text/IDs of Claude's q007 review and Codex's response.
  Partner reruns remain reported scratch evidence.
- PLAN.json: five source bindings, fixed cases, tolerances and expected
  outcomes, frozen before execution.
- seam_index.py: bounded synthetic diagnostic with no production imports.
- RESULTS.json, RUN.log and RUN_RECEIPT.json: complete first-run evidence.
- MANIFEST.json: SHA-256 for all eight other package files.

From the repository root, with an output directory that does not exist:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -B research/benchmarks/research_questions_008/seam_index.py \
  --output /tmp/twistronics-questions008-fresh
```

No physical Hamiltonian, eigensolver, numerical sweep, production API,
v078 repair or merge is part of this package.

## Next evidence gate

Claude is asked to audit the corrected index and Euler sign, the full deck
cocycle and connection transformation, the joint comparison condition,
and the distinction between abstract and prescribed physical collars.

Before a physical two-cutoff comparison, declare the model and selected
real oriented fibres, common-fibre identification, physical reference and
exact corner construction. Then provide uniform isolation, boundary and
error bounds. More passing finite samples alone cannot fill these gaps.
