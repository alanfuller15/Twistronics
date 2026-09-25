# S1B-QUADRANT-A-002 executed packet

Status: **INCONCLUSIVE_WATCHDOG_TIMEOUT**.

This is the physical cutoff-a execution authorized after independent PASS on
implementation commit `c7b2ae26a12dce97b64eb54ed2a406c6013e091c`, under approved protocol
`8c86166a954b870145858ff0b783a5983fd90521`.

The separate supervisor stopped the one-worker run at its frozen 2,700-second
soft deadline and reaped the process group. The retained prefix contains 714
attempts, 2,856 primary and 2,028 recomputation factorizations (4,884 total).
It adds 507 accepted cells. The complete derived partition contains 590
accepted cells, 391 unprocessed frontier cells and 40 depth-9 unresolved cells.
Its exact quadrant-area fractions are 29663/65536 accepted, 35833/65536
frontier and 5/8192 unresolved, summing to one.

`verify.py --check-only` passed against the original fresh packet, including
the receipt, runtime provenance, caps, hash chain, exact priority replay,
partition and byte-exact derived artifacts. `N4_SPOT_RECOMPUTATION.json` is a
separate deterministic third-congruence check of five accepted cells. It uses
LAPACK `evx`, a seeded non-orthonormal perturbation, and 12-digit decimal
rounding. All 20 interval-LDL factorizations certify the retained 97/99 inertia
counts, including two depth-9 cells. Running `n4_spot_recompute.py` twice
produced byte-identical output with SHA-256
`f4bf8ac283e8eb7a771e628fc0f0b10073e14ba955a2aa72d60f52de0e6d8287`.

## Hosted log representation

The exact raw `ATTEMPTS.ndjson` is 196,613,136 bytes, above GitHub's 100 MiB
single-blob limit, and therefore is not stored as a normal Git blob. Its full
lossless canonical gzip representation is retained here as the 101 fixed parts
listed and hashed in `RESULTS.json`. The raw-log SHA-256 is
`328b42afbdb508b631fbccbaf13afbdf5197824ab97822a7c5a4aa755b674679`.

From the repository root, reconstruct a byte-identical fresh packet and run
the exact check-only verifier with:

```sh
python research/benchmarks/certification_s1b_quadrant_a_002/materialize_and_verify.py /tmp/s1b-quadrant-a-002-review
```

This representation accommodation changes no evidence bytes: the script
checks every hosted part, decompresses the exact raw log, checks its size and
SHA-256, and then invokes the reviewed verifier. The original execution
directory contained the literal raw log and passed check-only replay before
these hosted files were assembled.

## Claim ceiling

This packet is bounded continuation evidence only. The remaining frontier and
unresolved cells make the result inconclusive. It does not establish coverage
of the whole quadrant, uniform isolation, the full domain, cutoff-b or cutoff
agreement, topology, transport, seams, cutoff convergence, v078, or any
experimental claim.
