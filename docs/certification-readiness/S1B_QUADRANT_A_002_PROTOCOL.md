# S1b cutoff-a hard-quadrant continuation protocol 002

**Status: PROTOCOL FROZEN / INDEPENDENT REVIEW PENDING / NOT EXECUTED.**

This is a protocol-only continuation from `S1B-QUADRANT-A-001` at commit
`16c864c9d0d0c545f4369567e81bfdbc826953d9`. It adds no runner, changes no
scientific source, performs no factorization, and creates no new coverage
evidence. Implementation and execution are forbidden until an independent
review explicitly passes this exact protocol commit.

## Frozen source state

The predecessor's `PARTITION.json` is bound by SHA-256
`2bbc19927b996e6d3b43ed9c17fe1d3b92f029bd1866cc031390b76d5814e000`.
Its immutable accepted set covers `23/64` of `[1/2,1]^2`; its exact 437-cell
frontier covers the remaining `41/64` (73 depth-5 and 364 depth-6 cells).
Any binding mismatch is an execution error, not permission to reconstruct or
substitute a frontier.

## Deterministic continuation order

The continuation uses the exact retained frontier and a deterministic
best-first queue. For each cell `(depth, ix, iy)`, compute exactly the
L-infinity distance from the closed dyadic cell to `(23/32,23/32)`. Compare
exact rational distances by cross multiplication. The ascending priority key
is:

1. exact distance to the fixed target;
2. negative depth (deeper first at equal distance);
3. `ix`;
4. `iy`.

An inconclusive cell below depth 9 contributes four children in x-bit then
y-bit low-first order, after which the entire work queue is sorted by the
same key. Accepted cells are terminal. Depth-9 inconclusive cells enter the
unresolved terminal set. Every attempted record retains its key, and the
verifier must prove it was the unique current minimum under the complete
tie-break rule.

This order is deliberately targeted planning, not a scientific inference.
The target is frozen from the retained hard-window evidence; it does not
assume that the neighbourhood will certify.

## Bounded resources and real watchdog

The round may attempt at most 1,024 new cells, 4,096 primary
factorizations, 4,096 recomputations and 8,192 total factorizations. It uses
one physical case, cutoff `a`, one worker, 128-bit arithmetic, zero parameter
sweeps, zero retries and at most 2 GiB of address space.

The worker has 2,700 seconds. A separate supervisor must create the worker in
a new process group, send `SIGTERM` to the entire group at 2,700 seconds, and
send `SIGKILL` to the entire group at the 2,760-second hard deadline. An
in-process timer alone is insufficient. Timeout is retained as
`INCONCLUSIVE_WATCHDOG_TIMEOUT`; only fsync-complete records may survive. The
supervisor receipt, termination reason and elapsed monotonic times are
mandatory evidence.

The 1,024-cell cap is four times the predecessor's cap. The 2,700-second
worker ceiling is the predecessor's 613.7-second observation multiplied by
four with bounded headroom. These are deterministic ceilings, not a forecast
of completion or a claim that the physical case will pass.

## Fail-closed verification

The future verifier must bind this exact protocol and predecessor bytes,
replay the exact priority queue, check every attempt and both congruences,
enforce all count/time/memory caps, validate the supervisor receipt, and
prove that accepted, max-depth-unresolved and unprocessed-frontier cells are
pairwise disjoint and exactly cover the frozen quadrant. Exact rational areas
must sum to one. Missing, partial, duplicated, stale or substituted evidence
is rejection or an inconclusive/error outcome—never acceptance.

## Claim ceiling

Any future result is limited to bounded cutoff-a coverage of the hard
quadrant. It cannot by itself establish the whole quadrant unless the exact
partition does so, and it never establishes full-domain uniform isolation,
cutoff-b agreement, topology, projector transport, seam composition, cutoff
convergence, v078 correctness or an experimental claim.

## Independent review questions

1. Are the predecessor bindings and initial terminal/frontier state exact?
2. Is the priority key total, deterministic and replayable without floating
   comparisons?
3. Do the caps and separate process-group watchdog fail closed?
4. Does the required verifier establish a disjoint complete partition rather
   than only an area identity?
5. Is the claim ceiling preserved, with no execution authorized by this
   protocol-only commit?
