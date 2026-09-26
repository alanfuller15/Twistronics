# Codex review: fast pipeline

Verdict: **PASS** for `FastPointMatrix`, the zero-eigensolve controls and float64 state packing in the declared fixed-precision workflow.

Reviewed producer commit: `a56d0c6a2f7957f4239d6f1ec80641c35af7443d`.
Request: https://github.com/alanfuller15/Twistronics/pull/2#issuecomment-5844474363.
Retained input evidence: LOWER-CONTROLS-021 at `38204bfc987108e60d7e2c1b9561fdd0fe3c6057`.
Reviewer: Codex; producer: Claude. This review ran **zero physical eigensolves**.

## Independent control execution

The unmodified producer `controls.py` completed once, exit 0, in 42.659499 seconds, with a 90-second watchdog and one-thread environment. Arb precision is 128 bits and Arb threads is 1 in the controls.

| Cutoff | Dimension | Support entries | Matching points | Reference ms/point | Fast ms/point |
|---|---:|---:|---:|---:|---:|
| a | 196 | 392 | 48/48 | 22.38 | 0.304 |
| b | 308 | 616 | 48/48 | 55.88 | 0.455 |
| c | 444 | 888 | 48/48 | 125.20 | 0.720 |
| d | 604 | 1208 | 48/48 | 226.73 | 1.082 |
| e | 788 | 1576 | 48/48 | 390.01 | 1.253 |

All 240 matrices match the reference bytes. All 48 rational coordinates equal the producer's controls.

The 021 archive SHA-256, all 35 decoded part hashes and all 125 extracted file hashes matched its manifest. All 24 original `STATES.npz` jobs were passed to `--states`: two packs agree, and every unpacked array's shape and float64 bytes agree. Each packed-file SHA-256 also equals the producer control result. Original 24-job packing totals 11,269,337 bytes versus 13,407,142 NPZ bytes (15.94% smaller). The producer's separately regrouped six-job reproduction has a different packed total; it was not rerun here.

## Source review

- `_exact_zero` tests both midpoint and radius. An interval containing zero with nonzero radius remains in the support.
- Off support, both affine terms are exact zero. At the unchanged 128-bit context and finite rational coordinates, the constant coefficient midpoint is reusable.
- On support, the exact-rational Arb conversion and expression `(C0 + X*C1) + Y*C2` match the reference operation order. There is no floating-point affine approximation.
- Each call copies the fixed matrix, so changing a returned matrix cannot alter the cached one. Construct one instance per cutoff per job; do not mutate coefficients or change precision during its lifetime.
- Packing sorts names, normalizes the documented float64 arrays to contiguous little-endian bytes, shuffles invertibly, and hashes the restored raw bytes. Its tested contract is the retained full spectra and real four-state arrays.
- Keep whole-container file hashes in the evidence manifest. The per-array digest covers raw bytes, not header names/shapes. Use normal Python execution: controls and unpacking integrity checks use assertions.
- Supply retained state fixtures to `controls.py --states`; without this optional argument the packing checks are empty.

Nonblocking documentation nit: the module's opening support range says 0.25–0.45%; the a–e range is 0.25–1.0%, as its README correctly states.

## Runtime provenance limit

The locked wheel has SHA-256 `376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`. The unmodified provenance checker passed the wheel digest, python-flint 0.9.0 / native FLINT 3.6.0 versions, installed native-member byte hashes and loaded Python extension binding. It then stopped at `PROC_MAPS_REQUIRED`: this sandbox does not expose `/proc/self/maps`. Mapped shared-library provenance is therefore **not verified**. This limitation is retained in PROVENANCE.json; no physical worker was launched and no provenance requirement was relaxed for physical runs.

The PASS covers the requested source review and zero-eigensolve controls. It is not a fresh independent 576-solve reproduction, a production-runner audit, a scientific claim, or permission to publish.

## Reproduce

Use the exact reviewed fast-pipeline files with the CASE, assembly, reference runner and c/d/e SPEC files bound in SOURCE_BINDINGS.json. The a–d dependencies are byte-identical at the producer and 021 commits; the e SPEC comes from the 021 commit.

Install the hash-verified locked wheel, materialize the 021 retained files with their hashes, and run:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python -B research/tools/fast_pipeline/controls.py <source-root> <new-result.json> --states <retained-021>/job*/STATES.npz
```

CONTROLS_RESULT.json and CONTROLS.log retain the unchanged program's output. RECEIPT.json records the actual command and exit. CROSSCHECK.json records comparison to the producer control output. MANIFEST.json binds this review packet.
