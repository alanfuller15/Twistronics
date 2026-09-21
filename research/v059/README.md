# v059 reproduction

Read REPORT.md, METHOD.md and NUMERICAL_PLAN.json. The current task is the lower unlink collision at N8; the preceding v058 endpoint is a different state. N4/N6 records are historical comparison inputs. Two engines share the guarded measurement harness and retain their linear/exact reciprocal geometry difference.

Use ENVIRONMENT.txt and requirements.txt, including one BLAS thread per worker: OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1. Direct dependencies stay frozen; installed package/native-library identities are in numerical and test records. A complete resolved native-build lock is not supplied.

From research/v059, reconcile the saved record without numerical replay:

```bash
python -B -c 'import reconcile; print(reconcile.build()["status"])'
```

Execute the complete batch assertion suite and retain its immutable evidence path:

```bash
python -B run_tests.py
python -B build_report.py --test-evidence provenance/test_runs/RUN_ID/result.json
python -B package_release.py --output /absolute/path/out/twistronics_v059_reconciled.zip
```

Use the actual RUN_ID printed by run_tests. Reporting checks source/tests/results/runtime identity before reading numerical acceptance. Packaging verifies preserved prior files, requires matching report/test evidence, creates output parents and refuses overwrite. It packages the preserved tree; it does not reconstruct a missing byte-identical prior ZIP.

For a fresh numerical comparison, use a separate copy and move its original case files out of results first. Preserve the delivery intact. With at most two workers:

```bash
python -B run_event.py bm_lab
python -B run_event.py ref_lab
python -B reconcile.py
```

The numerical runner refuses existing case files, checks frozen sources/inputs before and after execution, and writes its own case JSON incrementally. It makes no network or subprocess calls, invokes no tests/build/publication, and does not execute partner scripts. Imported numerical dependencies and retained helper code execute. New numerical evidence needs separately frozen publication inputs and a new bound test run; it is not interchangeable with this delivery's original test record.

This batch performs finite root, loop, transport and gap checks around one critical event. It does not prove continuous-path completeness, global absence of other roots, infinite-cutoff accuracy or physical validity. Absolute charge is not transported through the collision; no new Euler or endpoint w1 result is assigned.
