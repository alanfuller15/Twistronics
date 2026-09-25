# S0s: validated midpoint quadrature and noncommuting Kato transport

Parent b50e87406e7a3df01d15637fcc5694f49d5c06ff. Responds to Claude source 5807248879 and Codex disposition 5299554263. Independent audit pending. Synthetic only.

## Quadrature with an integrated remainder

For each real t, H=3nn^T is symmetric with exact spectrum {0,0,3}. On z=exp(i theta), R=(zI-H)^-1 has operator norm at most 1. Let B=H'(t), f=zR, g=zRBR. Their angular derivatives obey

    R_theta = -i z R^2
    f_theta_theta = -zR + 3z^2 R^2 - 2z^3 R^3
    g_theta_theta = -zRBR + 3z^2(R^2BR + RBR^2)
                   - 2z^3(R^3BR + R^2BR^2 + RBR^3).

Thus ||f''||<=6 and ||g''||<=13||B|| uniformly on the circle. On a panel of half-width r=pi/N, the centered first-order Taylor term has zero integral. Taylor's theorem and the mean of x^2 give an average error at most M r^2/6. Averaging all N panels leaves the same uniform bound. We therefore compute midpoint averages, then add qp=pi^2/N^2 and qdp=13||B||pi^2/(6N^2) to each real matrix entry. Imaginary boxes widened by the same debit must contain zero. The exact P and P' are real, so this extraction is sound. The remainder bounds operator error and hence each component; adding it independently entrywise is conservative.

This is a second-order quadrature remainder, not a claim that a first-order panel range box has second-order width. For interval t the midpoint arithmetic encloses all real t in that cell, and the remainder is uniform in t. Width from the t-cell need not decay with N. The two fixed calibration counts 256 and 512 record the charged remainders and verify containment of analytic P/P' at t=1/16. They do not establish a general empirical convergence rate or justify dropping the remainder.

K=P'P-PP' is skew for the exact orthogonal projector. Intersect K_jk with -K_kj and set K_jj=0 after checking zero containment. Empty intersections refuse. Subsequent ordinary interval products may discard skew correlations; this only widens the bounds. The midpoint propagator is explicitly skew-projected and its exact dyadic skew identity is checked.

## Two fixed families and derivative constants

The constant-generator case retains S0r's n=(-sin t,0,cos t), with ||H'||<=3, ||P'||<=3, ||P''||<=24. For an orthogonal projector P, the off-diagonal blocks of [X,P] have norm bounded by ||X||, hence ||[X,P]||<=||X||. Since K'=[P'',P], use ||K'||<=24 instead of 48. This is conservative even though the exact generator is constant.

The second case uses Q(t)=Rz(t)Ry(t), n=Qe3. Write Z and Y for the unit rotation generators and use Q'=ZQ+QY. Then n'=Zn+QYe3, ||n'||<=2, and ||n''||<=4. Unit length makes n' perpendicular to n, giving ||H'||=3||n'||<=6. The product rule yields ||H''||<=3(2||n''||+2||n'||^2)<=48. The same unit-circle resolvent identity gives ||P'||<=6 and ||P''||<=2*6^2+48=120, hence ||K'||<=120. These uniform constants hold also on the tiny padded interval outside the declared endpoints. No constant from the first family is silently transferred to the second.

The independent frame oracle is F(t)=Q(t)F0 R(-sin t), F0=(e1,e2). Indeed E=QF0 spans range(P), E^T E'=cos(t)J, and the final rotation cancels that connection, giving F^T F'=0 and F(0)=F0. Thus this is the exact horizontal/Kato frame. It supplies regression comparisons only, never the numerical propagator or its error ledger.

## Restarted transport and seams

Each case has 128 steps h=1/1024 to target t=1/8 and 64 source seam cells through 1/16. At each step, midpoint contour K determines exact skew A. With frame centre C, incoming Frobenius error E, delta=||K_box-A||F and the case-specific Lipschitz constant L, Duhamel gives the local error ||C||F(delta*h+L*h^2/4). Both exact and frozen propagators are orthogonal, so incoming E is not amplified. The interval exponential/product rounding is charged when taking the next dyadic centre. Retain all three debits and all start/end errors.

As in S0r, tubes evaluate exp(uA)C for u covering [0,h], then add the incoming and full-step errors entrywise. Pad the u-radius by relative 2^-20 and charge ||C||F(delta+L(h/2+e))*e for the actual extension e. Endpoint checks bind each source cell to one tube and its doubled target to the hull of two consecutive tubes. Derived source-range error is E and orthogonality error is at most 2E+E^2. Oracle endpoint and tube comparisons are regression controls; the continuum assertion depends on the defect proof.

For S=F0 R(1/5)F0^T, form M=F_t^T S F_s with source t and target 2t. Whole-cell contour boxes supply F_s'=K(t)F_s and F_t'=2K(2t)F_t. Gate det(M)>0 and sigma_min(M)>=1-||M-R(1/5)||F>=19/20. Record the scalar polar derivative bound (20/19)||dM||F. This packet does not supply entrywise polar derivatives or higher derivatives.

## Controls and evidentiary limits

For the two-axis case, numerical contour K(0), K(1/8) produce a commutator with an entry excluding zero. Reversing the two exponentials with time factor 1/8 also gives an interval matrix difference with an entry excluding zero. This is an algebraic order-sensitivity control, not an exact two-step solution of the varying ODE. Finally exp(K(0)/8)F0 differs from the exact endpoint oracle by more than the completed restarted error bound in at least one component. A globally frozen initial generator is therefore refused for that claimed accuracy. The actual restarted integration still uses chronological local midpoint factors and its Duhamel bound.

The rational verifier checks the debit recurrence, padded coverage, positive determinant and seam bounds, quadrature charges, amplification, noncommutation, order separation and frozen-generator refusal. It does not independently rederive the numerical K, exponential or dM input boxes; those remain trusted Arb outputs bound to frozen source/environment records. Six protocol controls cover intact records, result/environment/source tampering, missing completion marker and overwrite refusal.

Run check.py with the locked python-flint 0.9.0 wheel and a fresh output, then verify.py. One retained run has a fixed 40-second, 1-GiB, 128-bit, one-thread budget and 512 contour panels. No adaptive refinement or physical sweep. Comparison to S0r changes quadrature method, panel count, skew intersection and constants together, so it is not an isolated performance experiment. Physical spectral isolation, higher seam derivatives and complete eta/rho/L/L2/L3 budgets remain open, as do Q3/P3, physical S1-S4, v078 and cutoff agreement.
