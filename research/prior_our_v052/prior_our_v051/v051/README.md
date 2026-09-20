# Our v051: local preparation events

Start with REPORT.md and TEAM_SHARE_v051.md. METHOD.md gives the new local-domain gate. SOURCE_REVIEW.md contains the layered review and ranked actions. SUMMARY.json and PLAN.json hold machine-readable results and frozen scientific sources.

The complete prior delivery is retained in ../prior_our_v050/. This is our v051 continuation, not a partner log entry. No incoming record was overwritten.

From this directory, using the versions in ENVIRONMENT.txt / requirements.txt:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 run_local.py --engine bm_lab --N 4
python3 run_local.py --engine ref_lab --N 4
python3 run_local.py --engine bm_lab --N 6
python3 run_local.py --engine ref_lab --N 6
python3 -m pytest -q -p no:cacheprovider tests
python3 build_report.py
```

Run no more than two numerical workers. Each invocation runs birth then annihilation at the selected engine/cutoff. Existing ACCEPT results with the same protocol are skipped. To recompute, first preserve the delivered results and move the selected case files out of results/. Incomplete cases are recomputed from the start; the runner checkpoints every completed station but does not resume inside a loop. N4 records are also fixtures for the publication-guard mutation tests.

The first FOLD log line gives the actual located parameter/momentum. The later `FOLD None` line marks completion of the fold's boundary/control station: no positive local minimum is claimed at the collision itself. Authoritative values and station types are explicit in the JSON record.

For scope: 72 root-state records are not 72 fully charge-gated states; 16 charge measurements include four repeats of the common A=0.2,B=0 station. Original roots are separately checked, but their charge and full preparation frame transport are not measured by this batch. The global flat gap is not opened by these local events.

No new dependency installation or network access is required in the measured environment. Package construction is a workspace operation; numerical and report reproduction work from the extracted archive. The original supplied tests remain the historical v050 result and are not counted among the 24 tests run here.
