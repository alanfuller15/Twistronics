# v041 source review

The new input contains 97 ZIP entries: 96 regular files and one directory.
There are 18 numbered log files (v023–v039, then v041), not 19; v040 is adopted
by reference rather than included as a numbered file. The separately attached
v041 Markdown is byte-identical to the archive's v041 log. The original input
files are preserved unchanged.

The review cutoff is explicit: full changed sections of `bm_strain.py`,
`tbg_ref.py`, and `test_tbg_ref.py`, the new `cross_kinetic.py`, their numerical
imports, the relevant v041 claims, and the reused measurement gate/adapters.
Earlier unchanged source was compared by bytes to the previously reviewed
archive. Historical scripts were mechanically inspected for direct API calls;
this is not a fresh full-read audit of every project file. The older connecting
logs were consulted to identify the next path work, not to certify it.

The reviewed model/test changes use local NumPy/SciPy/pytest calculations.
They contain no network calls, subprocess invocation or deletion operations.
The numerical drivers here write explicit JSON/log outputs and atomically
replace their own result checkpoints. No uploaded source was modified or
silently imported from an older engine version.

| Item | Code-grounded finding | Disposition |
|---|---|---|
| Lab-frame kinetic/gauge prescription | Both engines use R^T[I+(1-beta)E] and rotate the crystal-frame gauge back to the lab | Verified. Adapter/matrix checks cover baseline and later campaign states at N4/N6. |
| Remaining geometry difference | BM uses `(I-E)R` for reciprocal corners; TBG uses `(I+E)^(-T)R` | Retained and quantified. It is a higher-order geometry approximation, not purely cutoff error. Matching only q/G removes the measured matrix discrepancy to roundoff. No such replacement is made in a primary replay. |
| Explicit TBG kinetic option | Missing/invalid option raises ValueError | Verified. Every primary adapter names `lab_nn_full`. BM retains its documented `none` default. |
| Invalid charge sentinel | `node_charge` returns None for failed overlap/unit-winding gates; classifier handles None before arithmetic | Verified. A new integration test requires None from a deliberately poor projection; the supplied test permits either None or a unit charge. |
| Per-loop overlap | Both loop minima are collected and `last_smin` becomes their minimum | Verified in source. Primary measurements additionally retain each loop and every transport diagnostic. |
| Radius and coincident seeds | Coincident seeds are rejected; positive requested radii are capped by 0.01 and 0.3 times separation | Improved. Negative/nonfinite radius inputs are still not explicitly validated. These inputs are never used by the primary harness. |
| Bounded gap search | Bounds [0,1]^2 and candidate-derived boundary seeds are present | Improved. `gap_min` still skips failed optimizations and can return positive infinity if none succeed. It does not return a failure record or check seed-value worsening. The primary harness uses explicit failure, finiteness, seed and grid gates instead. |
| Seam coverage | Integer shifts of an interior candidate are usually outside the cell; the other two projections choose only one side per coordinate | The added code is not a general search-completeness guarantee. Primary searches include all edges/corners and opposite-side seeds. |
| Legacy driver compatibility | Five retained drivers call TBG without `kinetic`; two also pass removed `vrenorm` | They need explicit historical options or matching historical source before reuse. The missing-kinetic call in the new negative test is intentional. No old driver was executed. |
| First-annihilation comparison in v041 §2 | Its “original-model root -0.7120” conflicts with the accepted v038/v040 source records | Transcription correction: original N4/N6 roots were -0.71514090/-0.71505612; v040 full roots were -0.71354964/-0.71347762. The adopted shift remains about +0.0016. |
| “Below every other uncertainty” | The 0.004 meV comparison is a baseline model sensitivity; no comprehensive uncertainty budget is supplied | Keep it specific to measured states and compared errors. New replay data quantify later-state effects without promoting this phrase to a universal bound. |

All 27 supplied tests pass. That establishes the supplied suite's checks, not
the N6 paths; those have separate raw numerical evidence here. Seven new
integration tests verify the real-Hamiltonian gate, isolation rejection,
phase-resolution rejection, invalid projection sentinel and coincident seeds.
Matrix attribution and scientific path measurements are recorded separately.

The two remaining public-helper guard issues are reproduced without a
physical calculation in `probe_source_guards.py`. A forced optimization
failure makes the uploaded helper return positive infinity, which would pass
a naive `gap > 0` test. The primary harness never calls this helper. A small
ready-to-apply patch and eight focused regression cases are supplied in
`fixes/` and `tests/test_helper_patch.py`. It rejects failed/nonfinite or
seed-worsening minimization and invalid radii. A subsequent real endpoint
probe found that the revised public helper still overestimates the N4 lower
gap: 23.04897392 versus 23.03669106 meV for full, and 23.04217862 versus
23.02919135 meV for lab_nn_full. Both tested grids agree on those higher
values. The patch also adds both faces and inward seeds, with two additional
endpoint regression cases (ten patch tests total). It is not substituted into
the scientific runs; it changes no Hamiltonian or claimed label.

The close-pair search still has no global completeness certificate. Distinct
seed continuation, residuals and local fold checks are used for the known
annihilating pair; no failed global search is interpreted as annihilation.
Likewise, a code flag identifies something to investigate, not a topological
verdict. The report distinguishes accepted measurements from recorded claims
and from work not performed in this batch.
