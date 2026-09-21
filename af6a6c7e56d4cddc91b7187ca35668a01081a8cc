# Reproduce the v058 evidence

This batch measures four gaps at one N8 endpoint under lab_nn_full in two retained engines. Read REPORT.md and NUMERICAL_PLAN.json before execution. Prior N4/N6 values are saved evidence, not fresh measurements. The numerical plan was fixed before the N8 runs; PLAN.json covers the later publication sources and inputs.

Use the declared Python/package versions in ENVIRONMENT.txt and requirements.txt, with OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1. A complete transitive/native build lock is not supplied. Actual runtime package lists and native-library hashes are in each numerical and test record.

From research/v058, read-only reconciliation:

```bash
python -B -c 'import reconcile; print(reconcile.build()["status"])'
```

To run assertion tests, retain the immutable run record printed by:

```bash
python -B run_tests.py
```

To regenerate the report, use that exact record; a historical or source-mismatched pass count is rejected:

```bash
python -B build_report.py --test-evidence provenance/test_runs/RUN_ID/result.json
```

The packager preserves the tracked prior tree and the current batch; it does not reconstruct a missing byte-identical historical ZIP. It requires matching publication/test evidence, creates the output directory and refuses overwrites:

```bash
python -B package_release.py --output /absolute/path/out/twistronics_v058_reconciled.zip
```

Numerical replay is optional and materially more expensive. Use a separate copy, preserve the original results first, and give each engine a fresh results path by moving its old result outside that copy's results directory. Do not overwrite evidence in this delivered copy. Then run these commands, with at most two workers:

```bash
python -B run_endpoint.py bm_lab
python -B run_endpoint.py ref_lab
python -B reconcile.py
```

The runner refuses an existing case file and checks frozen inputs before/after execution. It imports the retained v055 models and guarded measurement helpers, walks no unrelated tree, makes no network calls, and invokes no subprocess, tests or publication. It writes its own case JSON incrementally, including failed attempts and runtime identities. Dependencies execute when imported. A copied replay produces new evidence and will need a new bound test run before publication.

The two engines share the eight-band eigensolver/gradient/search harness. This guards some implementation differences, not shared conceptual errors. Positive sampled minima and mesh agreement are not mathematical global bounds or physical validation. N8 w1 and path labels were not measured.
