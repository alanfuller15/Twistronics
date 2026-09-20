# Our v052: lower-pair preparation birth

Read REPORT.md, TEAM_SHARE_v052.md and METHOD.md. SOURCE_REVIEW.md gives the layered review and ranked actions. PLAN.json binds the scientific sources and retained v044 root anchors. SUMMARY.json is generated only from the complete four-window accepted grid.

The complete v051 delivery is preserved at ../prior_our_v051/. No new upload was supplied. Both historical geometry conventions remain explicit; no Hamiltonian file was changed.

From this directory with the versions in ENVIRONMENT.txt / requirements.txt:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 run_lower.py --engine bm_lab --N 4
python3 run_lower.py --engine ref_lab --N 4
python3 run_lower.py --engine bm_lab --N 6
python3 run_lower.py --engine ref_lab --N 6
python3 -m pytest -q -p no:cacheprovider tests
python3 build_report.py
```

At most two numerical workers. Qualify both N4 windows before N6. Accepted results with matching protocol are skipped; to recompute, first preserve the delivered records and move the selected JSON files out of results/. An incomplete window is recomputed from its start. Each completed station is checkpointed; no resume inside a charge loop is claimed. The delivered N4 record is a fixture for publication mutation tests.

pilot_backward.py is exploratory, not an acceptance gate. Its unresolved point is retained as a failed search, not promoted to an event location. Four older anchor files are included so both root joins and reporting remain reproducible from the extracted package.

The new test count of 31 refers to the gate/join suite in this directory, not a rerun of the historical 31 supplied regression tests. The positive gap is the lower remote-to-flat gap, not the internal flat-pair gap. Same-state root joins are not parameter-frame joins. Full-chart searches remain finite numerical evidence, not analytic global bounds.
