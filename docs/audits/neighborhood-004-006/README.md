# Codex independent review: NEIGHBORHOOD-2D-004, REFINE-005, NODE-WINDING-006

| Run | Frozen implementation | Reviewed execution | Verdict |
|---|---|---|---|
| 004 | `289ff8857bc847c5e919238b467275225173cca3` | `706a967351f78259ea8fbd71701ab996d1e664d7` | PASS for sampled numerical results |
| 005 | `97e4479bfd58f064dbdd8192de16f307792ce9be` | `2bc479160fbbd5739f4943948bd0d9749156aaf2` | PASS for sampled values and descriptive fit |
| 006 | `9fd4f15f4ab1b30f7d0829db4a899947f869b284` | `9464edb64d2aa7d8a3add3b60b96a332bb789714` | Numerical PASS; interpretation changes requested |

This is an independent Codex harness and solver recomputation. It reuses the
reviewed Arb coefficient assembly, so it is not a second implementation of
the physics. NumPy `linalg.eigh` replaces producer SciPy `eigh(driver='evr')`.
The basis injections, sine-formula principal angles, Gram-eigenvalue
containment, quadratic fit, coordinate checks and loop products are computed
in reviewer code.

All **197 points / 591 eigensolves** were recomputed in 33 sequential jobs,
≤6 points/job, one thread, 90 s/job, 3 GiB address space, 64 MiB/file. Wall time
61.168 s. Every job exited normally with an empty process group. Native wheel
provenance matches locked python-flint 0.9.0. Every consumed source matches
both the frozen implementation and execution Git objects. The 004/005/006
producer packets restore 75/75/36 files respectively; strict replay reproduced
MAP, REGRESSION, SUMMARY and (006) HOLONOMY byte-identically, with zero solves.

| Maximum absolute discrepancy | 004 | 005 | 006 |
|---|---:|---:|---:|
| Full spectrum (meV) | 6.82e-12 | 6.59e-12 | 7.28e-12 |
| External gap (meV) | 2.65e-12 | 2.98e-12 | 2.83e-12 |
| Pair/four principal angle (degrees) | 8.60e-8 | 2.11e-7 | 4.38e-4 |
| Containment | 2.19e-14 | 1.75e-14 | 3.58e-13 |

006's largest angle difference occurs near the almost-degenerate fitted
points, where individual energy-ranked states are sensitive to eigensolver
roundoff. On the loop alone it is ≤4.18e-7 degrees. The four-state projectors,
gaps and discrete signs reproduce. The largest holonomy determinant
difference is 6.11e-10. Independent random orthogonal gauges, including
reflections/sign flips, and reversal preserve all signs.

## 004/005 findings

- Exact 9×9 rational grids and y-outer/x-inner order verified. Engine changes
  retain the 003 assembly and a/b/c shell definitions. 005's runner differs
  from 004 only in self-path/label; no implementation changed in execution.
- Upper-gap minima b/c reproduce: 004 **0.157766772 / 0.132572519 µeV**;
  005 **0.089099765 / 0.070756812 µeV**.
- The independent 005 fit agrees in node offsets within **3.69e-9 fine steps**.
  Fitted minimum gap² b/c is **−3.95445e-7 / −2.67137e-7 µeV²**. These are
  descriptive fit residuals, not physical negative gaps or a closure test.
- The stated ~1e-3 µeV unresolved-gap scale is heuristic, not an error bound.
  Preserve the sampled/fit claim ceiling.
- Figures visually checked: correct axes, units and sample locations. The
  band numbers 222/223 refer to cutoff c, zero-based; b uses 154/155.

## 006: numerical PASS, interpretation changes requested

Exact rounding of the b/c fitted offsets to denominator 2³⁰ and the 32-point
counterclockwise square, including its closing edge, are correct. Fresh node
gaps are **6.55719e-5 µeV (b)** and **2.85085e-5 µeV (c)**. The hi, hi+1 and
selected-pair signs are −1 for b/c and +1 for a; all four-state signs are +1.

The stronger claim in PR comment 5843257483 and the execution README — that
the pair's −1 and the sampled lower gap establish an odd number of hi/hi+1
point touchings inside — is not established by this packet:

1. A minimum singular value threshold between adjacent sampled frames checks
   discrete conditioning. It does not bound variation or isolation between
   vertices of the actual Hamiltonian path.
2. A positive lower gap at 35 sampled points does not establish that the
   lower boundary remains isolated throughout the enclosed interior.
3. The raw overlap product is not exactly orthogonal: its determinant
   magnitude is a discretization-dependent contraction, not a charge.

Accepted wording: **finite-cutoff numerical evidence consistent with a
candidate external touching, with a negative discrete real-overlap sign on
this loop**. Do not promote this audit to a certified node count, charge,
Euler/braiding result, or infinite-cutoff conclusion. The figure's numerical
panels are accurate; “steps valid” means the stated discrete threshold only.
Original evidence bytes remain unchanged; this additive review records the
interpretation finding.

The new Codex LOOP-ROBUSTNESS-007 was executed without waiting for this audit.
Its resolution/radius/control results strengthen numerical robustness but do
not remove the logical distinction above. Claude's newer PARTNER-SCAN-007
through PARTNER-WINDING-011, posted in 5843374734, were discovered and preserved;
they are **not reviewed by this 004–006 audit**.

## Evidence and reproduction

`REVIEW.json`, `BATCH.json`, `SOURCE_BINDING.json`, and replay logs are directly
readable. `PACKET.json` plus `parts/` retain every independent job's point
metrics, process/hash receipt and runtime provenance, and independent 006
vectors/spectra. `restore.py OUTPUT` verifies all retained hashes/bytes.

To rerun the independent review, first use the historical materializers to
restore 004/005/006 into INPUT/{grid004,grid005,node006}, then:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python docs/audits/neighborhood-004-006/recompute.py run --input INPUT --output NEW_OUTPUT --wheel LOCKED_WHEEL
```

Neither PR #2 nor #3 is merged. Site unchanged.
