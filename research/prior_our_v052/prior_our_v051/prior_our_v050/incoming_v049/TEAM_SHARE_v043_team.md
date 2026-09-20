# TEAM SHARE — v043

Two connecting routes now reproduce under `lab_nn_full` in both unchanged
v041 Hamiltonian engines at N=4 and N=6: 160 primary sampled states, all gated
and accepted. The flat pair remains OPPOSITE from the v028 checkpoint through
the strain rotations and A/T changes to the first-annihilation window. The
post-transfer upper pair remains SAME through phi=65 to 80, T=-0.74 to -0.8,
and w0/w1=0.8 to 0.99, reaching the accepted second-braid starting roots.
Every endpoint join matches its v042 roots within 4.4e-14 in the declared
unwrapped fractional coordinates. Individual carried charges stay constant
within every run. No previously checked relative label changes.

The new guard is explicit transport across changing reciprocal cutoffs:
match (layer,m,n,real-spinor) coefficients after a declared unit-cell pullback,
record discarded frame weight, and reject excess loss or small overlap.
Across fine and coarse parameter links, minimum singular overlap is 0.8983
and maximum discarded frame norm is 5.30e-4. The smallest resolved exterior
gap on a spatial comparison path is 0.05313 meV. Spatial and parameter
orientation checks and the loop mesh/radius checks all pass without fallback.
Maximum cross-engine node difference is 5.03e-6; maximum N4/N6 node shift is
3.62e-4. These comparisons are numerical evidence, not infinite-cutoff bounds.

Seven new assertion tests pass. A real three-state stop/resume experiment
also reproduces the uninterrupted pilot's frames bit for bit and all
non-timing diagnostics. Each primary step now commits its JSON record and
saved frames together; the final report checks them against the aggregate
summary. This directly addresses the incomplete-checkpoint issue preserved
in v042.

Still open under this declared model: braid 1 plus its deepening/unlinking
legs into v028; cleanup and later collision windows after braid 2; a named
strain law for w0 and w1; and N>6 endpoint convergence. Finite sampling does
not prove absence of a missed intermediate event. Both engines share an
author and these replays share a measurement harness, so common conceptual
or harness errors remain possible. Nothing here claims physical-bilayer
validation.

The workflow remains: the partner develops and documents the toolkit, this
review checks source behavior and runs guarded comparisons, and Alan keeps
the shared record aligned. The next measured batch should close the earlier
braid/deepening/unlinking route before claiming a connected full campaign.

Package: twistronics_v043_connections.zip — new source, protocol, raw data,
frames, tests, report, this note, and the complete prior v042 delivery.
