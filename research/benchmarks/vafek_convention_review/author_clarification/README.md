# Author clarification: reviewed qualifications incorporated

Prepared 2026-09-23 from PR #4 at `8eefe10d93c5f30d713c3da7e85d77ad285ab517`. **Draft only; not sent.** [AUTHOR_QUESTION.md](AUTHOR_QUESTION.md) supersedes the question in `source_context_review/`, which remains unchanged as review history.

This revision incorporates [Claude comment 5789193155](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5789193155) and [Codex review 5286979704](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5286979704). It adds a self-contained projection, explicit parameter qualifications, both HTML/PDF equation numbers, absolute evidence links, and the missing K subscript on B28's right factor. It does not turn that missing subscript into evidence of an intended valley exchange.

One point in the partner feedback was corrected: the omission of M-prime is explicitly declared immediately after B28. The end of Sec. II also states the mu1/mu2 simplification. [SOURCE_PROSE.json](SOURCE_PROSE.json) now retains those passages and the K-first column-order prose after B31, with source anchors, extraction method and hashes. All come from the same previously retained arXiv v2 HTML; this is not independent retrieval by a second reader.

## Algebra and scope of the question

Let `N=gamma²+v²(kx²+ky²)`, with real parameters and nonzero gamma, and use the six-component flat-band frame `W=(0,C,F)^T`, where

\[
C=\gamma I/\sqrt N,\qquad F=-v(k_xI+i k_y\sigma_3)/\sqrt N.
\]

This is a comparison gauge of the printed K-valley columns, not an assertion that the paper explicitly chooses it. At nonzero k with the printed polar angle theta, `W=U_K diag(1,exp(-3i theta))`. For the unperturbed Hamiltonian at `M=v'=0`, the nonzero first block of `h0 W` cancels as `v(kx I+i ky sigma3) C+gamma F=0`; also `W†W=I`. As in the retained audit, M is then restored as a first-order perturbation.

For `T=-i c'' epsilon_minus sigma3`, the two contributions are

\[
C^\dagger TF=\frac{i\gamma v c''\epsilon_- k_x\sigma_3-\gamma v c''\epsilon_- k_yI}{N},
\qquad
F^\dagger T^\dagger C=\frac{-i\gamma v c''\epsilon_- k_x\sigma_3-\gamma v c''\epsilon_- k_yI}{N}.
\]

Their sum is the scalar in the question. A common sign of the columns relative to the code gauge has no effect. The disagreement being queried is the scalar term; the previously documented traceless column-phase conversion is not being asserted away.

| Term | First-order projection in this frame | Treatment |
|---|---|---|
| c-double-prime strain coupling | `-2 gamma v c'' epsilon_minus ky/N` times I | The sign under review |
| `M sigma1` in c2 | `M gamma²/N sigma1` | Retained; traceless |
| `Mf epsilon_minus sigma2` in f | `Mf epsilon_minus F† sigma2 F` | Retained; trace zero because `F F†=v²|k|²/N I` |
| Constant `mu2 I` in c2 | `mu2 gamma²/N I` | Omitted in this comparison; ky-even, so cannot fix the ky-odd difference as an identity |
| `M' epsilon_plus sigma2` in c2 | `M' epsilon_plus gamma²/N sigma2` | Explicitly neglected after B28; traceless |
| mu1, c, c-prime and gamma-prime terms involving c-Gamma3 | Zero, since the corresponding components of W vanish | No coefficient-zero assumption is needed for this first-order statement |

These statements concern the displayed first-order flat-band projection. They do not establish that omitted terms have no effect on the full six-band problem, higher-order corrections, or a different flat-band frame with nonzero v-prime. No new numerical run was performed.

## Evidence gate remains open

The question addresses a **provisional same-labelled-K scalar-sign discrepancy against arXiv v2 under the declared mapping**. Existing algebra reconciles the implemented families through valley exchange and Q reversal, but that does not establish the paper's intended physical convention. Claude reviewed supplied excerpts; independent retrieval by Claude remains unverified. The later journal equations are still unchecked. There is no author-confirmed correction and no selected production convention.

A later manuscript or author clarification is the next substantive input. No further round of acknowledgment messages is needed. This package does not change the model, run a sweep, establish a new braid or Euler-class result, or close the v078 corrections owned by Fable.

## Validation and attribution

[VALIDATION.json](VALIDATION.json) records file/source checks for this documentation-only revision. [MANIFEST.json](MANIFEST.json) covers four content files. Source quotations are attributed to J. Herzog-Arbeitman et al., *Kekulé Spiral Order from Strained Topological Heavy Fermions*, [arXiv:2502.08700v2](https://arxiv.org/html/2502.08700v2), 2025-02-18, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Prose extraction replaces inline math markup with its decoded alttext and normalizes whitespace; the analysis and question are our own.
