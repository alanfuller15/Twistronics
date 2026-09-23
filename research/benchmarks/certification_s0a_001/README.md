# S0a: bounded synthetic inertia and transport calibration

Date: 2026-09-23. **10/10 fixed jobs passed**, including seven small regression
checks, seven full-dimensional point-inertia jobs and two transport jobs.
See [RESULTS.json](RUN/RESULTS.json) and the
[design amendment](../../../docs/certification-readiness/AMENDMENT.md).

This implements part of S0, not the physical case or the whole certification
backend. All matrix spectra and ODE solutions are prescribed synthetic
known answers. The dimensions 196/308 match the target sizes. The favorable
known eigenbasis and block-skew ODE do not model physical conditioning or
dense projector/transport cost. No archived source is imported.

## Reproduction

Use CPython 3.12 on x86_64 Linux and the wheel
`python_flint-0.9.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl`,
SHA-256 `376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`.
It was obtained from PyPI and reports native FLINT 3.6.0. Its native libraries
and extension modules are individually hashed in [ENVIRONMENT.json](RUN/ENVIRONMENT.json).
The wheel is not vendored. Obtain the exact artifact, verify its hash before
installing into an isolated target, and use that target for PYTHONPATH.

From this directory, with WHEEL and FLINT_TARGET set to those local paths:

```sh
PYTHONPATH="$FLINT_TARGET" python run_calibration.py --wheel "$WHEEL" --output "$PWD/REPRO_RUN"
```

The destination must not exist. The frozen [SPEC.json](SPEC.json) is read
before execution; no shifts, precision choices, thresholds or retries adapt
to the outcome. Every worker gets a 100-second timeout and a 2-GiB address
space ceiling; the parent imposes a 900-second cumulative time limit. A
zero-containing LDL pivot or timeout is retained as INCONCLUSIVE. A known
answer mismatch is EXECUTION_ERROR and stops later jobs. The retained RUN
was the first complete execution of this spec and passed in 24.018 seconds.
Source/spec hashes in the run manifest bind the actual executed version.

## What is checked

- Incorrectly dropping the shift Gram matrix changes inertia; the corrected
  dense congruence recovers both sides of a repeated rank-two eigenvalue.
- A nonsingular matrix with a zero leading pivot is inconclusive for
  unpivoted LDL. Symmetric permutation preserves inertia. A tiny uniform
  Schur family passes; zero coupling does not erase direct diagonal motion.
- The exact-skew Taylor remainder plus the full midpoint rounding radius
  bounds an n-by-2 state after 512 steps, with comparison against the
  separately evaluated closed-form solution. The bound is below 1.807e-11.
- A declared uncertain rate has a real additional error debit above 1e-8;
  it is not discarded as roundoff.

Each exact interval endpoint is stored as `mantissa * 2**exponent`, including
all signed LDL pivots. Reported norm bounds use the **upper** endpoint;
`sigma_min_V_lower_bound` uses the **lower** endpoint of its stored enclosure.
Timings and RSS are floating diagnostic observations, not certified bounds.

The mathematical contracts and proofs are in AMENDMENT.md. The backend
uses official [Arb scalar](https://python-flint.readthedocs.io/en/stable/arb.html)
and [Arb matrix](https://python-flint.readthedocs.io/en/latest/arb_mat.html)
operations. Backend and machine correctness are trusted, not formally proved.

## Retained diagnostic inspection

`python inspect_retained_diagnostics.py` reproduces
[RETAINED_DIAGNOSTICS.json](RETAINED_DIAGNOSTICS.json) using standard-library
ZIP/JSON reads. Its 1,486 rows are sampled physical evidence from two old loop
runs, kept separate from the ten synthetic jobs. It neither evaluates a
Hamiltonian nor certifies a domain-wide gap or a minimum required mesh.

The package and amendment are bound by PACKET_MANIFEST.json; RUN/MANIFEST.json
separately binds the frozen calibration source and outputs. Existing q001–q008
and the previous eight-file case/plan packet are unchanged.

`python verify_packet.py` checks all retained hashes and accepts the recorded
pivot signs and transport predicates using exact rational arithmetic. This
static check neither reruns the numerical jobs nor proves the algorithms.
