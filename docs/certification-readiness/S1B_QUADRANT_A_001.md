# S1b cutoff-a hard-quadrant coverage round 001

This packet executes one bounded adaptive coverage round for cutoff `a` on the
hard quadrant `[1/2,1]^2`. It uses breadth-first dyadic subdivision through
depth 9 and the independently reviewed direct affine-cell interval-inertia
method retained in `certification_s1b_method_004`.

Every accepted cell must pass both the 17-digit primary congruence and the
independent 10-digit recomputation. The packet retains every attempted cell,
every accepted cell, every max-depth unresolved cell, and the complete
unprocessed frontier. Its verifier reconstructs the exact BFS queue and proves
that the three terminal sets are a disjoint, complete partition of the frozen
quadrant.

The round is limited to one pinned physical case, cutoff `a`, 128-bit
arithmetic, depth 9, 256 attempted cells, 1024 primary factorizations, 1024
recomputation factorizations, 2048 total factorizations, one worker, a 900
second admission cap, a 930 second watchdog, and 2 GiB of address space.
Exhaustion is retained and reported fail-closed as an inconclusive result.

The claim ceiling is bounded cutoff-a quadrant coverage only. This packet does
not establish full-domain uniform isolation, cutoff-b agreement, topology,
transport, seam composition, cutoff convergence, or experimental claims.

## Retained result

The round exhausted the frozen 256-cell cap after 613.7325 seconds. Of the 256
attempted cells, 83 passed both the primary and independent recomputation. They
cover exactly `23/64` of the frozen quadrant. No cell reached depth 9; the
complete retained frontier contains 437 cells (73 at depth 5 and 364 at depth
6) and covers the remaining `41/64`.

The result is therefore `INCONCLUSIVE_BOUNDED_COVERAGE`, not a quadrant or
uniform-isolation certificate. The packet records 1024 primary and 332
recomputation factorizations (1356 total), remains within every deterministic
cap, and preserves the complete disjoint accepted/frontier partition for the
next bounded continuation.
