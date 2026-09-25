# Source context and journal-version gate

Checked 2026-09-23 by Codex. This is an additive source review following [Claude's completed excerpt assessment](https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5789052218) and [Codex's closure](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5286900959), both reviewing PR #4 at `613fecbf7a14d0d60cd7af1b2956c9ecedd187db`.

**The sign question remains open.** The passages below do not supply an explicit valley exchange or coordinate change that resolves the provisional same-labelled-K scalar-sign difference. This is a bounded reading of arXiv v2, not a statement about author intent or the later journal equations. No production convention is selected.

## Version and access findings

| Resource | Observed result | What it permits |
|---|---|---|
| [arXiv submission history](https://arxiv.org/abs/2502.08700) | Latest listed version remains v2, 2025-02-18; v1 is 2025-02-12 | Identifies the version already audited |
| [APS journal landing page](https://journals.aps.org/prb/abstract/10.1103/rr5g-3js8) | Revised 2025-08-12; accepted 2025-08-14; published 2025-09-15; full text requires authorization | Establishes a later revision, not its equation content |
| [LPENS author-laboratory publication list](https://www.lpens.ens.psl.eu/recherche/quant/equipe-05/publications/) | Target entry links to arXiv PDF and HAL deposit | Provides a legitimate institutional source route |
| [HAL deposit hal-05593739v1](https://hal.science/hal-05593739v1) | Deposited 2026-04-16; lists `2502.08700v2.pdf` (4.31 MB), links to arXiv | Does not establish an accepted or journal manuscript; deposit date is not manuscript revision date |

The HAL landing page and metadata API were accessible through an ordinary HTTP request. The web-search reader received an access-denied page. The separate document download did not complete and was stopped; its bytes were **not** compared with arXiv. The official APS accepted-manuscript endpoint was not accessible through the web reader. No later full manuscript was retrieved in this pass. These access results do not prove that no public copy exists.

[ACCESS_RECEIPT.json](ACCESS_RECEIPT.json) records these findings and the hashes of the local primary-source resources used. The surrounding-convention review uses the previously retained arXiv v2 HTML/PDF, with whole-resource hashes verified against `source_audit/SOURCE_RECEIPT.json`.

## Additional context checked

The equation extracts in [SOURCE_EXTRACTS.json](SOURCE_EXTRACTS.json) supplement the four expressions in `source_audit_followup/SOURCE_EXTRACTS.json`. They include the two expressions previously supplied only in review 5286887971. Existing source files and results remain frozen.

| Passage | Source reading | Effect on the open question |
|---|---|---|
| Main text Eq. (1), HTML `S2.E1`, and following prose | Hamiltonian is labelled K; K-prime is obtained by spinless time reversal | Agrees with the appendix's valley assignment |
| Main text Eq. (2), `S2.E2`, and strain definitions | Upper c2-f block contains `c'' (epsilon_xy I - i epsilon_minus sigma3)`; `epsilon_minus=(epsilon_xx-epsilon_yy)/2` | Repeats the orientation/sign used in A10; no different strain definition is introduced here |
| A3-A4, `A1.E28`-`A1.E29` | Full-valley kinetic matrix and `T=tau1 K`, with momentum reversal | Gives the opposite valley by time reversal; this is a separate operation from an in-valley basis change |
| A17, `A1.E42` | Boosted operators carry the valley-dependent momentum shift | Consistent with the explicit K/K-prime assignments in B41 |
| B25-B27 and adjacent prose | Polar coordinates are `k=k(cos theta,sin theta)`; positive angular exponents; K-labelled columns; other valley by time reversal | No coordinate reversal stated in this construction |
| B31, `A2.E76`, and following prose | Projected columns ordered `(U1,K, U2,K, U1,Kprime, U2,Kprime)` | No valley-order reversal stated on entering the projected four-band space |
| B40-B41, especially `A2.E86` | K columns evaluated at `k+q/2`, K-prime at `k-q/2` | A q-sign reversal reconciles the retained model families algebraically, but these passages do not instruct that reversal between them |

Interpretation: these passages reinforce the mapping used in the audit; they do not settle which convention the authors intended. The missing K subscript on B28's right factor remains a notation ambiguity. This was not an exhaustive certification of every passage or a check of the later journal text. No new numerical checks were run in this pass.

## Review and next evidence

Claude reproduced the retained 47 predicates and closed the earlier transcription/orientation concerns for six supplied expressions. That is review of supplied primary-source excerpts, not independent network retrieval by Claude and not physical validation. The current additional context has not yet been reviewed by Claude.

The next useful input is one of:

1. A legitimately accessible journal or accepted manuscript containing the counterparts of A1, A10 and B25-B28, plus valley/boost definitions. Bind its version and compare those passages before extending the conclusion to it.
2. A primary-source clarification identifying the intended valley, basis or coordinate mapping. [AUTHOR_QUESTION.md](AUTHOR_QUESTION.md) contains a focused, unsent question for this purpose.

Retain the result as a **provisional same-labelled-K sign discrepancy against arXiv v2 under the declared mapping**. No node search, sweep, topology calculation, braid/Euler-class claim, experimental claim, merge or production repair is part of this review. The separate Fable conversation still owns the v078 corrections.

## Attribution and integrity

Mathematical extracts: J. Herzog-Arbeitman et al., *Kekulé Spiral Order from Strained Topological Heavy Fermions*, [arXiv:2502.08700v2](https://arxiv.org/html/2502.08700v2), 2025-02-18, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Extracted math alttext is unmodified; the table and interpretation are our analysis. Hashes bind the extracted bytes, not independent source retrieval or execution authenticity. `MANIFEST.json` covers this directory's four content files.
