TEAM SHARE — v042

The one-engine limitation is closed for the v040 windows and checkpoints.
With kinetic='lab_nn_full', BOTH uploaded engines pass the second-braid and
first-annihilation gates at N4 and N6. Spatial SAME→OPPOSITE, unchanged
carried charges, rejected singular comparison, and the fold diagnostics all
reproduce. The post-transfer U pair remains SAME. The ratio-1.04 candidate
and recorded endpoint keep identical measured per-band w1.

TBG braid-2 crossing: 0.99054140 / 0.99076879.
TBG first-annihilation T: -0.71338674 / -0.71331426.
BM values and full cross-engine differences are in the report.

Two qualifications: BM still linearizes reciprocal geometry while TBG uses
the exact inverse; matching only that geometry makes their matrices agree
to roundoff. Also, the ~1.6e-4 frame-convention shift in the annihilation root
exceeds its ~7.2e-05 N4-to-N6 shift. Sensitivity must be quoted per
observable; no checked label changes. The v041 table's old root -0.7120 is
a transcription error: the earlier original roots were -0.71514090/-0.71505612.

Residual helper defects are fixed in a separate tested patch: gap_min can
return +infinity if all minimizers fail. The patch raises on failed/nonfinite
or seed-worsening refinement and rejects invalid radii. Expanded boundary
seeds also recover the known N4 edge minimum, which the uploaded revised
helper still misses by ~0.013 meV despite two-grid agreement. The scientific replay
uses the unmodified uploaded Hamiltonians and its existing external gate.

Next: basis-aware connecting legs, remaining cleanup under the declared
model, then named tunneling strain dependence and N>6 endpoint convergence.
This remains declared-model numerical evidence, not physical-bilayer validation.

Package: raw results for all 20 accepted jobs, 27 supplied tests plus 17 new
checks, source review, helper patch, and preserved prior records in one ZIP.
