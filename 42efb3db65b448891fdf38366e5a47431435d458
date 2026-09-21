# v057 reproduction

Start with TEAM_SHARE_v057.md, REPORT.md, ATTRIBUTION.md, SUMMARY.json and IMPACT.json. This batch contains controlled historical-model replays and a source-to-log ledger. It does not rerun the entire modern lab_nn_full campaign.

Use the declared environment in requirements.txt and ENVIRONMENT.txt. The full preserved repository tree is required; no reconstructed prior ZIP is needed.

```bash
cd research/v057
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python -B attribution.py
python -B probe_evidence.py
python -B run_tests.py
python -B build_report.py --test-evidence provenance/test_runs/ACTUAL_RUN_ID/result.json
python -B package_release.py --output /absolute/path/outside/repository/twistronics_v057_reconciled.zip
```

Substitute the test-evidence path printed by run_tests.py. Report generation validates a completed test run and rebuilds the reconciliations in memory; it does not run new numerical measurements. Tests include synthetic optimizer failures and corrupted-evidence rejection, not a full numerical coverage measurement.

To repeat the numerical probes, make a separate complete copy of this extraction. Preserve its supplied probe records elsewhere and remove only the two copied `results/probe_N4.json` and `results/probe_N6.json` files before running:

```bash
python -B run_probe.py --N 4
python -B run_probe.py --N 6
python -B probe_evidence.py
```

The runner refuses to overwrite its measurement files and requires normal Python mode because the older source includes assertions. This session used at most two workers, one per cutoff. A numerical run is independent of the later report/test run; each worker records its own before/after runtime identity and native-library hashes.

NUMERICAL_PLAN.json was frozen before these probes. PLAN.json freezes the completed batch source and supporting documents before final bound tests/publication. These are internal records, not external timestamp attestations. Historical v034 package versions differ; the retained v035 endpoint record lists the same three direct versions as this session but does not establish complete native-build identity.

The final ZIP preserves all prior tracked files except the replaced top-level README, whose old contents are in provenance/README_v056.md. The new package manifest covers every payload file. Repackaging unchanged supplied files is deterministic; rerunning tests adds a new immutable evidence directory and intentionally changes the resulting archive.
