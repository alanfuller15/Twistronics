# v062: N8 braid-2 continuation

Read REPORT.md and TEAM_SHARE_v062.md for results, COVERAGE.md for remaining campaign work, and METHOD.md for exact scope. NUMERICAL_PLAN.json froze the numerical code, inherited frames and six root seeds before workers ran. PLAN.json separately binds publication after measurement. The complete earlier tree and its failure history are retained.

Use requirements.txt and ENVIRONMENT.txt. Set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1 for every command. Run at most two numerical workers. The supplied numerical outputs are immutable; run_window.py refuses to overwrite its result/checkpoint paths. A new numerical replay requires a separately labelled copy and plan, preserving the supplied delivery and predecessor checkpoints.

```bash
python3 -B research/v062/run_window.py bm_lab
python3 -B research/v062/run_window.py ref_lab
python3 -B research/v062/reconcile.py
python3 -B research/v062/coverage.py
python3 -B research/v062/run_tests.py
python3 -B research/v062/build_report.py --test-evidence research/v062/provenance/test_runs/RUN_ID/result.json
python3 -B research/v062/package_release.py --output /absolute/path/outside/repository/twistronics_v062_reconciled.zip
```

The coverage JSON is generated before the publication freeze. In the unchanged delivery, the supplied coverage and impact are recalculated and compared by the report builder. The source-bound test record selected in SUMMARY.json can be used for unchanged standalone repackaging only when complete code, inputs and runtime still match. It is evidence of that retained run, not a new test pass. run_tests.py records a new immutable complete-suite execution when a fresh run is needed.

The wrapper executes only the two declared numerical engines, SciPy/NumPy calculations and local reads/writes. There are no network calls or subprocesses in the numerical runner or its local helpers. run_tests.py invokes a fixed pytest worker as a subprocess; that intentionally executes the tests. The packager writes a new ZIP outside the repository and refuses an existing output path. Reconcile/report commands write their derived local files. The report is gated by current matching test evidence and preservation hashes.

The root chart is explicitly unwrapped. The executable alias difference between the old python and new python3 invocation is recorded and checked by resolved path and binary hash. Preserved environment identity includes native library hashes and thread settings, but is not a portable dependency lock or independent attestation. No scientific or security clearance is inferred from a passing suite.
