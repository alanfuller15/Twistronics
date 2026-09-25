# S0e: integer and partial-shift corrections

2026-09-23. Evidence parent: `2260ed4958785f49842d9cf70e885811d46f5721`.
Responds to Claude source comment 5804846025 and Codex review comment 5804864384.
Independent review pending. Physical S1-S4 remain NOT_IMPLEMENTED / NOT_RUN /
BUDGET_NOT_FROZEN. No physical calculation, class, or cutoff agreement is claimed.

## Integer enclosure

The lift now requires the candidate integer inside its interval, half-width at
most 1/8, and containment inside that integer's nearest-integer cell. The latter
is conservative and implies uniqueness. A fixed 16-step path with total angle
2*pi+1/100 is refused even though its small endpoint mismatch passes the closure
consistency gate. A closed wider loop is separately refused by the width cap.

Exact closure and continuous per-step variation are explicit caller obligations,
represented by required declarations. These booleans are not independently
validated certificates; the future composition layer must bind them to retained
repair and whole-step evidence. The open-path negative control deliberately
supplies the false exact-closure declaration to verify the enclosure still refuses.
Containment alone cannot prove integrality. A small closure residual is never a
substitute for exact closure. Positive adjacent dot products select increments
inside (-pi/2,pi/2); they do not exclude hidden turns between samples. The fixture
uses the explicitly known monotone angle path, whose step size is below pi/2.

## Partial-shift interface

`seam_map(F1,S,F0,gram_tolerance,map_target)` forms M=F1^T S F0 internally and
returns an enclosure of J=F1 polar(M) F0^T. F0 and F1 are the original frame
balls, not shifted frames. Exact orthonormal frames contained by those balls
remain a caller obligation. Gram tolerance is a sanity gate, not the physical
frame-distance certificate.

Positive determinant and polar denominator are checked. The sufficient gate
rho=||I-M^T M||_F <= 39/400 implies lambda_min(M^T M)>=361/400 and hence
s_min(M)>=19/20. This conservative Frobenius condition may refuse overlaps that
would pass a sharper singular-value bound. It cannot falsely pass on that account.

The fixed 3-dimensional partial shift is diag(1,1,0). F0's second column is
(0,c,sqrt(1-c^2)); both original frames remain orthonormal. c=24/25 passes;
c=9/10 refuses. This explicitly distinguishes deletion loss from frame error.
The final interval evaluation uses the unshifted F0 on the right of J.
A separate diag(2,-1) control reaches the negative-determinant refusal with a
nonzero conformal denominator.

## Nonfinite and composition boundaries

An additive copy of the primitive module defines `NonfiniteEnclosure` at both
bound serialization and LDL-pivot checks. Public S0e arithmetic entry points
translate only this class to INCONCLUSIVE. Finite exp input that overflows the
backend exercises both paths. An ordinary ArithmeticError with the same text
remains an execution error; a dimension error remains a ValueError.

The composition reason gate requires each role's exact accepted reason. A
CERTIFIED / BUDGET_CONDITIONALLY_SUFFICIENT record is refused as a lift result.
Successful allow-list admission is named SYNTHETIC_REASON_GATE_ONLY: it does not
validate provenance or produce (q_a,q_b,relative). Full composition remains open.

## Retained validation and next gate

14/14 fixed expected outcomes: four CERTIFIED synthetic implications, eight
INCONCLUSIVE controls, and two deliberate EXECUTION_ERROR controls. Ten runner
protocol checks pass. The portable run binds 27 files and every source snapshot.
Precision 128 bits, one worker, 30 seconds/job, 180 seconds total, 1 GiB worker
address space, no adaptive retry. python-flint 0.9.0 wheel hash:
`376b88cacd30612479e839ffdba887599d3f9c8c0e214852bf80bb2b194e4d76`.

Next: independent S0e audit, then bounded synthetic composition of projector
error into frame enclosures, intended shifts, exact corner repair, both complete
lifts and the joint integer. Riesz spectral splits must be certified uniformly;
full-size interval-power wrapping and derivative error lemmas remain open.
Frozen S0a-S0d evidence and v078 implementation ownership are unchanged.
