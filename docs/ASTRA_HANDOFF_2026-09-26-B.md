# Twistronics: handoff to a new Astra chat (26 September 2026, late)

Welcome back. This replaces `docs/ASTRA_RESTART_HANDOFF.md` as the current state.

Everything below is on GitHub in `alanfuller15/Twistronics`. Comment numbers refer to PR #2.

## Roles and rules (unchanged)

- **Roles.** Codex (Astra) produces research runs and publishes the site. Claude independently reviews them. Claude-run work is audited by Codex.
- **Review tags.** Reviews bind an exact commit and give PASS, BLOCKED or MATERIAL_FINDING.
- **Batch size.** Alan wants small batches: at most 20 cells or points per job, under a spec frozen before execution.
- **Claim ceiling.** Finite-cutoff-a local cell isolation and exact area accounting only. No topology, seam, infinite-cutoff, convergence or experimental claim. Accepted area is not project completion.
- **Merges.** No PR is merged; PR #2 and PR #5 stay open.
- **Site source.** Claude cannot reach `*.chatgpt.site`. Every site change must be mirrored to `codex/atlas-sites` with a restorable version for review.

## Where the research stands

| Result | Figure | Status |
|---|---|---|
| Depth-11 refinement (THREE-FRONT-001) | **4194193/4194304 ≈ 99.997354%**, 3,040 accepted, **111 unresolved depth-11 cells** (92 in Q11, 19 in Q00), 77 of 120 parents fully resolved | Claude PASS 5842413474 |
| Batches 002–006 (Claude-run) | 131057/131072 ≈ 99.9886% at batch 006 | Codex PASS 5841846394 |
| Batch 001 | 105951/262144 | Claude reproduction PASS 5841153373 |

The overall status stays `INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE`.

- **Execution:** `3f52be02cf0dd27ac1d6c1cece8d45045358f2b4` on `codex/three-front-batch-001`.
- **Implementation:** `23ef1c1d182d399636cbb3de75ce9d77e8909e1c`.

### Cutoff a/b point study

It passed the pre-execution review (5842312301) and the post-execution review (5842413474).

- **Sampled minimum upper gap.** Cutoff a: 0.00308997 meV at (22501, 23605)/32768. Cutoff b: 0.00302731 meV at (22505, 23605)/32768.
- **Correct wording.** "A ~3 μeV sampled narrow-gap region appears at both cutoffs; its local landscape and minimum location shift with cutoff."
- **Pointwise, the gap is not cutoff-stable.** The ratio b/a ranges from 0.30 to 3.16, and b−a from −7.4 to +7.4 μeV.
- **Band correspondence is unproved.** The comparison uses the central index pairs in each model.

### Dynamics

- **THREE-FRONT-001 dynamics.** It ran correctly, but its grid 16-vs-32 gate failed (L1 0.354 and 0.255 against 0.05).
  - The cause was the finite periodic box, not numerical error. The grid-16 box is only 16 moiré cells wide, and the packet wraps around it.
  - It stays off the site.
- **DYNAMICS-002** is frozen at `b95e5000f98995d4229fc9f6b7d3d1dae353e924` (`codex/dynamics-002`).
  - It compares grid 32 with grid 64 over 0–125 fs at 2.5 fs steps. It requires L1 ≤0.05 and edge mass ≤1% on both boxes at every frame.
  - It runs as 205 jobs of 20 points or fewer.
  - Claude looked at the design and saw no problems. The grid-32 edge mass at 125 fs is 0.91% for σ=0.07, so the margin is thin, and 0.49% for σ=0.11.
  - **Results need Claude's post-execution audit before any animation replaces the site's.**

## Live site

- **Live version.** https://twistronics-atlas.alanfuller15.chatgpt.site is at Sites **v23**: source `37c08e41`, mirrored at `cd89cc7b` on `codex/atlas-sites`.
- **Reviews.** Claude PASS 5842557373 covers v23, and 5842417319 covers the v22 wording fix. It shows the depth-11 figure and the qualified cutoff wording.
- **Other pages.** `explorer.html` is the historical batch 001–006 snapshot, with a banner. `/retained-atlas.html` keeps the earlier separate sequence.
- **Claude's copy.** Claude's hosted copy (https://claude.ai/artifact/28As4ae7YSmnFJR684WjjL) and `claude/site-updates` (`fce501ae`) are the older single-file summary only. The canonical atlas is Codex's.

## Open items, in priority order

1. **Run DYNAMICS-002, then request Claude's audit.** Post the execution commit, a `materialize.py`, and a no-physics replay that reproduces the summary byte-for-byte.
2. **Fix the site's data labels on the next site change.** This is non-blocking; neither field is shown on the page.
   - In `scripts/build-audited-coverage.py`, the payload `sequence` string wrongly says Claude audited batches 001–006.
   - Suggested wording: "Baseline and batch 001 (Claude reproduction); batches 002–006 executed by Claude, audited by Codex; depth-11 refinement executed by Codex, audited by Claude".
   - The payload-level `audit_url` should list both audits.
3. **Alan decides what happens to the 111 unresolved cells.**
   - Option A: a depth-12 refinement. That is 444 children, which is about 23 jobs at 20 cells or fewer.
   - Option B: stop refining. At a ~3 μeV gap, the width heuristic suggests roughly depth 17 would be needed, so a core may never certify. That may itself be the finding.
   - Either way, freeze the spec first.
4. **Minor cleanups.**
   - The docstring comment in `parallel_domain_006/parallel.py` `initial()` is stale. It should be fixed only in a new runner, because that directory is audit-bound.
   - Every model bundle embeds its own copy of three.js. This causes a console warning and extra download, but has no correctness impact.
   - Add a physical-evidence glue control to the retained control suites for batches 003–006.

## Key branches

| Branch | Head | Contents |
|---|---|---|
| `claude/parallel-domain-execution` | `96333a8f` | Batch 002–006 runners and packets |
| `codex/audit-parallel-domain-002-006` | `eb14511a` | Codex audit artifacts |
| `codex/three-front-batch-001` | `3f52be02` | Depth-11, cutoff and dynamics runs and evidence |
| `codex/dynamics-002` | `b95e5000` | Frozen grid-64 follow-up |
| `codex/atlas-sites` | `cd89cc7b` | Sites v18–v23 source mirror; restore with `python docs/atlas-sites/materialize.py <dir> 23` |
| `claude/twistronics-github-handoff-gvo3uf` | PR #2 | Review notes and these handoffs |
