# S0m: centred matrix screen and phase/repair perturbations

Parent `049578c4378a6530f78350096a1cfdc64cb3f949`; Claude source 5806294776.
This addresses S0l S1-S4 within the same exact synthetic geometry. No physical
Hamiltonian, eigensolver, v078 correction or parameter sweep is involved.

## Actual matrix screen

At each cell midpoint compute Ja, Jb and Q by the existing frame, ambient
Rodrigues, overlap, polar and principal-repair functions. Compute
D=Ja-Q_target^T Jb Q_source in Arb matrix arithmetic. The acceptance expression
does not evaluate the closed-form relative angle or its sine.

There are exactly 4096 cells per edge. For midpoint m and half-cell r,
the mean-value bound is ||D(t)||F <= ||D(m)||F + L*r. For rotations, ||R'||F
equals sqrt(2) times angular speed and ||R||2=1. The product rule gives
L=sqrt(2)*(va+vb+vq_target+vq_source). Each repaired seam speed is bounded by
pi/d on edge 1, and |2*pi*w-pi/d+epsilon|+4|b|+15|delta|/8 on edge 2.
The existing synthetic identity Q=R(2*pi*(c_b-c_a)*y) supplies its speeds:
edge 1 has sum 2*pi*(|c_b(1)-c_a(1)|+|c_b(0)-c_a(0)|); edge 2 has
pi*|1/d_a-1/d_b| (the bottom source is constant). These are domain-wide
analytic derivative bounds, not derivatives estimated from samples.

All points in both edges are covered by the cell bounds. The norm test uses
the computed matrix centres, with a conservative sum of derivative bounds;
it does not exploit cancellation in D'. Smoothness, orientation and uniform
invertibility follow from the inherited synthetic formulas and gates.
This is a synthetic matrix-screen calibration, not a general numerical
projector/transport certificate. It removes interval polynomial dependency
inflation from cell evaluation by evaluating each centre at a point and
charging variation once. It does not improve S0l's archived polynomial code.

The frozen amplitudes 0.70, 0.72, 0.722 and 0.75 test a passing margin, a
smaller passing margin, an unresolved cell budget and a genuinely over-gate
case. Report the smallest certified margin among this finite inventory;
do not call it a global optimal resolution. Inconclusive is not evidence of
unequal classes. Include differing-defect and unequal-winding controls.

## Sample perturbations and repair charge

For each of 65 samples, multiply the actual repaired seam matrix by R(e_k).
Edge 2 alternates -eta,+eta and ends at +eta; edge 1 uses the opposite
pattern. On edge 2 also add rho*chi(t) to the rotation error. Thus the sample
increments themselves are perturbed, including the endpoint extremes.
The phase perturbation and repair perturbation are separate declared inputs.
They are not obtained from a numerical projector computation.

The branch guard is speed/64 + 2*eta + (15/8)*rho/64 < pi/2 on edge 2;
edge 1 omits rho. It runs before angle extraction. The increments telescope
under that guard. Widen the edge totals by 2*eta each and edge 2 by rho once.
The q radius is (4*eta+rho)/(2*pi) plus arithmetic. With eta=rho=0.1, the
perturbed centres shift by +0.5/(2*pi); their widened intervals still contain
the exact signed winding. eta=0.15,rho=0.2 exceeds the 1/8 halfwidth gate.
eta=0.8 deliberately fails the branch guard. These are conditional error
consumer checks, not claims that the physical error ledger has been met.

## Reproduction and next dependency

Use the locked python-flint wheel, one thread, 128-bit precision, 1 GiB per
worker, 40 seconds/job and 180 seconds total. Run driver.py with --wheel and
a fresh --output path; run verify.py on retained RUN. Ten jobs, no adaptive
refinement or retry. Prior evidence stays frozen. Independent review pending.

Next dependency: derive projector, frame, seam and repair error bounds from
uniform numerical enclosures and bind them to these consumers. General
numerical Kato transport, Q3/P3 and physical S1-S4 remain open.
