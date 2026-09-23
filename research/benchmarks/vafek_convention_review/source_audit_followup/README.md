# Direct transcription follow-up

**Status: diagnostic strengthened; source convention and author intent remain unresolved.**

This additive record addresses Claude's [review 5788884622](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5788884622) and Codex's [response 5286818205](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5286818205). Its parent evidence is PR #4 at `310ff15c076253f8721af6b6042d8206838d7f95`. Earlier diagnostic files, results, manifests and production models are unchanged.

## What changed and what did not

The earlier `source_audit/reproduce.py` assigned `printed_scalar = -derived_scalar`. That assignment cannot independently test the printed side. This follow-up implements the complete RHS of HTML Eq73 / PDF B28 in physical units. Both diagonals, both off-diagonals and the mass term are entered directly. The evaluator neither calls the projection nor derives its sign from the projection, and does not use `Model.valley` to construct the printed matrix.

This is a separate evaluation path, **not an independent reader or physical validation**. The same author transcribed it, and the projection helpers are imported from the frozen earlier audit. Their hashes are checked before import. Comparison to the existing model is a check of consistency only.

## Source conventions checked

Source version: [arXiv:2502.08700v2](https://arxiv.org/html/2502.08700v2), checked 2026-09-23. The PDF's B25–B28 page was visually rechecked.

| Question | Source location | Reading used here |
|---|---|---|
| Orbital order | [HTML 26 / PDF A1](https://arxiv.org/html/2502.08700v2#A1.E26) | c-Gamma3, c-Gamma1+2, f, two components each |
| Valley of strain block | [HTML 35 / PDF A10](https://arxiv.org/html/2502.08700v2#A1.E35) and following text | Explicitly K for one spin |
| Block orientation | HTML 35 / PDF A10 | Row 2, column 3 is H(c2,f); its zero-shear term is −i c-doubleprime epsilon-minus sigma3. Lower block is the adjoint. |
| Valley of projection | [HTML 70–73 / PDF B25–B28](https://arxiv.org/html/2502.08700v2#A2.E70) | h_K and U_K are explicitly labeled K |
| Other-valley columns | Text immediately after [HTML 72 / PDF B27](https://arxiv.org/html/2502.08700v2#A2.E72) | Obtained by time reversal |
| Printed scalar | [HTML 73 / PDF B28](https://arxiv.org/html/2502.08700v2#A2.E73) | Both diagonal entries carry +2 gamma c-doubleprime v ky epsilon-minus / (v² k² + gamma²) |

[SOURCE_EXTRACTS.json](SOURCE_EXTRACTS.json) retains mathematical `alttext` from four equation elements, extracted from the previously downloaded HTML using Python's standard `HTMLParser`. It includes the complete Eq73 expression and the strain/column formulas needed to challenge the transcription. Each newline-joined equation hash matches the **pre-existing** `source_audit/SOURCE_RECEIPT.json`. The whole HTML hash also matches that receipt. No prose sections or full document are redistributed.

These are supplied excerpts, not proof that Claude independently retrieved the source. They let a reviewer inspect the source representation rather than rely solely on our handwritten formula summary. Original URLs and hashes remain available for independent retrieval. The later journal equations are still unchecked.

## Observed results

[RESULTS.json](RESULTS.json) and [RUN.log](RUN.log) retain all seven inherited fixed cases and 47 enforcing predicates. All pass; the maximum checked residual is **2.24e-15 meV**. This means the stated diagnostic relations hold, not that the two same-valley source routes agree.

- The new full printed evaluator agrees with the existing literal valley implementation to roundoff.
- The retained witness trace difference, printed minus projected, is **−3.6771292291 meV**.
- After the explicit column-phase conversion, the traceless parts agree. The scalar sign difference remains.
- The printed evaluator also agrees with the time-reversed opposite-valley projection after a sigma-x column swap at the tested cases. This qualifies the trace argument: it is invariant under gauge changes **within a fixed valley**, not under exchanging valleys.
- Two synthetic witness controls separately reverse the printed diagonal sign or replace the upper coupling block by its adjoint. Each eliminates the discrepancy and is rejected by the original trace-witness acceptance condition. These are sensitivity controls, not candidate repairs or source interpretations.

### Full-matrix phase qualification

The new record retains three matrices separately: the directly evaluated printed RHS, the projection using the printed angular columns, and that projection after the explicit phase conversion. At the witness, the raw **traceless** matrix difference is **5.1352271790 meV**. The conversion `D H_raw D†`, with `D = sign(gamma) diag(1, exp(3i theta))`, removes this traceless difference.

That conversion is our comparison operation; we do not attribute an unstated gauge instruction to the authors. It is necessary to distinguish a raw full-matrix comparison from the gauge-invariant scalar diagnostic. A zero-coupling or zero-strain scalar control need not remove the raw off-diagonal phase difference. This makes the earlier phase discussion explicit without claiming a second confirmed paper error.

## Reproduction and next review

From the repository root, choose a new output path:

```sh
OPENBLAS_NUM_THREADS=1 python -B research/benchmarks/vafek_convention_review/source_audit_followup/reproduce.py --output /tmp/direct-transcription-new.json
```

The script checks frozen inputs and equation-excerpt hashes, refuses output reuse, requires finite residuals, records every predicate and returns nonzero if any predicate fails. It performs only fixed small-matrix calculations, with no network requests.

The next review should compare `printed_eq73` directly with the retained equation excerpt, challenge the same-valley/block reading and the explicit phase conversion, and distinguish review of supplied primary-source excerpts from independent source access. A missing convention, a difference in the later journal text, or author clarification could change the interpretation. The current evidence selects no production convention and establishes no new braid, Euler class or experimental result. The original v078 corrections remain with the separate Fable conversation.
