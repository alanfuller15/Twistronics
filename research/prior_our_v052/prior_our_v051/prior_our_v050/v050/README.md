# v050 reproducibility

Read REPORT.md, SOURCE_REVIEW.md and TEAM_SHARE_v050.md. SUMMARY.json and PLAN.json provide machine-readable results and frozen scientific inputs. Incoming and prior delivery records are preserved outside this directory, with both meanings of v048 intact.

Run from this directory with Python 3.12, NumPy 2.3.5, SciPy 1.17.0 and pytest 9.1.1 (the measured environment):

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 replay_events.py --engine bm_lab --N 4 --case prep_upper_birth
python3 replay_events.py --engine ref_lab --N 4 --case prep_upper_birth
python3 replay_events.py --engine bm_lab --N 6 --case prep_upper_birth
python3 replay_events.py --engine ref_lab --N 6 --case prep_upper_birth
python3 reconcile_probe.py
python3 -m pytest -q -p no:cacheprovider tests
python3 build_report.py
```

Keep at most two numerical workers active. Each fold writes its located event, charge stage and opposite-side checks to JSON; failures are REJECTED, never death/birth verdicts. A rerun recomputes that bounded case and replaces its result; it does not resume an incomplete charge loop. Preserve the delivered results before experimenting. Only `prep_upper_birth` is in this batch's frozen scientific scope; other inherited case definitions are historical, not authorized coverage in the v050 ledger.

31 supplied tests were run in incoming_v049/v023_code using the explicit test_regression.py and test_tbg_ref.py paths. Fourteen new/inherited reporting tests are local; the endpoint tests use injected optimizer outcomes, not fresh physical measurements. An initial unscoped pytest collection was interrupted before results and is excluded from counts.

The optional fixes/endpoint_locate.py and unified patch improve failure logging and coordinate validation. They were not used for the decisive fold/gap measurements. anchor_quality.py classifies provisional anchor rows and never upgrades their charge label into a gated measurement. build_report.py requires finite ACCEPT records, the full four-case engine/cutoff grid and matching frozen protocol hashes.

review_inventory.py records the original workspace comparison; its upload-ZIP path is specific to that workspace. The preserved provenance/inventory.json and archive manifest carry its output for recipients. All helpers needed to rerun the numerical batch are included. No network access is needed once the listed Python dependencies are installed.
