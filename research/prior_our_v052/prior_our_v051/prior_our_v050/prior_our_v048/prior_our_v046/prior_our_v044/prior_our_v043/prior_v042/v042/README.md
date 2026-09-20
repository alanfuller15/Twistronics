# v042 — Two-engine lab_nn_full replay

Read REPORT.md and TEAM_SHARE_v042.md for results, SOURCE_REVIEW.md for the
source-level findings and review cutoff, and PLAN.json for the fixed protocol.

The two adapters import the uploaded v041 Hamiltonian engines verbatim and
explicitly request `lab_nn_full`. BM's B and T harmonics are added with the
uploaded `knobs.add_harmonic`; TBG uses its constructor's B/Bt options. The
models retain their different reciprocal-geometry approximations. The
verification program matches geometry only on disposable diagnostic objects
to identify the difference; it never changes a replay model.

From this directory, using the environment in requirements.txt:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python verify_models.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python run_engine.py --engine bm_lab
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python run_engine.py --engine ref_lab
OPENBLAS_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider tests
python build_report.py
```

Each engine runs N4 and then N6, saving completed jobs before proceeding. The
source hashes in PLAN.json must match. Accepted jobs are resumed; exceptions
produce rejected result records and stop that sequence. For a fresh replay,
use a copy and move its primary result files aside while retaining
results/discovery.json. Preserve the delivered measurements. No input deletion
or network activity is performed by the numerical programs.

The uploaded 27-test suite is separate, in `team_v041/v023_code`. Its test result
is recorded in provenance/uploaded_tests.json. New gate tests, model-assembly
checks and numerical measurements have distinct records.

Current validation totals seven integration tests and ten helper-patch tests.
The older 15-case optimized-mode log predates the two numerical endpoint
regressions and expanded boundary seeds; provenance/validation.json makes
that chronology explicit. The incomplete saved endpoint record caught during
report assembly and its completed rerun are both retained.

The delivery preserves `team_v041`, `prior_v040` and this `v042` in separate
directories. The prior package itself retains the two distinct v038 records.
Original files remain attributable; no historical result is relabeled as a
new-model replay. Earlier connecting legs, full-variant cleanup and the other
collision windows are not included in this batch's acceptance claim.
