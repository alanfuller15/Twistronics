# v061: first annihilation at N8

Read REPORT.md and TEAM_SHARE_v061.md for measured results and limits. NUMERICAL_PLAN.json froze numerical code/inputs before execution; PLAN.json separately binds publication after measurements. Both engines and the complete prior tree remain in this repository.

Use the versions in requirements.txt and ENVIRONMENT.txt. Set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1 for every command. Initial event and recovery workers refuse to overwrite their named records. The diagnostic helper writes its named output path and can replace it; its commands below document the recorded workflow, and should only be repeated on a separately preserved copy. For a fresh numerical experiment, create a separately labelled plan/copy preserving this delivery. The supplied recovery is deliberately bound to the exact rejected-result hashes; newly executed initial workers produce new timestamps/hashes and cannot silently replace those recovery inputs.

```
python -B research/v061/run_event.py bm_lab
python -B research/v061/run_event.py ref_lab
python -B research/v061/recovery/diagnose.py bm_lab
python -B research/v061/recovery/diagnose.py ref_lab
python -B research/v061/recovery/run_recovery.py bm_lab
python -B research/v061/recovery/run_recovery.py ref_lab
python -B research/v061/reconcile.py
python -B research/v061/run_tests.py
python -B research/v061/build_report.py --test-evidence research/v061/provenance/test_runs/RUN_ID/result.json
python -B research/v061/package_release.py --output /absolute/path/outside/repository/twistronics_v061_reconciled.zip
```

For an unchanged extraction, the evidence path in SUMMARY.json can support report/packaging only if the complete source, result and runtime identities match. It is evidence of the supplied run, not a new test pass. run_tests.py creates a new immutable execution record. Keep numerical and publication freezes distinct; changing a plan requires a newly labelled comparison, not relabelling existing measurements.
