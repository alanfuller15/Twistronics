# Local-event method frozen before decisive runs

The original flat-band nodes survive these preparation events. Consequently the full-chart flat gap has zeros on the nominal “open” side of each extra-pair fold. v051 introduces a separate local event gate. It does not relax the global positive-gap gates used for the earlier isolated-pair events.

The common fractional-momentum rectangle is `[0.42,0.63] × [0.52,0.63]`. The two events share the same pair-present state, A=0.2 and B=0. Both use T=0, phi=0, ratio=0.8, eps=0.003, theta=1.05 degrees, kinetic=lab_nn_full and constant tunnelling amplitudes. Birth varies A between 0.16 and 0.2 at B=0; annihilation varies B between −0.05 and 0 at A=0.2. The BM N4 pilot estimates were A=0.1763069111 and B=−0.0339767312; pilots are not accepted measurements.

BM retains linear reciprocal geometry, cutoff_tol=1e−6; TBG retains exact geometry, cutoff_tol=1e−9. The Hamiltonian source bytes are unchanged from v050. Two numerical workers at most, single-thread BLAS. Both N4 engines must complete both events before N6 begins.

Acceptance requires:

- A fold solver bounded to the local rectangle, gap components below 1e−6, rank-one spatial Jacobian at steps 2e−5 and 1e−5, parameter agreement below 1e−6, positive adjacent-band gap, nonzero null curvature and transverse parameter slope with 1% step refinement at 2e−4 and 1e−4, and the predicted pair-present side.
- Nine resolved two-root states between the common pair-present state and fold ±0.001 on the node side. Separation >0.001, each root >0.005 from the rectangle boundary, and each continuation jump <0.06. All root optimizations are bounded; an out-of-domain result is rejected.
- Opposite charge at the first and last root state. Same-radius meshes 256/512 and half-radius mesh 512 must agree; the inherited phase-resolution-only fallback uses 1024/2048/2048. Comparison-path transport uses 128/256 meshes and locates both external-gap minima. Loop circles and their straight connecting segment stay within the rectangle. Charges are measured at two stations, not every root state; no parameter-transported absolute charge is claimed.
- Positive internal flat gap along all four rectangle edges at all nine root stations, the fold, and two open-side stations. Edge grids 24/48 retain corners and refine every sampled local minimum with a bounded scalar optimizer. Both refinements must exceed 1e−5 meV and agree within 0.01 meV.
- Positive *local* flat gap at fold ±0.001 on the open side and at the far-open anchor (A=0.16 or B=−0.05). Closed 17×17 and 25×25 grids generate neighborhood-minimum seeds, supplemented with all corners and the located fold momentum. Gradient optimization is bounded to the rectangle, records success, rejects a worsened seed, and may use a recorded SLSQP fallback after L-BFGS-B. The same positivity/refinement thresholds apply.
- Two original flat nodes are separately resolved at all 12 stations, each outside the rectangle by >0.02 with residual <1e−6. This is a control that prevents confusing a local opening with a global one. No new charge label is assigned to the original pair.
- Birth/annihilation extra-pair and original-pair roots must join within 1e−6 at the common A=0.2, B=0 station.

All searches and parameter stations are finite. A positive numerically located boundary minimum is not an analytic interval certificate; unseeded narrow minima or events between parameter stations are not excluded. This gate supports the specified local fold and sampled root windows, not a complete global node inventory, a continuously certified whole route, an Euler class, or physical-bilayer validation.

PLAN.json binds the scientific sources and input anchors. Reporting sources added later are separately hashed by the deliverable manifest. Each completed station is saved atomically in its window record. Rerunning an incomplete window recomputes that bounded case; an accepted case with the same protocol is skipped. There is no resume inside a partially computed loop.
