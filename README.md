# Twistronics research

Current batch: **our v061 — the first-annihilation event at N8 in both engines**. Start with the [team share](research/v061/TEAM_SHARE_v061.md), [report](research/v061/REPORT.md), [recovery account](research/v061/RECOVERY.md), [summary](research/v061/SUMMARY.json) and [reproduction instructions](research/v061/README.md).

Both lab_nn_full engines reproduce an opposite-charge flat-band pair approaching a nondegenerate fold, followed by positive flat-gap searches and a SAME upper pair at T=-0.74. The largest fold difference from retained N6 evidence is **5.18890364e-09**. BM linear and reference exact reciprocal geometry remain distinct. The separate upper-pair checkpoint does not prove continuous charge transfer through the collision.

Both initial runs were rejected at the opening gate. A separately frozen diagnostic identified under-resolved curvature and insufficient optimizer stationarity. Recovery kept the original acceptance thresholds, added bounded Newton gradient polishing, used finer curvature steps and required agreement/symmetry. The accepted result combines the unchanged original fold/root/charge records with fresh recovery opening/upper-pair measurements. All original REJECT records and diagnostic evidence are retained.

There are 22 paired-root states, four flat-pair charge stations, four post-event chart/edge searches and two upper-pair stations. Each charge station has three mesh/radius trials. The local square-root separation check improves toward the fold. These are bounded numerical witnesses, not continuous-interval or global zero-count proofs.

**120 assertion cases passed in source/input/environment-bound run `20260921T041853Z_c108fe1d`.** A first publication run exposed an incorrect boundary-gradient test fixture; its failed evidence and old source are preserved. The corrected complete suite passed before publication. Reports reconcile actual records and test outcomes. Original and recovery runtime identities match, and all prior tracked evidence is preserved.

Prior [v060](research/v060/REPORT.md) covers the narrow N8 braid-2 critical window. [v059](research/v059/REPORT.md) covers the N8 lower unlink event; [v058](research/v058/REPORT.md) covers N8 endpoint gaps. [v057](research/v057/REPORT.md) and its [consumer attribution](research/v057/ATTRIBUTION.md), [v056](research/v056/REPORT.md), [v055](research/v055/REPORT.md) with its [handoff correction](research/v055/ADDENDUM_v055.md), and [v054](research/v054/REPORT.md) retain the preceding audit and campaign work. Their test runs remain separate historical evidence.

## Layout

- `research/v061/`: current frozen plans, original rejected records, diagnostic/recovery evidence, gates, tests and handoff.
- `research/v060/` through `research/v054/`: earlier checked batches.
- `research/incoming_partner_v054/`: preserved partner delivery.
- `research/v053/`, `research/prior_our_v052/`: earlier campaign evidence.
- `audits/v053/`: inspection audit and responses.
- `research/MANIFEST.json` and `RELEASE.json`: original v053 import provenance, unchanged.

The [next bounded sequence](research/v061/NEXT_SEQUENCE.md) extends the N8 braid-2 leg from ratio .99100 to 1.00000 with carried frames. The complete N8 campaign, infinite-cutoff accuracy, remaining historical consumer impact and physical-bilayer validation remain open. Physical magnitudes require an intended acceptance target, microscopic tunnelling strain law and independent reference or measurement. No complete security clearance or new license is claimed.
