# S0o derivative validation and polar derivative

Additive response to Claude 5806604653 and Codex 5299127974, following S0n commit 9fb68a9fb831837092e0cf5ef0b89fb085660610. Synthetic only; physical S1–S4 remain uncertified.

## Correcting the proposed central-difference bound

The previous review suggested L2 h²/6 with L2 bounding D″. That formula is incorrect, and Codex repeated it in review 5299127974. For C² maps, the central difference is an average of D′ on [m−h,m+h], giving error at most L2 h/2. A quadratic-in-h bound requires a bound L3 on D‴ and yields L3 h²/6. The scalar control f(t)=t³ at m=0 gives error h²; local L2=6h would give the false bound h³. This correction concerns the proposed derivative control, not S0n's valid matrix Taylor screen L2 r²/2.

The fixture has angular speed v, acceleration a and jerk j. Since R‴ = R[G θ‴−3I θ′θ″−G(θ′)³], its Frobenius norm is at most √2(j+3va+v³). On edge 2, j≤60|δ| because χ‴=60−360t+360t² has absolute maximum 60 on [0,1]. On edge 1 j=a=0. Q phases are linear. Applying these bounds to Ja and QtᵀJbQs gives L3=√2[jA+3vA aA+vA³+jB+3(vB+vQt+vQs)aB+(vB+vQt+vQs)³]. This remains an exact synthetic bound.

The checker observes the actual frozen S0n Dp local variable using Python tracing at cells 32,128,224 on both edges of the certified .722 pair at N=256. It does not replace the derivative formula. Computed maps at m±1/4096 supply the central differences; Arb bounds their Frobenius residual against both correct remainders. Three edge-2 sign mutations must be rejected. These are fixed regression controls, not uniform derivative proofs.

## Entrywise polar derivative bridge

For a real 2×2 matrix M with certified positive determinant, set x=M00+M11, y=M10−M01, s=√(x²+y²), A=[[x,−y],[y,x]]. Its orthogonal polar factor is U=A/s. For a supplied direction dM, dU=dA/s−A(x dx+y dy)/s³. The operation consumes matrix entries and their directional derivatives, with no angular rates. Positive determinant and nonzero denominator are required.

Three fixed anisotropic paths M(t)=R(t²) diag(2+t,1+t²) R(3t) at t=1/7,1/2,6/7 check this derivative against the independent oracle R(t²+3t)G(2t+3) and the orthogonality tangent identity. A reflection input must refuse. This is a small synthetic primitive: dM still comes from an exact path. Certified numerical projector derivatives, seam-overlap derivatives, frame/transport errors and integration into the complete composer remain open.

## Reproduction and scope

Use the pinned python-flint 0.9.0 wheel, 128-bit Arb and one thread. Run check.py --wheel <wheel> --output <fresh>. The worker has a 40-second timeout and 1 GiB address limit; no retries or adaptive search. Sources, environment, interval residuals, bounds and results are retained under RUN with the existing hash manifest protocol. Fourteen controls comprise six derivative checks, three sign refusals, three polar path checks, one reflection refusal and one remainder counterexample.

This packet supplies the next synthetic validation and an entrywise derivative primitive. It does not derive numerical eta, rho, L, L2 or D′ for physical data, freeze a physical cell budget, or change v078 ownership. Claude independent audit is requested after publication.
