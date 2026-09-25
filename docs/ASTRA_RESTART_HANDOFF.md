# Astra restart handoff — 25 September 2026

Paste this into a fresh Astra/Codex conversation after the OpenAI "Issues with
Codex" incident (status.openai.com, 25 Sep, 3:19 PM) clears. Do not resume the
failed threads that show "Reasoning failed / Error in message stream".

## Where the research stands

| Item | State | Reference |
|---|---|---|
| Certified cutoff-a coverage | **105951/262144 ≈ 40.42% of [0,1]²** after parallel batch 001 (702 accepted, 903 frontier, 40 unresolved depth-9 cells). Status `INCONCLUSIVE_PARTIAL_DOMAIN_COVERAGE`. | PR #5 `bc88ff0d` (`parallel_domain_001_execution/`) |
| Batch 001 independent audit | **Pending.** Claude reran batch 001 from the reviewed implementation on a separate host as a reproduction check; see the PR #2 comment for the result. | implementation PASS: PR #2 comment 5827238845 |
| Batch 002 | Runner published at `7494c360` (`parallel_domain_002/`): resumes the batch-001 partition, 128 attempts per worker, 512 total. Alan authorized execution without waiting for audit (`EXECUTION_AUTHORITY.json`). Execution and publication status: see the latest PR #2 comment. | PR #5 `7494c360` |
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

1. Audit the batch 001 execution (`bc88ff0d`) and, once run, batch 002.
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
  to the full-square number (40.42% after batch 001) or state both
  denominators, and refresh the 25 Sep snapshot, which is bound to `3f174f19`.
