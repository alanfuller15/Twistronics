# v043 connecting-path replay

Start with REPORT.md and SUMMARY.json. This directory contains a new measured
connection between selected windows already accepted in v042. It does not
claim that the entire campaign is now continuously validated.

Both engines under engines/ are the unchanged uploaded v041 sources. The
measurement adapters explicitly request lab_nn_full; the original reciprocal
geometry differences remain. The optional v042 helper patch is not used here.
Both Hamiltonians are measured with this same acceptance harness; this is not
a claim of two independently implemented topological estimators for these runs.
The twelve accepted v042 anchor files are copied without alteration into
anchors/ and bound into PLAN.json by SHA-256.

## Reproduce or resume

Use the versions in requirements.txt and provenance/environment.json. From
this directory, run each engine/cutoff/route combination. Limit concurrent
primary numerical jobs to two and keep BLAS single-threaded:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python replay.py --engine bm_lab --N 4 --case pre_ann
```

Engine choices: bm_lab, ref_lab. Cutoffs: 4, 6. Routes: pre_ann, post_ann.
`--max-new 3` stops after three additional accepted states; rerun without that
option to resume. Existing complete states are immutable and hash checked.
To reproduce from scratch, use a fresh copy of the source and anchors with
an empty results directory, keeping the delivered evidence intact.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python -m pytest tests -q
python build_report.py
```

The report builder refuses incomplete routes, stale source/anchor hashes,
noncontiguous or corrupted records, and a summary that disagrees with the
individual committed steps. Failure files and unfinished staging directories
are retained for inspection; they do not count as accepted steps.

## Source map

- routes.py: explicit states and fine parameter meshes.
- basis.py: Fourier-index pullback with overlap and discarded-weight gates.
- spatial.py: both exterior gaps along the unwrapped straight comparison path.
- replay.py: two-root continuation, parameter/spatial refinement, charge loops,
  endpoint identity checks, and preservation of valid unexpected labels.
- checkpoints.py: paired JSON/array commit and digest-checked resume.
- models.py, measure.py: unchanged v042 adapters and local measurement guards.
- tests/: six basis tests and one interruption/corruption test, each checking a
  numerical or persistence failure mode rather than just successful execution.

Signed charges can differ by a simultaneous sign between engines because
their initial real-frame orientations are arbitrary. Compare the spatial
SAME/OPPOSITE relation and constancy within each carried frame, not bare
signed charges across independently initialized engines.

No physical tunneling strain law is supplied by this numerical replay. The
ratio schedule is a declared model control, not an inferred material response.
