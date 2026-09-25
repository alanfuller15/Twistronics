# S0z: assembly-derived path derivatives

Parent `fe60caae1f1c04a2c42ce99b92ce19ba2cbcda60`. Follows the completed S0y audit. Synthetic interface evidence only; physical S1–S4 and v078 remain outside this packet.

## Why this packet exists

S0y derived a common contour from a complete two-dimensional window cover, but each cell also supplied its own `H1`, `H2`, and `H3`. A uniform understatement could therefore pass while the retained assembly stayed unchanged. S0y also described validity over a rectangle, whereas transport consumes a one-dimensional path.

S0z closes those two interface gaps together. Spectral cells are no longer allowed to supply derivative bounds. A separate exact path artifact is hash-bound to the exact affine assembly, and the checker derives the pathwise matrix derivatives and their operator norms from those two artifacts.

## Exact retained derivation

The synthetic assembly is unchanged:

    H(x,y) = diag(-3-x, -1/3+x, 1/3-y, 3+y),
    (x,y) in [0,1/8] x [0,1/8].

Its retained coefficient diagonals are

    H_x = diag(-1,1,0,0),
    H_y = diag(0,0,-1,1).

The new exact path is

    gamma(t) = (t,t/2),   t in [0,1/8].

The checker proves both endpoints, and hence the whole affine path, lie in the retained rectangle. Exact chain-rule evaluation gives

    dH/dt = diag(-1,1,-1/2,1/2),
    d2H/dt2 = 0,
    d3H/dt3 = 0.

For real diagonal matrices, the operator norm is the largest absolute diagonal entry, so the derived bounds are exactly

    (H1,H2,H3) = (1,0,0).

The common window geometry remains

    c = 0, rho = 1/3, g = 3, r = 5/3, d = 4/3,

and the contour formulas therefore retain

    (K,K1,K2) = (15/16,45/32,1485/256).

The contract's valid domain is now the path parameter interval `t in [0,1/8]`. The two-dimensional rectangle remains separately recorded as the window domain.

## Refusal coverage

Thirty executed mutations cover the S0y window and provenance gates plus the new boundary: any cell-supplied derivative override, assembly schema/coefficient/formula changes, path schema or assembly-binding changes, invalid path domains, paths leaving the certified cover, incorrect path derivatives, incorrect pathwise matrix derivatives, and a non-operator norm.

The direct understatement mutation adds `(H1,H2,H3)=(0,0,0)` to a cell and is refused as `CELL_DERIVATIVE_OVERRIDE_FORBIDDEN`. The accepted bounds can only come from the hash-bound assembly and path artifacts.

The independent verifier reconstructs every cell window, path endpoint, chain-rule diagonal, norm, contour quantity and derivative bound. It also checks source/note bindings and the portable record's tamper and overwrite controls.

## Evidence limits

S0z is a provenance-and-refusal proof over one synthetic diagonal affine family and one affine path. It does not certify graphene assembly, physical spectral windows, an accepted S1 partition, inertia or pivot evidence, a physical path, non-affine chain-rule terms, projector motion, transport, seam derivatives, the composed physical error budget, topology, or v078. The result remains `DECLARED_UNEXECUTED` and ineligible for physical transport.
