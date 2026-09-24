# Reproducibility guide

There is no single repository-wide execution command or canonical root
environment. Historical deliveries and active review packets retain their own
instructions, dependencies, hashes, and claim boundaries. Choose the smallest
reproduction level that answers your question.

## Level 1: recreate the published figures

This performs no new scientific simulation. In a separate Python environment
with NumPy and Matplotlib, run:

```bash
python docs/visual-guide/render.py
```

The renderer verifies the hashes in
[`docs/visual-guide/sources.json`](visual-guide/sources.json), reads retained
v060/v062 JSON, and writes presentation images under
`docs/visual-guide/figures/`. See the
[figure instructions](visual-guide/README.md#recreate-the-figures).

## Level 2: inspect retained v062 evidence

Read these without executing a research engine:

1. [`research/v062/SUMMARY.json`](../research/v062/SUMMARY.json)
2. [`research/v062/REPORT.md`](../research/v062/REPORT.md)
3. [`research/v062/METHOD.md`](../research/v062/METHOD.md)
4. [`research/v062/COVERAGE.md`](../research/v062/COVERAGE.md)

The raw records are under [`research/v062/results/`](../research/v062/results/).

## Level 3: reproduce a historical packet

Enter through the packet's own README and environment records. Do not combine
dependency instructions from different versions or assume that a newer Python
environment preserves a historical numerical result. Preserve supplied
manifests and evidence before running any command that writes outputs.

Use the [archive map](ARCHIVE_MAP.md) to locate the intended packet.

## Level 4: inspect active draft evidence

Use an exact commit, not only a moving PR branch:

```bash
git fetch origin <commit-sha>
git switch --detach <commit-sha>
```

The exact snapshots current when this guide was written are listed in
[STATUS.md](STATUS.md). Follow only the instructions inside the bounded packet
being reviewed. A package verifier, test suite, or review controller may check
software and provenance without reproducing the scientific calculation.

## Level 5: execute physical certification work

This is specialist work and is not a first-time reproduction exercise. It
requires the exact case declaration, source and artifact digests, arithmetic
backend, finite budgets, gate semantics, and retained limitations. Do not begin
S1b or later work merely because an S1a file exists. The S1a hardening audit
closed for commit `654ef460…`; a later or modified packet needs its own exact
binding. S1b must also carry the remaining gate that connects the locked wheel
to the loaded extension and native-library files.

## Reporting a reproduction

Record at least:

- repository commit and packet/artifact digest;
- operating system, Python version, and exact dependency artifacts;
- command invoked and exit status;
- retained output and its digest;
- deviations from the declared environment;
- the strongest conclusion supported and explicit limitations.
