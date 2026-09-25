# Start here

This page is the shortest reliable path into the Twistronics repository.

## The project in one paragraph

Twistronics studies selected band crossings in a continuum model of strained
twisted bilayer graphene. The project follows numerical nodes in momentum
space, compares charge relationships under declared frame conventions, and
retains software and review evidence for each bounded claim. It is an active
computational research record. It is not an experimental data set, a complete
proof of a material's topology, or a single polished software package.

## Pick your path

### I want the accessible scientific story

1. Explore the [interactive field guide](interactive-guide/README.md): rotate
   the layers, inspect coordinate scales and select retained samples.
2. Read the [illustrated research guide](visual-guide/README.md) for the
   historical v060/v062 narrative.
3. Use the [glossary](GLOSSARY.md) when a version or evidence label is unclear.
4. Read [current status](STATUS.md) before treating any result as current.

The visual guide is intentionally centered on the retained v060/v062 evidence.
It is the best introduction, but it is a historical snapshot rather than the
complete current research frontier.

### I want to evaluate the evidence

1. Read the [status and claim boundaries](STATUS.md).
2. For v062, read the [report](../research/v062/REPORT.md),
   [method](../research/v062/METHOD.md), and
   [coverage ledger](../research/v062/COVERAGE.md).
3. Follow the [reproducibility ladder](REPRODUCIBILITY.md).
4. Use exact commit links for draft work. A moving branch name is not an
   evidence binding.

### I want to understand the active research

The active public work is split across draft pull requests. They are evidence
under review, not extensions already accepted into `main`:

- [PR #2](https://github.com/alanfuller15/Twistronics/pull/2): migration-contract
  review and research-status material.
- [PR #5](https://github.com/alanfuller15/Twistronics/pull/5):
  certification-readiness and bounded physical S1a assembly work.
- [PR #6](https://github.com/alanfuller15/Twistronics/pull/6): deterministic
  review and packaging mechanics for the v079p acceptance line.

The [status page](STATUS.md) records the exact reviewed heads used for this
learning snapshot and explains what each track does and does not establish.

### I want to contribute

Read [CONTRIBUTING.md](../CONTRIBUTING.md). Keep new work bounded, retain both
positive and negative outcomes, identify the exact source and artifact digests,
and state what the evidence does not establish.

## Five layers that must not be collapsed

| Layer | Question it answers | What it does not answer |
|---|---|---|
| Scientific question | What behavior is being investigated? | Whether the proposed behavior is true |
| Retained numerical evidence | What happened in a declared finite computation? | Continuous or infinite-cutoff truth |
| Software acceptance evidence | Did the consumer reject malformed or inconsistent records? | Physical correctness |
| Certification-readiness evidence | Do bounded arithmetic and control mechanisms behave as declared? | A physical case result unless that case was executed |
| Review/package acceptance | Are exact bytes, reviews, and artifacts consistently bound? | Scientific certification |

Whenever a document says **PASS**, first identify which row of this table it
belongs to.

## What not to do first

Do not begin by reading the nested `prior_*` directories or by assuming that a
higher version number represents a stronger physical claim. Do not infer a
scientific result from a test count, a green workflow, or an accepted package.
Use the [archive map](ARCHIVE_MAP.md) when historical provenance becomes
necessary.
