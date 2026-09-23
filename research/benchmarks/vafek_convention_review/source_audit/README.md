# Signed-convention audit of arXiv v2

**Status: source comparison completed; convention selection remains UNRESOLVED, pending partner review.**

Direct evaluation of the checked arXiv-v2 Hamiltonian and flat-band columns gives the sign used by `Model.direct_projection`. The printed projected formula gives the sign used by `Model.h`. Our calculation therefore leaves an equation-level sign question after accounting for basis phases. It does not establish an author-confirmed correction, select a production model, or evaluate the later journal equations.

This is an additive follow-up to [the original diagnostic](../README.md), commit `caa700bfa285b889502bc902779b114b868b1aad`, and the Q-reversal review on [PR #2 at f052fcb](https://github.com/alanfuller15/Twistronics/tree/f052fcb7dfd15ae376f5b9de93919678d33c4ef5/docs/convention-review). Their sources and evidence are unchanged.

## Sources and version boundary

Checked on 2026-09-23: [arXiv:2502.08700v2 HTML](https://arxiv.org/html/2502.08700v2) and [v2 PDF](https://arxiv.org/pdf/2502.08700v2). The PDF pages containing A10 and B25-B28 were also rendered and inspected visually. The relevant signs and phases agree with the HTML. [SOURCE_RECEIPT.json](SOURCE_RECEIPT.json) records resource hashes, equation-element hashes, and the HTML/PDF numbering crosswalk.

The [journal landing page](https://journals.aps.org/prb/abstract/10.1103/rr5g-3js8) lists revision on 2025-08-12 and publication on 2025-09-15. arXiv v2 is dated 2025-02-18. The journal's full text was not accessible without authorization. We have not established whether it differs at these equations. The source-access blocker from Claude's environment is resolved here for **arXiv v2 only**.

## Signed mapping

Equation numbers below are HTML / PDF. The code column states our checked mapping; it does not attribute our dimensionless variable names to the authors.

| Item | Source location and signed input | Mapping to the unchanged model |
|---|---|---|
| Orbital order | 26 / A1: two components each in c-Gamma3, c-Gamma1+2, f | Six-component blocks, then a documented valley/sector permutation |
| Pauli and valley order | 28-29 / A3-A4: K, K-prime; time reversal exchanges valleys and conjugates | Standard Pauli matrices; minus valley evaluated at minus momentum, then conjugated |
| Velocity | Table 1: v = -4.3 eV Angstrom | -4300 meV Angstrom |
| Hybridization | Table 1: gamma = -24.8 meV | Same sign; v/gamma > 0 |
| c-f strain coupling | Table 1: c-doubleprime = -3362 meV | Same sign |
| Strain | Section II: epsilon-minus = -(1+0.16)epsilon/2 | -0.00087 at epsilon = 0.0015 |
| Coordinates | Our definition: K = v k/gamma, Q = v q/gamma | Positive scale for the tabulated parameters |
| Boost | 42, 86 / A17, B41: K valley k+q/2; K-prime k-q/2 | x+Q/2, x-Q/2; no reversal introduced |
| c2-f block | 35 / A10: -i c-doubleprime epsilon-minus sigma3 for zero shear | Direct assembly's upper c2-f block |
| Flat columns | 70-72 / B25-B27 | Related to code columns by D = sign(gamma) diag(1, exp(3i theta)) in K valley |
| Parent density | 57, 74 / B12, B29: P = Of transposed | Gives the implemented z z-dagger, z=(1,i,i,1)/2 |
| Printed scalar | 73 / B28: +2 gamma c-doubleprime v ky epsilon-minus / (gamma squared + v squared k squared) | Literal assembly; opposite to our direct projection below |

The declared projection retains M, Mf and c-doubleprime, sets v-prime and subleading terms to zero, and omits damping and relaxation terms. Interaction constants remain the existing rounded benchmark values. This audit does not certify their accuracy for the full paper or an experiment.

## Our derivation and the role of phases

Write x=vkx/gamma, y=vky/gamma, c=c-doubleprime, e=epsilon-minus, d=1+x squared+y squared. Solving the unperturbed kernel condition in the K valley gives a normalized two-column matrix

```text
W = (0; I; -(x I + i y Z)) / sqrt(d).
```

For nonzero momentum, the printed columns reduce at v-prime=0 to `U_paper = W D`, with `D = sign(gamma) diag(1, exp(3i theta))`. At the origin we choose theta=0. This phase relation is checked using the original physical-unit angular formulas rather than assumed. The sign(gamma) arises from gamma/sqrt(gamma squared); dropping it before comparing individual columns would be misleading. The other valley follows by time reversal. In the four-column boosted projection, both valley phases are included before comparison to code.

For `C=I/sqrt(d)`, `F=-(x I+i y Z)/sqrt(d)`, and the checked upper strain block `T=-i c e Z`, our direct algebra gives

```text
C† T F + F† T† C = -2 c e y I / d.
```

The corresponding scalar in the printed projected expression is `+2 c e y I/d`. The difference in **single-valley trace** is therefore `8 c e y/d`. It is independent of the internal two-column unitary gauge. This isolates the sign question without using any parent state, boost, inter-valley interaction, eigenvalue ordering or node search.

At our retained K=(0.23,-0.17) witness, that trace difference is -3.6771292291 meV. Rephasing the second column removes angular differences in the non-scalar terms, but cannot remove the scalar trace difference. We have found no extra sign instruction in the checked passages that would reconcile these two routes while retaining the same declared coordinates and coupling signs. This is our source-reading and algebraic inference, pending independent review.

The earlier result remains valid: the two implemented four-band families are related by Q reversal and a valley/orbital unitary. That re-labeling does not determine which same-signed physical q is intended in a specific source figure or in a later journal version. A change to gamma alone is not a solution: at fixed physical momentum, coordinates must change with gamma; at fixed dimensionless coordinates, the kernel relation retains its minus sign. The artificial positive-gamma control verifies the latter algebra and is not a proposed published parameter choice.

## Retained fixed diagnostic

[reproduce.py](reproduce.py) independently transcribes six-component, physical-unit Hamiltonian blocks and the printed angular columns. It assembles two valleys and the source parent-density formula, then compares the projected matrices to the unchanged, hash-checked `model.py`. It uses seven specified cases: six earlier points/zero controls and one artificial gamma-sign control. These are diagnostic cases, not preregistered observations or a numerical sweep.

[RESULTS.json](RESULTS.json) retains matrices, spectra, all residuals, source hashes and 76 enforcing predicates. [RUN.log](RUN.log) records the exact command and exit status. Observed:

- All 76 predicates pass; largest checked residual is 7.11e-14.
- The source-column kernel, orthonormality, gauge relation, scalar projection, parent transpose and both interaction blocks satisfy their checks.
- The full source projection, converted to the code gauge, agrees with the direct assembly at all seven fixed cases.
- The prior same-Q adjacent-gap witness remains 1.5320713556 meV. Axis, origin, zero-coupling and zero-strain controls remove the scalar discrepancy as predicted.

Reproduce from the repository root, choosing an unused output path:

```sh
OPENBLAS_NUM_THREADS=1 python -B research/benchmarks/vafek_convention_review/source_audit/reproduce.py --output /tmp/source-audit-new.json
```

The script checks the model's SHA-256 before importing it and refuses to overwrite output. It does not fetch the paper or automatically validate its own transcription: primary-source reading remains a separate review step. The source receipt binds the accessed documents and equation locations. The manifest binds all files in this folder except itself.

## Next decision and limits

Claude should challenge the signed mapping, source-column phase relation, trace derivation and physical-unit reproduction against the cited v2 passages. A later journal text comparison or author clarification is still needed before describing the issue as a published correction or claiming to reproduce the paper's intended signed trajectory. A reviewer may instead identify a missing convention and close this question; the present evidence must remain available either way.

Both project assemblies remain frozen. This review chooses no replacement implementation and validates no roots, node inventory, braid, Euler class, continuum campaign or experimental effect. Original v078 consumer corrections remain owned by the separate Fable conversation.
