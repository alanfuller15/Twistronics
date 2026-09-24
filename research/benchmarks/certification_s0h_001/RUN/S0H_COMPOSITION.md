# S0h: one analytic rectangle and separately screened relative data

Status: synthetic implementation pending independent audit. No physical
Hamiltonian, archived physical data, spectral sweep, or physical S1–S4
execution is involved. This packet addresses the common
geometry requested in Claude source comment 5805215136 at S0g commit
5c119991786da432148b0393c9bb66492b14eaa3. It does not generalize the fixture
identities into a generic certifier.

## Common geometry and computed gauge

For t=1/32 and t=1/40 separately, let c=(1-t²)/(1+t²), s=2t/(1+t²),
E=((c,0,-s),(0,1,0)) (columns), φ(x,y)=x/4+y/2+xy/4, and
F=Rz(φ)E on [0,1]². P=FFᵀ is an exact analytic rank-two projector.
The program computes EᵀE=I and EᵀGzE=cJ using rational matrices, then
checks the connection cancellation with the selected gauge rate.

The bottom gauge is O(x,0)=R(-cx/4). The vertical solution with that
x-dependent initial value is R(-c(y/2+xy/4))O(x,0)=R(-cφ).
Thus K=FO is the bottom-then-vertical Kato frame: KᵀK_x=KᵀK_y=0,
PK=K, and differentiation gives K_j=[P_j,P]K. This is an analytic
identity over the whole rectangle, not a sample-based residual inference.
One global oriented chart suffices; chart changes and general strip ODE
enclosures remain unimplemented. The initial oriented basis is E.

## Seams with both deficits

Both oriented boundary shifts are S=diag(1,1,0), an actual partial
projection. Every overlap is formed internally as M=K_targetᵀ S K_source.
With Δ=φ_target-φ_source and D=diag(c,1), it equals
R(cφ_target) D R(-Δ) D R(-cφ_source). Its determinant is c⁴>0 and
s_min(M)≥c². The 19/20 gate is checked both analytically and through
the sufficient cell enclosure ||I-MᵀM||_F≤39/400 on 64 closed cells
covering each edge. Endpoints and entire cell balls use the same frames.

The source deletion L=K_sourceᵀ(I-SᵀS)K_source and off-target term
R=(I-K_target K_targetᵀ)S K_source are computed separately. The exact
identity I-MᵀM=L+RᵀR follows from orthonormality. Interval residual
containment checks are consistency checks, not proofs of this identity.
Both traces are certified strictly positive at the origin seam; cell
enclosures for each deficit are retained.

The SO(2) polar is computed from (tr M, M21-M12), with positive
determinant and positive real-part gates. Its angle is
g(Δ)=cΔ-atan(k tan Δ), k=2c/(1+c²), using the continuous small-angle
branch for this fixture (Δ ranges from 1/4 to 3/4).

## Actual corner repair and both lifts

The same seam maps form A=J2(1)J1(0), B=J1(1)J2(0). The conservative
charged gate is ||A-B||_F+2(2η+η²)≤1 with η=1/128. A and B here
are enclosures of exact maps; the charge is extra allowance, not a claim
that an approximate physical map was validated.

δ=Arg(AᵀB) is evaluated from the actual corner product. Its enclosure
is used without midpoint replacement. Repair is exactly the CASE sign
and profile: J2_hat(x)=J2(x)R(δχ(x)), χ=10x³-15x⁴+6x⁵.
Since SO(2) commutes and exp(δJ)=AᵀB, the repaired corner identity
is exact. The nonzero defect is retained; this is not an already-closed
loop fed into a nominal repair routine.

Both edge angle changes are accumulated from adjacent polar maps. The
uniform derivative bound |g'|≤c+1/k and Δ'=1/4 gives a whole-cell
variation bound. The repaired edge adds |δ| max χ'=15|δ|/8. Each
bound divided by 64 must be below π/2, and every computed increment
also has positive real part. Thus the principal increments follow the
continuous lifts with no missed between-sample turns.

q=(Δβ_hat-Δα)/(2π) must contain zero with absolute bound below 1/8,
and exact positive-sign gluing is separately required. The fixture has
q=0 by the small-angle corner identity. Wrong-sign repair is refused;
near-zero numerical closure alone never establishes integrality.

## Separate relative result

The two planes share the same R³ ambient fibre and identity embedding.
E_bᵀE_a=diag(v,1), v=c_a c_b+s_a s_b>1/2. This gives the exact
uniform singular gate for the cross-plane map. Its coordinate polar Q
is computed from K_bᵀK_a at the source and target of every cell.
Both repaired edges are screened using
||J_a-Q_targetᵀ J_b_hat Q_source||_F≤1. Each relative angle is at
most π/3, so their sum is at most 2π/3<π. This result is independent
of subtracting the individual integers. The output contains individual
q records and a separate relative status. Deliberate Q refusal and a
zero screen budget preserve both individual results as the relative
result becomes inconclusive. These controls test refusal, not a
physical counterexample or different synthetic topological classes.

## Full-dimension numerical bridge calibration

Two additional fixed jobs use dimensions 196 and 308, at (x,y)=(1/2,1/2).
Pad the same analytic K with zeros and apply the dense rational orthogonal
Householder U=I-2·11ᵀ/n. H=2(I-KKᵀ) has exactly two zero eigenvalues
and n-2 eigenvalues equal to two; this proves the spectral-ratio premises
without sampled gaps. Dense entries are passed to the existing Riesz
primitive at 256 bits, radius one and 32 nodes. The projector error target
is 1/1024. There is no sparse/block shortcut inside the primitive.

The candidate frame is E=(uK1+wν,K2), where ν is the transformed unit
normal, u=9999/10001, w=200/10001 and u²+w²=1. Exact PE=(uK1,K2)
has normalized projection K since u>0. The numerical projector error
upper endpoint is passed directly to the existing frame bridge with
budget 1/16. Thus all its conditional premises are proved for this
fixed point and the projected frame matches the analytic gauge there.
The candidate has a nonzero off-plane component; it is not simply K.

Two fixed negative jobs reduce the contour to two nodes or the frame
budget to 1/1024. They must return inconclusive. These tests exercise
dense full-size arithmetic on a two-level synthetic spectrum, not the
conditioning, spectral spread or uniform-cell cost of the physical
Hamiltonian. No full-dimension uniform Riesz cost conclusion follows.

## Frozen evidence and remaining work

SPEC pins external source dependencies by SHA-256 before workers run.
The locked wheel/native environment, source snapshots, fixed twelve-job
budget, atomic records, manifest and completion marker follow the
reviewed S0g protocol. A dependency mismatch is inconclusive. Source
pins establish reproducibility under the reviewed SPEC, not external
authenticity. The fixed input family is defined by the frozen source.

This joins analytic projectors, gauges, two-point seams, charged repair,
both lifts and a Q-pullback comparison, plus pointwise full-dimension
numerical Riesz-to-frame calibration. It does not yet supply uniform
numerical Riesz output over the rectangle or physical tolerances.
Representative full-dimension conditioning, general derivative/strip bounds,
nontrivial chart transitions and physical budgets remain open. Synthetic
success does not certify a graphene class or cutoff agreement.
