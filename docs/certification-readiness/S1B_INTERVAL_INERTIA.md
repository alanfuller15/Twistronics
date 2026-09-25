# S1b: bounded interval-inertia attempt

Parent `654ef460af1dc9594457feff37cf04d628f7d558`. The parent S1a
hardening packet passed independent review before this physical S1b attempt
began.

## Retained result

Status: `INCONCLUSIVE` on the predeclared wall budget.

The worker used the frozen breadth-first dyadic order, the declared 3/8 and
5/8 rational shift candidates, 128/256/512-bit Arb arithmetic, and unpivoted
interval LDL inertia. It attempted 27 cells and 324 factorizations for cutoff
`a`, reaching depth 3, and 8 cells and 96 factorizations for cutoff `b`,
reaching depth 2. No cell met the complete closed-cell acceptance test before
the compute caps. The retained accepted/unresolved partitions cover both
declared parameter rectangles exactly.

The replay-free verifier checked 93,072 signed interval pivots from all 420
factorizations. Every retained certified inertia record has a zero-excluding
pivot sequence whose signs reproduce its recorded negative count. The verifier
also checks the cell, factorization, depth, case, and no-sweep caps; source and
manifest digests; and the result claim ceiling.

Runtime checking binds the exact locked python-flint wheel, all 42 installed
native members, the loaded `pyflint` extension, and the three mapped native
libraries. The public retained record omits executor-local paths and
per-library identities; it keeps the exact wheel lock, versions, counts, and
binding flags. Exported bounds are exact rational endpoints derived from each
Arb ball's exact binary midpoint and radius.

## Interpretation and next gate

The bounded sufficient method did not certify complete uniform external
isolation. This is not evidence that a physical gap closes. It establishes no
projector, transport, seam, integer, topology, relative class,
cutoff-convergence, or experimental claim.

Any next S1b round requires independent review of this exact packet and a new
bounded method proposal. The present run must not be extended by silently
raising its caps or changing its pivot/shift policy.
