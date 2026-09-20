# Optional public-helper guard patch

`tbg_ref.py` here is a copy of the uploaded v041 source with public-helper
guards and boundary seeds strengthened. `tbg_ref_guard.patch` is the diff.

- Reject nonpositive/nonfinite requested radii and nonfinite/coincident seeds.
- Reject failed, nonfinite, or seed-worsening gap refinements; retain optimizer
  records. Never return positive infinity as a successful gap estimate.
- Add both boundary faces, corners/edge centers, and inward seeds. The uploaded
  helper agrees on two grids but overestimates the N4 endpoint lower gap by
  0.01228 meV for full and 0.01299 meV for lab_nn_full.

The patch changes no Hamiltonian, loop mesh or physical parameter. A failed
optimization now requires investigation rather than being
silently skipped. It does not make the public search globally complete or add
the harness's loop-resolution gate.

Ten focused tests include deterministic failure injection, a known bounded
quadratic minimum, and both numerical endpoint regressions. This patched copy is **not** imported by any
primary replay. Those preserve the uploaded v041 engines verbatim; their
existing external acceptance gate already rejects these numerical failures.

To review/apply, compare this file or apply the diff from the project root to
`v023_code/tbg_ref.py`. Keep the original archive as provenance. No existing
uploaded file has been overwritten by this work.
