# Retained momentum-mapping summary

`summary.py` reads the completed scout 001 and 002 four-file `RUN` packets,
checks their manifest and result/receipt/log bindings, and calculates statistics
using exact rational arithmetic on the retained approximate spectra. It never
assembles a Hamiltonian, evaluates a new momentum point, or calls an eigensolver
or interval factorization. Each scout's own check-only verifier supplies the
separate full record/source/runtime replay.

From the repository root:

```sh
python -B research/benchmarks/momentum_mapping_scout_001/scout.py --check-only \
  --output research/benchmarks/momentum_mapping_scout_001/RUN
python -B research/benchmarks/momentum_mapping_scout_002/scout.py --check-only \
  --output research/benchmarks/momentum_mapping_scout_002/RUN
python -B research/benchmarks/momentum_mapping_summary_001/summary.py
```

The default output directory is `OUTPUT` beside this file. The four generated
artifacts are `SUMMARY.json`, `REPORT.md`, `upper_gap_samples.svg` and
`upper_gap_samples.png`. Alternative retained inputs and an output directory can
be supplied with `--coarse`, `--refined`, and `--output`.

The two-panel scientific scatterplot uses explicitly labeled parent-relative
fractional coordinates and a shared approximate upper-gap color scale in meV.
It shows sample points only: marker area and background do not represent
certified coverage. Both original and refined sample minima retain their exact
fractional coordinates in the JSON and report. The refinement was selected from
four low-gap coarse observations in one cluster, so it is neither independent
validation nor uniform refinement of the whole parent box.

All claims remain approximate point diagnostics. The observed minima are not
lower bounds between samples. No cell interior, physical gap closure, seam,
topology, or increased certified coverage follows.
