# Four workers toward full-domain coverage

Status: implementation candidate; independent pre-execution review pending.
Alan requested replicating the successful bounded engine across more quadrants
and working toward full-domain coverage on 25 September 2026 UTC.

This additive packet uses four isolated processes on one host. Each owns one
quarter of the literal coordinate square [0,1]². q00, q01 and q10 start with
complete depth-4 tilings. q11 resumes the exact retained 590 accepted, 40
unresolved and 391 frontier cells. Existing accepted cells are never rerun.
The imported interval engine is unchanged. Precision is set to 128 bits before
coefficient assembly. Every attempted cell gets its own local windows and
17-digit/10-digit congruences. No symmetry between quadrants is assumed.

Each queue uses ascending (depth, ix, iy), prioritizing larger areas. Failed
cells split into four children up to depth 9; depth-9 failures remain unresolved.
This changes scheduling from the prior focused run, not acceptance criteria.
Each worker is capped at 64 attempts, 512 endpoint factorizations, one native
thread, 2 GiB address space and 600 seconds plus 10 seconds termination grace.
Total admission ceilings are 256 attempts, 2,048 factorizations and 8 GiB worker
address space. No worker retries or spawns children. A supervisor reaps every
process group, binds the log and stderr, and retains receipts. A failed worker
blocks the entire aggregate; surviving records remain available for diagnosis.

Every durable attempt is fsynced before its queue transition. Recovery discards
only a final non-newline fragment. Offline replay validates each record, exact
queue order, window widths, bands, pivot counts/signs, Gram bounds, and both
congruences. A complete depth-9 occupancy raster independently rejects duplicate
cells, ancestor overlap, out-of-quadrant cells and missing area. Four closed
quadrants share measure-zero edges; area accounting counts interiors once.
Boundary periodicity/sewing is a separate research obligation.

The baseline retained accepted area is 29663/262144 = about 11.3155% of this
full square. This is precisely the old 29663/65536 quadrant fraction divided by
four. It is a conservative aggregation of the named packet, not an inventory
of every earlier isolated feasibility cell. Count, area and unresolved regions
are reported independently. Complete accounting of accepted/frontier/unresolved
cells is not complete accepted coverage. A true gap closing could prevent the
selected external-isolation condition from holding everywhere; it must then
be mapped and characterized, not relabeled accepted.

## Execution and replay

After Claude reviews the exact published implementation commit with PASS,
retain a review receipt containing reviewed_commit, status and review_url.
Run `parallel.py run --output NEW_DIRECTORY --implementation-commit SHA
--wheel LOCKED_WHEEL --review-receipt RECEIPT_JSON`.
Run `parallel.py verify` with the same output/commit for read-only replay.
`--synthetic` is only a process/partition control and reports no physical
coverage. Production execution has no deadline overrides.

A later round must freeze the new partition and budget in a separate packet.
This first run is bounded, not a persistent cloud service or purchased cluster.
