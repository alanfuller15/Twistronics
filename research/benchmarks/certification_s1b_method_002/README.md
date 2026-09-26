# S1b method 002: cell-intrinsic feasibility probe

This additive packet tests a fixed, predeclared set of 18 cells.  It replaces
the global row-sum/Weyl envelope with direct interval inertia on the exact
affine parameter box in each cell.  It is a method probe, not a domain cover
and not a uniform-isolation certificate.

Run with the exact locked wheel named by the parent S1a hardening packet:

```sh
python -B check.py RUN /path/to/python_flint-0.9.0-...whl
python -B verify.py RUN
```

The retained cell record is a deterministic gzip stream split into numbered
18,000-byte parts for transport; the verifier requires a contiguous part set.

The retained claim ceiling excludes projector, transport, seam, integer,
topology, relative-class, cutoff-convergence, and experimental claims.
