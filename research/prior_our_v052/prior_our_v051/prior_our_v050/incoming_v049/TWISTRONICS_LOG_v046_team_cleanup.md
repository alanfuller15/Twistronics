# Twistronics v046 — measured continuation and v045 reconciliation

Numerical evidence: `[self-tested]`. Recipient consumption: `[unconfirmed]`. Sources and raw records are included; this is not external physical validation.

All 68 scheduled cleanup states pass the full pair gate in both engines at N4/N6. The upper pair remains OPPOSITE and joins four accepted upper-annihilation windows. The supplied 30 tests and nine new adapter/optional-patch assertions pass. The v045 gap and sensitivity results are separately checked with explicit limits below.

## What was measured

The cleanup starts at the accepted end of braid 2: (A,B,T,phi,ratio)=(0,-0.4,-0.8,80,1). Its four legs are T→−1.2, A→−0.2, T→−1.8, A→−0.35, each in four intervals. Common endpoints are stored once: 17 states per engine/cutoff. Each state has two-seed refinement, separate roots, exterior-gap checks, comparison-path mesh refinement, loop-mesh/radius agreement and fine/coarse parameter transport. The initial roots match the v042 braid endpoint; the final roots match the fresh upper-collision seeds. Historical absolute frame signs were not saved at the braid endpoint, so that join reinitializes orientation and asserts root identity/relative charge only.

The upper-collision window uses nine root-continuation states, charge checks at its start and near the collision, a rank-one spatial Jacobian, derivative-step halving, nonzero null curvature and transverse parameter slope. Positive open-side minima are checked just beyond the collision and at ratio 1.1, using explicit chart boundaries. No failed root solve is interpreted as a node death. Interior root-continuation states do not each have a separate loop measurement.

| Engine | N | Upper-annihilation ratio | Gap at ratio root+0.001 (meV) | Gap at ratio 1.1 (meV) |
|---|---:|---:|---:|---:|
| bm_lab | 4 | 1.0206603966 | 0.05672344 | 3.80248828 |
| bm_lab | 6 | 1.0194793307 | 0.05655949 | 3.82775223 |
| ref_lab | 4 | 1.0206664403 | 0.05672335 | 3.80223565 |
| ref_lab | 6 | 1.0194854044 | 0.05655940 | 3.82750123 |

Maximum cleanup-to-fold root mismatch is 1.1e-14. The smallest sampled cleanup comparison-path exterior gap is 0.31411971 meV; minimum spatial overlap is 0.98572405, and minimum parameter overlap is 0.97255740. Maximum root step is 0.031202 in fractional coordinates. Maximum relative eigen residual in cleanup is 8.88e-16. Cleanup loop refinements used 0 fallback stages; fold charge measurements used 0. Rejected refinement stages, if any, remain in the raw records.

Both engines explicitly use lab_nn_full. BM retains linear reciprocal geometry and 1e-6 cutoff padding; TBG retains exact inverse deformation and 1e-9 padding. Thus their tiny numerical differences are not attributed solely to independent estimators. The replay uses a common charge/transport harness. The input engines are unchanged; BM average mode has kappa=0. At sixteen full-matrix points, the checks found that default and average±5 reproduce the prior exact-geometry BM matrices bit for bit.

## v045 endpoint check

Each previously located minimum was freshly refined from its seed and two diagonal offsets of size 0.002 at N6 and N8. Optimizer success, non-worsening, projected gradient below 1e-4, positive local curvature and agreement across three starts are recorded. This is local multistart confirmation, not a global N8 search or an infinite-cutoff error estimate.

| Gap | N6 (meV) | N8 (meV) | N8−N6 (meV) |
|---|---:|---:|---:|
| lower | 23.1813478720 | 23.1813873982 | +0.0000395263 |
| flat | 2.7767262482 | 2.7766516597 | -0.0000745885 |
| upper | 3.3924978115 | 3.3925337386 | +0.0000359272 |
| next | 10.8560871686 | 10.8560868677 | -0.0000003009 |

Largest absolute shift among these four tracked local minima: 7.45885e-05 meV. No N8 path labels or global topological invariant were remeasured.

## v045 tunneling scenario check

Exact-geometry BM at N4 was checked at three baseline configurations and four braid endpoints. Both exterior gaps receive bounded 18/24-grid multistart searches at baseline; pair labels use comparison-path and loop refinements. Average±5 need no separate eigensolver runs because their full Hamiltonians are identical to average0 at the checked points and cancellation follows directly from the implemented opposite strains.

| Mode | kappa | Baseline remote gap (meV) | Change | Pair label |
|---|---:|---:|---:|---|
| average | +0 | 4.97092114 | +0.00000% | SAME |
| layer1 | +5 | 5.33784385 | +7.38138% | SAME |
| layer1 | -5 | 4.62146723 | -7.02996% | SAME |

| kappa (layer1) | B | Gated pair label |
|---:|---:|---|
| +5 | -0.25 | SAME |
| +5 | -0.30 | OPPOSITE |
| -5 | -0.25 | SAME |
| -5 | -0.30 | OPPOSITE |

These are sampled scenario results, not a calibrated worst-case physical bound. The same directional factor multiplies w0 and w1, so their ratio is not independently varied by this strain option. The average-mode cancellation is built into the ansatz; it does not validate the general physical claim in the v045 headline. The source review provides primary literature and a concrete finite-twist qualification: the proposed mean of rotated valley radii has an O(epsilon theta) term. That calculation tests the geometric argument, not a microscopic hopping law.

## Sequence status and limits

| Segment | Current status |
|---|---|
| Early braid/deepening/unlinking parameter legs | v044: 148 accepted sampled states; separate lower unlink collision not resolved there. |
| Connections around the first annihilation | Our v043: 160 accepted states; v042 provides the first-annihilation fold and braid-2 window. |
| Post-braid-2 cleanup and upper collision | This batch: 68 fully gated cleanup states, four fold windows with 36 root-continuation states. |
| Later flat-pair birth, final annihilation and joins to gapped checkpoints | Next declared-model replay; historical results are retained as historical. |
| Earlier v023 preparation / lower unlink collision itself | Do not imply complete coverage from neighboring legs. |
| N>6 path replay / global N8 search / microscopic bilayer validation | Not performed. |

See SOURCE_REVIEW.md for the layered review, graded findings and ranked actions. The optional finite-coefficient patch has nine targeted passing assertions and preserves valid matrices. It is not used to generate the primary results. The v044 cutoff-tolerance patch remains separate and unadopted by the incoming toolkit. The new raw NaN witness establishes an input defect, not corruption of a recorded conclusion. PROTOCOL_ERRATA.md corrects the half-radius mesh metadata in the frozen plan: executed trials used the finer 512/2048 counts recorded in the source and results.

Finite searches can miss other nodes or extrema. Loop/mesh agreement and nondegenerate-fold diagnostics strengthen these local conclusions without establishing mathematical completeness. No claim is made that all original audit defects affected, or did not affect, every historical conclusion.
