# v055 reproducibility

Read METHOD.md and PLAN.json first. The active sources are copied from our corrected v054 plus the v052 fold/domain machinery, with a new unlink runner and publication validator. Partner source is preserved separately. No incoming script is executed to establish acceptance.

Use Python and package versions in ENVIRONMENT.txt/requirements.txt, with OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1, MKL_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1. A trusted fresh reproduction copy must have no existing results/lower_unlink_*.json. Retain supplied records in the original package; never overwrite them. Run from this directory:

```bash
python -B run_unlink.py --engine bm_lab --N 4
python -B run_unlink.py --engine ref_lab --N 4
python -B run_unlink.py --engine bm_lab --N 6
python -B run_unlink.py --engine ref_lab --N 6
python -B run_tests.py
python -B build_report.py --test-evidence provenance/test_runs/RUN_ID/result.json
python -B package_release.py --output /absolute/path/outside/the/tree/twistronics_v055_reconciled.zip
```

Use the actual result.json path printed by run_tests. The complete suite includes source-bound evidence rejection, optimizer metadata and legacy runtime regression, analytic fold character, archive provenance, and corrupt-event publication rejection. Reporting and packaging validate saved outcomes without rerunning the numerical engines. Their required runtime identity is recorded, including loaded native-library hashes and thread settings.

The packager verifies the supplied v053 manifest and every preserved v054 file, creates output parents, refuses output overwrite, retains the complete incoming partner ZIP and verifies its extracted members. It packages the preserved tree; it does not reconstruct a byte-identical older ZIP. Its own deterministic output is checked by extraction/repack separately.
