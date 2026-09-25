# S1a bounded physical affine-assembly bridge

This packet begins the declared S1 stage for `FC49-77-K-Bm025-v2`. It
constructs the 196- and 308-dimensional real symmetric affine Hamiltonian
coefficients with Arb ball arithmetic from the pinned archived formulas,
checks the exact nested principal-submatrix identity, and compares midpoint
matrices with the archived floating assembler at the three predeclared bridge
points `(0,0)`, `(1,0)`, and `(0,1)`.

It is deliberately narrower than S1 completion. It does **not** run the
cell partition, interval LDL inertia, or uniform external-gap proof. The
floating eigenvalue gaps recorded at the bridge points are diagnostics only.
No projector, transport, seam, integer, relative-class, cutoff-convergence,
or experimental claim is permitted from this packet.

Run from the workspace root:

```text
python3 s1a_physical_assembly/check.py s1a_physical_assembly/RUN
```

The run refuses a pre-existing output directory and binds the fixed case,
the original v078p archive, the three inspected archived source files, and
the exact checker source.
