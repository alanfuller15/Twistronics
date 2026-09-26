# Momentum mapping scout 001

This separate exploratory packet maps 64 new point spectra inside the retained
`upper_both` parent cell `(9,351,368)`. It does not change the audited diagnostic
packet, revisit the 40 old depth-9 centers, subdivide a certification partition,
or perform interval-LDL. Every result is an approximate finite-cutoff-a point
diagnostic, with historical coverage unchanged at `29663/65536`.

`SPEC.json` freezes all 64 depth-12 tile centers in ascending `(ix,iy)` order:
`ix=2808..2815`, `iy=2944..2951`, each coordinate `(2*i+1)/8192`.
The successful centered eighth-radius diagnostic box is half a depth-12 grid
spacing offset from these dyadic children; it establishes no child-tile pass.

The runner reuses the pinned CASE, 128-bit Arb affine assembly and exact locked
runtime checks. It assembles the coefficients once at 128 bits, forms each
exact-dyadic-center Arb matrix, converts its midpoint to binary64, checks exact
floating symmetry and finiteness, and calls `numpy.linalg.eigvalsh` once per
point. A durable start record precedes each eigensolver call. All 196 sorted
eigenvalues are retained as `.17g` decimal strings. The matrix SHA256 refers to
row-major little-endian float64 midpoint bytes; it is provenance, not a retained
matrix or independently reconstructible numerical certificate.

Exact rational arithmetic on those approximate decimal spectra derives band
energies 96..99, lower and upper adjacent-gap estimates, local 3/8..5/8 window
proposals, and diagnostics for all four frozen parent-window endpoint shifts.
Each endpoint reports strict negative/equality counts, left and right spectral
margins, their minimum, and distance to the closest approximate eigenvalue.
Every report shares the point, matrix hash and source/runtime bindings of its
spectrum. None is a certified inertia, rounding enclosure or physical gap bound.

Limits are 64 eigensolver starts, one worker and one native thread, 2 GiB address
space, 120-second soft and 150-second hard watchdog deadlines, no retries, and
8 MiB raw evidence. The supervisor uses a separate process group, reaps it,
checks that no group survives, and retains a receipt. Timeout prefixes preserve
completed points and distinguish an interrupted solver from unstarted points.
Only a complete 64-point run reports `EXPLORATORY_COMPLETE`; a timeout is not
evidence for a failed gap. No point result certifies a tile interior.

Run only after the implementation has been reviewed, using the previously
verified local Python environment and pinned wheel:

```sh
python -B research/benchmarks/momentum_mapping_scout_001/scout.py \
  --run-reviewed-scout --output /tmp/momentum-scout-new \
  --wheel /path/to/pinned-python-flint.whl
```

Offline reproduction uses no numeric imports or solver calls:

```sh
python -B research/benchmarks/momentum_mapping_scout_001/scout.py \
  --check-only --output /tmp/momentum-scout-new
```

`SOURCE_MANIFEST.json` binds this packet and the unchanged audited helper closure.
Each run retains exactly `EVENTS.ndjson`, `SUPERVISOR_RECEIPT.json`, `RESULTS.json`
and `MANIFEST.json`. The verifier replays record hashes, ordering, point membership,
source/runtime identity and all spectrum-derived arithmetic. It does not rerun
assembly or diagonalization. A tiny synthetic spectrum fixture is available via
`--self-test`; it makes no physical calls.
