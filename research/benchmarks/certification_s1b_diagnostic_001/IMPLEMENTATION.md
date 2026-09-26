# S1B-DIAGNOSTIC-001 implementation audit packet

This is an implementation-only addition to the protocol approved by Claude in
PR #2 comment `5825600482`, binding protocol commit
`a4c1720401913946d776e707f2bcb690189bc942`. `SPEC.json`, `INPUTS.json`, the protocol
README and their historical manifest remain unchanged. Their “not implemented”
wording describes that earlier protocol-only snapshot. This addition supplies
the runner and controls; it does not authorize or report a physical execution.

The next gate is Claude's explicit implementation PASS binding this commit and
the approved protocol. No physical diagnostic, eigensolver on CASE data,
coverage run, merge or v078 correction was performed for this packet.

## Files and responsibilities

| File | Responsibility |
| --- | --- |
| `diag_common.py` | Frozen identities, complete source closure, exact configuration bindings, fsynced hash-chain journal |
| `engine.py` | Lazy physical engine; fresh affine assembly at each arm precision; exact retained basis; formed-matrix reversal; reviewed unpivoted interval LDL |
| `worker.py` | Seven counted basis starts, frozen arm order, primary/repeat ordering, deterministic admission, durable events and bounded synthetic fixtures |
| `runtime_identity.py`, `NATIVE_LOCK.json` | Exact wheel/native-member identities, observed Python/NumPy/BLAS build lock, mapped binaries, redacted provenance and offline checks |
| `supervisor.py` | One worker process group, launch-relative deadlines, TERM/KILL, reap/ESRCH receipt and timeout suffix handling |
| `verify.py`, `assessments.py` | Longest validated prefix, exact record/receipt schemas, rational pivot signs/counts, exact repeat equality, baseline comparisons and persistent nullable review flags |
| `package_io.py` | Exact output membership, deterministic gzip parts, bounded lossless materialization and manifest checks |
| `*_controls.py` | Synthetic arithmetic, mocked assembly, truth controls, mutations, full frozen-order replay, and real supervised SIGKILL controls |

## Preserved protocol boundaries

There are seven fixed specimens and eight fixed arms, in the approved arm-major
order. At most seven eigensolver starts and 224 primary plus 224 repeat LDL starts
are admitted. An interrupted start still consumes its budget. A failed primary
Gram calculation receives a fresh repeat Gram calculation and eight skipped
endpoint slots, with zero LDL starts. There are no retries, adaptive pivots,
extra arms, parameter sweeps or partition updates.

The physical engine sets the precision before every fresh coefficient assembly.
It forms the basis once per specimen using the specified 128-bit center midpoint
and serializes `.17g` values into exact reduced rational strings. The worker
rereads all seven durable basis records before the arm stage and reconstructs
fresh objects for primary and repeat stages. Reverse ordering permutes both axes
of the already formed K and Gram matrices; canonical unpermuted hashes must
match `original_128`. The repeat is a retention/reconstruction check using the
same backend, not an independent numerical method.

The runtime lock includes all 42 python-flint wheel-native members, the observed
complete NumPy binary inventory, Python interpreter identity, BLAS build and
threadpool inspector. Mapped native members are checked against those locked
identities; versions or count booleans alone cannot pass. The collector reads
only an explicit thread-variable allowlist and emits no hostnames, personal
paths or arbitrary environment variables. This locks one concrete runtime build;
a different build requires a reviewed lock change. Offline replay needs only
the standard library and does not load that runtime.

## Interrupted and invalid evidence

The verifier processes records in order and stops at the first invalid complete
record. It never repairs a complete line. Only the supervisor may remove an
incomplete final line, after a deadline termination and process-group reaping.
Unknown, partial and invalid baselines remain explicit. Already validated paired
failure evidence survives a later error. All seven baseline assessments and both
three-valued aggregate review flags appear under every terminal outcome,
including source errors, missing evidence, malformed logs and packaging errors.
An invalid source closure permits only pinned-identity unknown assessments.

Historical failure specimens that pass the reconstructed baseline are marked
`BASELINE_DIVERGENCE`; changed endpoint sets or failure types are excluded from
historical mechanism comparisons. An accepted-control mismatch remains visible
through watchdog and error precedence. A completed diagnostic can contain
divergence or inconclusive arms; completion is not a scientific success claim.

`RESULTS.json` lists all pending configurations and the interrupted counted call.
Check-only replay compares regenerated results and manifest bytes without writing.
Unexpected files, symlinks, stale manifests and invalid receipt identities fail.
If an invalid directory cannot receive a valid manifest, error RESULTS are still
written and the directory remains invalid; it is never silently reblessed.

## Retained implementation validation

`CONTROL_RESULTS.json` records the completed control families and their scope.
`IMPLEMENTATION_CONTROLS/` retains lossless hosted logs, results and receipts for
the complete synthetic run, a mixed divergence/control/Gram fixture, and a real
supervised SIGKILL after all seven synthetic baselines. The all-zero implementation
commit in these records means unpublished synthetic test source, not an execution
against the protocol commit. Each header binds the exact implementation source
manifest. This avoids a self-referential commit hash in prepublication evidence.

`IMPLEMENTATION_MANIFEST.json` binds the implementation and its transitive source
inputs. `CONTROL_MANIFEST.json` separately binds control reports and retained
control artifacts, avoiding a source/report hash cycle. Source manifests do not
authenticate themselves: the requested audit binds them to the published commit.

Reproduce the nonphysical controls from this directory:

```sh
python -B assessment_controls.py
python -B engine_controls.py
python -B package_controls.py
python -B runtime_controls.py --wheel /path/to/the/locked/python_flint.whl
python -B integration_controls.py --output /tmp/diagnostic-controls.json
```

`engine_controls.py` uses small synthetic matrices and mocked assembly/eigensolver
objects. Runtime controls import native libraries to hash their actual binaries;
they do not assemble the CASE, call an eigensolver or factor the physical model.
Integration controls select only the synthetic evaluator. They include a 12/13
second synthetic watchdog override; physical overrides are rejected and remain
1200/1260 seconds, one worker/native thread, 2 GiB address space and 256 MiB raw
evidence. No physical-run command is part of this validation sequence.

To inspect a retained control without numerical imports:

```sh
python -B verify.py /tmp/diagnostic-control-replay \
  --materialize IMPLEMENTATION_CONTROLS/sigkill \
  --implementation-commit 0000000000000000000000000000000000000000 \
  --allow-test-mode --check-only
```

## Evidence ceiling

Offline verification checks exact rational records, ordered inputs, source and
runtime bindings, Gram bounds and signed-pivot/count consistency, and repeated
evidence equality. It does not independently recompute the physical matrices or
prove a different interval algorithm. Synthetic controls establish implementation
behavior only. A zero-containing unpivoted LDL pivot alone proves neither a
nearby eigenvalue, singularity nor gap closure.

Historical hard-quadrant coverage remains `29663/65536` with
`INCONCLUSIVE_WATCHDOG_TIMEOUT`. These diagnostic arms never add coverage, even
if a point or nested box passes. No whole-quadrant or full-domain isolation,
cutoff-b agreement, topology, transport, seams, cutoff convergence, v078 or
experimental claim follows from this packet.
