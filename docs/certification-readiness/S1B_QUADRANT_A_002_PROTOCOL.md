# S1b cutoff-a hard-quadrant continuation protocol 002

**Status: PROTOCOL AMENDED / INDEPENDENT REVIEW PENDING / NOT EXECUTED.**

This protocol-only amendment resolves M1 and M2 from Claude review
`issuecomment-5821711346` of commit `35664fc7f3a028a7b8d32848bc719e9fc01b8b74`.
It adds no runner, changes no scientific source, performs no factorization and
creates no new coverage evidence. Implementation and execution remain
forbidden until an independent review passes this exact amendment commit.

## Frozen source and order

The predecessor remains `S1B-QUADRANT-A-001` at
`16c864c9d0d0c545f4369567e81bfdbc826953d9`. Its `PARTITION.json` SHA-256 is
`2bbc19927b996e6d3b43ed9c17fe1d3b92f029bd1866cc031390b76d5814e000`:
83 accepted cells cover `23/64`; the exact 437-cell frontier covers `41/64`.
The predecessor accepted array is the byte-identical prefix of any combined
accepted array, and replay begins from the exact predecessor frontier.

The exact-rational best-first key is unchanged: L-infinity distance from the
closed dyadic cell to `(23/32,23/32)`, then negative depth, `ix`, and `iy`.
An inconclusive cell below depth 9 adds its four children; accepted cells and
depth-9 inconclusive cells are terminal.

## Frozen status mapping and precedence (M1)

The precedence is total, high to low:

1. `EXECUTION_ERROR` for any source/evidence binding mismatch, malformed or
   hash-invalid durable record, worker exception, memory-limit failure,
   unexpected worker exit, supervisor crash, missing/invalid receipt,
   nonempty process group after reap, or replay/partition/package failure.
2. `INCONCLUSIVE_WATCHDOG_TIMEOUT` only when a valid receipt proves the
   deadline signal, reap and empty-group check, and the surviving durable log
   prefix verifies.
3. `INCONCLUSIVE_RESOURCE_CAP` when admission before the next queue pop lacks
   room under a frozen cell or factorization cap.
4. `CERTIFIED_CUTOFF_A_HARD_QUADRANT_COVERAGE` only after normal verified
   completion with both derived unresolved and frontier sets empty.
5. `INCONCLUSIVE_BOUNDED_COVERAGE` only after normal verified queue exhaustion
   with a nonempty depth-9 unresolved set and an empty frontier.

Anything else is `EXECUTION_ERROR`. A partial resource-capped or timed-out
round can never receive a `CERTIFIED_*` status.

## Crash-safe log and deterministic recovery (M2)

The worker writes `ATTEMPTS.ndjson` as canonical, newline-terminated JSON.
The header binds the approved protocol, predecessor bytes, implementation and
runtime provenance. Attempt records have contiguous sequence numbers, the
exact cell and priority key, factorization counts, complete interval evidence,
outcome, and a SHA-256 chain back to the header.

The selected cell is not durably removed from the queue until its complete
record is appended, the file is flushed and fsynced, and the parent directory
is fsynced. Only then may the queue transition be committed and another cell
be selected. On recovery, only a final non-newline fragment may be discarded;
a complete malformed or hash-invalid line is an execution error. The worker
streams records and does not retain the complete evidence set in memory.

The supervisor or offline verifier—not the worker—replays the predecessor
state and the durable log. Each record must be the current minimum priority
cell. A killed in-flight cell without a durable record remains in the
frontier. Counts come only from durable records. Accepted, unresolved and
frontier sets are derived by replay, never trusted from worker output.

After the worker group is reaped, the supervisor writes its receipt atomically
and fsyncs it and its directory. The receipt binds the protocol,
implementation and durable log; records monotonic times, signals and exit
status; and proves `killpg(group, 0)` returned `ESRCH`. The worker may spawn no
children and may not create another session. A missing receipt is an execution
error. Gzip parts are produced only after the durable log verifies.

## Resources and verification

The unchanged caps are 1,024 new cells, 4,096 primary, 4,096 recomputation
and 8,192 total factorizations; one worker; zero retries; 2 GiB address space;
2,700 worker seconds; SIGTERM then SIGKILL by 2,760 seconds. Admission reserves
the worst-case four primary and four recomputation factorizations before each
pop.

Verification binds every source, predecessor array and durable record; replays
every priority choice; derives the combined partition; checks the 83 accepted
cells as a byte-identical prefix and the exact 437-cell starting frontier; and
proves no duplicate or ancestor relation plus exact rational area one. This is
a disjoint complete-partition proof, not merely an area identity.

## Claim ceiling

Any future result is limited to bounded cutoff-a hard-quadrant coverage. It
does not establish full-domain uniform isolation, cutoff-b agreement,
topology, projector transport, seam composition, cutoff convergence, v078
correctness or an experimental claim.

## Review questions

1. Is the status mapping total and does its precedence prevent partial
   evidence from receiving a certified label?
2. Does the write-ahead hash chain make every durable queue transition
   replayable, leaving an interrupted cell in the frontier?
3. Are the post-reap receipt, empty-group check and verified-log-only packaging
   sufficient to fail closed after timeout?
4. Are the predecessor arrays, caps, exact queue and claim ceiling unchanged?
5. Does this remain protocol-only with implementation and execution gated?
