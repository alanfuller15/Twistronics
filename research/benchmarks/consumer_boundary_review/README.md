# Consumer boundary review: plan binding and output preservation

**Two previously unprobed v078p acceptance gaps now have executable counterexamples.** A changed plan can be recorded as COMPLETE while the constructor uses the original parameters. Reusing an output directory can erase earlier rows and diagnostics before model construction succeeds.

This is a software review of the unchanged [v078p input](../migration_contract_review/partner_v078p.zip), based on public checkpoint `44dc66951057a995ee0999c785aca3e0e6c67092`. The original archive SHA-256 is `d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e`. These probes supplement items 2–3 of [FABLE_NEXT_PASS.md](../migration_contract_review/FABLE_NEXT_PASS.md); they do not implement the requested corrections.

## Observations retained on 2026-09-23

| Synthetic scenario | Actual consumer result | What it establishes |
|---|---|---|
| Matching original plan, fresh directory | Exit 0; COMPLETE; eight unique synthetic rows | Control: the instrumented path reaches normal completion. This is not a numerical positive run. |
| Plan declares N=5 instead of 4 | Exit 0; COMPLETE; all 11 constructor calls still receive N=4 | The plan's cutoff is not bound to the executed constructor. No N=5 model is measured. |
| Plan declares strain ε=0.004 instead of 0.003 | Exit 0; COMPLETE; all 11 calls still receive ε=0.003 | The plan's strain is not bound to the executed constructor. |
| Existing directory with prior synthetic records | Exit 0; COMPLETE; all three prior files replaced | Replacement is performed without an explicit opt-in. |
| Same existing directory; injected first-constructor error | Exit 1; prior rows and diagnostics become empty; old summary remains | An unsuccessful attempt can destroy prior evidence and leave a stale summary. |

In both changed-plan cases, the summary records the **changed plan hash**, while all ten model records retain the original defaults. This demonstrates a consistency gap; the genuine retained v078p plan and constructor agree. It does not show that the original numerical results used incorrect parameters.

The existing-directory tests use disposable sentinel files: 36 bytes of prior rows, 43 bytes of prior diagnostics, and a 33-byte summary marked `SYNTHETIC_PRIOR`. They never target retained research output. In the injected-error case, the first two files shrink to zero bytes, and the summary remains byte-identical. The tested error is a controlled Python exception after `Run` initialization, not a hardware-failure experiment.

## Evidence and reproduction

- [Receipt](evidence/20260923T0328Z/RECEIPT.json): actual subprocess exits, named predicates, input/probe hashes and hashes of every retained observation/log.
- [Matching-plan control](evidence/20260923T0328Z/matching_plan/OBSERVATION.json).
- [Changed N](evidence/20260923T0328Z/plan_N/OBSERVATION.json) and [changed strain](evidence/20260923T0328Z/plan_eps/OBSERVATION.json).
- [Existing-directory completion](evidence/20260923T0328Z/existing_success/OBSERVATION.json) and [existing-directory abort](evidence/20260923T0328Z/existing_abort/OBSERVATION.json).
- [Probe source](probe_consumer.py) and [outcome-checker regressions](test_probe_outcomes.py).

The probe extracts and hash-checks the unchanged archive into a separate temporary source tree for each scenario. A transparent wrapper records actual constructor arguments and delegates to the real constructor, except for the declared injected error. The consumer uses its existing discovery/measurement injection points. The synthetic measurements return invented SAME labels and no frame diagnostics; these are **not scientific evidence**, and are not submitted to the numerical record checker.

The observations retain complete consumer rows, summary, constructor-call records, model defaults and before/after file hashes; the collision cases also retain prior contents and their final contents. Transient full geometry/basis/model files are represented by hashes, not all copied into this review. The original archive and probe regenerate them; these hashes do not independently establish numerical correctness.

Runtime: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0. From the repository root, use a **new** output directory:

```sh
python research/benchmarks/consumer_boundary_review/probe_consumer.py --output /tmp/twistronics-boundary-new
python research/benchmarks/consumer_boundary_review/test_probe_outcomes.py
```

Do not use Python `-O`; the preserved archive extractor uses assertions. Existing review output directories are refused before writing. Each scenario runs in a fresh process with a 60-second limit and one BLAS thread.

**Probe exit 0 means the pinned baseline observations, including its defects, were reproduced. It does not mean the consumer is repaired or accepted.** The outcome checker checks exact exits, the intended injected error, constructor arguments, case inventory and actual file changes. A source mismatch or missing current observation prevents success. The outcome-checker tests exercise counterexamples that must not be mistaken for the intended reproductions.

## Required behavior in the corrected package

1. The declared plan and actual constructor must agree under an explicit policy. A fixed-baseline consumer can reject a changed plan before work starts; a configurable consumer must actually use and record it. Do not report COMPLETE with conflicting plan/model identities.
2. Reusing a run directory must follow a declared policy. Refuse it while preserving existing bytes, create a fresh run, or require an explicit replacement option with tested evidence retention. The original outputs must survive a refused attempt.
3. Add enforcing corrected-package regressions for both directions: permitted matching/fresh operation, and refused or safely handled inconsistent/colliding input. Do not turn this baseline-reproduction suite's exit zero into the delivery gate.

The original Claude/Fable conversation continues to own those implementation changes. PR #2 owns the shared intake handoff. The corrected package remains unreviewed until its source and evidence arrive. No new node discovery, charge measurement, cutoff campaign, continuous-path proof, Euler-class change or experimental claim is made here.
