# S0d: projector, seam-map and continuous phase-lift primitives

2026-09-23. **13/13 expected behaviors and 10/10 protocol checks passed.**
The first fixed run completed in 1.151 seconds with no retries. It retains six
CERTIFIED synthetic implications, six INCONCLUSIVE controls and one deliberate
EXECUTION_ERROR. The latter seven are successful regression controls, not
certificates.

This package implements H1-H4 from Claude comment 5799275603 and completed
[review 5294252575](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5294252575),
then adds the bounded synthetic projector, seam and phase-lift primitives
described in [S0D_PRIMITIVES.md](../../../docs/certification-readiness/S0D_PRIMITIVES.md)
and [PLAN_005](../../../docs/certification-readiness/PLAN_005.json).

| Fixed fixture | Raw outcome | Reason |
|---|---|---|
| Renamed conditional ledger | CERTIFIED | Budget conditionally sufficient |
| Charged branch distance 15/16 | CERTIFIED | Approximate branch gate |
| Approximate-only distance 63/64 | INCONCLUSIVE | Charged branch margin fails |
| Internally formed six-dimensional congruence | CERTIFIED | Declared pair windows |
| Recognized nonfinite enclosure | INCONCLUSIVE | Nonfinite enclosure |
| Malformed tuple dimensions | EXECUTION_ERROR | ValueError preserved |
| Eight-node circular Riesz quadrature | CERTIFIED | Projector enclosure below 1/64 |
| Weak four-node projector bound | INCONCLUSIVE | Projector budget not met |
| Internally formed oriented seam map | CERTIFIED | Seam enclosure below 1/128 |
| Singular conformal polar factor | INCONCLUSIVE | Denominator not separated |
| Sixteen-step positive phase loop | CERTIFIED | Continuous lift, integer +1 |
| Antipodal phase step | INCONCLUSIVE | Local branch not separated |
| Wide but locally separated phase loop | INCONCLUSIVE | Unique integer not isolated |

The branch threshold is exactly `7935/8192 = 0.9686279296875` under the fixed
`eta=1/128` allowance. The positive Riesz fixture uses a Householder-rotated
spectrum `[-3,-2,0,0,2,3]`; its analytic error encloses `1/255`, and the full
projector error is below `1/64`. The seam fixture forms its overlap internally
and encloses the complete map below `1/128`. The positive phase record has 16
locally separated increments and isolates winding `+1`.

## Reproduction and evidence

The frozen SPEC SHA-256 before execution was
`cb3f390d78a29d877470cf5059d26c0a8b8f102ae2dc566aceacfe55fd604489`.
Limits are 180 seconds total, 30 per job, 1 GiB per worker, one worker,
128-bit precision and no retries. The run uses the locked python-flint 0.9.0 /
FLINT 3.6.0 wheel with SHA-256
`376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`.

`RUN/RESULTS.json` retains every raw outcome; `RUN/MANIFEST.json` binds 25
files and `COMPLETE.json` was written last. The complete current and inherited
sources are under `RUN/SOURCE`. Timings and RSS are observational; numerical
bounds use exact dyadic endpoints. From this directory:

```sh
PYTHONPATH="$FLINT_TARGET" python -B driver.py --wheel "$WHEEL" --output "$FRESH_OUTPUT"
python -B test_driver.py
python -B verify_evidence.py
```

The static verifier checks every file binding, source snapshot, raw status,
24 signed inertia pivots, exact branch threshold, Riesz error identity, seam
budget, 16 phase increments, unique/refused integer predicates and all ten
protocol controls. Never reuse archived `RUN` as an output directory.

## Scope

These are fixed synthetic arithmetic implications. The circular-projector
routine requires a separately certified self-adjoint spectral split. The seam
routine requires valid common-ambient frame enclosures and does not identify a
physical translation. The phase routine requires its samples to enclose the
whole per-step path variation; it does not certify an unsampled path.

Independent review is pending. Physical S1-S4 remain NOT_IMPLEMENTED,
NOT_RUN and BUDGET_NOT_FROZEN. No physical Hamiltonian, eigensolver or sweep
was executed, and no physical gap, frame, seam, winding, Euler class or cutoff
agreement is certified.
