# PARALLEL-DOMAIN-004 — slots 2 and 3 execution notes

- Implementation commit: `e12b74eb137a1623968b2bf459474942ffd55929` (detached from `claude/parallel-domain-execution`)
- Wheel: `python_flint-0.9.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl`, SHA-256 `376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76` (verified)
- Python 3.12.3, numpy 2.5.3, scipy 1.18.1, python-flint 0.9.0
- nproc: 4
- Controls (`test_controls.py`): PASS
- Start UTC: 2026-09-26T00:15:59Z
- End UTC: 2026-09-26T00:25:22Z
- Slot 2 exit status: 0
- Slot 3 exit status: 0
- Both slots ran concurrently on this machine; stderr was empty for both.

ATTEMPTS.ndjson is stored as gzip (compresslevel 9, mtime 0) split into consecutive 500000-byte `ATTEMPTS.ndjson.gz.partNNN` files; reassemble with `cat ATTEMPTS.ndjson.gz.part* | gunzip`.

| Shard | Raw log bytes | Raw log SHA-256 | gzip bytes | parts |
|---|---:|---|---:|---:|
| q00h2 | 8542565 | `df883d37a8ff030d733e053e6ba35c65fdbc1a13089dfb3570788dc5f09d9da3` | 2168314 | 5 |
| q01h2 | 988 | `d5004543a1e8f16990ca2b02a07cdc7416ce41a1bfb83395e367e30bead0f182` | 587 | 1 |
| q10h2 | 988 | `d918c9f02be861d44e88029ceb932702f8957e5f78e12c891fd602aa53b022c7` | 586 | 1 |
| q11h2 | 30339752 | `bdd86485ac98579fc0d928b24bd24038890d049e6b2c8c725b3422ff1af5af6b` | 7702684 | 16 |
| q00h3 | 7249234 | `9c16149f18ef8d37fdbb832b3588986a30b6410eeb85ae8cb989cb335689d0a2` | 1844219 | 4 |
| q01h3 | 988 | `58f1a8dc14bc139e67f2a4142aa6ab95c5b66fc152095f17432bc31a8cfb8570` | 585 | 1 |
| q10h3 | 988 | `fee5be40a9e512e0697a21865238826f5b4663bcc391c47c936eb567b5b51917` | 585 | 1 |
| q11h3 | 32600848 | `9df3348d27144e33c1079d1d943fc65f95d40a5c0e192c55601a2899af45c6bf` | 8289649 | 17 |
