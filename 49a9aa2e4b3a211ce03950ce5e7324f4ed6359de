# v056 reproduction

Start with TEAM_SHARE_v056.md, REPORT.md, CLAIM_MAP.md and SUMMARY.json. This batch reconciles saved campaign evidence and performs a five-recipe BM helper comparison. It does not rerun the full scientific campaign.

Use the declared Python/dependency versions in requirements.txt and ENVIRONMENT.txt. The preserved earlier repository tree is required, with paths given by SOURCE_INDEX.json. No missing prior ZIP needs to be reconstructed.

```bash
cd research/v056
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python -B campaign_map.py
python -B legacy_trace.py
python -B compare_impact.py
python -B run_tests.py
python -B build_report.py --test-evidence provenance/test_runs/ACTUAL_RUN_ID/result.json
python -B package_release.py --output /absolute/path/outside/repository/twistronics_v056_reconciled.zip
```

Substitute the evidence path printed by run_tests.py. Report generation validates saved outputs and test identity; it does not silently run tests or numerical measurements. A changed source, input, runtime or test outcome prevents publication. Re-running tests creates a new immutable run directory. Regeneration can therefore produce a different release archive containing additional run evidence.

To repeat the numerical probe, first make a separate copy of the complete extraction. Preserve its supplied result files elsewhere, then remove only the two copied `results/legacy_defective.json` and `results/legacy_repaired.json` outputs before running:

```bash
python -B legacy_impact.py --variant defective
python -B legacy_impact.py --variant repaired
python -B compare_impact.py
```

The runner refuses to overwrite existing measurements and requires normal Python mode because the historical recipe contains an assertion. No more than two numerical workers were used. The frozen IMPACT_PLAN predates the probe. The campaign-map PLAN was frozen after preliminary inspection and before the final bound test/publication pass; no stronger chronology claim is made.

The final bound test result records the installed environment and native-library hashes. The numerical probe used that session's declared environment, but its own records do not contain before/after runtime identity snapshots. Neither mechanism is an external attestation of authenticity.

The package preserves earlier tracked files against PRESERVED_TREE.json, except the top-level README, whose previous contents are retained at provenance/README_v055.md. It includes a new package manifest with every payload member's hash and size. This is an explicit tree-based release contract, not a claim to recreate any prior ZIP byte stream.
