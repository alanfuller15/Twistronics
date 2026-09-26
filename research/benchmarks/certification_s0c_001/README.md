# S0c: corner allowance and declared spectral outcomes

2026-09-23. **11/11 expected behaviors and 8/8 protocol checks passed.**
The first fixed numerical run completed in 28.558 seconds, with no retries.
It retains four CERTIFIED synthetic claims, six INCONCLUSIVE controls and
one deliberately triggered EXECUTION_ERROR. The latter seven outcomes
are successful regression controls, not certificates.

This implements the corrections from Claude comment 5798619931 and
[completed review 5293785199](https://github.com/alanfuller15/Twistronics/pull/2#pullrequestreview-5293785199).
See [the derivation](../../../docs/certification-readiness/S0C_CORRECTIONS.md)
and [PLAN_004](../../../docs/certification-readiness/PLAN_004.json).
S0a and S0b remain frozen; this package supplies a corrected successor.

| Fixed fixture | Raw outcome | Reason |
|---|---|---|
| Rebalanced corner allowance | CERTIFIED | Conditional error budget |
| Old 1/32 corner allowance | INCONCLUSIVE | Corner bound not justified |
| Overspent 1/4 allowance | INCONCLUSIVE | q budget not certified |
| Uncertain center complement | INCONCLUSIVE | Inverse not certified |
| Invertible center, wide cell | INCONCLUSIVE | Uniform residual not certified |
| Uncertain Gram bound | INCONCLUSIVE | Basis not certified |
| Dimension 196, declared pair [97,98] | CERTIFIED | Counts 97/99 at both window endpoints |
| Dimension 308, declared pair [153,154] | CERTIFIED | Counts 153/155 at both window endpoints |
| Small wrong pair [1,2] | INCONCLUSIVE | Spectrum-free windows have other indices |
| Small correct pair [2,3] | CERTIFIED | Counts 2/4 at both window endpoints |
| Malformed matrix dimensions | EXECUTION_ERROR | ValueError preserved by worker |

The revised conditional ledger gives a geometric corner-angle bound
<0.165353 rad, within the 3/16 allocation, and q half-width <0.120287,
within 1/8. These are implications of certified input errors, not actual
physical frame or seam certificates. Branch separation, continuous lifts,
orientation, all upstream errors, compatible gluing and integrality remain
additional requirements. The old cap's failed sufficient test does not
prove an actual error exceeds that cap.

The full-size cases exercise the same perturbed rational family and
nonzero center residuals as S0b. The corrected code derives required counts
from the declared pair. Synthetic center labels select the Schur block
but do not determine certified inertia. The two small pair controls use
the same exact diagonal matrix and spectral windows, changing only the
declared pair. Their different results catch false acceptance of a
spectrum-free window that belongs to the wrong bands.

The inverse-exception control reaches the previously uncaught
ZeroDivisionError path. A second case reaches the later residual test,
and a third reaches the Gram gate. Numerical uncertainty survives the
worker boundary as INCONCLUSIVE. Malformed dimensions remain an error.
The driver checks expected status, reason and exception type separately
and stops on any unexpected result. It has no adaptive physical policy.

## Retained evidence and reproduction

[RUN/RESULTS.json](RUN/RESULTS.json) retains every raw outcome.
Every signed pivot and numerical bound uses exact dyadic endpoints;
timings and RSS are observational. The static verifier checks 2,064 pivot
signs and six windows at the declared indices, including the full-size
cases. It also checks the wrong-index refusal and both inverse paths.

The frozen spec SHA-256 before execution was
`4a8b447ecf67db257dccedfdfac623796385c35d4069011781ba3060752e7c3b`.
Limits: 300 seconds total, 90 per job, 2 GiB worker address space, one
worker, 128-bit precision, no retries or case changes after outcomes.
The numerical output was written to a fresh absolute directory outside
the packet, then copied intact into RUN. Its complete dependency sources
are retained under RUN/SOURCE. The portable manifest binds 22 files;
COMPLETE is written last and binds its hash and result status.

Use the existing isolated python-flint 0.9.0 / FLINT 3.6.0 x86_64 wheel
with SHA-256 `376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`.
The driver checks installed native artifacts against that wheel before
running; the retained environment used CPython 3.12.14. From this directory:

```sh
PYTHONPATH="$FLINT_TARGET" python -B driver.py --wheel "$WHEEL" --output "$FRESH_OUTPUT"
python -B test_driver.py
python -B verify_evidence.py
```

FLINT_TARGET is the locked installation, WHEEL its local wheel artifact,
and FRESH_OUTPUT a new directory. Never use the archived RUN directory
as the output. The standard-library protocol checks need no numerical
backend. Their captured outcomes are in PROTOCOL_CHECKS.json; the static
verifier checks hashes and rational predicates, without rerunning numerics.
The parent packets and CASE bindings are recorded in PACKET_MANIFEST.json.
Backend, compiler, hardware and the analytic hypotheses remain trusted
assumptions; hash integrity is not an independent proof of arithmetic.

## Remaining gate

S0c awaits independent review. S0 is incomplete. Riesz projectors and
quadrature, polar-map error enclosures, continuous phase lifts and actual
corner enclosures still need implementation and tests. Physical S1–S4
budgets are unfrozen. No physical model, physical Hamiltonian, eigensolver
or sweep was evaluated, and no physical class or cutoff agreement is certified.
