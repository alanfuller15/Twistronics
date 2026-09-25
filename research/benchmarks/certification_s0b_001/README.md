# S0b: uniform windows, variable transport and portable records

2026-09-23. **All nine frozen behavior jobs and ten runner controls passed.**
The numerical run took 87.687 seconds. Three jobs intentionally returned
INCONCLUSIVE and are successful negative controls, not certificates.
This is a partial synthetic validation packet pending independent review.

The [derivation](../../../docs/certification-readiness/S0B_DERIVATION.md)
addresses the completed S0a audit in
[review 5292777390](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5292777390).
The original S0a packet and its recorded runner bug remain frozen;
`run_calibration.py` here is the repaired successor.

| Fixed job | Outcome | Seconds |
|---|---|---:|
| Phase and spectral-window controls | All three predicates passed | 0.002 |
| 196-dimensional narrow cell, 128 bits | Both windows certified | 5.629 |
| 308-dimensional narrow cell, 128 bits | Both windows certified | 19.363 |
| 308-dimensional narrow cell, 256 bits | Both windows certified | 38.141 |
| 196-dimensional wide cell | Expected INCONCLUSIVE | 3.725 |
| 308-dimensional wide cell | Expected INCONCLUSIVE | 11.730 |
| 196-dimensional variable transport | Within frame budget | 2.376 |
| 308-dimensional variable transport | Within frame budget | 3.504 |
| 308-dimensional coarse transport | Expected INCONCLUSIVE | 0.263 |

The narrow cells are closed one-parameter synthetic intervals. Four shifts
per job certify the two spectrum-free windows [-5/4,-3/4] and [3/4,5/4].
Equal endpoint counts are 97/99 for dimension 196 and 153/155 for 308.
Each window has width 1/2 and gives distance 1/4 for the vertical contour
through its center, in synthetic units. A Riesz contour's horizontal
segments still need their own distance bounds.

The perturbed rational bases are not exact eigenbases: retained center
coupling Frobenius norms are approximately 0.065–0.104. Narrow-cell inverse
residual bounds are below 0.024, and all 3,248 associated signed pivots
are decisive. Wide-cell inverse residual bounds exceed 2.96, so these
cases correctly stop without claiming an inertia count over the cell.
The synthetic perturbation is rank one; it exercises nonzero off-block
coupling but is not a general physical conditioning benchmark.

The variable-generator tests repeat noncommuting 3-by-3 rotations with a
fixed fourth coordinate across the full state. Both fine runs give a
uniform strip error bound below **0.054553**, including parameter debit,
against the candidate **1/16** frame cap. The coarse case has a sufficient
bound above 2.88 and remains inconclusive. Closed-form endpoint comparisons
are consistency checks using the same backend, not independent numerical
proofs. The whole-strip guarantee comes from the analytic residual bounds.
The structured generator does not calibrate dense physical transport cost.

The conditional phase ledger produces a q half-width bound below 0.095419,
within 1/8, **only if** the separate frame, seam-map, repair-angle and
arithmetic gates all pass. Corners may require tighter frames; certified
continuous lifts and branch separation remain mandatory. S0b has not
computed a physical seam map, repair, lift or integer.

## Runner integrity and reproduction

The retained run used a fresh absolute output directory **outside** the
packet directory, then the complete bundle was copied byte-for-byte into
[RUN](RUN). [RUNNER_CHECKS.json](RUNNER_CHECKS.json) records ten finite
standard-library controls for absolute/relative destinations, copy
portability, reuse refusal, tampering, write failure, missing completion,
worker schema, nonzero exit and timeout. No previous failure was removed
or rerun; this was the first full execution of the frozen spec.

Use CPython 3.12 with the same x86_64 Linux wheel and native artifacts as
S0a: python-flint 0.9.0 / FLINT 3.6.0, wheel SHA-256
`376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`.
The driver checks the wheel hash, backend versions and installed native
artifacts against the wheel before running. The full executed source is
snapshotted under RUN/SOURCE; workers use that snapshot. From this directory:

```sh
PYTHONPATH="$FLINT_TARGET" python -B run_calibration.py --wheel "$WHEEL" --output "$FRESH_OUTPUT"
python test_runner.py
python verify_evidence.py
```

FLINT_TARGET is an isolated installation of the locked wheel, WHEEL its
local artifact path, and FRESH_OUTPUT a directory that does not yet exist.
The standalone RUN/SOURCE layout also supports rerunning the snapshotted
driver with another fresh output destination. Do not run into the archived
RUN directory. Resource ceilings are 900 seconds overall, 180 seconds per
job, 2 GiB worker address space, one worker and zero retries.

Every JSON record is written atomically. MANIFEST.json binds paths relative
to the output directory, then COMPLETE.json is installed last and binds
the manifest hash. Completion means records are complete, not that their
result status is successful. Missing completion or changed bound artifacts
fail verification. Exact bound endpoints are stored as mantissa times a
power of two; timings/RSS are observational floats.

`verify_evidence.py` uses only the standard library and exact rational
predicates; it does not rerun numerics. Its checks do not disappear under
Python optimization. The package manifest additionally binds the docs,
the executed source snapshots, and prior case/S0a dependencies. Backend,
compiler and hardware correctness remain trusted assumptions.

## Remaining gate

S0b is implemented on these synthetic examples, pending Claude's audit.
S0 remains incomplete: Riesz projectors and quadrature, polar/seam error
enclosures, phase lifts, physical coefficient assembly, general parametric
Kato generators and full outcome dependencies still need implementation
and tests. Physical S1–S4 budgets remain unfrozen. No physical model was
evaluated and no finite or infinite physical class was certified.
