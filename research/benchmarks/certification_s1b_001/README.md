# S1b bounded interval-inertia attempt

This packet begins the physical S1b stage for fixed declaration
`FC49-77-K-Bm025-v2`, from independently reviewed S1a hardening commit
`654ef460af1dc9594457feff37cf04d628f7d558`.

It uses the reviewed Arb affine assembly, intrinsically binds the loaded
python-flint extension and mapped native libraries to the exact locked wheel,
and attempts a breadth-first closed-cell covering. Every accepted spectral
window requires signed pivots from unpivoted interval LDL inertia at both
endpoints and the declared Weyl extension to the complete cell.

An approximate eigensolver proposes a fixed nonsingular congruence and rational
window candidates only. It licenses no count or gap: interval Gram bounds prove
the congruence nonsingular, and interval LDL signs prove the inertia.

Large retained cutoff records are deterministic gzip streams split into fixed
750,000-byte parts. `verify.py` reassembles and decompresses them before
checking the manifest, partitions, limits, and signed pivots.
Executor-local filesystem paths and per-library identities are deliberately
omitted from public retained provenance. The checker still requires every
installed native member, the loaded extension, and all mapped native libraries
to match the exact wheel; the public record retains the wheel lock, versions,
counts, and pass/fail binding flags.

Run from the repository root with the exact wheel named in the parent packet:

```bash
python research/benchmarks/certification_s1b_001/check.py \
  /fresh/output/directory \
  /path/to/python_flint-0.9.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl

python research/benchmarks/certification_s1b_001/verify.py \
  /fresh/output/directory
```

The first reached cell, factorization, wall, memory, or depth limit produces
`INCONCLUSIVE`; it is not evidence that a physical gap closes. Even a complete
S1b certificate would establish uniform external isolation only for the two
declared finite systems. It would not establish projectors, transport, seams,
an integer, a relative class, cutoff convergence, or an experimental claim.
