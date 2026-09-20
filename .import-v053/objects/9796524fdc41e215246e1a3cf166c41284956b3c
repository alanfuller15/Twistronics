# Our v053: preparation frames and v044 join

Start with REPORT.md, TEAM_SHARE_v053.md and METHOD.md. SOURCE_REVIEW.md contains the layered review and ranked next actions. PLAN.json freezes the scientific protocol; SUMMARY.json is generated from complete primary checkpoints and endpoint frame verification.

The full previous delivery is at ../prior_our_v052/. No new archive was supplied and no incoming or historical scientific record was overwritten. The four original v044 JSON/NPZ endpoint anchors are included here for portable reproduction.

From this directory with the versions in ENVIRONMENT.txt / requirements.txt:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python3 replay_prep.py --engine bm_lab --N 4
python3 replay_prep.py --engine ref_lab --N 4
python3 replay_prep.py --engine bm_lab --N 6
python3 replay_prep.py --engine ref_lab --N 6
python3 -m pytest -q -p no:cacheprovider tests
python3 build_report.py
```

Run at most two numerical workers and qualify N4 before N6. Existing complete checkpoints are verified/reused; incomplete cases resume from the last atomic state. To recompute from scratch, preserve the delivered results and use a separate copy with the selected case folder moved out of results/. `--max-new 3` stops after three new states; rerunning without it continues. `--pilot` uses a separately tagged exploratory grid and directory.

Each step folder holds record.json and frames.npz, including both fine/coarse parameter frames and basis labels. Anchored frames are loaded with allow_pickle=False and verified against their recorded digest. Publication rejects missing steps, changed frame bytes, pilot/partial results and missing parameter refinement.

The 18 tests are frame/checkpoint/publication tests for this batch. The original toolkit regression suite was not rerun against unchanged Hamiltonians. The pilot and production stop/resume exercise are separate from unit-test counts. No claim of an uninterrupted bitwise replay comparison is made.

This replay follows the original flat pair, not a complete inventory of every node at every parameter. The earlier preparation event windows remain separately scoped. Relative frame orientation is joined; no gauge-independent SO(2) angle or Euler class through remote-band contacts is claimed.
