# S0i: nonzero sewing classes and integer consistency

Status: pending independent audit. Source findings: Claude 5805761394,
Codex 5805777568. Parent c7ed0d08f2ecb07c01fff23b6091ed06184e0d43.
This additive packet retains S0h unchanged. All geometry is synthetic.

## Geometry and reference class

Use the S0h analytic plane, global oriented Kato frame K, and partial
projection S. On one declared seam e, replace the ambient shift by
S_w(t)=S U_s(t), where U_s=K_s R(f(t)) K_s^T + I-P_s and
f(t)=(2*pi*w+d)t, w an integer and d=1/4. U_s is exactly orthogonal,
so S_w is a partial isometry. The actual overlap is formed internally as
K_target^T (S K_source R(f)). Its polar is J_base R(f), since right
orthogonal multiplication commutes with polar decomposition. This is a
declared parameter-dependent synthetic sewing, not a physical lattice
translation or a claim about an unchanged physical model.

The same projection/gauge proofs from S0h apply. Singular values are
unchanged. Deletion and off-target deficit traces are unchanged by the
right rotation; the unrotated interval singular bound avoids unnecessary
wrapping. This still tests a flat connection. It tests nonzero sewing
classes and sign conventions, not curvature or Kato path-order dependence.

Let delta0 be the S0h corner defect. For winding on seam 2, the new
principal delta is delta0-d; for winding on seam 1 it is delta0+d.
The corner product is calculated rather than substituting this formula.
The charged branch gate verifies the chosen branch. Positive quintic
repair J2 R(delta*chi) is structural and checked before lifting.
Since chi(1)-chi(0)=1, exact gluing and the S0h zero-class identity give
q=w for seam 2 and q=-w for seam 1. The frozen expectations are +1,
-1, and -1 for the swapped-edge positive winding. These values are test
oracles; the certifier derives its integer from the numerical enclosure.

## General integer and angle handling

The polar formula uses (tr M,M21-M12) with positive determinant and
strictly positive squared denominator. It has no absolute real-part
gate. Adjacent increments retain their positive real-part gate. The
uniform variation bound adds |2*pi*w+d| on the winding edge and
15|delta|/8 on the repaired edge. All 64 cells on each edge are checked.
The q enclosure is obtained by accumulated beta minus alpha increments.

Integer extraction computes ceil(lower) and floor(upper), requires these
to coincide and requires half-width <=1/8. It therefore checks actual
containment and uniqueness, including negative integers. Empty, multiple
and too-wide enclosures are deliberate refusal controls. The public
routine is not restricted to a zero-centered interval.

The positive repair sign is checked independently of numerical width.
The wrong-sign control returns EXACT_GLUING_REQUIRED before containment
can accidentally hide a convention error. Its quarter-radian defect is
substantially larger than the S0h residual defect.

## Relative composition

The two S0h planes retain their proved common-fibre Q gate. Both repaired
edges are compared with Q at their source and target over complete
parameter cells (256 fixed cells per edge, independently of the 64 lift
cells). Equal winding +1/+1 and -1/-1 must certify. The +1/-1
pair must independently refuse its edge screen while retaining each
individual integer. A failed sufficient screen alone is not a proof of
different classes; in this fixture their individually certified integers
supply that distinction.

If a screen is certified and the individual integers disagree, composition
returns EXECUTION_ERROR. A labeled fault-injection control corrupts one
integer after a real equal-class screen to exercise this state transition.
It is intentionally inconsistent data, not an alleged geometric example.
There is no claim here of a generic authenticated record-ingestion API.

## Calibration, provenance and limits

The four unchanged S0h dense Riesz/bridge fixtures run again at dimensions
196/308 with the frozen 256-bit settings and deliberate budget failures.
Each worker now retains wall time, user/system CPU time and Linux peak
RSS in KiB; the summary copies those counters. Timing is observational,
machine-dependent calibration, not a physical runtime promise.

SPEC pins reused sources by SHA-256. The runner verifies the locked
python-flint wheel and installed native artifacts, executes source
snapshots with fixed budgets, and writes atomic manifest-bound records.
Expected integers are checked by the runner separately from certification.
No archived physical code is imported. Uniform numerical Riesz coverage,
representative spectra/conditioning, curved strip transport, chart changes
and physical S1-S4 remain open. No graphene class is inferred.
