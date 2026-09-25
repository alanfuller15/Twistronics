# S1B-DIAGNOSTIC-001: bounded physical trial

Implementation: `853c00d3271d93d3d7721b73e65e0904a196d537`.
Approved protocol: `a4c1720401913946d776e707f2bcb690189bc942`.
Claude implementation PASS: PR #2 comment `5825941940`, recorded by Codex
in `5825958828`. This execution packet awaits its own independent audit.
No implementation, protocol, source lock or historical evidence was changed.

## Execution and retention

`RUN/RESULTS.json` reports `DIAGNOSTIC_COMPLETE`: all 56 configurations,
seven eigensolver starts and seven retained bases, 224 primary plus 224
same-backend repeat factorization starts. There are no interrupted calls,
pending configurations or verification errors. The seven bases were sealed
before any endpoint call. All required Gram bounds and exact repeated
evidence passed the offline checks.

The worker exited normally in **692.320273 seconds**, within the unchanged
1,200/1,260-second soft/hard deadlines. No signal was needed; the supervisor
reaped the worker and verified its process group was absent. Limits remained
one worker/native thread, 2 GiB address space and 256 MiB raw evidence.

The 1,137-record journal is 33,713,755 bytes, SHA-256
`60dcaae4ae7eeb62f704dad98f618f675fd572783e3e0f83a39da18f7aa14609`.
It is hosted losslessly as 17 gzip parts capped at 500,000 bytes, totaling
8,247,998 bytes,
compressed SHA-256
`d055d5407549545a88afdd5ab789adb9e88b48ee646f5be64d4e28651902d7b6`.
RESULTS and the supervisor receipt are copied byte-for-byte. A fresh
materialization reproduced all four raw files exactly, and check-only
verification reproduced RESULTS without numerical recomputation.

The physical HEADER contains the real implementation SHA, exact source
closure and redacted runtime provenance. Its digest is
`334fc9e0d81f22240f626791f105b42ede65cb945f34f5bdf60b59bf228e8107`.
The exact Python 3.12.14 build, NumPy native inventory, OpenBLAS binary and
SkylakeX architecture, threadpool inspector and all 42 wheel-native members
matched the reviewed host-bound lock. This is not cross-host byte agreement
or an independently implemented numerical verification.

## Fixed-specimen outcomes

All five historical-failure specimens reproduced their historical failed
endpoint sets in `original_128`. Both accepted controls passed that baseline.
Thus `baseline_divergence_detected=false` and
`control_mismatch_detected=false`, with no unresolved baseline flags.
All 35 comparisons of the five failure specimens against the seven other
arms are eligible under the frozen baseline-relative rules.

The table counts complete, repeat-consistent four-endpoint passes. It is
descriptive evidence for these specimens and arms only.

| Frozen arm | Historical-failure specimens passing / 5 | Accepted controls passing / 2 |
|---|---:|---:|
| `original_128` | 0 | 2 |
| `point_128` | 5 | 2 |
| `point_256` | 5 | 2 |
| `original_256` | 0 | 2 |
| `original_reverse_128` | 1 | 0 |
| `half_128` | 4 | 2 |
| `quarter_128` | 4 | 2 |
| `eighth_128` | 5 | 2 |

Reversal passed only `lower_left` among the historical-failure specimens
and failed both accepted controls. This does not set `control_mismatch`,
which the protocol defines for the original baseline, but must not be
hidden or described as an across-the-board improvement. The `upper_both`
specimen still failed at half and quarter radius and passed at eighth radius.
Higher precision alone did not produce four-endpoint passes for any of the
five historical-failure specimens at their original box size.

These observations do not identify a unique cause of historical failures.
An inconclusive interval factorization is not evidence of a nearby
eigenvalue, singularity or gap closure. Passing a point or nested box does
not certify the historical parent cell or change any coverage partition.

## Preserved startup error and environment repair

`STARTUP_ERROR_001/` retains a separate failed startup: the supervised
`-E -s` interpreter could not import `flint`, which had been installed only
in the user site. It exited before HEADER, CASE assembly, basis construction
or LDL. Its empty event log and error RESULTS replay exactly, with zero
counted work, seven unknown baselines and `EXECUTION_ERROR`. This is not a
successful scientific packet and was not overwritten or reclassified.

An import-only diagnostic reproduced `ModuleNotFoundError: No module named
'flint'` under the worker's isolation flags. The managed system site was not
writable. The repair used a local virtual environment with the same resolved
interpreter and system packages, installing the already-pinned wheel there
with `--no-index --no-deps --no-user`. The successful run then used that
environment's Python to launch the unchanged supervisor. All exact native
identity checks still applied. No gate, runtime lock or resource limit was
bypassed; no numerical attempt was retried and no extra arm was run.

## Offline reproduction

From the repository root, using Python's standard library only and a new
output directory:

```sh
python -B research/benchmarks/certification_s1b_diagnostic_001/verify.py \
  /tmp/s1b-diagnostic-reconstructed \
  --materialize research/benchmarks/certification_s1b_diagnostic_001/RUN \
  --implementation-commit 853c00d3271d93d3d7721b73e65e0904a196d537 \
  --check-only
```

The startup-error packet may be checked directly with the same verifier and
implementation SHA; its expected terminal status and CLI return code are
`EXECUTION_ERROR` and 1, respectively. This is a retained failed launch, not
a reason to discard its receipt or fabricate a HEADER.

`EXECUTION_MANIFEST.json` binds this note and exact membership of both
retained directories. Their inner manifests bind each package separately.

## Claim ceiling and next gate

Historical coverage remains **`29663/65536`**, and the historical coverage
packet remains **`INCONCLUSIVE_WATCHDOG_TIMEOUT`**. `DIAGNOSTIC_COMPLETE`
describes completion of these fixed comparisons, not scientific success.
No new coverage, whole-quadrant or full-domain uniform isolation, cutoff-b
or cutoff agreement, topology, transport, seams, cutoff convergence, v078
or experimental claim follows. No follow-on run or merge is authorized by
these results. The next step is Claude's separate executed-packet audit.
