# LOOP-ROBUSTNESS-007

A bounded follow-up to NODE-WINDING-006, with unchanged assembly and a/b/c cutoffs.
128 exact rational coordinates: 96 new and 32 explicitly repeated regression points.
22 sequential jobs of at most 6 points; 384 eigensolves. Limits: 90 s/job, 600 s
summed jobs, 3 GiB address space/worker, 64 MiB/file, one thread.

Three squares are evaluated: the c-centered original radius with 64 vertices,
half radius with 32 vertices, and an off-node control translated by four original
radii in x with 32 vertices. Subsets give 16/32-vertex original-radius loops.
The original 006 loop is the 32-point regression subset. No rerun of 004/005.

Engine additions: rational square reconstruction; multiple loop groups; stable
log-determinant sign and polar transport; closure/reversal checks; sampled
external gaps for each tracked band/group; process-group watchdog receipts;
strict native wheel/thread/limit validation on replay. Fixed-matrix controls
cover gauge changes, reversal, singular links, and positive/negative signs.

The 0.5 overlap threshold measures discrete conditioning only. Gap checks are
at vertices. Neither proves isolation between samples or inside the loop.
Results are finite-cutoff numerical evidence, not node count/charge certificates.
Computation is authorized independently of audit; independent review is PENDING.

Run with the exact frozen commit and locked wheel:
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python run.py run --commit COMMIT --output NEW_DIR --wheel WHEEL
python run.py replay --commit COMMIT --output NEW_DIR
```
