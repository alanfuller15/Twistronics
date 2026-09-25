# Parallel full-domain continuation 002

Alan authorized continued engine runs without waiting for audit acceptance on
25 September 2026 UTC. This additive runner records that change explicitly in
EXECUTION_AUTHORITY.json. It does not fabricate a PASS or change the prior
reviewed runner. Independent review status remains separate from execution.

Four processes resume the exact completed packet001 partition: 702 accepted,
903 frontier and 40 depth-limit unresolved cells. Accepted cells are never
rerun, and unresolved cells remain distinct. Each worker attempts at most 128
queued cells, prioritizing ascending (depth,ix,iy), with the unchanged reviewed
method004 evaluator. Total caps are 512 attempts / 4096 factorizations, 600
seconds plus 10 seconds grace per worker, 2 GiB and one native thread each.

The predecessor's hash-chain logging, replay and full-square occupancy proof
are retained. Explicit factorization caps and mode derivation from actual log
headers incorporate non-blocking observations from the first implementation
review. Source bindings, runtime provenance, exact cell evidence, process-group
cleanup and fail-closed error handling remain mandatory.

Baseline accepted area: 105951/262144 (40.417099%) of [0,1]² at cutoff a.
This bounded batch adds local cell-isolation evidence, not topology, seams,
cutoff convergence or experimental validation. No audit acceptance is claimed.

Run parallel.py run --output NEW_DIRECTORY --implementation-commit LOCAL_SHA
--wheel LOCKED_WHEEL. Replay with parallel.py verify using the same output and
commit. Physical output remains auditable even though audit no longer blocks
execution. A later round must bind its own predecessor partition and limits.
