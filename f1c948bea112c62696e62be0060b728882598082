# v060: bounded N8 braid-2 crossing

Read REPORT.md and TEAM_SHARE_v060.md for measured results and limits. NUMERICAL_PLAN.json froze the five-state workers before execution. PLAN.json separately binds publication sources and inputs after measurements. Both engines and prior evidence are retained in the repository.

Use Python 3.12 with the versions declared in requirements.txt and ENVIRONMENT.txt. Set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1 for all commands. Existing result files are protected from overwrite. Fresh numerical execution requires a separately labelled working copy with empty v060/results, preserving this delivery's evidence.

```
python -B research/v060/run_window.py bm_lab
python -B research/v060/run_window.py ref_lab
python -B research/v060/reconcile.py
python -B research/v060/run_tests.py
python -B research/v060/build_report.py --test-evidence research/v060/provenance/test_runs/RUN_ID/result.json
python -B research/v060/package_release.py --output /absolute/path/outside/repository/twistronics_v060_reconciled.zip
```

For an unchanged extraction, the supplied test-evidence path in SUMMARY.json can be reused for report/packaging only if source, result and complete runtime identities match. It represents that historical run, not a new pass. Run_tests creates a new immutable test record. Do not edit a frozen plan or present a new numerical run as the old evidence identity. METHOD.md describes gates; NEXT_SEQUENCE.md bounds the follow-up.
