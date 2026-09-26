# Batch 006 — depth-10 refinement restricted to unresolved cells

After batch 005, no frontier remains. Of [0,1]², 262021/262144 is accepted and
123 depth-9 cells are unresolved. This packet reopens **only those 123 cells**,
replacing each with its four depth-10 children (492 cells). No other cell is
refined, and accepted cells are inherited unchanged. A depth-10 child is
either accepted or left unresolved at depth 10. There is no further
subdivision, no change to the evaluator or its windows, and no retry.

This follows Alan's request to allow subdivision one level finer only inside
the narrow-gap strip. The restriction is to cells that already failed at
depth 9, which includes the strip and a few isolated cells in q00 and q11.

A heuristic estimate from retained records puts about 35 of the 49
batch-004 unresolved cells within reach at depth 10, if the D1 width scale
holds (about 105 meV / 2^d for upper windows, about 176 meV / 2^d for lower).
This is a planning heuristic, not a bound. For the strip core, the
fixed-specimen diagnostic suggests depth 11–12 may be needed.

Shards: 8 slots × 4 quadrants, with the frontier dealt round-robin by quadrant.
Each 4-core machine runs 4 slots. The merge raster is 1024×1024 at depth 10.
Claim ceiling as before.
