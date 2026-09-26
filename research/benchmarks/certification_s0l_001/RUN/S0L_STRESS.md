# S0l: nonzero comparison and conditional finite-width extraction

Parent: `18e2419497dec0db70b63dad3bc6194c61d95414`. Responds to Claude source
comment 5806117739 and Codex review 5806138647. Synthetic only; no physical
Hamiltonian, eigensolver, sweep, v078 correction, or physical class claim.

## Geometry and domain-wide reduction

Retain S0k's curved Kato frame, partial shift, positive orientation and both
deficits. Add the ambient normal-axis Rodrigues angle `4*b*t*(1-t)` to edge 2.
This vanishes at both corners, so the principal repair remains delta=-epsilon
and the integer remains the winding w. The lift-speed bound gains `4*abs(b)`.
The seam singular values and partial-shift deficit identities are unchanged:
the additional rotation acts in the same tangent plane.

For two systems the exact relative repaired edge-2 angle is

    2*pi*(w_b-w_a)*t + (epsilon_b-epsilon_a)*(t-chi(t))
        + 4*(b_b-b_a)*t*(1-t).

Edge 1 has zero relative angle. This follows by cancelling the Kato frame
phases in Q_target^T J_b Q_source as in S0k, then applying each actual corner
repair. The Frobenius distance is `2*sqrt(2)*abs(sin(angle/2))`.
Evaluate this expression on 1024 closed interval cells per edge. This is an
analytic reduction with uniform interval coverage, not a generic numerical
projector bound. Independently check the matrix pullback identity at nine
points on each edge for passing cases; those checks alone are not a proof.

Equal-winding fixtures include delta-epsilon=-0.75, and b_b-b_a=0.70 and 0.75.
The initial development choice epsilon_b=1.25 failed CHARGED_CORNER_BRANCH;
epsilon_b=-0.5 preserves that existing guard. No guard was relaxed.
The latter two have exact maximum distances respectively about 0.970 and
1.036. The Frobenius threshold 1 corresponds to angle
`2*asin(1/(2*sqrt(2)))`, NOT pi/3 (which applies to an operator-norm gate).
The 0.75 equal-class fixture must refuse: the screen is sufficient, not
necessary for class equality. An unequal-winding matched control also refuses.

## Finite-width error model and limitation

Declare a uniform lifted-phase error eta on each edge, without claiming to
have computed it from numerical frames. Errors in a continuous lift telescope
to two endpoint errors; enlarge each computed edge total by [-2 eta,2 eta].
The resulting q radius is `2*eta/pi`, plus arithmetic enclosure error. Include
`2*eta` in the per-cell branch guard. For eta=0.1, q radius is about 0.06366
and signed integers -1,+1 pass; eta=0.2 gives radius about 0.12732 and fails
the inherited halfwidth <=1/8 rule, despite containing a unique integer.

This checks the geometric extraction consumer under declared finite-width
premises. It does NOT close Q3/P3's missing derivation of realistic error
bounds from numerical projector/frame/transport computations. General Kato
transport, uniform numerical derivatives and physical S1-S4 remain open.

## Reproduction

Run driver.py with the locked python-flint wheel and a fresh --output path;
then verify.py on the retained RUN. The frozen 15-job inventory has no adaptive
search, retries or sweeps; inherited limits are 40 seconds/job, 180 seconds
total, 1 GiB/worker, 128-bit precision, one thread. Retained outcome counts
are evidence only after successful execution. Preserve prior S0k unchanged.
