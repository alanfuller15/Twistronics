# S0x: rho-sensitive refusals and exact rational centre comparison

Parent `43360c760b98ea9b4f2aeae9444f94a48be980a0`. Responds to Claude source `5808083677` and Codex disposition `5300092820`. Independent audit pending. Synthetic only.

## Bounded purpose

S0w established exact-rational contract reconstruction and one passing nonzero-cluster control, but all sixteen retained refusals executed on a contract with `rho = 0`. Those refusals could not distinguish the required inequalities

    r > rho,
    d <= r-rho

from incorrect implementations that ignored `rho` and checked only `r > 0` and `d <= r`.

S0x leaves every contour, transport, tube, seam and calibration operation unchanged. It adds two mutations to the existing passing control

    rho = 1/2, r = 3/2, g = 3, d = 1.

The first sets `r = 1/2 = rho` and must refuse with `CONTOUR_INSIDE_CLUSTER`. An implementation that checks only `r > 0` would accept it. The second sets `d = 5/4`; this remains below `r = 3/2` but exceeds `r-rho = 1`, so it must refuse with `RESOLVENT_INNER_DISTANCE_EXCEEDED`. An implementation that checks only `d <= r` would accept it.

The retained inventory is therefore eighteen refusals: the sixteen S0w controls plus these two positive-`rho` controls.

## Exact centre comparison

The contour and cluster centres are now compared after exact `Fraction` reconstruction rather than as lexical JSON strings. A retained acceptance control compares `cluster_center = "0"` with `contour_center = "0/2"` and requires identical derived outputs. This demonstrates numerical equality for generalized rational encodings while the primary contract remains canonically serialized.

## Retained numerical scope

The two transport families retain the S0w bounds and numerical calculation unchanged:

    constant: (K,K1,K2) = (3,24,438),
    two_axis: (K,K1,K2) = (6,120,4656).

The bounded calculation remains fixed at 1,024 midpoint panels, 128 transport steps per family, 64 seam cells per family, `h=1/1024`, 128-bit Arb, one thread, 40 seconds and 1 GiB. It performs no adaptive refinement or physical evaluation. The full-step signed endpoint recurrence and conservative partial-step tube recurrence remain distinct.

## Evidence limits

The `self_adjoint`, `fixed_contour` and `uniform_over_parameter_domain` fields remain declared synthetic facts. Physical status remains `DECLARED_UNEXECUTED`. S0x does not derive `rho`, `g`, the contour geometry or uniformity flags from S1 evidence and does not certify a physical cluster, a physical spectral window, higher seam derivatives, the full eta/rho/L/L2/L3 composition, Q3/P3, physical S1-S4, v078 corrections, a physical class or cutoff agreement.
