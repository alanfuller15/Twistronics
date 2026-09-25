# S0p: interval overlap derivatives and polar amplification

Response to Claude 5806697692 (W1/W2) and Codex 5299181707, parent eda7e647c632581fdc4292d9d820e5460817a72e. Synthetic only.

## Edge-1 cancellation control

Trace the actual frozen S0n D′ at edge 1, cell 128 of 256. The correct sum is zero. Negate only the Ja′ term by subtracting twice that term from the captured result. Its norm must exceed the valid L2 h/2 derivative allowance with h=1/4096. This supplies the missing single-term mutation; negating the entire zero derivative would test nothing.

## Whole-cell derivative enclosures

Let B(t) have columns (cos t,sin t,0) and (0,0,1), F(t)=B(t)R(t²), and S=diag(1,1,49/50). Form M=F(2t)ᵀSF(t). Derive dM from the product rule using interval enclosures of both frames and their derivatives, including the factor 2 on the target frame derivative. S is a fixed ambient contraction, not a truncated translation model.

Four declared cells have centres 1/8,3/8,5/8,7/8 and radius 1/256. Interval arithmetic encloses every point of each cell; the union does not cover [0,1]. Each cell must certify det M>0 and s=sqrt((M00+M11)²+(M10−M01)²)>0. The entrywise polar derivative dU=dA/s−A(x dx+y dy)/s³ returns an interval matrix for the entire cell.

The independent oracle follows from M=R(−4t²)diag(cos t,49/50)R(t²), whose diagonal is positive on these cells. Thus polar(M)=R(−3t²), dU=R(−3t²)G(−6t). Three fixed points per cell verify oracle containment and the direct formula. These finite checks supplement the interval enclosure construction; they do not themselves prove coverage.

## Uniform amplification bound and refusals

Writing z=(x,y), the derivative of z/||z|| has Euclidean norm at most ||dz||/s. Mapping z to A multiplies the norm by sqrt(2), and ||dz||≤sqrt(2)||dM||F. Consequently ||dU||F≤2||dM||F/s. Use the interval upper bound for ||dM||F and certified lower bound for s to obtain a whole-cell amplification bound. No extra triangle-inequality factor is needed because the normalized-vector derivative is an orthogonal projection divided by s.

Uncertain determinant, singular and reflection inputs must refuse with POSITIVE_DETERMINANT_REQUIRED. Such refusal is a failure to certify the domain, not a statement that every matrix in an uncertain box is invalid.

## Reproduction and limits

check.py uses the pinned python-flint 0.9.0 wheel, 128-bit Arb, one thread, a 40-second worker timeout and 1 GiB address limit. Run with --wheel <wheel> --output <fresh>, then verify.py for retained interval margins and integrity controls. Eight outcomes comprise one edge-1 mutation, four cell certificates and three domain refusals; each cell includes three oracle checks. Frozen sources and native environment are retained.

This advances from pointwise exact dM inputs to interval product-rule dM on four synthetic cells. Frame derivatives still come from an exact analytic path. Numerical projector/resolvent derivatives, frame/transport error eta/rho, higher derivative bounds, full composer integration and physical S1–S4 remain open. No physical cell budget or cutoff agreement is claimed. Independent audit is pending.
