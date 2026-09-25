# S1B-QUADRANT-A-002 implementation candidate

Status: **IMPLEMENTATION REVIEW PENDING / PHYSICAL EXECUTION NOT AUTHORIZED**.

This directory implements the protocol approved at
`8c86166a954b870145858ff0b783a5983fd90521`. It does not contain physical
results. `common.py` freezes exact priority, line hashing, replay and partition
rules. `worker.py` is single-process and never spawns children. `supervisor.py`
creates and owns the worker process group, enforces both deadlines, reaps it,
proves the group is empty and atomically writes the receipt. `verify.py`
reconstructs all state from the exact predecessor bytes and durable log.

The hash convention is unambiguous: `record_sha256` hashes the canonical JSON
object with that field omitted; `previous_record_sha256` hashes the exact prior
canonical line bytes excluding the newline. The header uses the same rule.
Raw `ATTEMPTS.ndjson` is retained. Gzip parts are derived only after replay.

`test_faults.py` is synthetic only. It forces a real SIGKILL after a partial,
fsynced attempt fragment, then verifies that the fragment is discarded, the
attempt is not counted, the selected cell remains in the exact 437-cell
frontier, the 83-cell accepted prefix is unchanged, the timeout label wins,
and the reaped process group is absent. The supervisor retains pre/post-trim
byte counts and removes the test-only readiness marker before packaging. The
suite re-binds the receipt before proving that a complete malformed record is
rejected by its record hash, exercises empty-queue-before-cap classification,
retains a complete 1,024-attempt synthetic cap replay, and pins the exact hash
encoding.

The physical verifier now binds every evidence record to the selected queue
cell and exact rational box, cutoff-a dimension 196, 128-bit precision,
17-digit primary and 10-digit recomputation, both recorded certified flags,
the frozen lower/upper inertia counts 97 and 99, and the frozen `1/100000 meV`
target. The full runtime provenance object is retained in the header, hashed,
and checked against `WHEEL_LOCK.json`, including wheel SHA-256, FLINT 3.6.0,
loaded extension, mapped native libraries, and `/proc/self/maps` gates.

Verification has two explicit modes. A fresh supervisor output contains only
the raw log and receipt and is packaged once. `verify.py --check-only` then
recomputes all derived bytes without writing and requires the exact final file
set; stale, substituted, partial, or unexpected files fail closed. A missing
`RESULTS.json` after supervisor/verifier failure means `EXECUTION_ERROR`.
Fault injection and deadline overrides are synthetic-only. The supervisor
freezes `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` before the worker
starts, and receipt timing/mode/exit consistency is independently checked.

No physical Hamiltonian, factorization or parameter sweep is run by the test.
The physical evaluator must not be invoked until this implementation commit
receives an independent PASS. The later executed packet must also include the
separately requested third-congruence spot recomputation of accepted cells.
