# S1b method 003: hard-region two-sided chain

This additive packet probes the narrow-window region identified by the
independent review of method 002. At each depth 2 through 7 it evaluates the
two diagonal cells immediately below and above `(3/4, 3/4)`, for both declared
cutoffs. The 24-cell set is frozen and is not a parameter sweep or domain
cover.

Every primary accepted cell is independently recomputed at its recorded
shifts with a separately rounded and certified fixed congruence. A cell is
retained as accepted only when both congruences certify all four endpoint
counts.

The retained run completed 24 cells with 96 primary factorizations. The two
depth-7 cells in each cutoff certified and independently recomputed, giving
four retained cells and 112 total factorizations. Depths 2 through 6 did not
certify in either chain.

```sh
python -B check.py RUN /path/to/python_flint-0.9.0-...whl
python -B verify.py RUN
```

The cell evidence is a deterministic gzip stream split into contiguous
18,000-byte parts. The claim ceiling is method feasibility only: no uniform
isolation, projector, transport, seam, topology, cutoff-convergence or
experimental claim follows.
