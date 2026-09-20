# v038 — later events and an earlier gapped endpoint

Read REPORT.md, then METHOD.md and STRAIN_CONVENTION.md. This is a self-contained
numerical package for this entry. It does not replace the team upload or claim
to include every historical exploratory script.

Use Python 3.12 with requirements.txt in a separate environment. Numerical jobs
use one BLAS thread. The two queue files run jobs sequentially and checkpoint
after each subprocess; two concurrent queues are sufficient. Source files and
protocol hashes are included; results/ contains raw accepted and failed runs.

From this directory:

```bash
OPENBLAS_NUM_THREADS=1 python -B verify_models.py
OPENBLAS_NUM_THREADS=1 python -B strain_check.py
OPENBLAS_NUM_THREADS=1 python -B -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 python -O -B -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 python -B replay_second.py --engine original --N 4
OPENBLAS_NUM_THREADS=1 python -B replay_second.py --engine partner --N 4
OPENBLAS_NUM_THREADS=1 python -B replay_second.py --engine original --N 6
OPENBLAS_NUM_THREADS=1 python -B run_queue.py queue_original_N6.json
OPENBLAS_NUM_THREADS=1 python -B run_queue.py queue_partner.json
```

The saved queues reflect the actual run order. The original N4 initial event
batch was run with `batch.py --engine original --N 4`. Its first event failed
the phase-resolution gate; the subsequent accepted replacement command is:

```bash
OPENBLAS_NUM_THREADS=1 python -B replay_events_refined.py --engine original --N 4 --case first_ann
OPENBLAS_NUM_THREADS=1 python -B check_gapped.py --engine original --N 4 --state bridge
OPENBLAS_NUM_THREADS=1 python -B fold_character.py
```

Run `replay_cleanup.py --engine ENGINE --N CUTOFF` for each engine and cutoff
after its second-braid and collision jobs. Run
`boundary_audit.py --engine ENGINE --N CUTOFF` after the gapped-state jobs; it
also supplies the lower-remote outer-gap checks. Then run `fold_character.py`,
`build_report.py` and `render_figure.py`. The earlier standalone
check_lower_isolation.py is retained but superseded by boundary_audit.py.

Every command writes predictable files under results/ and may overwrite them.
Work in a copy to preserve supplied evidence. RUNNING or REJECTED is never an
accepted result. A nonzero job exit is retained in its log and queue record.
The job runners invoke local allowlisted Python scripts without a shell; the
numerical programs make no network calls and do not delete files.

Requirements record the versions actually used, which differ from the team
upload's pins. The supplied historical 21-test suite was run in v037; it is not
counted as a fresh v038 test. This entry adds seven focused tests, a model assembly
comparison and 36 monolayer strain checks.
