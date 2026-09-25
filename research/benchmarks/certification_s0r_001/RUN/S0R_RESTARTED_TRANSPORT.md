# S0r: restarted contour-driven Kato transport

Parent 4a7df867909128c88e755234ea91b11444a8db6d. Responds to Claude 5807050140 (Y1-Y3) and Codex 5299419514. Synthetic only; independent audit pending.

## Frozen construction

Retain S0q's H(t)=3n(t)n(t)^T, n=(-sin t,0,cos t), exact spectrum {0,0,3}, H' product rule, unit contour and K=[P',P]. Whole-arc interval integration with 2048 panels supplies enclosures of P and P'. The analytically justified spectral separation and bounds ||K'||op<=48 remain fixture assumptions proved in S0q. The exact frame oracle never supplies the propagator or its error ledger.

Transport F0=(e1,e2) through 128 steps h=1/1024 to target length 1/8. At each midpoint m, compute a numerical contour K-box. Take its entrywise midpoint and skew-project it: A=(mid(K)-mid(K)^T)/2. These are exact dyadic entries, and the code requires A+A^T=0 exactly. Define delta=||K_box-A||F. It encloses ||K(m)-A||op even though independent interval entries need not form a skew matrix.

Given a numerical frame centre C and Frobenius error E from the exact Kato frame, propagate with exp(hA)C. Exact K and A are skew, so both propagators are isometries and the incoming error E is not amplified. Duhamel's identity gives the local defect

    ||C||F [delta*h + 48*h^2/4].

The second term integrates |s-h/2| over [0,h]. The delta term must be charged separately: replacing the contour box by its midpoint without this debit is unsound. Charge the interval matrix-exponential/product rounding when replacing its output by a dyadic midpoint, then add all three debits to E. The record retains each start/end error, centre norm, delta, contour debit, variation debit and rounding debit.

This error also bounds ||(I-P)C||F because the exact Kato frame is in range(P). Since the exact frame has orthonormal columns, ||C^T C-I||F<=2E+E^2. These are derived bounds, recorded at each endpoint, not independent measured residual certificates. Endpoint oracle differences must be below the charged E.

## Continuous tubes and seams

For each step use exp(uA)C, u in [0,h], widened entrywise by E plus the full-step local defect. Each entry is bounded by the Frobenius error. Because the integrand is nonnegative, the full-step defect also bounds every partial step. Pad the interval u radius by relative 2^-20 to cover downstream coordinate-radius rounding. If e is the actual extension beyond h (also bounding the negative extension), charge an additional ||C||F [delta+48(h/2+e)]e. Bounds hold for negative as well as positive local time; the model and derivative bounds are uniform on the enlarged interval. The code checks that the seam source and doubled target parameter endpoints fit their respective padded tubes.

Sixty-four adjoining source cells cover [0,1/16]. Each target interval 2t is covered by the hull of two consecutive transport tubes. Compute contour K(t) and K(2t) on the whole parameter cells, and derive F_s'=K_s F_s, F_t'=2K_t F_t. Use the rank-two partial isometry S=F0 R(1/5)F0^T and the actual product rules for M and dM. Require det(M)>0 and 1-||M-R||F>=19/20 on each cell. The resulting uniform polar derivative bound is (20/19)||dM||F. No entrywise dU is claimed by this packet.

Every tube is checked against the exact frame at its start, midpoint and end. These 384 point comparisons and 128 endpoint-error comparisons are regression controls; the continuum claim rests on the interval integrals and defect proof. The generator for this family happens to be constant. The numerical construction does not substitute that identity, but this run does not exercise general noncommuting Kato generators. S0b's separate noncommuting fixture remains component evidence.

## Controls, comparison and limits

An explicit symmetric matrix fails the exact-skew predicate. A separate geometric refusal at source t=1/4 and target 1/2 has first-column norm ||M e1||<19/20, which proves sigma_min(M)<19/20; that control uses the exact synthetic frame only and is not an attempted numerical transport to 1/2.

Compare the accumulated restarted error at target 1/8 with the old single-origin remainder 42sqrt(2)(1/8)^2. This is an error-bound comparison for this declared fixture and budget, not a physical scaling claim. Increasing the panel count from S0q's 1024 to 2048 is part of the frozen budget, so this is not an isolated one-variable performance experiment.

Run check.py --wheel <locked wheel> --output <fresh>, then verify.py. The fixed worker cap is 40 seconds, 1 GiB, 128-bit Arb, one thread, no adaptive refinement or retries. Source, verifier, specification, native environment and all step/seam endpoints are retained in the manifest. Verification reconstructs the debit inequalities using exact rational endpoint arithmetic and tests record tampering and overwrite refusal.

The domain is eight times S0q's source/target domain. Physical spectral isolation, variable/noncommuting contour-derived transport, higher seam derivatives and the complete composer/lift budgets eta, rho, L, L2 and L3 remain open. Q3/P3, physical S1-S4, v078 and cutoff agreement remain open. No physical model or sweep is executed.
