# Twistronics: following band crossings through a changing model

This AI-assisted computational research project studies how band crossings and
their topological charge relationships evolve along parameter paths in a model
of strained twisted bilayer graphene.

In plain language: two slightly rotated graphene sheets can have unusual
electronic behavior. This project calculates where selected electron-energy
bands meet, follows those meeting points as model parameters change, and checks
whether their relationships change consistently. These points live in
**momentum space**, not at physical locations on a graphene sheet.

> **New here?** Begin with [Start here](docs/START_HERE.md). It separates the
> established learning material from active draft research and explains which
> documents to read for your goal.

> **Current status:** [`main`](https://github.com/alanfuller15/Twistronics/tree/main)
> retains the v060/v062 numerical presentation and v065 software evidence.
> Later migration, certification-readiness, physical S1a, and packaging work is
> public in draft pull requests but is not part of `main`. See the dated
> [status page](docs/STATUS.md) before interpreting “latest” or “PASS.”

## Explore the interactive field guide

The new [interactive visual guide](docs/interactive-guide/README.md) lets you
turn two reference lattices, zoom into 128 retained momentum-space samples,
and step through saved band-crossing paths. Each view explains its units,
magnification, and evidence limits. Download its single-file explorer to run
it in a browser; GitHub's Markdown viewer cannot execute interactive controls.

[![Interactive momentum map with explicit coordinate and energy scales](docs/interactive-guide/preview-map.jpg)](docs/interactive-guide/README.md)

The map presents draft observations at exact commit `3f174f1`; it does not
merge or certify that research. The geometry lesson is explanatory, and the
node-path lesson retains its historical v062 label.

## The established visual introduction

The [illustrated research guide](docs/visual-guide/README.md) explains the
scientific question, terminology, v060/v062 evidence, and open work without
requiring readers to reconstruct the repository history.

![Measured node locations through the v062 continuation in both implementations](docs/visual-guide/figures/node-paths.svg)

*Actual retained numerical data, not an artist's illustration. Markers are
measured states; connecting lines guide the eye. This continuation segment
alone is not a demonstration of a complete braid.*

## What the retained v060/v062 evidence shows

The latest numerical batch presented on `main` is **v062**. Two separately
coded engines retain the same spatial charge classification, **OPPOSITE**, at
eleven measured tunnelling ratios from 0.991 to 1.000. Joining the retained
v060 window gives fifteen distinct sampled ratios per engine, including earlier
SAME classifications. Definitions and caveats are in the
[guide](docs/visual-guide/README.md#what-do-the-charge-labels-mean).

![Spatial charge classifications at the fifteen sampled ratios](docs/visual-guide/figures/charge-comparison.svg)

The engines share a measurement framework and model assumptions. Their
agreement is a useful numerical check, not independent physical validation.
Finite sampling does not establish a continuous-path proof, a complete N8
campaign, or accuracy at infinite momentum cutoff. The microscopic relation
between strain and interlayer tunnelling remains open.

## Choose a reading path

| Your question | Start here |
|---|---|
| What is this repository, and what should I read first? | [Start here](docs/START_HERE.md) |
| What do the pictures and scientific terms mean? | [Illustrated research guide](docs/visual-guide/README.md) |
| What is established, draft, or still open? | [Research status](docs/STATUS.md) |
| What do v062, S0, S1a, and acceptance gates mean? | [Glossary](docs/GLOSSARY.md) |
| What precisely was calculated for v062? | [v062 report](research/v062/REPORT.md), [method](research/v062/METHOD.md), and [coverage ledger](research/v062/COVERAGE.md) |
| Where are the data? | [v062 summary](research/v062/SUMMARY.json), [raw results](research/v062/results), and [instructions](research/v062/README.md) |
| How can I reproduce a presentation or inspect evidence? | [Reproducibility guide](docs/REPRODUCIBILITY.md) |
| How is the large research archive organized? | [Archive map](docs/ARCHIVE_MAP.md) |

## Claim boundary

The repository contains several different kinds of evidence: sampled numerical
results, software acceptance checks, synthetic certification-readiness tests,
and a bounded physical affine-assembly bridge in draft work. A successful
software test, review gate, or package-acceptance round is not automatically a
physical or topological certification.

As of the dated status snapshot, the project has not established a complete
continuous-path proof, uniform physical isolation over the declared rectangle,
certified projector/transport/seam composition, an Euler-class result for a
physical material, infinite-cutoff convergence, or experimental validation.

## Scientific feedback and contributions

Useful outside feedback includes a decisive topology benchmark, a check on
symmetry and band-isolation assumptions, or a realistic observable and
experimental control path. Before proposing changes, read
[CONTRIBUTING.md](CONTRIBUTING.md) and bind claims to exact retained evidence.

Earlier research remains part of the record. It should be entered through the
[archive map](docs/ARCHIVE_MAP.md), not treated as a sequence of progressively
stronger physical claims.
