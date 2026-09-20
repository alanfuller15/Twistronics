# v048 — later folds, gapped joins and ledger reconciliation

Read REPORT.md, LEDGER.md and TEAM_SHARE_v048.md. SOURCE_REVIEW.md provides the layered review, findings and ranked actions. Incoming v047 and our previous v046 remain separately preserved; the partner's v046 and our v046 are different contributions.

Primary numerical inputs and thresholds are bound by PLAN.json. Uploaded engines retain their historical cutoff defaults, now passed explicitly. Both use lab_nn_full; bm_lab uses linear reciprocal geometry, ref_lab exact geometry. Constant tunneling amplitudes remain the campaign approximation. No source patch is applied silently to the primary engines.

Use the versions in provenance/environment.json and set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1 and PYTHONDONTWRITEBYTECODE=1. Run at most two primary workers from this directory:

```
python run_sequence.py --engine bm_lab
python run_sequence.py --engine ref_lab
```

Accepted fold records are reused only under the same protocol. Each gapped state saves intermediate gap/cycle results and commits ACCEPT only after all its checks pass. Re-running verifies state/protocol before reusing accepted gapped records; incomplete states are recomputed. Failed stages are preserved. This is finite sampled continuation and local fold evidence, not a proof of all parameters or all momenta.

The optional fixes/finite_tunneling_v047.patch updates the current v047 BM file to reject nonfinite w_kappa and correct the modeling comments. It includes the already-adopted cutoff API in the full replacement file; it does not alter historical cutoff defaults. Twenty-two targeted assertions cover eight adopted-cutoff cases, nine adapter/optional-patch cases and five ledger-guard cases; the 31 supplied tests are recorded separately.

Acceptance on your machine: read the report with its limits, run `python -m pytest tests -q -p no:cacheprovider`, and run `python build_report.py` to check the completed record set and regenerate the ledger. The preparation probe can be reproduced with `python preparation_join_probe.py`. Numerical results are [self-tested]; recipient consumption remains [unconfirmed] until reported. No external physical validation is claimed.
