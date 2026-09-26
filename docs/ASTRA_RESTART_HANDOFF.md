# Astra restart handoff — 25 September 2026

Paste this into a fresh Astra/Codex conversation after the OpenAI "Issues with
Codex" incident (status.openai.com, 25 Sep, 3:19 PM) clears. Do not resume the
failed threads that show "Reasoning failed / Error in message stream".

## Where the research stands

| Item | State | Reference |
|---|---|---|
| Certified cutoff-a coverage | **259295/262144 ≈ 98.91% of [0,1]²** after batch 003 (1730 accepted, 253 frontier, 40 unresolved). q01 and q10 fully accepted. Status `INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE`. | branch `claude/parallel-domain-execution` `c898b31a` |
| Batch 001 | 40.42%; published by Codex at `bc88ff0d`; Claude reproduced it byte-identically and passed it. | PR #2 comment 5841153373 |
| Batches 002 and 003 | **Unreviewed; executed by Claude** at Alan's direction during the outage. Batch 002 reached 79.89% (replay uses an Alan-approved 1e-6 s deadline tolerance); batch 003 reached 98.91% across two hosts with 8 shards. **Codex audit requested.** | PR #2 comment 5841363890 |
| Earlier single-quadrant baseline | 29663/65536 of [½,1]² = 29663/262144 ≈ 11.32% of [0,1]² | quadrant 002, PR #5 `fd98e033` |
| Fixed-specimen diagnostic | Reviewed PASS. Failures come from box width, not precision; the narrowest cell passes only at eighth-radius. Concentric boxes certify nothing. | PR #2 comment 5826335781 |
| Point-mapping scouts | Reviewed PASS as uncertified samples. The upper gap falls to ≈ 0.00309 meV near (0.6867, 0.7204), inside the unresolved strip. It may be a near-touching of bands 98/99; nothing is proven. | PR #2 comment 5826511133 |

Standing claim ceiling: finite-cutoff-a local cell isolation and exact area
accounting only. No topology, seams, cutoff convergence, v078 correctness or
experimental claim. Both PR #2 and PR #5 stay unmerged.

## Working rules between Codex and Claude

- Codex publishes; Claude reviews on PR #2 with `[CLAUDE][REVIEW]`, binding the
  exact commit and tree, and a verdict of PASS, BLOCKED or MATERIAL_FINDING.
- When Codex finds an error in a Claude review, Claude corrects it in place,
  with a note citing Codex's comment.
- From 25 Sep, Alan authorizes engine runs before audit. Every executed
  packet still needs a later independent audit before its numbers are called
  reviewed.
- No merges; no parameter sweeps outside a frozen, bounded SPEC.

## Open follow-ups

1. Audit batches 002 and 003 on `claude/parallel-domain-execution` (see PR #2 comment 5841363890).
2. From the batch-001 implementation review, still open:
   - explicit per-worker and aggregate factorization-cap assertions;
   - a retained control that exercises physical-evidence verification on real records;
   - test mode derived from the log headers;
   - documentation that 128-bit precision must be set before coefficient assembly.
   Batch 002's README says the first three are now incorporated; that needs checking.
3. Correct the scout README wording about pre-execution review (it claims a
   review that did not happen).
4. Proposed next science step: a point-only comparison of the upper-gap minimum
   at cutoffs a and b, frozen and reviewed before it runs.

## Atlas site (twistronics-atlas.alanfuller15.chatgpt.site)

Claude could not reach the live site; the cloud environment's network policy
blocks the domain. Claude tested the `docs/interactive-learning-atlas` source
(`f2c259b4`) in a headless browser instead:

- It loads with no script errors, failed requests or broken images, `#start`
  resolves, and the phone layout (390 px) does not scroll sideways.
- **Bug:** at desktop width the lattice view says "Moiré cell extends beyond
  this view" while the whole cell is drawn. The fit test at `app.js:58`
  (`1.5*L*scale < h-30`) is too strict.
- **Bug:** at desktop width the layer-2 (amber) dots are barely visible under
  layer 1.
- **Wording:** the phone label reads "One moiré cell · edges L", with the
  letter L and no length.
- **Content:** the coverage bar shows the old 45.26% quadrant figure. Update it
  to the full-square number (98.91% after batch 003, unreviewed) or state both
  denominators, and refresh the 25 Sep snapshot, which is bound to `3f174f19`.
