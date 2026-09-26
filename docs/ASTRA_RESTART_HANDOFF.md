# Twistronics — restart handoff for Astra (26 September 2026)

This zip is a compact snapshot of the work done while Astra/Codex was
unavailable during the 25 September OpenAI incident. Everything in it is also
on GitHub; this file says where. The raw per-record logs are not included
because of their size. They are on the branches listed below, and each batch
has a `materialize.py` that rebuilds and re-verifies them.

## 1. Where the research stands

Certified cutoff-a S1b coverage, as a fraction of the full coordinate square [0,1]²:

| Batch | Ran on | Accepted area | Accepted / frontier / unresolved | Review status |
|---|---|---|---|---|
| Quadrant-002 baseline | Codex | 29663/262144 = 11.32% | 590 / 391 / 40 | reviewed |
| 001 | Codex, `bc88ff0d` (PR #5) | 105951/262144 = 40.42% | 702 / 903 / 40 | **reviewed**: Claude reproduced it byte-identically (PR #2 comment 5841153373) |
| 002 | Claude, 1 host × 4 | 209439/262144 = 79.89% | 1191 / 483 / 40 | **reviewed**: Codex PASS (5841846394) |
| 003 | Claude, 2 hosts × 4 | 259295/262144 = 98.91% | 1730 / 253 / 40 | **reviewed**: Codex PASS (5841846394) |
| 004 | Claude, 2 hosts × 8 | 65469/65536 = 99.898% | 2154 / 179 / 89 | **reviewed**: Codex PASS (5841846394) |
| 005 | Claude, 1 host × 4 | 262021/262144 = 99.953% | 2299 / 0 / 123 (depth 9) | **reviewed**: Codex PASS (5841846394) |
| 006 | Claude, 2 hosts × 16 | **131057/131072 = 99.9886%** | 2671 / 0 / **120 (depth 10)** | **reviewed**: Codex PASS (5841846394) |

Status for every batch: `INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE`.

- Quadrants q01 and q10 have been fully accepted since batch 003.
- The 120 remaining unresolved depth-10 cells (0.0114% of the area) are 101
  in q11 and 19 in q00. They lie where point samples show the upper gap
  falling to about 3 μeV (scout 002).

Claim ceiling, unchanged: finite-cutoff-a local cell isolation and exact area
accounting only. No topology, seam, cutoff-convergence, v078 or experimental
claim. Accepted area is not project completion.

## 2. What Codex needs to audit (Claude ran these, so Claude cannot review them)

**Update, 26 September:** Codex audited all five batches and passed them
(PR #2 comment 5841846394; reviewer artifacts at `eb14511a`). The points below
are kept as the record of what was asked.

Audit requests are posted on PR #2 as comments 5841363890 (batches 002–003),
5841524567 (batch 004) and 5841646067 (batches 005–006). Specific points:

1. **Batch 002 deadline tolerance.** The unchanged runner `7494c360` failed its
   own `DEADLINE_BINDING` check, because `soft_deadline − start` was
   `600.0000000000001`: float rounding, not a real overrun. With Alan's
   explicit approval, replay uses `replay_002.py`, which loads the unchanged
   runner and relaxes only that comparison to 1e-6 s. Batches 003 onward
   recompute the supervisor's exact expressions instead, so the issue cannot
   recur.
2. **Sharding (003 onward).** Each quadrant's frontier is sorted and dealt
   round-robin to slots. Descendants stay with their owner, and inherited
   accepted/unresolved cells go to slot 0. Controls prove the shard union
   equals the predecessor partition. Merges fail on a missing or swapped shard.
3. **Batch 006 rule change.** Only the cells unresolved at depth 9 were
   reopened, as depth-10 children, so the partition now mixes depths up to 10
   and uses a 1024² raster. Is this an acceptable extension of the partition
   rules?
4. **High acceptance rates.** Batch 002 accepted 119 of 128 cells in q00, for
   example. This is consistent with the D1 width scale, but please spot-check
   accepted depth-8, 9 and 10 records independently.
5. **Second hosts.** These were sibling Claude sessions. Each verified the
   wheel `376b88ca…4d76` and ran the controls, and all pushed outputs were
   rebuilt and checked against their receipts' byte counts and SHA-256 before
   the merged verification.

## 3. Branches and commits

- `claude/parallel-domain-execution`: all batch 002–006 runners and executed
  packets. Created from PR #5's head `7494c360`; no PR opened.
  - Runners: 003 at `32ea5246`, 004 at `e12b74eb`, 005 at `accee93c`, 006 at `9cfa9129`.
  - Packets: 002 at `32ea5246`, 003 at `c898b31a`, 004 at `017ac54c`, 005 at
    `07ac73fd`, 006 at `645cbb99` (README count fix at `96333a8f`).
- Second-host output branches: `claude/parallel-domain-003-host1`,
  `-004-slots23`, `-006-slots4567`.
- `claude/site-updates`: Atlas source fixes and current coverage (latest
  `d6209b61`), based on `docs/interactive-learning-atlas`.
- `claude/twistronics-github-handoff-gvo3uf` (PR #2): review notes and
  `docs/ASTRA_RESTART_HANDOFF.md`.

Rebuild and verify any batch without physical calls:
`python research/benchmarks/parallel_domain_00N_execution/materialize.py /tmp/replay`.

## 4. Atlas site

- **Update, 26 September:** Astra published `claude/site-updates` `d6209b61`
  to https://twistronics-atlas.alanfuller15.chatgpt.site (PR #2 comment
  5841805747). The deployed `explorer.html` SHA-256 `4dc6fa60…356b` matches
  the branch file byte-for-byte, as Claude checked. The prior atlas is kept at
  `/retained-atlas.html`. Claude still cannot fetch `*.chatgpt.site` directly,
  because the cloud network policy blocks it.
- Claude-hosted copy, which Claude can update directly:
  https://claude.ai/artifact/28As4ae7YSmnFJR684WjjL (shared as anyone with the link).
- Fixes, on `claude/site-updates` and in `site/` in this zip:
  1. The moiré view wrongly said "Moiré cell extends beyond this view" at
     desktop width. It now tests the real bounding box and shows
     "edge L = 13.42 nm".
  2. The layer-2 (amber) dots were nearly invisible at the 40 nm view; they
     are now larger and more opaque.
  3. The coverage panel showed the old 45.26% quadrant figure. It now shows
     131,057/131,072 ≈ 99.989% of the full square, with review status, and
     keeps the historical figure with its full-square equivalent.
- To republish chatgpt.site, use `site/explorer.html`, or rebuild from
  `claude/site-updates` with `build_standalone.py`.

## 5. Suggested next steps

1. Codex audits batches 002–006 (section 2).
2. Decide whether to push the restricted refinement to depth 11 or 12. Each
   round takes about 5 minutes on two 4-core hosts. The narrowest strip gap
   (about 3 μeV) would need roughly depth 17 by the D1 heuristic, so a core
   will likely stay unresolved, which may itself be the finding.
3. The previously proposed point-only structural study of the upper-gap
   minimum at cutoffs a and b, frozen and reviewed before it runs.
4. Open follow-ups: correct the scout README's wording about pre-execution
   review; add a physical-evidence glue control to the retained controls.

## 6. Contents of this zip

- `START_HERE.md`: this file.
- `results/`: for each batch 001–006, the `RESULTS.json`, `PARTITION.json`,
  `README.md` and `MANIFEST.json`, plus per-slot `RECEIPT.json`,
  `HOST_RESULTS.json` and host notes.
- `runners/`: `parallel_domain_002` to `006` source (`parallel.py`, `SPEC.json`,
  `EXECUTION_AUTHORITY.json`, `SOURCE_BINDINGS.json`, `test_controls.py`,
  `README.md`), plus `replay_002.py` and each batch's `materialize.py`.
- `site/`: the updated `explorer.html` (single file), `index.html`, `app.js`,
  `style.css`, and `site-updates.diff` against `docs/interactive-learning-atlas`.
- `docs/ASTRA_RESTART_HANDOFF.md`: the earlier handoff, which this file supersedes.
