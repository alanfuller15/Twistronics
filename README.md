# Twistronics research

Current batch: **our v058 — N8 endpoint gaps in both modern engines**. Start with the [team share](research/v058/TEAM_SHARE_v058.md), [report](research/v058/REPORT.md), [summary](research/v058/SUMMARY.json) and [reproduction instructions](research/v058/README.md).

Both lab_nn_full engines pass the declared checks for all four endpoint gaps at N8. Fresh chart meshes, explicit edge searches and bounded multistart refinements reproduce the partner's four rounded N8 reference values. Across both engines, the largest difference from retained N6 gap measurements is **7.45902754e-05 meV**. The BM/reference N8 difference is at most **0.000320892265 meV** with their retained linear/exact reciprocal geometry conventions.

The workers record 486 refinements and 514 optimizer attempts; 28 rejected attempts precede successful fallbacks. Both meshes agree, selected local minima pass stationarity and curvature checks, and runtime identities match before/after each run. These are finite sampled gap checks: no global-minimum certificate, infinite-cutoff error bound, N8 topology/path replay or physical-bilayer validation is claimed.

**58 assertion tests passed in source/input/environment-bound run `20260921T025546Z_b2dbd1e0`.** Report publication reconciles the stored numerical records and verifies actual collected/executed/JUnit test evidence. Prior files and the previous README are preserved. N4/N6 values and original partner output are explicitly historical evidence.

Prior [v057](research/v057/REPORT.md) contains the historical kinetic='none' branch-exercised metadata comparison and [consumer attribution](research/v057/ATTRIBUTION.md); remaining scalar/mass/angle sweeps and exploratory braid detours are impact-unverified. [v056](research/v056/REPORT.md) reconciles 80 selected campaign case records. [v055](research/v055/REPORT.md) contains the modern-model lower unlink fold and its [handoff correction](research/v055/ADDENDUM_v055.md). [v054](research/v054/REPORT.md) contains audit repairs and the 76-state preparation replay. Their test runs remain separate historical evidence.

## Layout

- `research/v058/`: current N8 workers, full optimizer records, tests and frozen plans.
- `research/v057/`, `research/v056/`, `research/v055/`, `research/v054/`: earlier checked batches.
- `research/incoming_partner_v054/`: preserved latest partner delivery.
- `research/v053/`, `research/prior_our_v052/`: original versioned campaign evidence.
- `audits/v053/`: inspection audit and recorded responses.
- `research/MANIFEST.json` and `RELEASE.json`: original v053 import provenance, unchanged.

The [next bounded sequence](research/v058/NEXT_SEQUENCE.md) is a separately planned N8 continuation through one previously gated critical event. Physical magnitude claims require the inventor's intended acceptance target, a named microscopic tunnelling strain law and independent validation. No complete security clearance or new license is claimed.
