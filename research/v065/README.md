# v065 — evidence recorder repairs

This source-only iteration hardens the test-evidence recorder. It does not modify numerical engines, previous measurements or their frozen dependency pins. The published numerical campaign remains v062.

The recorder retains recursive source/configuration hashes, current-runtime comparison, independent pytest collection/phase logs, mandatory stdout/stderr/JUnit/execution artifacts, rejection of skipped/xfail/xpass/deselected tests, and separate non-certifying historical checks. This iteration additionally rejects failed or incomplete native-library identity capture, missing/duplicate/extra setup/call/teardown records, and inconsistent session collection counts.

The self-contained selection has **22 passing assertions**: 12 recorder behavior cases and 10 added native/phase rejection cases, including parametrized cases. These execute synthetic fixtures, not the historical numerical regression suite. The complete recorded run is in `evidence/test_evidence/`; `EVIDENCE.json` identifies its source/runtime identity and measured result. The recorded environment uses Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, pytest 9.1.1 and threadpoolctl 3.6.0, with BLAS/OpenMP threads set to one.

From this directory, run a fresh selection into a new output directory:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
unset PYTEST_ADDOPTS PYTEST_PLUGINS
python -B run_acceptance.py --output /absolute/path/to/new-v065-run
```

`requirements.txt` records the four direct reviewer dependencies; it is not a complete transitive/native lock. A current certificate requires the same bound inputs and checked runtime fields as its run. A different runtime should produce fresh evidence; historical consistency alone never returns a publication certificate.

Limits remain: the source map covers `.py/.txt/.ini/.toml/.cfg` within the declared root and excludes evidence/cache directories. It does not bind arbitrary JSON/NPZ data, outside-root imports or every effective plugin/configuration input. Most recorded environment-filter fields and executable/platform fields are not current-runtime equality gates. Recorder JUnit matching uses terminal names rather than complete class/module identities. Selected tests/plugins can manipulate their own evidence, so this is not a security boundary or independent authenticity check. The accepted scope is the demonstrated behavior of this selection, not archive coverage or scientific truth.

No numerical calculation was rerun, and no scientific label changed. The original investigation's two counterexamples established incomplete-evidence acceptance; the new cases assert rejection rather than counting successful reproductions as proof of repair. The canonical numerical harness is unchanged.
