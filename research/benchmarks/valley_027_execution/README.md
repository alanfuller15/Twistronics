# VALLEY-027 execution: grid map complete; loop batch not derivable (design defect disclosed)

**Implementation:** `e44cb97e008b8d1339bc49cca0932b4a9e2dfd1f`, frozen and pushed before any physical call.

| Batch | Supervisor | Time | Replay |
|---|---|---:|---|
| A: 8772 grid points | PASS | 187.9 s | **PASS**: `A/MAP.json`, 8772 eigenvalue-only solves verified |
| B: 8773 grid points | PASS | 181.3 s | **PASS**: `B/MAP.json`, 8773 solves verified |
| C: 432 loop points, full `evr` | PASS (16 jobs, 18.6 s, every job `NORMAL_EXIT`) | 18.6 s | **FAILED** before writing a MAP: `KeyError 9115` |

## Defect in the frozen design (Claude's)

`build_spec.py` de-duplicated loop points against the grid. Loop points on the 1/4096 lattice that coincide with 1/1024 grid points (128 of 640) therefore received grid indices. They were solved in the eigenvalue-only batches A and B, which retain no state vectors, so the loop products cannot be formed.

- The grid evidence (A, B) is unaffected.
- The batch C receipts, spectra and vectors are retained as run, and C is **not** re-run or patched.
- The loop test is carried out by the separately frozen follow-up **LOOPS-028**, which does not de-duplicate against any eigenvalue-only point.
