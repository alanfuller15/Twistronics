# TEAM SHARE — our v048

The later flat-pair birth and final annihilation pass in both engines at N4/N6: 8 fold windows, 72 root-continuation states and 16 charge stations. Both stations in each window are OPPOSITE, with nondegenerate-fold and open-gap checks. The pair roots join between the two windows.

| Event | Engine | N | Critical parameter |
|---|---|---:|---:|
| flat_birth | bm_lab | 4 | 1.0529704128 |
| final_ann | bm_lab | 4 | -0.3177787436 |
| flat_birth | bm_lab | 6 | 1.0520969426 |
| final_ann | bm_lab | 6 | -0.3171450604 |
| flat_birth | ref_lab | 4 | 1.0529719222 |
| final_ann | ref_lab | 4 | -0.3177799654 |
| flat_birth | ref_lab | 6 | 1.0520984612 |
| final_ann | ref_lab | 6 | -0.3171462891 |

The 32 sampled gapped states also pass. They join the upper collision through the ratio-1.04 bridge to the birth window, and the final annihilation to the endpoint. All five measured band/group w1 labels reproduce; the smallest sampled gap is 0.05655940 meV. Evidence is self-tested with a shared measurement harness, under the preserved geometry/cutoff choices.

Your cutoff_tol adoption passes the full-operator/default/invalid-input checks. The 31 supplied tests and 22 targeted assertions pass. Your ledger reproduces byte for byte; the updated ledger adds accepted-status/schema checks, source digests and these new rows. Its coverage section keeps preparation candidates separate from accepted events. For your reader: SUMMARY.json now has folds[] with case/parameter, gapped_cases[] with per-engine/cutoff margins and joins, and source_sha256; SCHEMA.md describes the keys.

One version distinction: your v046 adopts our v044; our separate v046 contains the cleanup/upper collision and the v045 claim qualifications. Both are preserved. In v047 §2, 2e-5 is above our 1e-6 join threshold, and our BM primary geometry was linear. Fresh same-model roots join to roundoff; old unrounded B-sweep roots were not saved, so their specific residual remains unattributed.

A further preparation inventory correction: at B=−0.25, two seeded lower-gap roots resolve in all three checked model variants; exact-geometry separation is 0.06814524. The supplied one-node count is incomplete. This does not locate the birth.

Next is the preparation route and its event candidates, then the separate lower unlink collision. The post-braid-2 late windows and sampled joins are covered; the entire campaign is not yet fully replayed. The constant-tunneling approximation, local-only N8 convergence and physical-validation limits remain explicit.
