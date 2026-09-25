# S0v: contract-bound transport and nondegenerate-cluster separation

Parent `21dd8577d8e2d1841e9912ee69ef8c85361fa6b4`. Responds to Claude source `5807736006` and Codex disposition `5299871574`. Independent audit pending. Synthetic only.

## Contract-to-transport binding

S0u executed a synthetic Riesz-contour derivative contract but separately supplied the same numerical constants to transport. S0v removes that provenance gap. It executes one contract for each fixed synthetic family before transport and constructs each case's `(K,K1,K2)` transport bounds directly from that contract's outputs. Every case records its `contract_id`. The rational verifier reconstructs both contracts and requires the recorded transport bounds and every per-step bound to dominate their linked contract outputs.

The constant family declares `(H1,H2,H3)=(3,6,24)`, yielding

    (P1,P2,P3) = (3,24,294),
    (K,K1,K2) = (3,24,438).

The two-axis family retains `(H1,H2,H3)=(6,48,192)`, yielding

    (P1,P2,P3) = (6,120,3216),
    (K,K1,K2) = (6,120,4656).

The formulas and norm remain unchanged:

    P1 = r H1 / d^2,
    P2 = r (2 H1^2 / d^3 + H2 / d^2),
    P3 = r (6 H1^3 / d^4 + 6 H1 H2 / d^3 + H3 / d^2),
    K = P1,  K1 = P2,  K2 = P3 + 2 P2 P1.

## Nondegenerate-cluster separation

The contract no longer calls the centre-to-complement distance a spectral gap. For a cluster enclosed in the disk of radius `rho` about the declared centre, a fixed circular contour of radius `r`, a certified centre-to-complement distance `g`, and a resolvent distance `d`, it requires

    rho >= 0,
    r > rho,
    g > r,
    d <= min(r - rho, g - r).

The cluster enclosure, complement distance and Hamiltonian derivative bounds must be uniform on the whole required padded parameter domain. These synthetic fixtures have `rho=0`, `r=d=1`, `g=3`, and domain `[0,1/8]`; the interface now also represents nonzero `rho` without changing the theorem.

All eight defined negative paths execute on a deep copy and must return their exact code: missing theorem, non-self-adjoint input, wrong cluster dimension, missing centre-to-complement distance, failed contour separation, missing third derivative input, wrong norm and domain mismatch. The self-adjoint field remains a declared synthetic fact; a physical packet must bind it to its certified Hamiltonian construction.

## Unchanged retained calculation

The numerical fixture, panels and ledgers are unchanged from S0u: fixed 1024-panel midpoint contour, 128 transport steps per family, 64 seam cells per family, `h=1/1024`, 128-bit Arb, one thread, 40 seconds and 1 GiB. The full-step signed endpoint recurrence and the conservative partial-step tube recurrence remain distinct. Each tube radius is retained and verifier-checked before seam coverage.

This is a provenance and contract-semantics change, not a new numerical sweep or convergence claim. The packet should reproduce S0u's retained numerical bounds apart from environment timing and the added contract metadata.

## Evidence limits

Physical status remains `DECLARED_UNEXECUTED`. The exact synthetic formulas remain regression controls; Arb matrices and transcendental enclosures remain trusted inputs to the rational verifier. This packet does not certify a physical cluster, a uniform physical spectral window, higher seam derivatives, the full eta/rho/L/L2/L3 composition, Q3/P3, physical S1-S4, v078 corrections, a physical class or cutoff agreement.
