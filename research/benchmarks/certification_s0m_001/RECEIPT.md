# S0m retained receipt

The frozen driver completed all 10 expected outcomes with exit 0. The manifest
verifier accepted 26 files. verify.py accepted the source/record bindings,
nonzero cell debits, signed perturbed intervals, separate repair charge and
six integrity/protocol controls. Independent audit is pending.

At 4096 cells/edge the actual matrix-screen upper bounds were:

| Twist amplitude | Outcome | Retained upper bound |
|---|---|---|
| 0.70 | certified | 0.972755536 |
| 0.72 | certified | 0.999289883 |
| 0.722 | inconclusive | first unresolved cell 1.000030907 |
| 0.75 | inconclusive | first unresolved cell 1.000101543 |

The smallest remaining certified margin among the fixed tests is approximately
0.000710117. The exact 0.72 maximum is about 0.996381996: the edge-2 cell debit
is 0.002907942. The finite inventory is not an optimization or convergence
claim. The 0.722 refusal is a budget limitation, not unequal-class evidence.
The differing-defect pair certifies; the unequal-winding pair refuses.

Perturbed signed intervals (rounded for display only) are
[0.9999999963,1.1591549497] and [-1.0000000066,-0.8408450512]. Each includes its
exact winding and has radius approximately 0.07957748. The repair-width control
returns INTEGER_HALFWIDTH; the excessive sample error returns LIFT_VARIATION.
Exact binary endpoints and resource counters are in RUN/*.json.

No physical evaluations were performed. Eta/rho and derivative bounds remain
conditional synthetic inputs, not numerical physical-projector error bounds.
