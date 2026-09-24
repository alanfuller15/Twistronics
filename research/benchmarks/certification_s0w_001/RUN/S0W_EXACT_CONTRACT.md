# S0w: exact contract reconstruction and explicit contour geometry

Parent `38601e4c525fd41264870f7e3ab6ad5859c87cf0`. Responds to Claude source `5807917661` and Codex disposition `5299981287`. Independent audit pending. Synthetic only.

## Exact contract values

S0v serialized the two executed contracts with integer outputs. Its checker refused every non-integer derived bound, while its rational verifier reconstructed expected outputs with `int()`. That combination was safe inside S0v but could silently round downward if the integer-only gate were later removed.

S0w removes both assumptions. All contract geometry, derivative inputs and derived bounds are serialized as canonical exact rational strings. The checker and verifier reconstruct them with `Fraction`; transport converts linked bounds to Arb as exact numerator/denominator quotients. No `int()` conversion or integer-only gate remains.

The two transport families retain exactly the same values:

    constant: (K,K1,K2) = (3,24,438),
    two_axis: (K,K1,K2) = (6,120,4656).

The numerical transport, tube and seam calculation is otherwise unchanged from reviewed S0v.

## Positive-radius exact control

A third passing contract is retained as an interface control but is not consumed by transport. It declares

    rho = 1/2, r = 3/2, g = 3, d = 1,
    (H1,H2,H3) = (1,1,1).

It satisfies

    d <= min(r-rho, g-r) = min(1,3/2)

and produces the non-integer exact outputs

    (P1,P2,P3) = (3/2,9/2,39/2),
    (K,K1,K2) = (3/2,9/2,33).

The verifier requires both `rho > 0` and at least one non-integral retained output, so this path simultaneously exercises nondegenerate-cluster geometry and the exact-rational serialization.

## Explicit geometry and refusals

The fixed circular contour centre is now an explicit `contour_center` field and must equal `cluster_center`. For every point in the declared padded parameter domain:

- `rho` is a uniform upper bound on the cluster's distance from that centre;
- `g` is a uniform lower bound on the complement's distance from that centre;
- `r` is the fixed contour radius; and
- `d` is a positive lower bound no larger than either `r-rho` or `g-r`.

The retained synthetic contracts therefore require

    rho >= 0,
    r > rho,
    g > r,
    0 < d <= r-rho,
    0 < d <= g-r.

Sixteen negative controls execute on deep copies and must return their exact codes. They separately test the theorem, self-adjointness, cluster dimension, contour-centre equality, uniform geometry semantics, complement distance, nonnegative cluster radius, both contour-separation sides, positive resolvent distance, both resolvent-distance sides, the fixed-contour declaration, the third derivative input, operator norm, and domain equality.

The `self_adjoint`, `fixed_contour` and `uniform_over_parameter_domain` fields remain declared synthetic facts. A physical packet must derive them—and the uniform `rho` and `g` bounds—from certified S1 window data over every required parameter cell. S0w does not supply or simulate that physical evidence.

## Retained numerical scope

The bounded calculation remains fixed at 1,024 midpoint panels, 128 transport steps per family, 64 seam cells per family, `h=1/1024`, 128-bit Arb, one thread, 40 seconds and 1 GiB. It performs no adaptive refinement or physical evaluation. The full-step signed endpoint recurrence and conservative partial-step tube recurrence remain distinct.

## Evidence limits

Physical status remains `DECLARED_UNEXECUTED`. The exact synthetic formulas are regression controls; Arb matrices and transcendental enclosures remain trusted inputs to the rational verifier. This packet does not certify a physical cluster, a uniform physical spectral window, higher seam derivatives, the full eta/rho/L/L2/L3 composition, Q3/P3, physical S1-S4, v078 corrections, a physical class or cutoff agreement.
