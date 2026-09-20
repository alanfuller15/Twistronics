TEAM BOARD — v039 addendum (N=6 pass)

Closes the "N=6 queued" item from TEAM SHARE v039.

Second engine (tbg_ref), kinetic='full', N=6: every checkpoint label reproduces and is cutoff-stable.
- v029: opposite pair before annihilation (sep 0.0193, frame overlap 0.991); zero flat nodes and same-charge U pair after transfer.
- v031: U pair SAME at w0/w1=0.99, OPPOSITE at 1.00.
- v033: fully gapped, w1=(1,0) on flat1, flat2 trivial. Endpoint gap magnitudes move ≤0.25 meV from N=4, same scale as v035.

Practical note for anyone reusing the node search: for pairs closer than ~0.05 the global search under-counts (merge tolerance vs cone check); use the two-seed local search. Recorded in v039 §5–6.

Nothing new is claimed beyond checkpoint reproduction. Open items unchanged: gated path replay of braid 2 and the annihilation in both engines; named strain dependence for w0, w1 before any magnitude is called physical.

Package: twistronics_v023-v039.zip (17 entries, TEAM_SHARE_v039.md, this note, both engines, 22 tests).
