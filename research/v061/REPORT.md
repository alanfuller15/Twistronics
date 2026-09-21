# Our v061: bounded N8 first-annihilation event

The first-annihilation event now has a bounded N8 result in both lab_nn_full engines, completed through an explicitly recorded recovery after both initial runs were rejected at the opening gate. An opposite-charge flat-band pair approaches a nondegenerate fold, positive flat-band gap searches follow, and the surviving upper pair at T=−0.74 is SAME in both engines. These are separate numerical witnesses; the upper-pair label alone is not proof of continuous charge transfer through the collision.

| Engine | N4 saved fold T | N6 saved fold T | N8 fresh fold T | N8 − N6 |
|---|---:|---:|---:|---:|
| bm_lab | -0.713373536075 | -0.713301013215 | -0.713301008028 | +5.188e-09 |
| ref_lab | -0.713386735792 | -0.713314259426 | -0.713314254237 | +5.189e-09 |

Largest absolute difference from retained N6 fold evidence: **5.18890364e-09** in T. N8 BM minus reference: **1.32462096e-05**. N4/N6 are retained v042 data, with their original event definitions and source hashes checked; they were not freshly executed here. Their searches and runtime evidence differ from this batch, so the observed differences are not a pure cutoff error bound.

Held state: A=0, B=−0.4, phi=65°, w0/w1=0.8, theta=1.05°, eps=0.003, w_kappa=0 and w_mode=average. T decreases from −0.70 to −0.74. Constant w1=110 meV and w0=88 meV remain the declared approximation. The selected gap is flat1|flat2 (eight-band index 3). BM keeps linear reciprocal geometry and cutoff_tol=1e-6; reference keeps exact reciprocal geometry and cutoff_tol=1e-9. Each N8 matrix has 972 rows. Roots and gap searches stay in the explicitly bounded [0,1]² chart, without periodic wrapping.

Each engine passes two derivative-step fold solves, rank-one spatial Jacobian and adjacent-band isolation checks, plus two resolutions of nonzero null curvature and transverse parameter slope. Eleven two-root continuation states per engine retain final optimizer metadata, seeds, residuals, distinctness and jump checks. Opposite spatial charge is measured at T=−0.70 and at each engine's fold+0.001, with bounded root refinement, 128/256 spatial meshes, both exterior gaps checked and sampled interior minima refined, and three loop/radius trials. No charge is assigned at the collision itself.

The local square-root separation law is checked at offsets 0.002, 0.001 and 0.00025. Maximum relative discrepancy: **1.02613%**; at the closest offset it is at most **0.127591%**. The offsets and 2% gate were chosen from retained N6 behavior before N8 execution. This is a local consistency check, not an extrapolation to infinite cutoff.

| Engine | N8 gap at own fold − 0.001 | N8 gap at fixed T=−0.74 | Fixed-T gap change from N6 |
|---|---:|---:|---:|
| bm_lab | 0.006770054281 | 0.165012433710 | +4.480e-08 |
| ref_lab | 0.006769126643 | 0.164913701927 | +4.480e-08 |

All gaps are in meV. The accepted opening searches are fresh recovery measurements. Both post-event stations use 18/24 interior grids and 24/48 boundary grids, with explicit edge/corner seeds, bounded refinements, final-result success/value consistency, projected-gradient checks and positive local curvature. The near-event station follows each cutoff's own fold; the T=−0.74 station is at the same parameter across cutoffs. Positive finite searches do not certify a global zero count.

The initial BM run stopped because all three optimizer attempts at one seed missed the 1e-4 projected-gradient gate, despite reporting convergence. The initial reference run stopped at the positive-curvature gate; its failed curvature values were not retained by the original helper. A separately frozen diagnostic reproduced coarse-step negative curvature with large asymmetry, then positive, agreeing curvature at 1e-6/5e-7. One gradient-polishing step reduced diagnostic gradient errors below 6e-8. These are diagnosed resolution issues, not permission to bypass a failed gate.

Recovery keeps the original projected-gradient, positive-gap and positive-curvature thresholds. It adds bounded Newton gradient polishing after the three original optimizer fallbacks, uses finer curvature steps 1e-6/5e-7, and requires 0.1% curvature-eigenvalue agreement and relative symmetry. The new helper also retains full partial searches on a curvature rejection. Accepted searches used **4 Newton polishing attempts**. Both original REJECT files, their frozen sources, the diagnostic plan/output and the separate recovery plan/output remain in the package. The fold/root/flat-pair prefix is reused by exact hash; it was not unnecessarily recomputed or relabelled as an originally successful run.

The upper pair at T=−0.74 is re-rooted from retained N6 seeds and measured with the same bounded spatial/loop gates. Its SAME label matches retained N6: **True**. Across both engines there are **22 paired-root states, four flat-pair charge stations, four post-event chart/edge searches and two upper-pair charge stations**. All six charge stations have three mesh/radius trials. Loop phase retry stages: **0**. Opening searches retain **262 optimizer attempts**, including **46 rejected attempts before accepted fallback**.

Publication: **120 assertion cases pass** in actual complete-suite run `20260921T041853Z_c108fe1d`, bound to current source, tests, inputs, results and runtime identity. The initial numerical plan and recovery plan were each frozen before their respective workers. The publication plan follows the combined measurements and precedes that bound test run. Unresolved witness failures or stale test claims block publication. Development test-collection errors and the first publication run are retained in provenance/DEVELOPMENT_CHECKS.md. That first bound run had 119 passes and one incorrect boundary-gradient mutation fixture; constrained stationarity correctly excluded its outward descent direction. The fixture was corrected to use feasible descent, its exact old source and failed run were kept, and the complete bound suite was rerun under a new publication plan. All 3,208 preserved prior tracked files remain unchanged, with the prior README copied into this batch's provenance.

Limits:

- Both initial frozen runs were rejected at the opening gate. The accepted summary combines their unchanged fold/root/flat-pair evidence with separately planned, freshly measured opening and upper-pair recovery; original REJECT records are retained.
- N4/N6 are retained accepted v042 records, not freshly run in v061. Their event definitions embed the held state; lab_nn_full engine linkage is verified through the retained models source. Historical opening searches used weaker edge and optimizer guards than v061.
- Near-event charge/opening stations follow each cutoff own fold offset. The fixed T=-0.74 comparison uses the same parameter. Retained N4/N6 environments and numerical searches are not rerun here, so these differences are not an isolated error bound on cutoff alone.
- Eleven root states, finite charge loops, sampled/located comparison gaps and chart/edge searches establish a bounded numerical event witness, not a continuous-interval or global node-count proof.
- The upper pair is measured independently at T=-0.74. SAME there does not by itself prove a continuous transfer of topological charge across the collision.
- Both engines share this measurement harness and constant-tunnelling lab_nn_full approximation. BM linear and reference exact reciprocal geometry are kept distinct.
- Absolute charge is not transported through the collision. No new full N8 campaign, flat-pair frame path, Euler class or endpoint w1 is claimed.
- Infinite-cutoff accuracy, microscopic tunnelling strain dependence, physical-bilayer validation and remaining historical consumer impact remain open. Source/test/result hashes are internal consistency evidence, not independent authenticity or physical truth.

Next bounded target: extend the N8 braid-2 leg from the existing 0.99100 checkpoint to 1.00000 in both engines, with two-seed continuation, carried frames and a separately frozen plan. That would complete this particular historical ratio leg; other connecting legs and topology checks would still be required for a full N8 campaign. Physical magnitudes still require a microscopic tunnelling strain law and independent reference or measurement evidence.

Start with `research/v061/REPORT.md`, `SUMMARY.json`, `IMPACT.json`, `NUMERICAL_PLAN.json`, `HISTORICAL_TARGETS.json`, and `RECOVERY.md`. Original rejected event records and accepted recovery records are in `results/`; worker logs and exact test evidence are in `provenance/`. The ZIP retains all prior campaign, audit and team history.
