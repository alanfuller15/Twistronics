# PARALLEL-DOMAIN-003 — host 1 execution notes

- Host: 1
- Implementation commit: 32ea5246 (`32ea5246b9bc34b1602a1cf705d2df81fc47e96d`), branch `claude/parallel-domain-execution`
- Wheel: `python_flint-0.9.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl`, SHA-256 `376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76` — verified
- Python 3.12.3; numpy 2.5.3; scipy 1.18.1; python-flint 0.9.0
- `nproc`: 4
- Synthetic controls (`test_controls.py`): PASS, 0 physical calls
- Run start (UTC): 2026-09-26T00:00:11Z
- Run end (UTC): 2026-09-26T00:06:25Z
- Exit status: 0 (stderr empty)
- Run stdout: `RUN_STDOUT.json`

## Packaging

Each shard's `ATTEMPTS.ndjson` is stored as gzip (compresslevel 9, mtime 0), split into
consecutive 500000-byte parts `ATTEMPTS.ndjson.gz.partNNN`. Reassemble with
`cat ATTEMPTS.ndjson.gz.part* | gunzip > ATTEMPTS.ndjson`. Round-trip verified before commit.

| shard | raw bytes | raw SHA-256 | parts |
|---|---|---|---|
| q00h1 | 26358541 | f2d234351b5f62e2ddc8d2508b6bdd89e0f11e971b7e117ed38559c6229a14e6 | 14 |
| q01h1 | 32354466 | c7ebd27468a73bc2c8f7922e4be063a62b1df42c6957150961567b1953630fc1 | 17 |
| q10h1 | 5291842 | 44338d6f6e032b79188ff428241cf4d40cf2b6369aab184fa8c32f8a7e920c72 | 3 |
| q11h1 | 36031064 | 8f7482b7a97fc2f8b4ad6e9b088f559bb045bfa8cef287c3e68ac2c895b16d8f | 19 |

`WORKER.log` files are empty (0 bytes) as produced by the run.
