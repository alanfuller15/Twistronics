# v050 — preparation upper-pair birth and v049 reconciliation

[self-tested] Four upper-pair birth windows pass under lab_nn_full, constant w0,w1, B=T=0, phi=0, ratio=0.8, eps=0.003 and theta=1.05 degrees. This closes one preparation event, not the preparation route.

| engine / geometry | N | birth A | near-open gap (meV) | A=0.12 gap (meV) |
|---|---:|---:|---:|---:|
| bm_lab / linear | 4 | 0.1368190297 | 0.05815752 | 0.94842564 |
| bm_lab / linear | 6 | 0.1369609427 | 0.05853524 | 0.96240134 |
| ref_lab / exact | 4 | 0.1368222547 | 0.05815819 | 0.94861331 |
| ref_lab / exact | 6 | 0.1369641495 | 0.05853592 | 0.96258914 |

Each window includes nine distinct-root continuation states from A=0.14 toward the fold, charge measurements at two stations (start and fold+0.001), rank-one Jacobian refinement, nonzero null curvature and transverse parameter slope, and positive opposite-side gap searches at fold−0.001 and A=0.12. Both opposite-side searches use 18/24 grids with boundary seeds and bounded refinements. Total: 36 root states and eight charge stations, not 36 fully charge-gated states. The code and input hashes were frozen before the decisive runs. N4 passed in both engines before N6 began.

BM retains linear reciprocal geometry and cutoff_tol=1e-6; TBG retains exact inverse deformation and cutoff_tol=1e-9. These are the declared campaign variants, not identical matrices. Their agreement tests implementation sensitivity with a shared measurement harness, not conceptual independence.

## Reconciliation with v049

The partner's v048 disposition and our v048 measured batch are different records. Both are preserved. Our already accepted v048 supplies eight late fold windows and 32 sampled gapped states, so those late events were not rerun here. The exact N4 late birth is ratio 1.0529719221827458 near (0.67751830,0.90903862), refining v049's extrapolated 1.0534. The exact N4 final annihilation is A=−0.31777996539472003, consistent with the rounded −0.3178 anchor estimate.

At ratio 1.054, the new two-seed probe finds the missing partner at (0.67695168,0.90486606) alongside (0.67838909,0.91363691). Separation is 0.0088878553; exact BM/TBG agreement is better than 3.6e−15. This resolves the undercount. It does not isolate which detail of the old eight-start search caused the miss and adds no new charge claim.

The saved A=−0.31 row has residual gaps 1.26189219 meV in both engines. It is not the zero-gap duplicate-root signature described in v049 §2. The ratio=1.06 row really does contain duplicate zero-gap roots. The new anchor classifier keeps these cases separate and does not promote either to an event verdict.

v049's finite-twist geometric computation is consistent with the previously measured O(eps*theta) term. Its total radius shift also contains O(eps^2); exact doubling should be tested on the isolated first-order contribution, not on the full shift. No new microscopic tunnelling law or physical magnitude is established.

## Validation and limits

31 supplied tests pass; 14 reporting tests pass (six anchor-quality cases, five inherited ledger guards and three endpoint fault-injection cases). Source review covers the three changed Python files and three new Python scripts, their relevant outputs, and the new harness changes. It is an incremental review, not a reread or CVE recertification of the entire project. File inventory covers all 143 incoming files.

The positive-gap searches and nine parameter stations are finite numerical evidence, not exhaustive momentum or parameter-interval proofs. No independent physical-bilayer validation has been performed. The optional endpoint patch persists failed-start logs before raising and rejects nonfinite optimizer coordinates. It is tested with injected failed, invalid and successful outcomes; it does not replace the accepted numerical search harness.

The remaining preparation route, extra flat-pair birth/annihilation, lower-pair birth and separate lower unlink collision remain open. Recipient consumption is [unconfirmed].
