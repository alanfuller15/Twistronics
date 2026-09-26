# Momentum mapping scout 002

This is one frozen exploratory refinement batch of 64 new point spectra. It
retains the scout001 numerical, watchdog and offline replay implementation,
with an explicit versioned coordinate/selection contract. The completed
scout001 files and audited diagnostic packet remain unchanged.

Selection uses the exact rational upper-gap estimates in the complete scout001
`RUN/RESULTS.json`, SHA256
`45648684252cbc628a56f18fea593bf7baf6539c0363fa1ac7959979dc2bef29`.
Sort by upper-gap estimate and then `(depth,ix,iy)`; retain the first four cells:
`(12,2812,2950)`, `(12,2813,2950)`, `(12,2811,2950)`, `(12,2813,2951)`.
They are neighboring cells in one sampled cluster, not four independent minima.

For each selected parent `(12,ix,iy)`, freeze all 16 depth-14 child centers
`((2*j+1)/32768,(2*k+1)/32768)` with `j=4*ix..4*ix+3` and
`k=4*iy..4*iy+3`. Run parents in selection-rank order and children in ascending
`(j,k)`. All 64 coordinates are distinct and absent from scout001. `SPEC.json`
retains the parent ranks, source point indices, exact selection values and all
new coordinates. Stop after this single batch; no automatic further refinement.

The unchanged numerical path assembles the locked cutoff-a affine coefficients
once at 128-bit Arb precision, forms each exact-dyadic-center matrix, converts
its midpoint to finite symmetric binary64, and calls `eigvalsh` once per point.
All 196 `.17g` eigenvalues and the midpoint matrix hash are retained. Spectrum
arithmetic reports bands 96..99, adjacent lower/upper gap estimates, local
3/8..5/8 window proposals, and endpoint counts/margins against the original
depth-9 `upper_both` parent windows. These fixed windows are unchanged; they are
not the four selected depth-12 point proposals. All outputs remain numerical
diagnostics without certified rounding or spectral error bounds.

Limits remain 64 durable eigensolver starts, one worker/native thread, 2 GiB,
120-second soft / 150-second hard watchdog, 8 MiB raw log and zero retries.
There are zero interval-LDL or coverage attempts. The source manifest binds the
unchanged audited helper closure, predecessor scaffold and exact predecessor
results. A separate supervisor preserves the journal and receipt; offline
checking validates record/source/runtime integrity and replays exact arithmetic
on the approximate retained spectra, without reassembling matrices or rerunning
the eigensolver. Matrix hashes alone are not independently reconstructed.

After review, use the verified environment and pinned wheel:

```sh
python -B research/benchmarks/momentum_mapping_scout_002/scout.py \
  --run-reviewed-scout --output /tmp/momentum-scout-002-new \
  --wheel /path/to/pinned-python-flint.whl
```

Check the retained four-file directory without numerical calls:

```sh
python -B research/benchmarks/momentum_mapping_scout_002/scout.py \
  --check-only --output /tmp/momentum-scout-002-new
```

A smaller sampled gap or a boundary minimum motivates only a future decision;
it establishes no minimum between samples, node, gap closure, tile interior,
reciprocal seam, topology, cutoff agreement or coverage. Historical coverage
remains `29663/65536`. Further execution requires a separate decision.
