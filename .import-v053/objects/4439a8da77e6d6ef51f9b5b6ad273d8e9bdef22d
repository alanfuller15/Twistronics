# v046 — cleanup, upper collision and v045 claim checks

Read `REPORT.md` for the numerical result, `SOURCE_REVIEW.md` for the graded incremental review and `TEAM_SHARE_v046.md` for the short handoff.

`PLAN.json` fixes the primary sources, accepted anchors and numerical gates. `PROBE_PLAN.json` fixes the separate v045 claim probes. Primary replay retains the uploaded engine implementations, their historical cutoff padding, and constant tunneling amplitudes. `bm_lab` uses linear reciprocal geometry; `ref_lab` uses inverse deformation. Both explicitly request `lab_nn_full`. `bm_exact` is used only for the named tunneling sensitivity scenarios, matching the supplied sensitivity script.

Run from this directory with Python, NumPy and SciPy versions recorded in `provenance/environment.json`. Use `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`. Run at most two workers:

```
python run_sequence.py --engine bm_lab
python run_sequence.py --engine ref_lab
```

Each worker runs cleanup then the upper collision at N4, then N6. A committed cleanup step contains JSON and a digest-bound frame archive. Re-running resumes it after verifying protocol, step ordering and frame hashes. A partial write is never a committed step. The second-braid join reestablishes a local orientation and checks the two root identities: it does not claim recovery of an unsaved historical absolute frame sign. The carried charge signs are meaningful within this new continuation.

After a worker slot is free:

```
python claim_worker.py
```

This checks the two recorded protocols, then runs the guarded local endpoint and seven-configuration sensitivity probes. Full-matrix default invariance is independently reproduced with `python default_probe.py`, using the preserved comparison source under `provenance/prior_bm_strain.py`.

The supplied 30-test result is retained separately from the nine new adapter/optional-patch assertions. Run the latter using `python -m pytest tests -q -p no:cacheprovider`. The optional `fixes/tunneling_input.patch` applies to the incoming toolkit BM file. It is not used in primary measurements and does not incorporate the separate v044 cutoff-tolerance patch. Both patches are independently available in the preserved history; composing them requires reviewing their constructor edits together.

Finite meshes, seeds, loop refinements and two cutoffs provide numerical evidence. They do not prove global node completeness, bound the infinite-cutoff error, validate a microscopic strain law, or establish the physical behavior of a relaxed bilayer. The remaining campaign legs are recorded in the report rather than marked completed by association.

Acceptance on your machine: extract the single package, enter `v046/`, read REPORT.md together with SOURCE_REVIEW.md, and run the nine targeted assertions plus `python default_probe.py`. Confirm that the report's four engine/cutoff rows and the raw JSON records are usable for your next replay. The source hashes and committed-frame hashes can be checked with `python build_report.py`; it verifies completed records before rebuilding the summary. Numerical passes here are `[self-tested]`. File consumption is `[unconfirmed]` until you report successful use; this does not delay the authorized numerical work.

`PROTOCOL_ERRATA.md` records the half-radius loop-count metadata correction; the frozen source and raw measurements use the finer counts. `mean_radius_probe.py` separately checks the finite-twist qualification of the mean-valley-radius argument.
