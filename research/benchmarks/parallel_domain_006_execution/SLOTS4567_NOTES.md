# PARALLEL-DOMAIN-006 — slots 4, 5, 6, 7 execution notes

- Implementation commit: `9cfa9129de73c25ce6d5c3f7bf18919836bffbba` (verified with `git rev-parse HEAD` before the run)
- Wheel: `python_flint-0.9.0-cp310-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl`, SHA-256 `376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76` (verified)
- Python: 3.12.3; numpy: 2.5.3
- nproc: 4
- Controls (`test_controls.py`): PASS (physical_calls 0)
- Start UTC: 2026-09-26T00:39:23Z
- End UTC: 2026-09-26T00:42:46Z

## Exit statuses

| slot | exit |
|---|---|
| 4 | 0 |
| 5 | 0 |
| 6 | 0 |
| 7 | 0 |

stderr was empty for all four slots.

## Raw ATTEMPTS.ndjson logs

Stored as gzip (compresslevel 9, mtime 0) split into 500000-byte parts; concatenate `ATTEMPTS.ndjson.gz.part*` in order and gunzip to recover the raw log. Round trip verified before commit.

| slot | shard | raw bytes | raw SHA-256 | gzip bytes | parts |
|---|---|---|---|---|---|
| 4 | q00h4 | 2195989 | `737b2d2530ab89bcdbeab222cb6fb02b040e4cb0d393b47e8d631ff88ce0b60e` | 557455 | 2 |
| 4 | q01h4 | 988 | `2522f2f5c1f90d559c84549a11c8c0eeb208f393cda0f278e608f82d88cdd5fa` | 584 | 1 |
| 4 | q10h4 | 988 | `8829a3b776b141b5fa1bd205dac908d70675b53f3e5dd938a29d78b002560d22` | 585 | 1 |
| 4 | q11h4 | 16039903 | `05a46da6dcde02a1e87e57c9e5361d7f5d0ea2edd6a8a252eff7545717c9804b` | 4084225 | 9 |
| 5 | q00h5 | 2391342 | `475ff2d5b4de23dac781c4a3fab0e7c2c4290b4ee6aa01bbbec31cf218591501` | 607669 | 2 |
| 5 | q01h5 | 988 | `abfb8e7e436c343527025a0a9807056f487a5b1444e3e80931126093d14263b8` | 585 | 1 |
| 5 | q10h5 | 988 | `b1316df0442746498c5b85472c6e0863bf1f991be2c41b0c506c756b4902aa4e` | 585 | 1 |
| 5 | q11h5 | 15843256 | `54e47907896819ad4cdd9a765389836fefdc1a08dca6c517710d647b1905cbe7` | 4034479 | 9 |
| 6 | q00h6 | 2602172 | `36503fdda740df11ba1ff34168150640ced3b74c64b4f02fa054eb67729f6260` | 662797 | 2 |
| 6 | q01h6 | 988 | `95e04a34744fbe9b17a2e622dc209add066ec5ae53779b08c7a776753910e771` | 585 | 1 |
| 6 | q10h6 | 988 | `950815ffd3975a07f5cecaf4170f52ff6898bdc8610f795c2c78b94995141107` | 585 | 1 |
| 6 | q11h6 | 15483863 | `3be6caf9b2697b06d523dc9ce9ad86523c8ab81e40a263390b7776797061cee3` | 3942618 | 8 |
| 7 | q00h7 | 2782179 | `710ae9de0c50ab3c7d49a2d28b029f33f4c481ea700ebf9ef44008c451666059` | 709036 | 2 |
| 7 | q01h7 | 988 | `7289111f3ba150c5e3e38c6d9f955d17c2c34860889669f3897e13ebfc8418df` | 585 | 1 |
| 7 | q10h7 | 988 | `8ae301f6ec22d8a5e2d5432eadcbdc480fb6589466432538582b77473e5337b4` | 584 | 1 |
| 7 | q11h7 | 13816394 | `4787eec8deb34fc4f1f4868e82dc1a1b1e5f612e447d707f630adc5ea9efe2d8` | 3512618 | 8 |
