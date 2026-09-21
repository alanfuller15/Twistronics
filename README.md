# Twistronics: following band crossings through a changing model

This AI-assisted computational research project asks how band crossings and their topological charge relationships evolve along parameter paths in a model of strained twisted bilayer graphene.

In plain language: two slightly rotated graphene sheets can have unusual electronic behavior. Here, we calculate where certain electron-energy bands meet, follow those meeting points as a model parameter changes, and check whether their topological relationships change consistently. These points live in **momentum space**, not at physical locations on a graphene sheet.

**Start with the [illustrated research guide](docs/visual-guide/README.md).** It explains the question, terminology, evidence and open work without requiring you to reconstruct the version history.

![Measured node locations through the v062 continuation in both implementations](docs/visual-guide/figures/node-paths.svg)

*Actual retained numerical data, not an artist's illustration. Markers are measured states; connecting lines guide the eye. This continuation segment alone is not a demonstration of a complete braid.*

## What the published evidence shows

The latest numerical batch on the source commit used by this branch is **v062**. Two separately coded engines retain the same spatial charge classification, **OPPOSITE**, at eleven measured tunnelling ratios from 0.991 to 1.000. Joining the retained v060 window gives fifteen distinct sampled ratios per engine, including earlier SAME classifications. Definitions and caveats are in the [guide](docs/visual-guide/README.md#what-do-the-charge-labels-mean).

![Spatial charge classifications at the fifteen sampled ratios](docs/visual-guide/figures/charge-comparison.svg)

The engines share a measurement framework and model assumptions, so their agreement is a useful numerical check, not independent physical validation. Finite sampling does not establish a continuous-path proof, a complete N8 campaign, or accuracy at infinite momentum cutoff. The microscopic relation between strain and interlayer tunnelling remains open.

## Choose a reading path

| Your question | Start here |
|---|---|
| What is being investigated, and what do the pictures mean? | [Illustrated research guide](docs/visual-guide/README.md) |
| What precisely was calculated? | [v062 report](research/v062/REPORT.md) and [method](research/v062/METHOD.md) |
| What has not yet been covered? | [Campaign coverage ledger](research/v062/COVERAGE.md) |
| Where are the data and reproduction instructions? | [Summary](research/v062/SUMMARY.json), [raw results](research/v062/results), and [v062 instructions](research/v062/README.md) |
| How can I recreate just these figures? | [Rendering instructions](docs/visual-guide/README.md#recreate-the-figures) |
| What is the latest software work? | [v065 evidence-recorder repairs](research/v065/README.md) and [22-case execution evidence](research/v065/EVIDENCE.json) |

## Status and scientific feedback

This branch adds presentation material based on public source commit `7776ffd3ca219ff976e578103b895e25db60dcc2`. It does not run new eigenproblems or alter the numerical records. The v065 software iteration changes evidence recording; it is not a newer numerical batch.

Useful outside feedback includes a decisive topology benchmark, a check on symmetry and band-isolation assumptions, or a realistic observable and experimental control path. The project is seeking scrutiny before broader claims.

Earlier research remains in `research/v053/` through `research/v061/`, preceding deliveries, and `audits/v053/`. The historical results and their limitations remain part of the record.
