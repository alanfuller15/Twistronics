# S1b method 004: diagonal-minimum two-sided chain

This additive packet probes the retained diagonal minimum identified by the
independent review of method 003. At each depth 2 through 9 it evaluates the
two diagonal cells whose centres bracket `(23/32, 23/32)`, for both declared
cutoffs. The 32-cell set is frozen and is not a parameter sweep or domain
cover.

Every primary accepted cell is independently recomputed at its recorded
shifts with a separately rounded and certified fixed congruence. A cell is
retained as accepted only when both congruences certify all four endpoint
counts.

The retained run completed 32 cells with 128 primary factorizations. Both
bracketing cells certified at depths 8 and 9 for each cutoff and independently
recomputed, giving eight retained cells and 160 total factorizations. Depths 2
through 7 did not certify in either chain.

```sh
python -B check.py RUN /path/to/python_flint-0.9.0-...whl
python -B verify.py RUN
```

The cell evidence is a deterministic gzip stream split into contiguous
18,000-byte parts. The claim ceiling is local method feasibility only: no
uniform isolation, projector, transport, seam, topology, cutoff-convergence or
experimental claim follows.
