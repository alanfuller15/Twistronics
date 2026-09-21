# TEAM SHARE — our v060

The braid-2 critical window now has a fresh N8 replay in both lab_nn_full engines, with a separately frozen numerical plan. At five ratio values from 0.99000 through 0.99100, both engines reproduce the change in the spatial charge comparison. Each individually carried temporal node charge stays constant. The comparison path becomes singular when the upper-next node X1 crosses the U1–U2 segment; the isolation gate explicitly rejects that singular comparison.

| Engine | N4 saved crossing | N6 saved crossing | N8 fresh crossing | N8 − N6 |
|---|---:|---:|---:|---:|
| bm_lab | 0.990538737326 | 0.990766131348 | 0.990766131188 | -1.599e-10 |
| ref_lab | 0.990541398173 | 0.990768790949 | 0.990768790789 | -1.599e-10 |

Largest absolute N6→N8 crossing shift: **1.59939062e-10** in w0/w1. N8 BM minus reference: **-2.65960079e-06**. N4/N6 values come from retained v042 records. The held-state linkage of those historical records is contextual through the retained runner and State definition; it was not embedded in the old raw records.

| Ratio w0/w1 | BM N8 | Reference N8 |
|---:|---|---|
| 0.99000 | SAME | SAME |
| 0.99025 | SAME | SAME |
| 0.99050 | SAME | SAME |
| 0.99075 | SAME | SAME |
| 0.99100 | OPPOSITE | OPPOSITE |

Held state: A=0, B=−0.4, T=−0.8, phi=80°, theta=1.05°, eps=0.003, w_kappa=0 and w_mode=average. The approximation keeps w1=110 meV while w0=110 times the ratio. BM retains linear reciprocal geometry with cutoff_tol=1e-6; reference retains exact reciprocal geometry with cutoff_tol=1e-9. The root chart is explicitly unwrapped: [0,1] × [0,1.1]. U2 remains above f2=1; no periodic wrap is applied to a finite-cutoff Hamiltonian.

Evidence: **10 states, 60 continued roots, 4 coarse/fine parameter-frame comparisons, 10 saved frame checkpoints and 30 loop/radius trials**. Each loop/radius trial measures both temporal charges and the directly transported spatial B charge. Spatial transport is compared at 128/256 base steps, with explicit adjacent-node seeds and located minima of both exterior gaps. Minimum accepted sampled/located comparison gap: **0.00158857322 meV**. This positive off-event minimum is distinct from the rejected zero-gap crossing. Phase-only loop retry stages used: **0**.

Each crossing is solved at two Brent tolerances, with final optimizer metadata and all distinct evaluations retained. The point on the U segment has exterior gap below 1e-5 meV and fails specifically with `selected group loses isolation`. Saved frames are checked for hash/record agreement, shape, finiteness, orthonormality, temporal overlaps, spatial orientation and coarse/fine determinants. These artifact checks do not recompute the eigensolver.

At the common retained N6 ratios 0.99000 and 0.99100, labels agree: **True**. Largest displacement among the six tracked roots at those common ratios: **2.39570623e-09** in fractional reciprocal coordinates. Values at the three intervening N8 states are new finer sampling, not matched N6 measurements.

Publication evidence: **67 assertion cases pass**, actual complete-suite run `20260921T034451Z_53fc8635`, bound to source, tests, numerical inputs, result files and runtime identity. The numerical source plan was frozen before the workers. The separate publication plan is frozen after measurements and before the bound test run. Neither hash timing nor a self-authored test suite is independent attestation. All 3,149 preserved prior tracked files are retained unchanged; prior README is copied into this batch's provenance.

Limits:

- Five finite states per engine cover ratio 0.99000 to 0.99100, not the full historical 0.99 to 1.00 braid-2 leg, a continuous interval or the entire N8 campaign.
- The spatial comparison changes SAME to OPPOSITE; the two temporally carried individual charges remain constant. At the crossing the spatial comparison loses isolation and is rejected.
- Retained v042 accepted results; held-state linkage is contextual through replay_second.py -> models.State, not embedded in the old raw records. N4/N6 are not freshly executed in v060.
- The engines share this measurement harness and a constant-tunnelling lab_nn_full approximation; BM linear and reference exact reciprocal geometry remain distinct.
- Located gap minima, frame overlaps and mesh/radius agreement are finite numerical evidence, not global gap bounds or an independent scientific reference.
- This does not extend the flat-pair frame path, Euler class, endpoint w1, first-annihilation event or all connecting legs to N8. Infinite-cutoff accuracy, microscopic tunnelling strain dependence and physical validation remain open.
- Source/test/result hashes establish internal consistency, not independent authenticity, chronology or physical truth.

Next bounded target: the first-annihilation critical event at N8 in both engines, starting from retained N4/N6 roots and fold diagnostics under a new frozen plan. A complete N8 campaign would still require the connecting legs, longer braid-2 leg and relevant frame/topological checks. Any physical magnitude claim still needs a microscopic tunnelling strain law and independent reference or measurement evidence.

Start with `research/v060/REPORT.md`, `SUMMARY.json`, `IMPACT.json`, `NUMERICAL_PLAN.json`, and `HISTORICAL_TARGETS.json`. Complete records and ten frame checkpoints are in `results/`; test evidence and worker logs are in `provenance/`. This ZIP also retains prior campaign, audit and team history.
