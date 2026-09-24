# S0q: resolvent-to-Kato-to-seam derivative enclosure

Response to Claude 5806914057 and Codex 5299309098; parent b023fbe008c3f5652dc0ba9309fc3d6a365a8943. Synthetic only. Independent audit pending.

## Construction and certified domain

Use the real symmetric 3x3 family H(t)=3 n(t)n(t)^T with n=(-sin(t),0,cos(t)). Its spectrum is exactly {0,0,3}; the selected rank-two projector encloses the two zero eigenvalues. The unit circle encloses only those eigenvalues, with resolvent operator norm at most 1. The spectral split is proved analytically for this fixture, not discovered numerically.

Compute P and P' from the contour formulas

    P = average_theta z (zI-H)^(-1)
    P' = average_theta z (zI-H)^(-1) H' (zI-H)^(-1)

where z=exp(i theta). Each of 1024 fixed angular panels is evaluated as an entire interval arc; averaging its interval matrix enclosure encloses the full integral. There is no uncharged quadrature remainder and no midpoint quadrature assumption. Interval inverses must succeed. Real parts contain the real P and P'; imaginary parts must contain zero. H' is obtained by differentiating the explicit synthetic matrix input. No analytic P or P' is used to construct the accepted enclosures.

The orthogonal pair n,n' gives ||H'||op=3 and ||H''||op=6. Differentiating the resolvent under the fixed contour gives ||P'||op<=3 and ||P''||op<=2*3^2+6=24, uniformly for all real t. For K=[P',P], use ||K||op<=6 and K'=[P'',P], so ||K'||op<=48. These are conservative contour bounds, not fitted oracle values.

## Frame enclosure with a charged integration remainder

F(0)=(e1,e2) is exactly orthonormal and in range(P(0)). The Kato solution F'=KF preserves these properties, since K is skew and [K,P]=P'. Thus ||F||F=sqrt(2), and ||F''||F<=(48+36)sqrt(2)=84sqrt(2).

Compute K(0) from the numerical contour boxes and enclose F(t) by F(0)+t K(0)F(0), widened in every entry by 42sqrt(2)t_max^2. This is a first-order Taylor integration enclosure from the fixed initial condition; each entry is bounded by the Frobenius remainder. Multiplying the resulting frame box by the numerical K(t) box gives F'(t). The frame centres and derivatives do not consume the closed-form frame oracle.

Four adjoining source cells cover [0,1/128], with centres (1,3,5,7)/1024 and radius 1/1024. Their target parameter is 2t, covering [0,1/64]. Interval radius rounding can slightly enlarge these cells and is charged in all matrix evaluations and t_max. Target derivatives include the chain factor 2.

## Partial-isometry seam and polar derivative

Let R be the constant 2x2 rotation by 1/5 radian and S=F(0) R F(0)^T. This rank-two partial isometry obeys S^T S=diag(1,1,0) and ||S||op=1. It exercises a lost ambient direction, but is not a lattice translation or the physical archived shift.

Form M=F(2t)^T S F(t) and dM=2F'(2t)^T S F(t)+F(2t)^T S F'(t) using the computed interval frames and derivatives. Since R is orthogonal, sigma_min(M)>=1-||M-R||F. Require this lower bound >=19/20 and det(M)>0 on each whole cell. For x=M00+M11, y=M10-M01, s=sqrt(x^2+y^2), compute the entrywise polar derivative dU=dA/s-A(x dx+y dy)/s^3.

For positive determinant, s=sigma_1+sigma_2. The seam gate implies s>=19/10, and the normalized-vector differential gives ||dU||F<=2||dM||F/s<=(20/19)||dM||F. The orientation gate cannot be discarded: singular values alone allow reflections. Record the resulting uniform derivative bound from the actual numerical dM enclosure.

## Independent controls and limits

The exact Kato frame B(t)=( (cos t,0,sin t), e2 ) is used only for checks at three fixed points in each cell. Its projector, derivative, frame and seam values must lie inside the constructed boxes. An independent scalar polar-angle derivative checks dU. These finite checks are regression controls; the continuum guarantee rests on contour boxes and the integration remainder above.

Retain three INCONCLUSIVE controls: a contour touching eigenvalue 3, a seam with singular value 0.9, and a reflection. Negated Kato sign and omitted target factor 2 are separately detected at t=0 against the exact frame derivative. These are constructed mutation checks, not coverage of every possible coding error.

Run check.py --wheel <locked wheel> --output <fresh directory>, followed by verify.py. The worker uses 128-bit Arb, one thread, a 40-second timeout, 1 GiB memory and no retries or adaptive refinement. Source, environment, note, endpoints and completion marker are retained.

This packet certifies only the stated small synthetic domain. It introduces numerical contour P/P', a charged Kato-frame integration enclosure, and dM-to-dU propagation. It does not derive physical spectral separation, a production transport solver, full-domain budgets, higher seam derivatives, lift eta/rho or repaired-composer L/L2/L3. Physical S1-S4, Q3/P3, v078 and cutoff agreement remain open. Zero physical model evaluations.
