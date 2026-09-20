# v044 reconciliation and early-route replay

Read REPORT.md for the result, SOURCE_REVIEW.md for the partner update and
its review cutoff, and TEAM_SHARE_v044.md for the concise handoff. The
machine-readable result is SUMMARY.json. All primary engines are unchanged
copies from the partner's v043 upload; optional fixes are separate.

## Reproduce

Use the versions in provenance/environment.json and requirements.txt. From
this directory, run each engine and cutoff, retaining the explicit model ID:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python replay.py --engine bm_lab --N 4
```

Repeat with engine ref_lab and N=6. bm_lab means lab_nn_full plus linear
geometry; ref_lab means lab_nn_full plus exact geometry. Both retain their
uploaded cutoff padding. Do not relabel these runs as a matched-geometry
pair. Use at most two primary processes and one BLAS thread per process.

Existing committed states resume after source, anchor and array-digest
verification. `--max-new 3` stops after three additional accepted states.
For a fresh rerun, use a separate copy with an empty results directory;
preserve the delivered evidence. Each primary route has 37 states.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python exact_control.py
python build_report.py
```

The exact control measures crossing roots and singular-path rejection in
BM exact using the completed reference route as root seeds. It is not a
third full continuation. PLAN.json freezes primary source and anchors;
the control output also records its script hash. The release manifest
hashes all delivered source, data and documents.

## Review and tests

The supplied 29-test suite is retained in the partner package. Ten adopted
guard regressions run against engines/tbg_ref.py; eight cutoff-patch tests
run against fixes/. Run them separately if measuring their runtime:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python -m pytest tests/test_adopted_guards.py -q -p no:cacheprovider
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python -m pytest tests/test_cutoff_patch.py -q -p no:cacheprovider
python verify_geometry.py
python boundary_probe.py
```

The full-operator comparisons and the cutoff counterexample address
different scopes: matched geometry agrees at the checked campaign states,
but unequal padding can select unequal bases at a boundary angle. The
optional cutoff_tol parameter makes that choice explicit and preserves
historical defaults. No primary result here uses the optional patch.

These are finite numerical measurements, not interval proofs, a complete
node inventory, a full campaign or physical-bilayer validation. The lower
pair is tracked only through the B legs; its later collision is not newly
located. Both main engines share the measurement harness in this replay.
