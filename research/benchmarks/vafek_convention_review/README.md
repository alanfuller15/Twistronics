# Off-axis convention: a narrower, reproducible question

**The two existing projected-model assemblies differ by an explicit valley-diagonal term. At a nonzero boost, their band spacings differ, so a common energy shift or a pointwise unitary basis change alone cannot reconcile that witness. Which convention is physically intended remains unresolved.**

This advances the [earlier benchmark](../vafek_2025/README.md) by separating three questions: the origin of the matrix difference, whether it affects the spectrum beyond an energy offset, and what outside clarification is still needed. The old model, results and interpretation are preserved unchanged.

## Algebra in the implemented gauge

Use dimensionless momentum `(x,y)=vk/gamma`, boost `Q=vq/gamma`, and the existing fixed flat-band gauge. Write `c=c_doubleprime`, `e=epsilon_minus`, `d=1+x²+y²`. The conduction and f components in one valley are

\[
C=I/\sqrt d,\qquad F=-(xI+iy\sigma_3)/\sqrt d,
\qquad T=-ice\sigma_3.
\]

The c–f contribution to the direct projection is obtained without an eigensolver:

\[
C^\dagger TF+F^\dagger T^\dagger C
=-\frac{2cey}{d}I.
\]

For completeness, the other two retained one-valley terms are

\[
C^\dagger M\sigma_1 C=\frac{M\sigma_1}{d},\qquad
F^\dagger \delta\sigma_2 F
=\frac{\delta[-2xy\sigma_1+(x^2-y^2)\sigma_2]}{d}.
\]

The literal projected assembly uses the opposite sign for the scalar c–f term. The other displayed terms and the implemented projected interactions agree. Applying the implemented time reversal and boost conventions gives

\[
H_{\rm literal}-H_{\rm direct}
=4cey\;\mathrm{diag}(d_+^{-1},d_+^{-1},-d_-^{-1},-d_-^{-1}),
\quad d_\pm=1+(x\pm Q/2)^2+y^2.
\]

This is an algebraic diagnosis of **our implementations in the stated gauge**, not a correction to the paper. The numerical checks below test the assembled matrices against that expression; finite samples alone are not a general symbolic proof.

## Retained small-matrix checks

Seven fixed cases cover Γ, an axis point, two finite-boost off-axis points, an unboosted point, zero c–f coupling and zero strain. They use the original rounded benchmark parameters. [PLAN.json](PLAN.json) records inputs and tolerances; it explicitly notes that five points were explored before the retained run. This is not a preregistered independent test set.

At the main witness `(x,y,Q)=(0.23,-0.17,0.5)`, the maximum adjacent-band-spacing discrepancy is approximately **1.53207 meV**. Adjacent spacings survive both unitary conjugation and adding one scalar times the identity. Their disagreement therefore rules out that restricted explanation at the same momentum and parameters. It does not rule out a transformation of coordinates, boost, strain or the parent-state convention.

The unboosted off-axis case is instructive: the matrices differ, but their spectra agree to roundoff at that sampled point. A matrix-entry difference alone would not establish spectral inequivalence. Conversely, Γ and axis checks cannot detect this term because it vanishes at y=0. Zero-coupling and zero-strain controls also remove the discrepancy.

The retained run's exact matrices, spectra, formula residuals and verdicts are in [RESULTS.json](RESULTS.json), bound to source and plan hashes. Runtime and exact residuals are recorded there; [RUN.log](RUN.log) holds the command result. No node search, continuation, charge transport or large numerical sweep was performed.

## Source and next scientific gate

The reference is [Herzog-Arbeitman et al., arXiv:2502.08700v2](https://arxiv.org/html/2502.08700v2), checked on 2026-09-23. Equation numbers here use the HTML sequence: the c–f block in 35, flat-band vectors in 71–72, projected term in 73, and mean-field interaction in 74. The v2 reference is fixed; this note does not compare later versions or claim author agreement.

The next question is precise: **Does the derivation use a simultaneous coordinate/basis/strain/boost or parent-state convention change between these expressions, or is one of our transcriptions wrong?** A useful answer must state that transformation and recover the same off-axis spectra, not only Γ or axis formulas. Check the negative gamma convention and the flat-band column phases explicitly. Until this is settled, neither assembly is promoted as the accepted published braid benchmark.

The plan is to obtain a separately checked derivation, freeze the resulting convention with off-axis controls, and only then revisit the benchmark's full node sequence. No new outreach message has been sent. This diagnostic makes no experimental, novelty, full-braid or Euler-class claim.

## Reproduce

From the repository root with the [existing benchmark dependencies](../vafek_2025/requirements.txt):

```sh
OPENBLAS_NUM_THREADS=1 python research/benchmarks/vafek_convention_review/diagnose.py --output /tmp/twistronics-convention-new.json
```

The output must not already exist. The baseline model hash is checked before import. Exit zero means the diagnostic and its controls were reproduced; the recorded convention status still remains unresolved. Both old assemblies were written within this project, so this is not independent external validation.
