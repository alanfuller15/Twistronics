# Branch guide

Checked **25 September 2026 UTC** against all **46 remote branches** and all
open pull requests. A branch being older than `main` does not make an exact
research checkpoint obsolete. Use the development branches below for new
work and exact commit links when citing evidence.

## Active development and review

| Branch | Purpose | Synchronization policy |
|---|---|---|
| `main` | Published reader landing page and interactive lessons | Current published evidence summary; research PRs remain separate |
| `migration-contract-review` | Shared base for PRs #2, #3 and #4 | Receives current landing documentation; retains its scientific files |
| `claude/twistronics-github-handoff-gvo3uf` | PR #2: partner handoff and review notes | Updated from its shared base; branch-specific reading order remains available |
| `codex/consumer-boundary-probes` | PR #3: retained consumer defect probes | Updated from its shared base; probe evidence remains unchanged |
| `codex/vafek-convention-diagnostic` | PR #4: source convention review; base for PR #5 | Updated from its shared base; source evidence remains unchanged |
| `codex/research-questions-001` | PR #5: certification, point mapping and parallel coverage | Updated from PR #4's branch; latest published execution is batch 001 |
| `acceptance/v079p-loop` | PR #6: exact R06 acceptance review | **Pinned** at `d834fd0e06a7b5170cae933aeb2f645f836425d3`; candidate identity is part of its review contract |

The PR #6 branch is intentionally behind later reader-documentation commits.
Its `acceptance_loop/AGENTS.md` and round descriptor require an exact candidate
binding. Routine branch maintenance does not open a new review round or alter
that candidate. For the current reader experience, use `main`.

The scientific branches are kept current by merging their declared upstream,
without rebasing published evidence. Updating documentation is not acceptance
of a scientific PR. The current [evidence status](STATUS.md) links to immutable
execution and source commits; an independent review of an older commit does
not become a review of a later branch head.

## Completed documentation branches

These branches are retained at their completed PR heads; new presentation work
starts from `main`.

| Branch | Completed PR |
|---|---|
| `research-visual-guide` | #1 |
| `docs/first-viewer-learning-map` | #7 |
| `docs/interactive-learning-atlas` | #8 |

## Other retained branches

The following 36 branches have no open PR at this check. They retain previous
research, diagnostic, or review deliveries. Their age alone is not a reason
to merge, reset, or delete them. Consult their own evidence and the
[archive map](ARCHIVE_MAP.md) before starting new work from one.

- `codex/partner-v057p-reconciliation`
- `codex/v056-evidence-map`
- `codex/v057-historical-replay`
- `codex/v058-n8-endpoint`
- `codex/v059-n8-unlink`
- `codex/v060-n8-braid2-window`
- `codex/v061-n8-first-annihilation`
- `codex/v062-braid2-continuation`
- `joint-mapping-continuation`
- `joint-mapping-guarded`
- `joint-mapping-review`
- `origin`
- `paper-benchmark`
- `partner-selfchecks-review`
- `r1-contour-attachment`
- `r1-cutoff-n8`
- `r1-event-tracking`
- `r1-frame-holonomy`
- `r1-guarded-newton`
- `r1-interior-inventory`
- `r1-local-merger`
- `r1-n8-sequence`
- `r1-node-continuation`
- `r1-reproduction`
- `r1-stem-crossing`
- `r1-surface-isolation`
- `r1-temporal-transport`
- `r1-three-band`
- `r1-validation`
- `sparse-mode-review`
- `v054-audit-repairs`
- `v055-lower-unlink`
- `variant-controls-review`
- `variant-guard-repairs`
- `variant-response-review`
- `visual-story`
