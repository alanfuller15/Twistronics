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
and the reaped process group is absent. It also checks that a complete
malformed line is rejected and pins the exact hash encoding.

No physical Hamiltonian, factorization or parameter sweep is run by the test.
The physical evaluator must not be invoked until this implementation commit
receives an independent PASS. The later executed packet must also include the
separately requested third-congruence spot recomputation of accepted cells.
