# Twistronics research

Audited numerical toolkit and recorded research through **our v053**. This repository preserves the complete reconciled release, including the partner logs, both Hamiltonian engines, tests, measurement scripts, numerical results and frame checkpoints.

Start with [current report](research/v053/REPORT.md), [accepted coverage ledger](research/v053/LEDGER.md), [team share](research/v053/TEAM_SHARE_v053.md), and [reproduction instructions](research/v053/README.md).

The latest batch completes a sampled preparation frame replay: 76 accepted states in both engines at N=4/N=6, all SAME, with four root/relative-frame joins into v044. Eighteen frame/checkpoint/publication tests and a production stop/resume check pass. The **separate lower unlink collision remains open**; see [next sequence](research/v053/NEXT_SEQUENCE.md).

## Layout

- `research/v053/`: latest code, protocol, reports, tests and raw checkpoints.
- `research/prior_our_v052/`: complete prior delivery, retaining earlier batches and incoming partner packages.
- `research/MANIFEST.json`: hashes of the original release contents.
- `RELEASE.json`: provenance of the ZIP used to initialize this repository.

To reproduce, follow the instructions inside the selected batch directory. Preserve its relative paths: historical records are retained in their delivered locations so source hashes, frame anchors and report rebuilding remain reproducible. Run at most two numerical workers with single-thread BLAS.

These are self-tested results for a declared numerical model. Finite sampling is not an interval proof, infinite-cutoff bound or physical-bilayer validation. No new license or third-party permissions are assigned by this repository snapshot.
