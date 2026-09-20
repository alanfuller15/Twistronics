# v040 focused follow-through

Read REPORT.md for the measured conclusions, TEAM_SHARE_v040.md for a short
handoff, SOURCE_REVIEW.md for the ranked findings and review cutoff, and
STRAIN_NOTE.md for the exact convention issue.

The primary campaign uses the uploaded `tbg_ref.py` unchanged with an explicit
`kinetic='full'`. The efficient real-basis adapter is checked against the
uploaded antiunitary basis. The measurement harness comes from our v038 and
uses explicit runtime guards. `lab_nn_full` is a named sensitivity adapter
only; no campaign result here comes from that variant.

With Python and the versions in requirements.txt available, run from this
directory with one BLAS thread. No network is used by these programs.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python run_focused.py --N 4
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python run_focused.py --N 6
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python post_transfer.py --N 4
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python post_transfer.py --N 6
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python search_diagnostic.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python strain_audit.py
OPENBLAS_NUM_THREADS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider tests
python build_report.py
```

`run_focused.py` verifies the frozen source hashes, writes each checkpoint
before advancing, and stops on a rejection. It resumes accepted jobs. For a
fresh independent replay, work in a copy, retain `results/discovery.json` as
seed provenance, and move the existing primary result files out of its
`results` directory. Preserve the delivered originals. At most two primary
numerical processes were used concurrently in this work.

The uploaded suite is separate: run pytest on `test_regression.py` and
`test_tbg_ref.py` from the sibling `team_v039/v023_code` directory. Those
22 tests passed before the new measurements. Six adapter/gate tests also
pass, including under Python's optimized mode; pytest's warning about
non-test assertions under that mode is retained. Primary acceptance gates
use explicit exceptions rather than Python assertions.

Files written by the measurement programs are JSON/text results in `results`,
with temporary files atomically renamed to their intended result path. The
report builder writes REPORT.md, TEAM_SHARE_v040.md and results/summary.json.
No program deletes input files or sends data elsewhere.

The complete ZIP keeps three provenance groups separate:

- `team_v039`: the uploaded files, byte-for-byte unchanged.
- `our_v038`: our preceding sequence package, preserving its original evidence.
- `v040`: this focused extension and corrections.

The root MANIFEST.json contains the delivered paths and SHA256 digests. The
original input ZIP digests and exact code versions are also retained in the
protocol and provenance files. Results are finite numerical evidence for
declared models, not physical calibration or continuum certification.
