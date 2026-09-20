# Accepted batch ledger — v050

Generated from finite ACCEPT records after protocol and engine/cutoff-grid checks. The original partner ledger is preserved unchanged under incoming_v049/.

| engine / geometry | N | birth A | near-open gap (meV) | A=0.12 gap (meV) |
|---|---:|---:|---:|---:|
| bm_lab / linear | 4 | 0.1368190297 | 0.05815752 | 0.94842564 |
| bm_lab / linear | 6 | 0.1369609427 | 0.05853524 | 0.96240134 |
| ref_lab / exact | 4 | 0.1368222547 | 0.05815819 | 0.94861331 |
| ref_lab / exact | 6 | 0.1369641495 | 0.05853592 | 0.96258914 |

- Newly accepted: preparation upper-pair birth, four windows, 36 root states, eight charge stations.
- Retained from our v048: eight late fold windows and 32 sampled gapped states connecting the already measured late segments. See prior_our_v048/v048/LEDGER.md and its source records.
- Provisional only: v049's fixed-parameter anchors. Their duplicate/nonzero-residual rows are classified in provenance/anchor_quality.json and are never promoted to accepted pairs.
- Still open: original-flat-pair preparation continuation and joins; extra flat-pair local events; lower-pair birth; separate lower unlink collision.
- No whole-campaign, global convergence or physical-bilayer validation claim.
