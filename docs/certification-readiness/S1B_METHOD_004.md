# S1b method 004: diagonal-minimum probe

Parent reviewed evidence: `aab6bae4df0e8337322a2a57bcfdd4b8f5548521`.

## Question

Method 003 established local direct-cell feasibility next to `(3/4,3/4)` at
depth 7. Its independent audit found that the narrowest retained diagonal
windows instead occur near `(23/32,23/32)`: about `0.7613 meV` for cutoff a
and `0.7595 meV` for cutoff b. A full coverage round is not justified until
this harder retained location is tested at a bounded refinement depth.

## Frozen design

For each cutoff, this packet evaluates two diagonal cells at each depth 2
through 9. Their centres bracket `(23/32,23/32)`. This gives exactly 32
primary cells and 128 primary interval-LDL factorizations at 128 bits. The
cell list is explicit in `SPEC.json`; no adaptive extension or wall-time
truncation is allowed.

Every primary accepted cell is recomputed at the exact recorded shifts using
midpoint eigenvectors independently rounded to 10 significant digits. The new
congruence must independently pass the Gram nonsingularity certificate, and
all four interval-LDL counts must certify again. The conservative retained cap
is 128 primary plus 128 recomputation factorizations.

## Retained outcome

The fixed run completed all 32 cells and 128 primary factorizations. Eight
cells certified primarily and all eight passed the independent recomputation,
adding 32 factorizations for 160 total. For both cutoffs, the two cells
bracketing the target first certified at depth 8: `(183,183)` and `(184,184)`.
Both depth-9 refinements, `(367,367)` and `(368,368)`, also certified. No
depth-2-through-7 cell in either frozen chain certified.

This establishes local method feasibility at the retained diagonal minimum
for these fixed cells and this physical case. It supplies a measured local
refinement scale for planning; it does not license extrapolation to untested
off-diagonal or domain cells.

## Claim ceiling

The two chains do not cover a neighbourhood, quadrant, or the full parameter
domain. This packet may establish only a local method-feasibility depth and
measured cost scale. It cannot certify uniform isolation and establishes no
projector, transport, seam, integer, topology, relative-class,
cutoff-convergence, v078, or experimental claim.
