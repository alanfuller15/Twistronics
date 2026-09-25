# S1a: physical affine assembly bridge

Parent `f822345a50a823885c731e3e6984beae26c9b803`. This is the first bounded
physical-model execution for fixed declaration `FC49-77-K-Bm025-v2`. It does
not complete S1 and makes no finite-class or physical-material claim.

## Retained result

The pinned v078p archive was verified at SHA-256
`d703b6c027d5725ed173c69d221f450a34922e46d1320350ab1c08e3448c545e`.
From its archived formulas, the worker assembled Arb-ball affine coefficients
`H0`, `Hx`, and `Hy` for the declared 49- and 77-vector systems (real
dimensions 196 and 308). Decimal model inputs entered as exact rationals;
trigonometric and square-root quantities were evaluated by Arb at 128 bits.

All declared geometry denominators excluded zero. The coefficient radii give
whole-domain Frobenius assembly-radius upper bounds of
`1.858317698306357e-31 meV` and `2.7129672243397904e-31 meV`, both far below
the predeclared `1e-8 meV` target.

The 196-coordinate inclusion was checked against all three affine
coefficients. Every corresponding principal-submatrix entry overlapped; the
largest absolute difference upper bound was `2.715621213123868e-32 meV`.

The independent archived floating assembler was evaluated only at the three
predeclared bridge points `(0,0)`, `(1,0)`, and `(0,1)` for each cutoff. Its
largest midpoint difference from the Arb assembly was
`1.2732925824820995e-11 meV`; the transformed imaginary residual was zero in
all six evaluations. These noncollinear checks diagnose the complete affine
coefficient map but are not interval spectral certificates.

## Claim ceiling and next gate

Status: `PASS_PHYSICAL_AFFINE_ASSEMBLY_BRIDGE`.

This establishes only the source-to-affine-assembly bridge and nested ambient
identity for the fixed finite systems. The sampled floating external gaps in
`RESULTS.json` are diagnostics and may not be promoted to uniform isolation.
No interval inertia, cell covering, projector, transport, seam, integer,
relative-class, cutoff-convergence, or experimental claim was attempted.

The next bounded packet is S1b: apply the already-reviewed exact window and
path contract to a closed-cell partition and certify the four neighboring
eigenvalue brackets by interval LDL inertia under the frozen work limits. If
the conservative unpivoted recurrence or budget cannot certify coverage, the
result is `INCONCLUSIVE`, not a failed physical gap.
