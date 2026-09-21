# Our v054 — audit repairs and measured impact

Start with REPORT.md, TEAM_SHARE_v054.md and IMPACT.json. The original v053 remains at `../v053/`; the supplied inspection-only audit remains at `../../audits/v053/`. This is a separate repair and replay, not a rewrite of frozen history.

The numerical protocol is the same 19-state preparation route per engine/cutoff. PLAN.json binds this version's sources, tests, publication code, anchors and requirements before primary execution. BM reciprocal geometry remains linear, reference geometry exact; both use `lab_nn_full` and constant tunnelling. No numerical dependency version or Hamiltonian formula is changed. `threadpoolctl==3.6.0` is declared for native-library identity capture.

Run from this directory with the versions in requirements.txt:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 -B impact_replay.py --engine bm_lab --N 4
python3 -B impact_replay.py --engine ref_lab --N 4
python3 -B impact_replay.py --engine bm_lab --N 6
python3 -B impact_replay.py --engine ref_lab --N 6
python3 -B compare_results.py
python3 -B run_tests.py
python3 -B build_report.py --test-evidence provenance/test_runs/RUN_ID/result.json
python3 -B package_release.py --output /absolute/path/outside-repository/twistronics_v054_reconciled.zip
```

Use the actual evidence path printed by `run_tests.py`, not literal RUN_ID. Run at most two single-thread numerical workers and qualify both N4 cases before N6. The impact wrapper deliberately refuses an existing case directory so an old result cannot be mistaken for a fresh replay. To repeat from scratch, preserve this delivery and work in a separate copy with its generated results and IMPACT.json moved aside. The new wrapper is for primary impact runs; the earlier pilot remains preserved in v053.

The normal replay driver still supports checkpoint continuation, but only a fresh, fully instrumented `impact_replay.py` run yields this batch's fresh-replay guard. A failed instrumented run retains `guard_failure.json`; investigate it in place and use a new copy for another fresh run. A source change requires a separately versioned/frozen protocol, not editing old records to match a new digest.

`run_tests.py` invokes a fixed complete-suite worker and retains collection IDs, actual test-call outcomes, JUnit, stdout, source/test/input hashes, Python and installed-distribution identities, loaded native-library binary hashes and thread settings. Publication rejects failed, incomplete, skipped/xfail, missing or mismatched evidence. Hash binding is internal consistency, not external attestation or a complete dependency lock/security clearance. The historical v053 18-pass log remains historical.

Packaging now has an explicit **preserved extracted tree** contract. It verifies every original v053 manifest entry before copying the preserved research and supplied audit, creates the output parent, and writes/verifies a fresh delivery manifest. It does not need or claim to reproduce the original prior ZIP byte stream. `--prior-tree` may explicitly name the verified v053 extraction. Output must be outside the repository, and an existing ZIP will not be overwritten.

The BM helper's `return_result=True` mode exposes rejection metadata for diagnostic callers; plain rejected calls raise. Its convergence result alone does not certify a node. Legacy Euler/braid/knob analysis now requires explicit `exploratory=True` (or CLI `--exploratory`) and remains unsuitable for accepted scientific labels. Active preparation measurements use the independent guarded `Sample` path.

This batch addresses the audit and preparation-route impact only. The separate lower unlink collision, older legacy-helper consumers, continuous-interval proof, infinite-cutoff accuracy and physical-bilayer validation remain outside this result.
