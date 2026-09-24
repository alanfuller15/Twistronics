# S1b method 002: direct affine-cell interval inertia

Parent reviewed evidence: `cd22aa6950eb77a5220d84695abf10c60b68258b`.

## Purpose

The retained S1b-001 search was correctly inconclusive.  Its global row-sum
Weyl envelope requires depth 9 for the narrowest retained candidate window,
which is incompatible with its 512-cell cap.  This packet tests the smallest
bounded alternative: construct the exact affine interval matrix on each cell,
apply one certified fixed congruence proposed at the cell midpoint, and run
interval LDL directly at the four fixed window endpoints.

Every parameter-box endpoint is an exact rational converted directly to Arb.
The new path does not use `upper_float`, a rounded Python float, or a global
row-sum radius.  The exact dyadic output endpoints remain replay-verifiable.

## Frozen probe

The probe contains 18 predeclared cells: nine per cutoff.  It includes the
root, all four depth-1 cells, and one fixed centre-adjacent chain through
depths 2, 3, 4, and 5.  At 128 bits this is exactly 72 interval-LDL
factorizations, one physical case, one thread, and zero parameter sweeps.  The
set is not adaptively extended and cannot be interpreted as a domain cover.

## Retained outcome

`PASS_RETAINED_S1B_CELL_INTRINSIC_METHOD_PROBE`: 18 cells and exactly 72
factorizations were retained.  The depth-5 centre-adjacent probe cell
certified both fixed external windows for each cutoff.  At depth 4, the lower
window certified for each cutoff while the upper window remained
inconclusive.  The other 14 cells remained inconclusive.  All candidate
window widths exceeded the declared `0.00001 meV` target.

This closes only the method-feasibility question: direct affine-cell interval
inertia can succeed at depth 5 without the depth-9 global Weyl requirement.
It does not show that every depth-5 cell succeeds.  A later bounded coverage
round must freeze an adaptive policy and retain a complete accepted/unresolved
partition; it must not infer a 1024-cell certificate from this selected-cell
probe.

## Claim ceiling

A certified probe cell proves only the two fixed external windows on that
closed cell.  The overall packet is method-feasibility evidence.  It does not
certify uniform isolation and establishes no projector, transport, seam,
integer, topology, relative class, cutoff convergence, or experimental claim.
