# v039 source review and claim reconciliation

The uploaded archive has 93 regular files and one directory entry: 17 numbered
logs, two team notes, and 74 code/environment files. The input inventory and
SHA256 digests are preserved in provenance/. This is a focused review of the
v036-to-v039 changes, not a fresh full-read audit of all historical scripts.

Deep-read cutoff: the changed `tbg_ref.py` and `test_tbg_ref.py`, the five added
drivers, the regression tests, and the v037–v039 scientific notes relevant to the
new claims. `bm_strain.py`, `gate.py`, `knobs.py`, and `test_regression.py` are
byte-identical to their previously inspected v036 versions. The new measurement
adapter and reused gate implementation were also read before execution.

The reviewed uploaded model and test imports perform local numerical work with
NumPy/SciPy/pytest. They contain no network or subprocess calls and no deletion
operations. Historical scripts outside the cutoff were not executed. Tests
were explicitly authorized by the ongoing fix-and-remeasure task; the static
scanner's inspection-only default is a separate earlier workflow.

| Finding | Evidence in actual code | Grade and consequence |
|---|---|---|
| Original engine has no matching full-kinetic option | `bm_strain.py` is unchanged; only `tbg_ref.TBG` gained `kinetic` | Confirmed documentation overstatement in v039 §4. New full-variant measurements here use one Hamiltonian engine. |
| Full is not the constructor default | `kinetic=None` selects `geom_wrong` when `vrenorm=True` | Confirmed reuse risk. Every new run explicitly supplies `kinetic='full'`. |
| Tensor/gauge frame differs from the stated lab-strain expansion | `H` uses `V @ R(-theta)`; `Al` applies the crystal gauge formula to lab components | Confirmed convention mismatch against the explicitly specified nearest-neighbor monolayer model. Magnitude and label effects require separate measurements; no silent replacement is made. |
| Projection gate is useful but limited | `node_charge` checks loop subspace overlap >=0.9 and unit winding within 0.05 | Verified improvement, not complete acceptance coverage. No loop phase-step or mesh/radius agreement gate is present there; connecting transport has no isolation/SVD floor. |
| Charge function returns a numeric sentinel | Invalid `node_charge` returns 0; `relative_charge` converts nonunit results to INDETERMINATE | Callers must use the validated classifier. The raw function does not itself return the string INDETERMINATE. |
| Reported overlap is the second node only | Each `node_charge` overwrites `last_smin`; the two-seed driver prints it after both calls | The logged 0.991 is not demonstrably the minimum over the pair. The new harness records each loop and transport separately. |
| Radius bound can be bypassed | `r = r or min(0.01,0.3*sep)` | The stated bound holds for the default, not an arbitrary explicit radius. Coincident seeds have no explicit rejection in this routine. |
| Claimed merge-tolerance explanation is incomplete | Dedup threshold is 0.01, smaller than the reported 0.019 separation; separate cone checks use offsets 0.01 and gap threshold 0.05 meV | Under-counting is reported; the written inequality is false. A universal 0.05 completeness threshold is not established. Two refined seeds establish the known pair, not a complete node inventory. |
| Gap minimization can leave the fundamental chart | `gap_min` calls unbounded Nelder–Mead; periodic seed-neighbor comparisons do not enforce the refinement domain | A numerical convention matters at finite cutoff. New minima use bounded refinement and explicit seam seeds, following the v038 boundary correction. |
| N6 claims are not encoded by the 22 tests | The supplied suite covers baseline properties and cross-checks, predominantly N4/N3 | All 22 pass, but that alone does not verify the N6 campaign. This package supplies new raw gated N6 measurements. |
| A claimed 0.01 annihilation shift is not established by the cited brackets | Old and new brackets overlap; our prior old-model roots already lie between -0.72 and -0.71 | Compare located roots at matched cutoffs, not endpoints of coarse brackets. New roots are reported separately. |
| “Largest” endpoint shift is misidentified | v039 table gives lower-flat1 22.54→23.18 (about 0.64), versus flat2-upper 3.15→3.34 (about 0.19) | Arithmetic correction to §3; not a label change. |

The antiunitary basis and Hamiltonian adapter are checked for equivalence;
the measurement gate then verifies reality, Hermiticity, eigen residuals,
orthogonality, selected-group isolation, overlap, phase resolution, loop
closure, and mesh/radius consistency. A failed guard is a rejected measurement,
not evidence that a node disappeared or its charge changed.

The instrumented N4 replay now resolves the close-pair attribution. At the
v029 state, the 24x24 global search produces only **one local-minimum seed**.
It refines to the lower-x node; both of its cone samples pass (0.444 and
2.119 meV). The other node is never proposed, so neither merging nor rejection
by the cone check causes this observed under-count. Two local seeds recover
the pair with separation 0.01941555 and opposite charges. This diagnosis is
for the reproduced N4 run; the N6 search internals were not instrumented.

The same diagnostic independently reproduces the uploaded endpoint search's
23.17645445 meV lower gap. Evaluating the **same uploaded Hamiltonian** at the
boundary-seeded point (0.99217659, 0.29298133) gives 23.03669106 meV, matching
the guarded adapter. This is a search correction, not a model change.

At N4 the separately recorded loop overlaps are 0.995316 and 0.990871. Thus
the printed last value happens to equal the pair minimum for this ordering;
the bookkeeping limitation does not invalidate that particular rounded value.

There are two independently authored entries called v038. The partner's v038
discusses the audit and kinetic convention. Our v038 contains the later-path
replay and earlier-endpoint result. Both are retained in separate directories
in the delivery, so one cannot overwrite the other's evidence.
