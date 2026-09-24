# S0e fixed correction evidence

See ../../../..//docs/certification-readiness/S0E_CORRECTIONS.md for derivation,
caller obligations, limits and the next gate. Source review: Claude 5804846025.

The fixed run has 14/14 expected outcomes, including eight inconclusive and two
execution-error controls. These controls are not geometric certificates.

Reproduce from repository root with the locked python-flint 0.9.0 environment:

```sh
python research/benchmarks/certification_s0e_001/driver.py --wheel /path/to/locked.whl --output /tmp/s0e-new
python research/benchmarks/certification_s0e_001/test_driver.py
python research/benchmarks/certification_s0e_001/verify_evidence.py
```

The driver refuses existing output directories, snapshots its dependencies,
enforces bounded subprocess execution, and reports zero physical evaluations.
PACKET_MANIFEST.json binds this package and the derivation. The verifier checks
source snapshot equality, run hashes, expected outcomes and exact dyadic
predicates for containment, width and singular-value refusal. It does not execute
the physical model. Independent review is pending.
