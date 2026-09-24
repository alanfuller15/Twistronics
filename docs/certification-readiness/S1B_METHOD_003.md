# S1b method 003: narrow-window hard-region probe

Parent reviewed evidence: `fae7794fdec7f7135e9e58df95d3899071533722`.

## Question

Method 002 established that direct affine-cell interval inertia can certify a
selected centre-adjacent cell at depth 5. Its independent audit found that the
narrowest retained candidate window, about `1.773 meV`, instead occurs in the
depth-1 high-coordinate cell containing `(3/4, 3/4)`. Full-coverage cost cannot
be justified until that harder region is probed.

## Frozen design

For each cutoff, this packet evaluates two nested diagonal chains. At depths 2
through 7, one closed cell approaches `(3/4,3/4)` from below and one from
above. This gives exactly 24 primary cells and 96 primary interval-LDL
factorizations at 128 bits. The cell list is explicit in `SPEC.json`; no
adaptive extension or wall-time truncation is allowed.

Every primary accepted cell is recomputed at the exact recorded shifts using
midpoint eigenvectors independently rounded to 10 significant digits. The new
congruence must independently pass the Gram nonsingularity certificate, and
all four interval-LDL counts must certify again. Only then is the cell reported
as accepted. This makes the independent accepted-cell check part of the
retained packet rather than an external review action.

## Retained outcome

The fixed run completed all 24 cells and 96 primary factorizations. Four cells
certified primarily and all four passed the independent recomputation, adding
16 factorizations for 112 total. For both cutoffs, the first retained success
was depth 7; both diagonal cells adjacent to `(3/4,3/4)`, `(95,95)` and
`(96,96)`, certified. No depth 2--6 cell in either frozen chain certified.

This is evidence that the direct affine-cell interval-inertia method can close
the reviewed narrow-window region at depth 7 for these two selected cells and
this fixed physical case. It is also a measured local refinement scale, not a
license to extrapolate over untested cells.

## Claim ceiling

The two chains do not cover the high-coordinate quadrant or the full domain.
This packet may establish only a local method-feasibility depth and measured
cost scale. It cannot certify uniform isolation and establishes no projector,
transport, seam, integer, topology, relative-class, cutoff-convergence, v078,
or experimental claim.
