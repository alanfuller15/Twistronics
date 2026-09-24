# S1a hardening: case-bound assembly and runtime lock

Parent `38984059e5a6a755c0a9c24400f2030100ad024a`. This additive packet
closes only the four acceptance-mechanics findings from Claude's S1a audit.
It does not enlarge the physical claim.

## Closed findings

- `HBARV_meV_angstrom`, `A_LAT_angstrom`, `B`, and all harmonic semantics are
  consumed directly from the hash-bound fixed `CASE.json`.
- Unsupported `phi_deg`, `mass`, `Dfield`, `w_kappa`, `w_mode`, `geometry`,
  `kinetic`, valley, harmonic semantics, and implicit index-set construction
  are refused. Ten retained mutations exercise those refusal paths.
- The diagnostic bridge imports and runs the archived `knobs.add_harmonic`
  helper. Its complete import closure is independently digest-bound.
- The exact python-flint wheel is identified by filename and detached digest;
  retained evidence also binds python-flint `0.9.0` and native FLINT `3.6.0`.

The original affine coefficient digests, nested identity, and six diagnostic
bridge evaluations are recomputed. BLAS-dependent diagnostics retain numeric
tolerances; they are not compared by exact byte equality.

## Claim ceiling

Status remains `PASS_PHYSICAL_AFFINE_ASSEMBLY_BRIDGE`. This is physical affine
assembly evidence only. No interval inertia or uniform isolation is certified.
No projector, transport, seam, integer, topology, relative class,
cutoff-convergence, or experimental claim is made.

S1b interval-inertia work may begin only after an independent audit passes
this exact published commit and retained packet.
