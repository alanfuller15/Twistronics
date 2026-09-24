# S0u: refined contour, executable derivative contract and retained tubes

Parent `04b3377de5d08361d4da3c0ee4cd1aa7f821fcc3`. Responds to Claude source `5807622849` and Codex disposition `5299802358`. Independent audit pending. Synthetic only.

## Fixed 1024-panel calibration

S0u retains S0t's signed full-step recurrence and raises the fixed midpoint-contour count from 512 to 1024. This is one declared packet configuration, not an adaptive run or general convergence claim. The 512 and 1024 calibration records retain the charged projector and derivative remainders and must both contain the exact synthetic projector controls. Every other transport and seam parameter remains fixed: 128 steps per family, `h=1/1024`, 64 source seam cells, 128-bit Arb, one thread, 40 seconds and 1 GiB.

The endpoint proof is unchanged:

    E_next <= E + ||C|| delta h
                  + ||C|| [||K''|| h^3/24
                           + ||K'|| (||K||+||A||) h^3/12]
                  + rounding.

The constant and two-axis synthetic bounds remain `(||K||,||K'||,||K''||)=(3,24,438)` and `(6,120,4656)`. The legacy first-order endpoint recurrence still runs on the same boxes as a comparison control.

## Retained continuum-tube radii

For a partial step there is no centered cancellation. S0u therefore continues to widen each tube by

    T = E_start + ||C|| delta h + ||C|| ||K'|| h^2/4 + extension.

S0t applied this radius in code but did not retain it. S0u records `tube_radius=T` at every step. The rational verifier now checks the radius against the retained start error, generator debit, uncancelled variation debit and padded-radius extension before using the tube coordinates in the seam-coverage checks. The interval frame matrices themselves remain trusted Arb outputs; point-oracle containment remains a regression control.

## Executable synthetic gap-to-derivative contract

The positive contract names `self_adjoint_riesz_contour_differentiation_v1` and requires self-adjoint input, cluster dimension two, a positive spectral gap, a separated circular contour, Hamiltonian derivative bounds through order three, operator norm, and an agreed parameter domain. For contour radius `r`, resolvent distance `d`, and input bounds `H1,H2,H3`, it computes

    P1 = r H1 / d^2,
    P2 = r (2 H1^2 / d^3 + H2 / d^2),
    P3 = r (6 H1^3 / d^4 + 6 H1 H2 / d^3 + H3 / d^2),
    K  = P1,
    K1 = P2,
    K2 = P3 + 2 P2 P1.

These follow from differentiating the Riesz resolvent through third order and the projection commutator identities. On the declared two-axis synthetic inputs `r=d=1`, `H1=6`, `H2=48`, `H3=192`, the outputs are `P1=6`, `P2=120`, `P3=3216`, `K=6`, `K1=120`, `K2=4656`.

Four mutations now execute and must refuse: missing theorem, zero/missing gap, missing third derivative input and a mismatched parameter domain. The rational verifier reconstructs the positive outputs and checks the four exact refusal codes. This closes the schema-only limitation in S0t for the synthetic interface.

The physical status remains `DECLARED_UNEXECUTED`. A physical use must supply its own certified spectral window, cluster dimension, derivative inputs, contour separation and valid domain. The synthetic constants are not transferred to a physical Hamiltonian.

## Evidence limits

The exact projector, frame and seam formulas remain regression controls rather than numerical inputs. Arb matrices and transcendental enclosures remain trusted; the separate verifier checks rational implications and source/manifest integrity. This packet does not certify higher seam derivatives, the full eta/rho/L/L2/L3 composition, physical isolation, Q3/P3, physical S1-S4, v078 corrections, a physical class or cutoff agreement.
