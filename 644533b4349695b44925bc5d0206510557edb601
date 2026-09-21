# TEAM SHARE — our v059

The lower unlink collision now has a bounded N8 replay in both lab_nn_full engines. The held state is A=0.2, B=−0.4, phi=0°, w0/w1=0.8, theta=1.05°, eps=0.003, with T running from 0 to −0.4 and the lower-remote|flat1 gap selected. Constant w1=110 meV and w0=88 meV remain the declared approximation. BM keeps linear reciprocal geometry and cutoff_tol=1e-6; reference keeps exact reciprocal geometry and cutoff_tol=1e-9. This is the separate lower unlink event, not the final endpoint studied in v058.

| Engine | N4 saved fold T | N6 saved fold T | N8 fresh fold T | N8 − N6 |
|---|---:|---:|---:|---:|
| bm_lab | -0.312298156481 | -0.312154206436 | -0.312154197057 | +9.379e-09 |
| ref_lab | -0.312293103303 | -0.312149153587 | -0.312149144208 | +9.379e-09 |

Largest absolute N6→N8 fold shift: **9.37897943e-09** in dimensionless T. BM minus reference at N8: **-5.05284899e-06**; those engines retain different geometry approximations. N4/N6 are hashed v055 evidence, not fresh runs here.

Each N8 engine passes two derivative-resolution fold solves, rank-one Jacobian and external-isolation checks, and two finite-difference checks of nonzero null curvature and transverse parameter slope. Both predict the pair on the T>fold side. **22 bounded root stations** track the pair in total. In addition to the original nine-station layout, each engine samples fold+0.004 and fold+0.00025. At offsets 0.004, 0.001 and 0.00025, observed squared node separation agrees with the local fold coefficient times offset within the frozen 2% tolerance. Largest measured relative discrepancy across the six checks: **0.650310%**. This tests the local square-root closing law numerically.

The two charge stations in each engine are T=0 and that engine's fold+0.001. All four are **OPPOSITE** under the retained mesh/radius gate: 256/512 loops at the same radius, 512 at half radius, with 128/256 spatial transport, located exterior-gap minima and orientation checks. Only unresolved phase steps permit the recorded finer fallback. Agreement with the saved N6 station labels: **True**. Absolute charges are not transported through annihilation, and the closest extra root station at fold+0.00025 is a root/separation check, not an additional charge measurement.

| Engine | Gap at own fold − 0.001, N8 | Gap at fixed T=−0.4, N8 | Fixed-T gap change from N6 |
|---|---:|---:|---:|
| bm_lab | 0.052217474090 | 4.780530700292 | +9.408e-07 |
| ref_lab | 0.052217187750 | 4.780792736646 | +9.408e-07 |

Gap values and differences are meV. Opening checks use 18/24 interval grids including both chart faces, explicit 24/48 edge searches, corner/inward/fold seeds and bounded optimization. Every selected result passes finite-value, non-worsening, projected-gradient and local-curvature checks, and both meshes agree within 0.001 meV. Opening searches record **241 optimizer attempts**, including **23 rejected attempts before accepted fallback**. Near-fold gaps are compared at the same offset from each cutoff's own fold; the fixed-T=−0.4 gap is a same-parameter cutoff comparison. Positive finite searches are not a rigorous global no-node proof.

**85 tests passed in bound run `20260921T031515Z_8e5cfaca`**, evidence SHA256 `47949f04612026c6664b6e9923265f721647bc7f44b721cc1d8c0e3bb8d197ec`. Tests exercise normal forms, wrong fold side, nonfinite/failed optimization, separation scaling, corrupted event/charge/gap records, test-evidence binding and deterministic packaging. The published count comes from actual collection/execution/JUnit tied to current source/tests/inputs/runtime. Two single-thread numerical workers record matching runtime identities before and after execution. NUMERICAL_PLAN.json was frozen before the workers; PLAN.json is the later publication freeze. Prior tracked records and the previous README are preserved.

Coverage gained: one N8 critical event in each engine, in addition to v058's endpoint-gap comparison. The historical N4/N6 campaign coverage stays unchanged. The entire N8 braid sequence has not been replayed, and this batch does not extend the flat-pair frame path, Euler class or endpoint w1 to N8.

Limits: N8 is fresh; N4/N6 are hashed retained v055 evidence. Near-event charge/opening stations use each cutoff's own fold offset, not identical absolute T. This covers one N8 event with finite root, loop, transport and gap samples, not the complete N8 campaign or a continuous-interval proof. Positive finite chart/edge searches do not certify a global zero count; square-root agreement and derivative refinement are local numerical evidence. Both engines share the measurement harness and constant-tunnelling lab_nn_full approximation; BM linear and reference exact reciprocal geometry are kept distinct. Absolute charge is not transported through the collision. The flat-pair frame path, Euler class and endpoint w1 are not remeasured here. Infinite-cutoff accuracy, microscopic tunnelling strain dependence, physical-bilayer validation and remaining historical consumer impact are not established.

Next bounded numerical target: the braid-2 critical window at N8, selected from its retained N4/N6 brackets and continued with two seeds in each engine under a separately frozen plan. Broader historical consumer-impact questions remain open. Any physical magnitude claim still needs the inventor's intended acceptance target, a microscopic tunnelling strain law and independent reference or measurement evidence.

Start with `research/v059/REPORT.md`, `SUMMARY.json`, `IMPACT.json`, `NUMERICAL_PLAN.json`, `HISTORICAL_TARGETS.json` and both complete event records in `results/`. The ZIP includes prior campaign/audit/team history and the v055 handoff correction.
