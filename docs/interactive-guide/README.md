# Twistronics: an interactive visual field guide

Explore three different scales without confusing a teaching picture with a
saved computation. The guide runs entirely in your browser, with no numerical
engine, account, installation, or network connection needed for its interactions.

**Open it:** download [explorer.html](explorer.html) using GitHub's **Download raw
file** button, then open the downloaded file in a browser. GitHub's file viewer
shows source and does not run the interactive page. On mobile, use a browser
that opens local HTML, or the owner's hosted preview. The hosted preview is
initially private; it is not a public reader URL.

[![The interactive map, with exact sample selection and explained coordinate scales](preview-map.jpg)](explorer.html)

| Lesson | What you can do | What the picture means |
|---|---|---|
| Twist & length | Rotate two reference lattices; change field of view; inspect the ruler and moiré cell | Ideal unstrained geometry; not a band calculation |
| Momentum & energy | Move from a unit fractional chart to 512× and 1,024× views; filter batches; select samples; switch log/linear colors | 128 retained finite-cutoff-a point spectra in draft research |
| Moving crossings | Step or play 11 saved settings; switch BM/reference implementation; hide connecting lines | Historical v062 continuation of six seeded nodes, without interpolated solutions |
| What we know | Compare evidence types and follow exact source links | Claim boundaries and a dated research snapshot |

The interface explains nm versus Å, fractional coordinates versus physical
distance, linear versus area magnification, meV versus μeV, logarithmic versus
linear color scaling, and momentum cutoff versus display zoom. Tables and
native keyboard controls provide alternatives to pointing and color.

## Evidence bindings

- Mapping snapshot: `3f174f19b3ed5d57598accd1d7b1550fc7c9eeff`,
  [retained report](https://github.com/alanfuller15/Twistronics/blob/3f174f19b3ed5d57598accd1d7b1550fc7c9eeff/research/benchmarks/momentum_mapping_summary_001/OUTPUT/REPORT.md).
  Minimum sampled upper gaps: coarse 0.008193629349 meV; refined
  0.003089965450713 meV. Refinement was targeted, not an independent validation set.
- S1b retained area: 29,663/65,536 of **the quadrant [½, 1]²**, not the full
  momentum-space domain. This is an area fraction, not an accepted-cell count.
  The retained partition contains 590 accepted cells and remains inconclusive.
  The point map adds no certified area.
- Historical v062 data: read at main snapshot
  `4c43a663d9212ffaaa5e6bad9b5a9d831bf31b62`, verified against the existing
  visual-guide source manifest. Eleven states per engine, six nodes per state.

The source paths and SHA-256 bindings are in [sources.json](sources.json).
Nothing in this guide certifies a continuous path, uniform full-domain gap,
topological result, infinite-cutoff convergence, or experimental material.

## Rebuild the presentation

Python standard library and Git are sufficient. Ensure the two pinned commits
exist locally (a shallow main-only clone needs the mapping snapshot):

```bash
git fetch origin 3f174f19b3ed5d57598accd1d7b1550fc7c9eeff
git fetch origin 4c43a663d9212ffaaa5e6bad9b5a9d831bf31b62
python docs/interactive-guide/build_data.py
python docs/interactive-guide/build_standalone.py
```

`build_data.py` reads Git objects, verifies retained hashes, cell centers,
sample minima and quadrant coverage, and writes only `data.js` and
`sources.json`. `build_standalone.py` combines `index.html`, `style.css`,
`data.js` and `app.js` into `explorer.html`. Neither script imports a research
engine. `index.html` also works with its adjacent assets or on a static host.

## Validation performed

- Exported and checked all 128 sample records, exact dyadic centers, reported
  minima, 22 six-node states and retained coverage source bindings.
- Checked JavaScript syntax and exercised angle presets, physical zoom,
  layer-cell visibility, all spatial views, batch filters, both energy scales,
  sample stepping, minimum selection, both engines and saved-state playback.
- Inspected desktop and 390-pixel iframe layouts, including the compact axes;
  the mobile document had no horizontal overflow.
- Loaded the generated single-file explorer and verified sample selection.

These checks validate the presentation, not the underlying scientific claims.
