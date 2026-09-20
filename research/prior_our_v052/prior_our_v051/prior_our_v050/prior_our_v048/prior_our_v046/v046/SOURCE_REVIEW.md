# v045 incremental review

The strongest new evidence is local endpoint stability and a reproducible, limited tunneling sensitivity experiment. The most urgent correction is to separate that evidence from a universal physical law or worst-case bound. The supplied 30 tests pass; the new numerical results and nine guard assertions are `[self-tested]`, not independently validated physics. This is an incremental review of changed/new high-impact files, not a complete project or CVE audit. A flag establishes presence for triage, not truth.

## Ranked actions

1. **Red — unsupported physical closure.** Replace the universal tunneling-law / physical worst-case claims with the explicit constant-amplitude approximation and sampled scenario limits. **Tier:** `[fetched]` primary derivations plus `[checked]` code. **Verdict:** the broad claim remains unverified; no need to stop replay of the declared numerical model.
2. **Yellow — incomplete campaign connections.** Cleanup and the upper collision pass in this batch; next replay the flat birth/final annihilation and their checkpoint joins. Keep the omitted preparation/lower unlink event explicit. **Tier:** sandbox `[self-tested]` records and user-supplied sequence. **Verdict:** measured portions hold; whole-campaign completion remains unverified.
3. **Yellow — overly broad magnitude claims.** Describe N6→N8 agreement as local cutoff stability; use the measured ~7.4% sampled sensitivity instead of a strict 7% physical bound. **Tier:** sandbox `[self-tested]` results. **Verdict:** narrow measurements hold; broader bounds do not follow.
4. **Yellow — input and cutoff guards.** Adopt the finite-coefficient guard and review the v044 explicit cutoff-tolerance patch with historical defaults retained. **Tier:** `[checked]` code and sandbox `[self-tested]` counterexamples/tests. **Verdict:** guard gaps hold; no recorded-label impact established.
5. **Green — preserve reproducibility.** Keep sources, frozen protocols, raw accepted/rejected stages, comparison matrices and exact reproduction commands. **Tier:** sandbox `[self-tested]`. **Verdict:** supplied tests and the targeted matrix/default checks pass.

## Findings table — ground truth and grades

| Finding | Tier / verdict | Evidence and disposition |
|---|---|---|
| Average-mode cancellation | `[checked]` / holds for implemented algebra | The code sets the layer strains to exact opposites and projects both onto the same direction. Their average is identically zero. All finite tested coefficients therefore leave the matrices unchanged. There is no homostrain input or second-order tunneling term. |
| “Heterostrain has no first-order amplitude correction” | `[fetched]` + `[checked]` / unverified general physical claim | A common momentum does not by itself identify its magnitude with the mean of two valley magnitudes. The additional approximation must be stated. Constant amplitudes remain a usable declared model. |
| Layer-1 ±5 is a “worst-case bound” | `[checked]` / unverified physical bound | Both AA and AB amplitudes receive the same directional scale, preserving their ratio. Seven distinct N4 configurations cannot bound arbitrary AA/AB responses or the full path. No physical coefficient range was derived. |
| “≤7% and no label anywhere” | sandbox `[self-tested]` / fails as a universal or strict 7% claim | The logged baseline values already imply about +7.38% and −7.03%, not a strict 7% bound. The label evidence concerns the baseline and two braid endpoints for each sign. |
| N6→N8 endpoint agreement | sandbox `[self-tested]` / holds locally; global and infinite-cutoff claims unverified | Four known minima can establish local cutoff stability. This is neither a new global N8 search nor an upper bound on the error relative to infinite cutoff. The headline must retain that distinction. |
| Earlier braid/deepening/unlinking listed open | prior sandbox `[self-tested]` records / fails as current status | v044 completed the declared 148 sampled early-route states. It did not separately resolve the lower unlink collision or the earlier v023 preparation. |
| Full campaign completion after cleanup | `[checked]` sequence records / unverified | The later flat-pair birth/final annihilation and their joins still need the declared-model replay; any omitted preparation or lower unlink event stays explicit. |
| Cutoff padding | `[checked]` + prior sandbox `[self-tested]` / holds | BM retains 1e-6 and TBG 1e-9 inverse Angstroms. The v044 counterexample and optional patch are preserved; v045 did not adopt that API. |
| Nonfinite `w_kappa` | `[checked]` + sandbox `[self-tested]` / guard-gap claim holds; historical impact unverified | Raw BM accepts NaN and creates nonfinite tunneling matrices. The replay adapter rejects it. A separate nine-case tested patch rejects nonfinite input and corrects misleading comments without changing valid matrices. No campaign run used NaN. |

## Layer 1 — inventory and changes

The supplied archive contains 115 entries: 114 files and one directory. Its SHA256 is `cc22853d630eec758be15bd4e09145ddb2945661b332f959d2bba9590483b411`. Relative to the incoming v043 toolkit, only `bm_strain.py` and `test_regression.py` changed. Fourteen files were added: the newer logs/team notes, three numerical drivers and their recorded outputs. The full inventory and source diff are in `provenance/`.

All 30 supplied tests pass. That includes an assertion that the average-strain formula cancels; it is an implementation assertion, not a test of the physical derivation. No new dependency version or CVE conclusion is asserted in this incremental scientific review. The original audit scanner was not rerun on this already-reviewed toolkit; this sweep uses inventory, byte comparison and source inspection rather than claiming a fresh scanner report.

## Layer 2 — deep-read cutoff and runtime behavior

Deep review covers the changed BM constructor and tunneling assembly; the new regression test; complete `w_strain_sens.py`, `endpoint_locate.py` and `anchors_braid1.py`; the v045 log and team note; and the numerical guard/continuation code used for this batch. Unchanged legacy drivers were not all reread or rerun. The two engines, gate and shared measurement helpers retain the earlier review's scope and qualifications.

The three new drivers import local numerical modules, construct models, run eigensolvers/optimizers and print results. They have no explicit network calls, filesystem deletions or subprocess calls. `endpoint_locate.py` reads optional JSON seeds from a command-line argument; the other new drivers do not read project data files. These are executable numerical experiments, unlike the original inspection-only scanner. Their computations are authorized by the ongoing replay task. Python imports can create bytecode caches unless disabled; the runs here disable them. Output redirection writes only the recorded logs. The unchanged imports are not a renewed whole-environment security guarantee.

`w_strain_sens.py` uses one loop mesh and radius, plus an older gap search, so its printed labels alone do not satisfy the current mesh/radius gate. The v046 sensitivity probe uses the stronger shared gate. `endpoint_locate.py` bounds its local optimizer but silently drops failed starts, does not log each optimizer result and uses one prior seed per gap at N8. The v046 local probe retains success, improvement, projected gradient, curvature and three-start agreement.

## Layer 3 — source checks and claim limits

### A concrete limit of the mean-radius argument

The new `mean_radius_probe.py` checks the proposed geometric cancellation itself. For opposite lab-frame strains, exact inverse deformation and fixed nonzero twist, the mean of the two *rotated* valley radii has

\[\left.\frac{d(\bar K_j/K_D)}{d\epsilon}\right|_0=-\frac{1+\nu}{4}\sin[2(\phi-\alpha_j)]\sin\theta.\]

Thus the literal mean-radius cancellation is not exact at finite twist. Two centered difference steps agree with this analytic derivative. At phi=80 degrees and j=0 it is about −0.001818 per unit strain; even phi=0 has nonzero values for j=1,2. This is an O(epsilon theta) qualification of that *geometric argument*, not a computed physical tunneling correction. A declared joint small-angle approximation may discard it. The code instead projects both strains onto one unrotated direction and cancels identically. State that approximation rather than claiming only O(epsilon squared) remains. Tier: `[checked]` algebra and sandbox `[self-tested]` calculation.

### Physical interpretation and sources

Koshino's general coupling is evaluated at a matched extended-zone momentum, with cell-area normalization; the matching condition does not require that momentum to be the average of the two valley radii. Choosing an expansion point is an additional modeling step. This is why we do not accept the mean-radius cancellation as a general theorem. [Koshino, *Interlayer interaction in general incommensurate atomic layers*, equations 5–6](https://arxiv.org/pdf/1501.02116).

Koshino and Nam explicitly neglect small momentum shifts to obtain their long-wavelength coupling. For in-plane displacement, that approximation has a constant amplitude and displacement-dependent phase. Their more general expression retains momentum dependence, and they discuss restoring its linear contribution. This supports a declared constant-amplitude approximation, not an unrestricted absence of corrections. Our inference is to keep constant w0,w1 for the campaign while treating v045's layer-1 modification as a separate scenario. [Koshino and Nam, equations 15, 22–23 and section III](https://arxiv.org/html/1909.10786v2).

We have not computed a microscopic strain derivative for a relaxed physical bilayer, proved a universal nonzero correction, or bounded omitted terms. Neither source lookup nor cross-engine agreement supplies that missing validation.

### Search and charter provenance

Four named primary-paper candidates were considered: Bistritzer–MacDonald, Bi–Yuan–Fu, Koshino (2015), and Koshino–Nam. Two relevant full texts were fetched and read: the two linked above. The other two are not used to support this review. Broad keyword results were discarded as irrelevant. These authors derive the interlayer models being discussed; their purpose is theoretical modeling, not certification of this toolkit. The two relied-on papers share an author and are not counted as independent implementations or independent experimental corroboration.

The original charter boot block and audit method were consulted. No `genesis.py` was found: tool absent, boot/handoff presence checked by hand only. This continuation does not ratify or amend the charter. Artifact consumption remains `[unconfirmed]` until the user can use the package. A recipient-side acceptance check is provided in README.md; its successful execution would be another reproducibility check, not physical-bilayer validation.
