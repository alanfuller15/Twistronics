# Research questions 006: boundary sewing

The transport proof now has a partner hand audit, but applying it to the
physical finite-cutoff calculation still requires a justified boundary map.
This pass separates what the archived boundary code actually checks from
what an exact boundary identification requires. It changes no production
source and preserves all previous evidence.

## Main findings

The archived `shift_matrix` discards components translated outside the finite
index set. It is a partial isometry, not a unitary on the full finite space.
This follows algebraically for every nonempty finite index set and nonzero
translation. It does **not** imply a large error on the selected low-energy
subspace, whose boundary weight is a separate question.

Using exactly the 49 reciprocal indices retained in the v078p contract,
with four internal components per index:

| Axis | Ambient dimension | Shift rank, either valley | Lost indices per shift | `||I-S^T S||` |
|---|---:|---:|---:|---:|
| 1 | 196 | 168 | 7 | 1 |
| 2 | 196 | 160 | 9 | 1 |

The two same-valley shifts **commute exactly for this retained basis**.
The exact integer path inventory and matrix products both show zero corner
commutator, in both valleys. No ambient corner defect is reported here.
The shift also commutes with the fixed sublattice realification transform;
the numerical representation residual is below `2.45e-16`.

Those positive checks do not supply a selected-band, smooth, invertible
gluing map. In particular, commuting ambient contractions do not on their
own prove a cocycle for separately projected and polar-normalized maps.

## What the sewing tolerance means

For orthonormal endpoint frames F0,F1 and a contraction S, the singular
values checked by the archived gate combine two different effects:

```
I - (F1^T S F0)^T(F1^T S F0)
  = [I - F0^T S^T S F0] + [(I-P1)S F0]^T[(I-P1)S F0].
```

The first term is norm loss from truncation; the second is mismatch with
the selected endpoint subspace. A sewing loss limit of 0.05 permits either
corresponding amplitude up to `sqrt(0.0975)`, about 0.31225. It is **not a
0.05-radian phase-error bound**.

The fixed controls demonstrate the distinction:

- Pure contraction by 0.96 and a norm-preserving ambient rotation with
  overlap 0.96 both pass and produce the same singular values, despite
  different loss/mismatch mechanisms.
- Contraction by 0.94 is refused specifically for `sewing_loss`.
- In-plane rotations by 0.6, 1.4 and 2.4 radians have zero sewing loss and
  retain those angles in the returned polar factor. This is ambiguity
  relative to a separately declared identity transition, not evidence that
  every nonzero rotation is an invalid physical sewing.
- Four synthetic edge checks can all pass with zero loss while their
  corner transition products disagree by norm one. This tests the local
  link component, not a run of the full Euler API with variable sewings.

[DERIVATION.md](DERIVATION.md) proves the decomposition and bounds, gives a
narrow sufficient extension to constant commuting orthogonal sewings, and
states the extra obligations for selected-fibre polar sewings. No full
physical boundary certificate is claimed.

## Prior review correction retained

[Review 5287972357](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5287972357)
corrected the partner's denominator-free mesh-sizing expression. The exact
accumulated upper bound requires

```
N^2 > p*(q+p^2)*ell^3/(6*target) + p^2*ell^2/2.
```

At the three earlier conditional cell-gap values, taking ell=1 and
target=pi/4 gives sufficient integers 154, 722 and 107 for that algebraic
bound. These are **not selected physical meshes**: the earlier cell gaps
do not certify a unit-length loop, the arithmetic is not interval-enclosed,
and the remaining real-structure, boundary and orientation hypotheses have
not been established for a physical domain. No such loop was executed.

## Checks and reproducibility

The first declared run exited 0: **76/76 checks passed**. Counts include
intentional refusals and demonstrated limits, not 76 physical predictions.
Python 3.12.14 and NumPy 2.3.5 were used with one BLAS thread. There was no
failed attempt or post-result threshold adjustment.

- [PLAN.json](PLAN.json) binds six repository sources and three nested
  archive identities, with cases and thresholds fixed before execution.
- [sewing_audit.py](sewing_audit.py) reads the archives and compiles only
  the unchanged `shift_matrix`, `Rejected`, `Policy`, `Sampler`, and
  `sewing` definitions. Module imports/activation are not executed.
- Only `Sampler.link` and shift construction are exercised; `Sampler.frame`
  and all physical Hamiltonian/eigensolver/consumer methods are never called.
- [RESULTS.json](RESULTS.json) retains every check, the full index list,
  lost-index inventories, synthetic matrices, link ledgers and sizing data.
- [RUN.log](RUN.log) and [RUN_RECEIPT.json](RUN_RECEIPT.json) retain the
  captured output, command and actual exit code. The reported wall time is
  the execution tool's elapsed time, not a benchmark.
- [MANIFEST.json](MANIFEST.json) hashes the seven other package files.

Run from the repository root with the pinned NumPy version:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -B research/benchmarks/research_questions_006/sewing_audit.py --output NEW_DIRECTORY
```

An existing output directory is refused. This is a bounded component audit,
not a production replay, physical-model numerical sweep or independent
physical validation. Exact integer identities are distinguished from
floating-point diagnostics. The derivation is pending Claude's focused
review, not formally machine-verified.

## Next gate and ownership

Establish a uniformly controlled selected-fibre boundary map, its relation
to the intended physical translation, its corner compatibility, orientation
and connection/phase contribution. Merely tightening `sewing_loss_max` does
not supply those facts. Certified arithmetic and domain-wide isolation
remain separate requirements. The original conversation still owns Fable's
v078 corrections; the sign-convention question is unchanged. No graphene
Euler value, braid-label change, cutoff-convergence result or merge follows.
